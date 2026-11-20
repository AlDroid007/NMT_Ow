"""Integration test of the cloud schema and sync against real PostgreSQL + PostgREST (Docker).

Supabase = PostgreSQL + PostgREST + GoTrue (auth) + more. This test runs the first two
in Docker with the roles Supabase uses (anon, authenticated, authenticator), applies
supabase/migrations/*.sql and puts a tiny stand-in for GoTrue in front: it mints
signed JWTs for e-mail codes, so the app's real SupabaseClient talks HTTP to it
exactly as to Supabase.

Checks: migration applies (twice), begin/submit of trainings with answers and hints,
statistics and streak, two-device sync, no direct writes to server-managed tables,
RLS isolation between accounts, admin read access and views, anon gets nothing,
one profile per account, account deletion.

usage: python tests/cloud_integration_test.py        (needs Docker; containers are removed afterwards)
"""

import base64
import glob
import hashlib
import hmac
import http.server
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
import uuid

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

PG_IMAGE = "postgres:17-alpine"
PGRST_IMAGE = "postgrest/postgrest:v12.2.12"
NAME = f"nmt-cloud-test-{os.getpid()}"
JWT_SECRET = "nmt-integration-test-secret-at-least-32-chars"
ANON_KEY = None  # set in main()

BOOTSTRAP_SQL = """
create role anon nologin noinherit;
create role authenticated nologin noinherit;
create role authenticator login noinherit password 'authpass';
grant anon, authenticated to authenticator;
create schema auth;
create table auth.users (id uuid primary key, email text unique, created_at timestamptz default now());
create function auth.uid() returns uuid language sql stable as $$
  select nullif(current_setting('request.jwt.claims', true)::json ->> 'sub', '')::uuid
$$;
grant usage on schema auth to anon, authenticated;
grant execute on function auth.uid() to anon, authenticated;
grant usage on schema public to anon, authenticated;
"""


def sh(*args, check=True, input_text=None):
    return subprocess.run(args, check=check, capture_output=True, text=True, input=input_text)


