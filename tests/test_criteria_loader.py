"""Frozen-criteria loader (MS8 8a). Failure cases run on temporary git repositories built from copies of the criteria files;
the real tag is only read."""
import shutil
import subprocess

import pytest

from mprsurge import config as C
from mprsurge import criteria as K
from mprsurge import provenance as P
from mprsurge import run as R

FROZEN_SHA = "c7d2f36b74ea611c8777c1b408d5085333e55230834c27e5f0eb839f1162fa05"       # DL-164
FILES = [K.CRITERIA_PATH, "configs/S13.yaml", "configs/A4_grids.yaml", "configs/S5_cells.yaml"]
GIT = ["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false", "-c", "tag.gpgsign=false"]


def _git(root, *args):
    return subprocess.run([*GIT, "-C", str(root), *args], check=True, capture_output=True)


def _message(root, shas=None):
    s = shas or {f: K.lf_sha256((root / f).read_bytes()) for f in FILES}
    return (f"criteria-frozen: test.\nSHA-256 of the LF text of {K.CRITERIA_PATH} (as committed in abc): {s[FILES[0]]} (1 bytes).\n"
            f"Secondary: configs/S13.yaml {s[FILES[1]]}, configs/A4_grids.yaml {s[FILES[2]]}, configs/S5_cells.yaml {s[FILES[3]]}.\n")


def make_repo(tmp_path, gitattributes=True, tag=True, shas=None):
    root = tmp_path / "repo"
    (root / "configs").mkdir(parents=True)
    for f in FILES:
        shutil.copyfile(C.repo_root() / f, root / f)
    if gitattributes:
        (root / ".gitattributes").write_text("* text=auto eol=lf\n")
    _git(root.parent, "init", "-q", str(root))
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "freeze")
    if tag:
        _git(root, "tag", "-a", K.TAG, "-m", _message(root, shas))
    return root


def test_real_repo_verifies_against_the_recorded_hash():
    if subprocess.run(["git", "-C", str(C.repo_root()), "rev-parse", "-q", "--verify", f"refs/tags/{K.TAG}"],
                      capture_output=True).returncode != 0:
        pytest.skip("tag criteria-frozen is local only and absent in this clone")
    info = K.verify_frozen_criteria()
    assert info["sha256"] == FROZEN_SHA and info["commit"].startswith("dd8330c")
    assert set(info["secondary"]) == set(FILES[1:])


def test_clean_temp_repo_passes_and_loads_the_blob(tmp_path):
    root = make_repo(tmp_path)
    crit, info = K.load_frozen_criteria(root)
    assert info["sha256"] == K.lf_sha256((root / K.CRITERIA_PATH).read_bytes())
    assert crit["meta"]["frozen"] is True


def test_missing_tag_refuses(tmp_path):
    root = make_repo(tmp_path, tag=False)
    with pytest.raises(K.CriteriaError, match="not found"):
        K.verify_frozen_criteria(root)


def test_lightweight_tag_without_message_refuses(tmp_path):
    root = make_repo(tmp_path, tag=False)
    _git(root, "tag", K.TAG)
    with pytest.raises(K.CriteriaError, match="no message|no SHA-256"):
        K.verify_frozen_criteria(root)


def test_working_file_edited_after_the_tag_is_a_mismatch(tmp_path):
    root = make_repo(tmp_path)
    with open(root / K.CRITERIA_PATH, "a", encoding="utf8", newline="\n") as fh:
        fh.write("# changed after the freeze\n")
    with pytest.raises(K.CriteriaError, match="SHA-256 mismatch: working file"):
        K.verify_frozen_criteria(root)


def test_committed_change_after_the_tag_is_a_mismatch(tmp_path):
    root = make_repo(tmp_path)
    with open(root / K.CRITERIA_PATH, "a", encoding="utf8", newline="\n") as fh:
        fh.write("# changed and committed\n")
    _git(root, "commit", "-q", "-am", "edit")
    with pytest.raises(K.CriteriaError, match="SHA-256 mismatch: working file"):
        K.verify_frozen_criteria(root)


def test_wrong_hash_in_the_tag_message_is_a_mismatch(tmp_path):
    shas = {f: "0" * 64 if f == K.CRITERIA_PATH else K.lf_sha256((C.repo_root() / f).read_bytes()) for f in FILES}
    root = make_repo(tmp_path, shas=shas)
    with pytest.raises(K.CriteriaError, match=r"SHA-256 mismatch: .* in tag"):
        K.verify_frozen_criteria(root)


