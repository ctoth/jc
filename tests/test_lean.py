"""Gates for the generated Lean certificate (lean_export/Jc.lean).

Pattern after cold-start: the checked-in file must equal regeneration
output, must compile under a Lean 4 toolchain discovered via elan (skip
if none), and a corrupted copy must be *rejected* — the compile check is
only evidence if Lean would have complained.
"""

import re
import shutil
import subprocess

import pytest

from jc.lean_export import CORPUS_PATH, export_corpus
from jc.lean_export2 import CORPUS_PATH as CHAR2_PATH
from jc.lean_export2 import export_corpus as export_char2


def _lean_command():
    """A command list invoking a Lean 4 executable, or None."""
    elan = shutil.which("elan")
    if elan:
        listing = subprocess.run(
            [elan, "toolchain", "list"], capture_output=True, text=True
        )
        for line in listing.stdout.splitlines():
            toolchain = line.split()[0] if line.split() else ""
            if not toolchain:
                continue
            probe = subprocess.run(
                [elan, "run", toolchain, "lean", "--version"],
                capture_output=True,
                text=True,
            )
            if probe.returncode == 0 and "version 4." in probe.stdout:
                return [elan, "run", toolchain, "lean"]
    lean = shutil.which("lean")
    if lean:
        probe = subprocess.run([lean, "--version"], capture_output=True, text=True)
        if probe.returncode == 0 and "version 4." in probe.stdout:
            return [lean]
    return None


def _require_lean():
    cmd = _lean_command()
    if cmd is None:
        pytest.skip("no Lean 4 toolchain found")
    return cmd


CERTS = [
    (CORPUS_PATH, export_corpus, "((0, 2, 0), 4)", "((0, 2, 0), 5)"),
    (CHAR2_PATH, export_char2, "(1, 1, 0), (1, 2, 0)", "(1, 1, 0), (1, 3, 0)"),
]


@pytest.mark.parametrize("path,export,_old,_new", CERTS, ids=["char0", "char2"])
def test_checked_in_certificate_is_fresh(path, export, _old, _new):
    assert path.read_text(encoding="utf-8") == export()


@pytest.mark.parametrize("path,export,_old,_new", CERTS, ids=["char0", "char2"])
def test_certificate_contains_no_escape_hatches(path, export, _old, _new):
    text = path.read_text(encoding="utf-8")
    code = re.sub(r"/-.*?-/", "", text, flags=re.DOTALL)
    code = re.sub(r"--[^\n]*", "", code)
    for forbidden in ("sorry", "axiom", "native_decide", "import"):
        assert not re.search(rf"\b{forbidden}\b", code)


@pytest.mark.parametrize("path,export,_old,_new", CERTS, ids=["char0", "char2"])
def test_certificate_compiles_under_lean(path, export, _old, _new):
    cmd = _require_lean()
    result = subprocess.run(
        cmd + [str(path)], capture_output=True, text=True, timeout=600
    )
    assert result.returncode == 0, result.stderr or result.stdout


@pytest.mark.parametrize("path,export,old,new", CERTS, ids=["char0", "char2"])
def test_lean_rejects_a_corrupted_certificate(tmp_path, path, export, old, new):
    """Negative control: perturb one monomial of F and Lean must object
    (the Jacobian determinant identity fails)."""
    cmd = _require_lean()
    text = path.read_text(encoding="utf-8")
    corrupted = text.replace(old, new, 1)
    assert corrupted != text
    bad = tmp_path / f"Corrupted{path.stem}.lean"
    bad.write_text(corrupted, encoding="utf-8", newline="\n")
    result = subprocess.run(
        cmd + [str(bad)], capture_output=True, text=True, timeout=600
    )
    assert result.returncode != 0