def psql(sql):
    out = sh("docker", "exec", "-i", f"{NAME}-db", "psql", "-v", "ON_ERROR_STOP=1", "-U", "postgres", "-q", "-t", "-A",
             input_text=sql, check=False)
    if out.returncode:
        raise RuntimeError(f"psql failed:\n{out.stderr}")
    return out.stdout.strip()


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def b64url(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def make_jwt(claims):
    head = b64url(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    body = b64url(json.dumps(claims).encode())
    sig = hmac.new(JWT_SECRET.encode(), f"{head}.{body}".encode(), hashlib.sha256).digest()
    return f"{head}.{body}.{b64url(sig)}"


# --- stand-in for Supabase Auth + gateway ----------------------------------------------------


class Gateway(http.server.BaseHTTPRequestHandler):
    rest_url = None
    codes = {}
    refresh = {}  # refresh token -> user id

    def log_message(self, *_):
        pass

    def _send(self, status, body=None, headers=None):
        raw = b"" if body is None else (body if isinstance(body, bytes) else json.dumps(body).encode())
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _session(self, uid, email):
        token = str(uuid.uuid4())
        self.refresh[token] = (uid, email)
        exp = int(time.time()) + 3600
        return {"access_token": make_jwt({"sub": uid, "role": "authenticated", "email": email, "exp": exp}),
                "token_type": "bearer", "expires_in": 3600, "expires_at": exp, "refresh_token": token,
                "user": {"id": uid, "email": email}}

    def _proxy(self, method):
        length = int(self.headers.get("Content-Length") or 0)
        data = self.rfile.read(length) if length else None
        if self.headers.get("apikey") != ANON_KEY:
            return self._send(401, {"message": "Invalid API key"})
        path = self.path[len("/rest/v1"):]
        req = urllib.request.Request(self.rest_url + path, data=data, method=method)
        for h in ("Authorization", "Prefer", "Content-Type", "Accept"):
            if self.headers.get(h):
                req.add_header(h, self.headers[h])
        try:
            with urllib.request.urlopen(req) as resp:
                return self._send(resp.status, resp.read())
        except urllib.error.HTTPError as exc:
            return self._send(exc.code, exc.read())

    def do_GET(self):
        self._proxy("GET")

    def do_PATCH(self):
        self._proxy("PATCH")

    def do_POST(self):
        if self.path.startswith("/rest/v1/"):
            return self._proxy("POST")
        if self.headers.get("apikey") != ANON_KEY:
            return self._send(401, {"message": "Invalid API key"})
        body = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"{}")
        if self.path.startswith("/auth/v1/otp"):
            self.codes[body["email"]] = "654321"
            return self._send(200, {})
        if self.path.startswith("/auth/v1/verify"):
            email = body["email"]
            if self.codes.get(email) != body.get("token"):
                return self._send(403, {"error_code": "otp_expired", "msg": "Token has expired or is invalid"})
            uid = psql(f"select id from auth.users where email = '{email}'") or str(uuid.uuid4())
            psql(f"insert into auth.users (id, email) values ('{uid}', '{email}') on conflict do nothing")
            return self._send(200, self._session(uid, email))
        if self.path.startswith("/auth/v1/token"):
            pair = self.refresh.pop(body.get("refresh_token"), None)
            if not pair:
                return self._send(400, {"error_code": "refresh_token_not_found", "msg": "Invalid Refresh Token"})
            return self._send(200, self._session(*pair))
        self._send(404, {"message": "not found"})


# --- the test ----------------------------------------------------------------------------------


def start_stack():
    pg_port, rest_port = free_port(), free_port()
    sh("docker", "network", "create", NAME)
    sh("docker", "run", "-d", "--name", f"{NAME}-db", "--network", NAME, "-e", "POSTGRES_PASSWORD=postgres",
       "-p", f"127.0.0.1:{pg_port}:5432", PG_IMAGE)
    for _ in range(60):
        if sh("docker", "exec", f"{NAME}-db", "pg_isready", "-U", "postgres", check=False).returncode == 0:
            try:
                psql("select 1")
                break
            except RuntimeError:
                pass
        time.sleep(1)
    psql(BOOTSTRAP_SQL)
    migrations = sorted(glob.glob(os.path.join(ROOT, "supabase", "migrations", "*.sql")))
    assert migrations, "no migrations"
    for _ in range(2):  # must be safe to run again
        for path in migrations:
            with open(path, encoding="utf-8") as f:
                psql(f.read())
    sh("docker", "run", "-d", "--name", f"{NAME}-rest", "--network", NAME,
       "-e", f"PGRST_DB_URI=postgres://authenticator:authpass@{NAME}-db:5432/postgres",
       "-e", "PGRST_DB_SCHEMAS=public", "-e", "PGRST_DB_ANON_ROLE=anon", "-e", f"PGRST_JWT_SECRET={JWT_SECRET}",
       "-p", f"127.0.0.1:{rest_port}:3000", PGRST_IMAGE)
    rest_url = f"http://127.0.0.1:{rest_port}"
    for _ in range(60):
        try:
            urllib.request.urlopen(rest_url + "/", timeout=2)
            break
        except Exception:
            time.sleep(1)
    return rest_url


def stop_stack():
    sh("docker", "rm", "-f", f"{NAME}-rest", f"{NAME}-db", check=False)
    sh("docker", "network", "rm", NAME, check=False)


def raw(base, method, path, token=None, body=None, prefer=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"{base}/rest/v1/{path}", data=data, method=method, headers={"apikey": ANON_KEY})
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    if prefer:
        req.add_header("Prefer", prefer)
    try:
        with urllib.request.urlopen(req) as resp:
            raw_body = resp.read()
            return resp.status, (json.loads(raw_body) if raw_body else None)
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode()


def expect_denied(status, what):
    assert status in (401, 403, 404, 400) or status >= 400, f"{what}: got {status}"


def check_access_gate(base):
    """The web app's closed access: login + password -> device token (supabase/migrations/*_access_gate.sql)."""
    psql("select public.set_gate_login('Tester', 'secret123')")
    status, _ = raw(base, "GET", "app_gate_logins?select=login")
    assert status >= 400 or _ == [], f"anon read gate logins: {status} {_}"
    status, _ = raw(base, "POST", "rpc/set_gate_login", body={"p_login": "x", "p_password": "yyyyyy"})
    expect_denied(status, "anon set_gate_login")
    status, tok = raw(base, "POST", "rpc/gate_sign_in", body={"p_login": "tester", "p_password": "wrong"})
    assert status == 200 and tok is None, (status, tok)
    status, tok = raw(base, "POST", "rpc/gate_sign_in", body={"p_login": " TESTER", "p_password": "secret123"})
    assert status == 200 and tok, (status, tok)
    assert raw(base, "POST", "rpc/gate_check", body={"p_token": tok}) == (200, True)
    assert raw(base, "POST", "rpc/gate_check", body={"p_token": str(uuid.uuid4())}) == (200, False)
    psql("update public.app_gate_logins set enabled = false where login = 'tester'")
    assert raw(base, "POST", "rpc/gate_check", body={"p_token": tok}) == (200, False)
    psql("delete from public.app_gate_logins")
    print("OK    access gate")


def run_checks(base):
    from datetime import datetime

    from nmt_tutor import storage
    from nmt_tutor.cloud import sync
    from nmt_tutor.cloud.http import CloudError
    from nmt_tutor.cloud.settings import CloudSettings
    from nmt_tutor.cloud.supabase import SupabaseClient
    from nmt_tutor.engine import build_session_plan, build_session_result
    from nmt_tutor.profiles import new_profile, touch
    from nmt_tutor.selftest import _answered_session
    from nmt_tutor.storage.keystore import MemoryKeyStore

    client = SupabaseClient(CloudSettings(base, ANON_KEY))
    ks = MemoryKeyStore()
    tmp_a, tmp_b, tmp_c = (tempfile.mkdtemp(prefix=f"nmt_cloud_{n}_") for n in "abc")
    try:
        legacy = build_session_result(build_session_plan(["math"], "quick"), "quick", True)
        dev_a = storage.open_repository(tmp_a, keystore=ks, import_legacy=False)
        dev_b = storage.open_repository(tmp_b, keystore=ks, import_legacy=False)
        prof = new_profile("Інтеграція", subjects=["math"], targets={"math": 175}, exam_date="20.05.2027")
        dev_a.save_profile(prof)
        pid = prof["id"]
        cpid = sync.cloud_id(pid)
        sa = dev_a.for_profile(pid)
        sa.save_result(legacy)

        try:
            client.verify_code("liza@example.com", "000000")
            raise AssertionError("wrong code accepted")
        except CloudError as exc:
            assert "Код" in str(exc), exc
        client.send_code("Liza@Example.com ")
        s_a = client.verify_code("liza@example.com", "654321")
        assert sync.fetch_account_profile(client, s_a) is None
        sync.attach(dev_a, pid, s_a)
        assert sync.sync_profile(dev_a, client, pid) == (1, 0)
        assert sync.sync_profile(dev_a, client, pid) == (0, 0)
        assert psql("select imported from public.sessions") == "t"
        assert psql(f"select count(*) from public.profile_meta where profile_id = '{cpid}'") == "1"
        print("OK    profile + old history uploaded (imported session)")

        # A real training: begin on the server, answers and hints at the end.
        uid = uuid.uuid4().hex
        job = sync.prepare(dev_a, pid)
        began = sync.begin_session(client, job, uid, ["math"], "quick", True)
        assert began["allowed"] and began["session_id"] == sync.cloud_id(uid)
        assert sync.begin_session(client, job, uid, ["math"], "quick", True)["session_id"] == began["session_id"]
        assert psql(f"select status from public.sessions where id = '{sync.cloud_id(uid)}'") == "active"
        res = _answered_session(["math"], session_uid=uid, started_at=datetime.now().isoformat(timespec="seconds"))
        sa.save_result(res)
        assert sync.sync_profile(dev_a, client, pid) == (1, 0)
        sid = sync.cloud_id(uid)
        assert psql(f"select status || ' ' || imported::text || ' ' || (finished_at >= started_at)::text "
                    f"from public.sessions where id = '{sid}'") == "finished false true"
        n_ans = int(psql(f"select count(*) from public.session_answers where session_id = '{sid}'"))
        assert n_ans == len(res["answers"]) > 0, (n_ans, len(res["answers"]))
        assert psql(f"select count(*) from public.hint_events where session_id = '{sid}'") == "2"
        assert psql(f"select count(*) from public.session_answers where session_id = '{sid}' and not checked") != "0"
        stats = psql(f"select sessions_count || ' ' || answers_total || ' ' || hints_opened "
                     f"from public.profile_subject_stats where profile_id = '{cpid}' and subject = 'math'")
        assert stats == f"2 {n_ans} 2", stats
        assert sync.current_streak(sync.get_link(dev_a, pid)) == 1
        # Repeating the upload is harmless.
        assert client.rpc(s_a, "submit_session", {"p_session": sync.session_payload(
            {"uid": uid, "created_at": res["finished_at"], "payload": res}, pid)})["already"] is True
        print("OK    begin_session / submit_session: answers, hints, statistics, streak")

        # Expired access token is renewed transparently (refresh token rotates and is saved).
        link = sync.get_link(dev_a, pid)
        old_refresh = link["session"]["refresh_token"]
        link["session"]["expires_at"] = 0
        dev_a.set_meta(f"profile:{pid}:cloud", link)
        sync.sync_profile(dev_a, client, pid)
        assert sync.get_link(dev_a, pid)["session"]["refresh_token"] != old_refresh
        print("OK    token refresh")

        # Students cannot write server-managed data directly.
        tok = sync.get_link(dev_a, pid)["session"]["access_token"]
        fake_session = {"id": str(uuid.uuid4()), "owner": s_a.user_id, "profile_id": cpid, "length_mode": "quick"}
        expect_denied(raw(base, "POST", "sessions", tok, fake_session)[0], "insert session")
        expect_denied(raw(base, "PATCH", f"profile_subject_stats?profile_id=eq.{cpid}", tok, {"best_nmt": 200})[0],
                      "update stats")
        status, _ = raw(base, "PATCH", f"profile_meta?profile_id=eq.{cpid}", tok, {"data": {"medals": ["fake"]}})
        expect_denied(status, "update profile_meta.data")
        status, _ = raw(base, "PATCH", f"profile_meta?profile_id=eq.{cpid}", tok, {"client_data": {"theme": "dark"}})
        assert status in (200, 204), status
        assert psql(f"select client_data ->> 'theme' from public.profile_meta where profile_id = '{cpid}'") == "dark"
        for fn, args in (("recalc_subject_stats", {"p_profile_id": cpid, "p_subject": "math"}),
                         ("update_streak", {"p_profile_id": cpid, "p_at": "2026-01-01T00:00:00Z"})):
            expect_denied(raw(base, "POST", f"rpc/{fn}", tok, args)[0], fn)
        print("OK    no direct writes to sessions, stats, server metadata; client_data writable")

        client.send_code("liza@example.com")
        s_b = client.verify_code("liza@example.com", "654321")
        row = sync.fetch_account_profile(client, s_b)
        assert sync.local_id(row["id"]) == pid and row["targets"] == {"math": 175} and row["exam_date"] == "2027-05-20"
        dev_b.save_profile(sync.profile_from_cloud(row, s_b), _dirty=False)
        sync.attach(dev_b, pid, s_b, from_cloud=True)
        assert sync.sync_profile(dev_b, client, pid) == (0, 2)
        sb = dev_b.for_profile(pid)
        ra = {r.get("session_uid"): r for r in sa.list_results()}
        rb = {r.get("session_uid"): r for r in sb.list_results()}
        assert rb[uid]["subjects"][0]["nmt_200"] == ra[uid]["subjects"][0]["nmt_200"]
        assert rb[uid]["subjects"][0]["weak_sections"] == ra[uid]["subjects"][0]["weak_sections"]
        assert rb[uid]["started_at"] <= rb[uid]["finished_at"]
        assert dev_b.get_profile(pid)["exam_date"] == "2027-05-20"
        print("OK    restore on a second device (history rebuilt for the cabinet)")

        sb.save_result(_answered_session(["math"], session_uid=uuid.uuid4().hex))
        p = dev_b.get_profile(pid)
        p["name"] = "Ліза"
        dev_b.save_profile(touch(p))
        assert sync.sync_profile(dev_b, client, pid)[0] == 1
        sync.sync_profile(dev_a, client, pid)
        assert len(sa.list_results()) == 3 and dev_a.get_profile(pid)["name"] == "Ліза"
        print("OK    trainings and renames travel between devices")

        # Another account sees nothing and cannot write into this profile.
        client.send_code("other@example.com")
        s_o = client.verify_code("other@example.com", "654321")
        for table in ("profiles", "profile_meta", "sessions", "session_subjects", "session_answers", "hint_events",
                      "profile_subject_stats", "admin_students", "admin_sections", "admin_hint_levels"):
            assert client.select_all(s_o, table, order="owner.asc" if table != "admin_sections" and table != "admin_hint_levels"
                                     else "subject.asc") == [], table
        for fn, args in (("begin_session", {"p_session_id": str(uuid.uuid4()), "p_profile_id": cpid,
                                            "p_subjects": ["math"], "p_length_mode": "quick"}),
                         ("submit_session", {"p_session": {"id": str(uuid.uuid4()), "profile_id": cpid}})):
            try:
                client.rpc(s_o, fn, args)
                raise AssertionError(f"foreign {fn} accepted")
            except CloudError:
                pass
        print("OK    RLS: accounts are isolated")

        for table in ("profiles", "sessions", "app_settings"):
            status, body = raw(base, "GET", f"{table}?select=*")
            assert status in (401, 403) or body == [], (table, status, body)
        print("OK    anon key alone reads nothing")

        dev_c = storage.open_repository(tmp_c, keystore=ks, import_legacy=False)
        other_prof = new_profile("Друга")
        dev_c.save_profile(other_prof)
        client.send_code("liza@example.com")
        sync.attach(dev_c, other_prof["id"], client.verify_code("liza@example.com", "654321"))
        try:
            sync.sync_profile(dev_c, client, other_prof["id"])
            raise AssertionError("second profile accepted")
        except CloudError as exc:
            assert exc.status == 409, exc.status
        print("OK    one profile per account")

        # Admin reads everything and the views; cannot write.
        psql(f"insert into public.admins (user_id) values ('{s_o.user_id}')")
        assert len(client.select_all(s_o, "sessions")) == 3
        students = client.select_all(s_o, "admin_students", order="name.asc")
        assert len(students) == 1 and students[0]["sessions_total"] == 3 and students[0]["streak_current"] >= 1
        sections = client.select_all(s_o, "admin_sections", order="subject.asc,section.asc")
        assert sections and all(r["subject"] == "math" for r in sections)
        assert client.select_all(s_o, "admin_hint_levels", order="subject.asc,max_hint_level.asc")
        assert client.rpc(s_o, "recalc_stats", {}) >= 1
        try:
            client.upsert(s_o, "profiles", [dict(row, name="hacked")])
            raise AssertionError("admin write accepted")
        except CloudError:
            pass
        status, admins = raw(base, "GET", "admins?select=*", s_o.access_token)
        assert status in (401, 403) or admins == [], (status, admins)
        print("OK    admin: read-only access, views, recalc_stats")

        client.rpc(s_a, "delete_my_account")
        assert psql("select count(*) from public.sessions") == "0"
        assert psql("select count(*) from public.session_answers") == "0"
        assert psql("select count(*) from auth.users where email = 'liza@example.com'") == "0"
        assert psql("select count(*) from auth.users where email = 'other@example.com'") == "1"
        print("OK    delete_my_account")
        for repo in (dev_a, dev_b, dev_c):
            repo.close()
    finally:
        for t in (tmp_a, tmp_b, tmp_c):
            shutil.rmtree(t, ignore_errors=True)


def main():
    global ANON_KEY
    if shutil.which("docker") is None or sh("docker", "info", check=False).returncode:
        print("SKIP  cloud integration (Docker is not running)")
        return 0
    ANON_KEY = make_jwt({"role": "anon", "iss": "nmt-test"})
    rest_url = start_stack()
    Gateway.rest_url = rest_url
    gw_port = free_port()
    server = http.server.ThreadingHTTPServer(("127.0.0.1", gw_port), Gateway)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        check_access_gate(f"http://127.0.0.1:{gw_port}")
        run_checks(f"http://127.0.0.1:{gw_port}")
        print("CLOUD INTEGRATION PASSED")
        return 0
    finally:
        server.shutdown()
        stop_stack()


if __name__ == "__main__":
    sys.exit(main())
