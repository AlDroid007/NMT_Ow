"""One-time import of v3.5 plain files from the data folder into the repository.

v3.5 auto-loaded every *.json bank (except templates) from Documents/NMT_Tutor
and saved reports there as nmt_report_*.txt. They are copied into the encrypted
store once; the original files are left untouched.
"""

import os
from datetime import datetime

from . import files

FLAG = "legacy_import_v1"


def run_legacy_import(repo, folder):
    """Imports legacy files once. Returns (banks_imported, reports_imported)."""
    if repo.get_meta(FLAG):
        return 0, 0
    banks = reports = 0
    try:
        names = sorted(os.listdir(folder))
    except OSError:
        names = []
    for fname in names:
        path = os.path.join(folder, fname)
        if not os.path.isfile(path):
            continue
        created = datetime.fromtimestamp(os.path.getmtime(path)).isoformat(timespec="seconds")
        try:
            if fname.endswith(".json") and "template" not in fname.lower():
                bank = files.import_custom_bank_file(path)
                if bank:
                    repo.save_custom_bank(fname, bank, created_at=created)
                    banks += 1
            elif fname.startswith("nmt_report_") and fname.endswith(".txt"):
                repo.save_report(files.read_text(path), title=fname, created_at=created)
                reports += 1
        except Exception:  # a broken legacy file must not block the app
            continue
    repo.set_meta(FLAG, {"done_at": datetime.now().isoformat(timespec="seconds"), "banks": banks, "reports": reports})
    return banks, reports
