# PyInstaller spec: one-folder windowed build of the app (used by the Windows CI workflow).
#   pyinstaller --noconfirm packaging/nmt_tutor.spec
# Output: dist/NMT_Sova_Tutor/ (the exe, _internal/ and the readme).
import os
import shutil

APP_NAME = "NMT_Sova_Tutor"
ROOT = os.path.abspath(os.path.join(SPECPATH, ".."))
BUILD_DIR = os.path.join(ROOT, "build")
os.makedirs(BUILD_DIR, exist_ok=True)

# Windows wants an .ico for the exe and the window; make it from the PNG.
icon_png = os.path.join(ROOT, "owl_icon.png")
icon_ico = os.path.join(BUILD_DIR, "owl_icon.ico")
try:
    from PIL import Image

    Image.open(icon_png).save(icon_ico, sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
except Exception as exc:
    print(f"WARNING: no .ico icon ({exc})")
    icon_ico = None



def package_modules(pkg_dir, pkg_name):
    """All module names of the package, found from the files (no import needed)."""
    names = []
    for folder, dirs, files in os.walk(pkg_dir):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        rel = os.path.relpath(folder, os.path.dirname(pkg_dir)).replace(os.sep, ".")
        for f in files:
            if f.endswith(".py"):
                names.append(rel if f == "__init__.py" else f"{rel}.{f[:-3]}")
    return sorted(names)


hidden = package_modules(os.path.join(ROOT, "nmt_tutor"), "nmt_tutor")
assert any(n.endswith("generators.biology") for n in hidden), hidden

datas = [
    (os.path.join(ROOT, "nmt_tutor", "data", "bank_static.json"), "nmt_tutor/data"),
    (os.path.join(ROOT, "nmt_tutor", "data", "archive_2022_2025.json"), "nmt_tutor/data"),
    (icon_png, "."),
]
if icon_ico:
    datas.append((icon_ico, "."))

a = Analysis(
    [os.path.join(ROOT, "nmt_tutor_mac.py")],
    pathex=[ROOT],
    datas=datas,
    # Generator modules are imported lazily by name, so the analysis cannot see them.
    hiddenimports=hidden,
    excludes=["unittest", "pydoc", "test"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=APP_NAME,
    console=False,
    icon=icon_ico,
    upx=False,
)
coll = COLLECT(exe, a.binaries, a.datas, name=APP_NAME, upx=False)

readme = os.path.join(SPECPATH, "windows", "ПРОЧИТАЙ_МЕНЯ.txt")
shutil.copy(readme, os.path.join(DISTPATH, APP_NAME, os.path.basename(readme)))
