-- Closed access to the web app: before the e-mail sign-in the app asks for a login and a password
-- that the owner adds here. Like a Grails interceptor in front of every screen.
--
-- Run in the Supabase dashboard: SQL Editor -> New query -> paste this file -> Run.
-- The script can be run again safely.
--
-- Passwords are stored only as bcrypt hashes (pgcrypto) and are compared inside the database:
-- the browser never sees a hash. The tables have no RLS policies, so the API cannot read them;
-- the app only calls gate_sign_in / gate_check.
--
-- Add or change a login (SQL Editor):
--     select public.set_gate_login('tester', 'a-long-password');
-- Turn a login off (every device that used it is let out on its next start):
--     update public.app_gate_logins set enabled = false where login = 'tester';
-- See who has access:
--     select login, enabled, note, created_at from public.app_gate_logins;

create schema if not exists extensions;
create extension if not exists pgcrypto with schema extensions;

create table if not exists public.app_gate_logins (
    login text primary key check (login <> '' and login = lower(btrim(login))),
    password_hash text not null,
    enabled boolean not null default true,
    note text,
    created_at timestamptz not null default now()
);
alter table public.app_gate_logins enable row level security;  -- no policies: dashboard only

-- One row per device that passed the gate; the app keeps the token and checks it on every start.
create table if not exists public.app_gate_tokens (
    token uuid primary key default gen_random_uuid(),
    login text not null references public.app_gate_logins (login) on delete cascade on update cascade,
    created_at timestamptz not null default now(),
    last_seen_at timestamptz not null default now()
);
create index if not exists app_gate_tokens_login_idx on public.app_gate_tokens (login);
alter table public.app_gate_tokens enable row level security;

-- Wrong passwords, to slow down guessing: 10 per login in 15 minutes.
create table if not exists public.app_gate_failures (
    login text not null,
    at timestamptz not null default now()
);
create index if not exists app_gate_failures_login_at_idx on public.app_gate_failures (login, at);
alter table public.app_gate_failures enable row level security;

-- Dashboard helper: adds a login or sets a new password (and turns the login on).
create or replace function public.set_gate_login(p_login text, p_password text, p_note text default null)
returns void
language plpgsql
security definer
set search_path = ''
as $$
declare
    l text := lower(btrim(coalesce(p_login, '')));
begin
    if l = '' then
        raise exception 'login is empty';
    end if;
    if length(coalesce(p_password, '')) < 6 then
        raise exception 'password is shorter than 6 characters';
    end if;
    insert into public.app_gate_logins (login, password_hash, note)
    values (l, extensions.crypt(p_password, extensions.gen_salt('bf', 10)), p_note)
    on conflict (login) do update
        set password_hash = excluded.password_hash,
            enabled = true,
            note = coalesce(excluded.note, public.app_gate_logins.note);
end;
$$;

-- Login + password -> a new device token, or null when they are wrong.
create or replace function public.gate_sign_in(p_login text, p_password text)
returns uuid
language plpgsql
security definer
set search_path = ''
as $$
declare
    l text := lower(btrim(coalesce(p_login, '')));
    h text;
    t uuid;
begin
    delete from public.app_gate_failures where at < now() - interval '1 day';
    if (select count(*) from public.app_gate_failures
        where login = l and at > now() - interval '15 minutes') >= 10 then
        raise exception 'too many attempts';
    end if;

    select password_hash into h from public.app_gate_logins where login = l and enabled;
    if h is null or h <> extensions.crypt(coalesce(p_password, ''), h) then
        insert into public.app_gate_failures (login) values (l);
        return null;
    end if;

    delete from public.app_gate_failures where login = l;
    insert into public.app_gate_tokens (login) values (l) returning token into t;
    return t;
end;
$$;

-- Is this device token still valid (its login exists and is on)?
create or replace function public.gate_check(p_token uuid)
returns boolean
language plpgsql
security definer
set search_path = ''
as $$
begin
    update public.app_gate_tokens t
    set last_seen_at = now()
    from public.app_gate_logins l
    where t.token = p_token and l.login = t.login and l.enabled;
    return found;
end;
$$;

revoke all on function public.set_gate_login(text, text, text) from public, anon, authenticated;
revoke all on function public.gate_sign_in(text, text) from public;
revoke all on function public.gate_check(uuid) from public;
grant execute on function public.gate_sign_in(text, text) to anon, authenticated;
grant execute on function public.gate_check(uuid) to anon, authenticated;