def test_secondary_file_mismatch_refuses(tmp_path):
    root = make_repo(tmp_path)
    with open(root / "configs/S13.yaml", "a", encoding="utf8", newline="\n") as fh:
        fh.write("# x\n")
    with pytest.raises(K.CriteriaError, match="configs/S13.yaml"):
        K.verify_frozen_criteria(root)


def test_dirty_file_with_equal_lf_hash_refuses_without_gitattributes(tmp_path):
    """No .gitattributes: a CRLF copy of the same text hashes equal but git sees a modified file."""
    root = make_repo(tmp_path, gitattributes=False)
    f = root / K.CRITERIA_PATH
    f.write_bytes(f.read_bytes().replace(b"\n", b"\r\n"))
    with pytest.raises(K.CriteriaError, match="dirty"):
        K.verify_frozen_criteria(root)


def test_crlf_working_copy_hashes_equal_but_git_reports_it_modified(tmp_path):
    """With `* text=auto eol=lf` the hash of a CRLF copy still equals the LF hash (step 4 passes), but git status lists the
    file as modified (checked here and in DL-165), so step 5 refuses: the working file must be the LF file."""
    root = make_repo(tmp_path)
    f = root / K.CRITERIA_PATH
    f.write_bytes(f.read_bytes().replace(b"\n", b"\r\n"))
    assert K.lf_sha256(f.read_bytes()) == K.lf_sha256(_git(root, "show", f"{K.TAG}:{K.CRITERIA_PATH}").stdout)
    with pytest.raises(K.CriteriaError, match="dirty"):
        K.verify_frozen_criteria(root)


def test_parse_tag_message_real_format():
    m = ("criteria-frozen: x.\n    SHA-256 of the LF text of configs/robustness_criteria.yaml (as committed in dd8330c5eaa): "
         + FROZEN_SHA + " (30234 bytes).\n    Secondary: configs/S13.yaml " + "1" * 64 + ", configs/A4_grids.yaml " + "2" * 64 + ".\n")
    got = K.parse_tag_message(m)
    assert got["primary"] == FROZEN_SHA and got["secondary"] == {"configs/S13.yaml": "1" * 64, "configs/A4_grids.yaml": "2" * 64}
    with pytest.raises(K.CriteriaError):
        K.parse_tag_message("no hash here")


def test_runner_refuses_a_config_naming_the_frozen_file_when_verification_fails(monkeypatch):
    def refuse(*a, **k):
        raise K.CriteriaError("mismatch (test)")
    monkeypatch.setattr(K, "verify_frozen_criteria", refuse)
    with pytest.raises(K.CriteriaError):
        R.build_plan("configs/S5_ramp.yaml")
    assert R.main(["--config", "configs/S5_ramp.yaml", "--dry-run"]) == 2          # ConfigError path of main: exit 2, nothing run
    R.build_plan("configs/S5.yaml")                  # configs that do not name the frozen file are not gated
    R.build_plan("configs/A4.yaml")                  # A4 stays on replication.yaml (H-2)


def test_ramp_config_names_the_frozen_file_and_leaves_the_hash_unchanged():
    ramp, s5 = C.resolve_config("configs/S5_ramp.yaml"), C.resolve_config("configs/S5.yaml")
    assert ramp["robustness"]["criteria_file"] == K.CRITERIA_PATH and s5["robustness"]["criteria_file"] is None
    assert C.config_hash(ramp) == C.config_hash(s5)                  # the criteria key is outside the hash view
    assert C.resolve_config("configs/A4.yaml")["robustness"]["criteria_file"] == "configs/replication.yaml"
    assert K.is_frozen_criteria_path(str(C.repo_root() / K.CRITERIA_PATH)) and not K.is_frozen_criteria_path("configs/replication.yaml")


def test_run_record_hashes_the_frozen_file_as_lf_text():
    cfg = C.resolve_config("configs/S5_ramp.yaml")
    rec = P.make_run_record(cfg, P.environment_info(), name="t", status="dry_run", dry_run=True)
    assert rec["criteria_sha256"] == FROZEN_SHA
    rec = P.make_run_record(C.resolve_config("configs/A4.yaml"), P.environment_info(), name="t", status="dry_run", dry_run=True)
    assert rec["criteria_sha256"] == P.sha256_file(C.repo_root() / "configs/replication.yaml")      # other files unchanged
