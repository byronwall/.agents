#!/usr/bin/env python3
"""Run a test command against a copy of the code with one defense removed.

Answers "would a test catch it?" without touching the checkout: copies a source
tree into the run folder, applies one exact-text replacement (it must match once),
runs the given command inside the copy and reports whether the tests still pass.

    mutate.py --src <checkout>/server/app --run <run> --name duplicate-import \
        --file src/app/importer.py --old "row_id in imported" --new "False" \
        -- uv run pytest tests/test_importer.py -q

Exit status: 0 if the tests still PASS with the mutant (a test gap), 1 if they FAIL
(the suite catches it), 2 on a setup error or a test command that exited with
anything other than 0 or 1 (pytest uses 2 to 5 for collection and usage errors).
The copy's root is put first on PYTHONPATH. Always look at *why* they failed: a
mutant that breaks an import or crashes the harness looks like a kill but isn't.
Run one mutant you know the suite catches first, as the control.

The copy skips .git, node_modules, .venv, __pycache__ and build output, so a
command that needs the project's environment should point at it explicitly (for
uv: `uv run --project <checkout-subdir> ...`, run from the copy with PYTHONPATH
set to the copy's source root so the mutant is imported, not the checkout).
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

SKIP = {".git", "node_modules", ".venv", "venv", "__pycache__", ".pytest_cache", ".mypy_cache", "dist", "build", ".next", ".turbo"}


def main() -> int:
    if "--" not in sys.argv:
        print(__doc__)
        return 2
    i = sys.argv.index("--")
    p = argparse.ArgumentParser()
    p.add_argument("--src", required=True, help="source tree to copy (a checkout or a subfolder)")
    p.add_argument("--run", required=True, help="the break-it run folder")
    p.add_argument("--name", required=True, help="short mutant name, used for the copy's folder")
    p.add_argument("--file", required=True, help="file to mutate, relative to --src")
    p.add_argument("--old", required=True)
    p.add_argument("--new", required=True)
    a = p.parse_args(sys.argv[1:i])
    cmd = sys.argv[i + 1:]
    if not cmd:
        print("no test command after --", file=sys.stderr)
        return 2

    src = Path(a.src).resolve()
    dest = Path(a.run).resolve() / f"mut-{a.name}"
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest, ignore=lambda d, names: [n for n in names if n in SKIP])

    target = dest / a.file
    text = target.read_text()
    n = text.count(a.old)
    if n != 1:
        print(f"--old matches {n} times in {a.file}; it must match exactly once", file=sys.stderr)
        return 2
    target.write_text(text.replace(a.old, a.new))

    log = Path(a.run).resolve() / f"mut-{a.name}.txt"
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(x for x in [str(dest), env.get("PYTHONPATH", "")] if x)
    proc = subprocess.run(cmd, cwd=dest, capture_output=True, text=True, env=env)
    out = proc.stdout + proc.stderr
    log.write_text(f"$ {' '.join(cmd)}\n# in {dest}\n# {a.file}: {a.old!r} -> {a.new!r}\n\n{out}")
    tail = "\n".join(out.strip().splitlines()[-5:])
    if proc.returncode == 0:
        print(f"SURVIVED {a.name}: tests still pass with the mutant (test gap). Log: {log}\n{tail}")
        return 0
    if proc.returncode != 1:
        # pytest: 2 interrupted or collection error, 4 usage error, 5 no tests collected
        print(f"NOT A KILL {a.name}: the command exited {proc.returncode}, which usually means setup, import or collection failed, not a test. Log: {log}\n{tail}")
        return 2
    print(f"KILLED {a.name}: tests fail. Check the failing assertion is the one the mutant should trip. Log: {log}\n{tail}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
