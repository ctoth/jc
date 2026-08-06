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


def test_checked_in_certificate_is_fresh():
    assert CORPUS_PATH.read_text(encoding="utf-8") == export_corpus()


def test_certificate_contains_no_escape_hatches():
    text = CORPUS_PATH.read_text(encoding="utf-8")
    code = re.sub(r"/-.*?-/", "", text, flags=re.DOTALL)
    code = re.sub(r"--[^\n]*", "", code)
    for forbidden in ("sorry", "axiom", "native_decide", "import"):
        assert not re.search(rf"\b{forbidden}\b", code)


def test_certificate_compiles_under_lean():
    cmd = _require_lean()
    result = subprocess.run(
        cmd + [str(CORPUS_PATH)], capture_output=True, text=True, timeout=600
    )
    assert result.returncode == 0, result.stderr or result.stdout


def test_lean_rejects_a_corrupted_certificate(tmp_path):
    """Negative control: perturb one coefficient of F and Lean must object
    (the Jacobian determinant is no longer -2)."""
    cmd = _require_lean()
    text = CORPUS_PATH.read_text(encoding="utf-8")
    corrupted = text.replace("((0, 2, 0), 4)", "((0, 2, 0), 5)", 1)
    assert corrupted != text
    bad = tmp_path / "JcCorrupted.lean"
    bad.write_text(corrupted, encoding="utf-8", newline="\n")
    result = subprocess.run(
        cmd + [str(bad)], capture_output=True, text=True, timeout=600
    )
    assert result.returncode != 0