"""Frozen-criteria loader (MS8 8a; plan section 7 intro, D35; DL-084, DL-164; sheet rows H-2, H-3).

A ramp run may only start if configs/robustness_criteria.yaml is the file the annotated tag `criteria-frozen`
froze. The check, in this order, with a clear CriteriaError at the first failure:
  1. the tag exists;
  2. its message carries the SHA-256 of the LF text of the criteria file (the format of DL-164) and, for
     the secondary files, `configs/<name>.yaml <sha256>`;
  3. the blob in the tag (`git show criteria-frozen:<path>`), CRLF normalised to LF, hashes to that value;
  4. the working file, CRLF normalised to LF, hashes to that value;
  5. no hashed file is modified or untracked in the working tree (git status).
It reads the files and writes nothing. The hash is of the LF text, so step 4 does not depend on the line endings of the
checkout; but git lists a CRLF working copy as modified, so step 5 refuses it (the working files must be the LF files, as they are
in this repository). load_frozen_criteria parses the verified blob of the tag, not the working file.
"""
from __future__ import annotations

import hashlib
import re
import subprocess
from pathlib import Path

from .config import ConfigError, repo_root

TAG = "criteria-frozen"
CRITERIA_PATH = "configs/robustness_criteria.yaml"
_SHA = r"[0-9a-f]{64}"


class CriteriaError(ConfigError):
    """The frozen criteria cannot be verified: the run must not start."""


def lf_bytes(data: bytes) -> bytes:
    """CRLF (and a lone CR) to LF; the text the freeze hash is taken over (DL-084, DL-164)."""
    return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def lf_sha256(data: bytes) -> str:
    return hashlib.sha256(lf_bytes(data)).hexdigest()


def _git(root: Path, *args: str) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(["git", "-C", str(root), *args], capture_output=True, check=False)
    except OSError as exc:
        raise CriteriaError(f"git cannot be run ({exc}); the frozen criteria cannot be verified") from exc


def parse_tag_message(message: str, path: str = CRITERIA_PATH) -> dict:
    """{'primary': sha256 of `path`, 'secondary': {file: sha256}} from a tag message in the DL-164 format."""
    m = re.search(rf"LF text of {re.escape(path)}[^:]*:\s*({_SHA})", message)
    if m is None:
        raise CriteriaError(f"the tag message has no SHA-256 for {path} (expected 'SHA-256 of the LF text of {path} "
                            "(...): <64 hex>')")
    secondary = {f: h for f, h in re.findall(rf"(configs/[\w./-]+\.yaml)\s+({_SHA})", message) if f != path}
    return {"primary": m.group(1), "secondary": secondary}


def verify_frozen_criteria(root=None, tag: str = TAG, path: str = CRITERIA_PATH) -> dict:
    """Run the five checks; return {'sha256', 'tag', 'commit', 'secondary', 'path'} or raise CriteriaError."""
    root = Path(root) if root is not None else repo_root()
    tagref = _git(root, "rev-parse", "-q", "--verify", f"refs/tags/{tag}^{{}}")
    if tagref.returncode != 0:
        raise CriteriaError(f"git tag {tag!r} not found in {root}: the criteria are not frozen here; a ramp run refuses to start")
    commit = tagref.stdout.decode().strip()
    msg = _git(root, "tag", "-l", "--format=%(contents)", tag)
    if msg.returncode != 0 or not msg.stdout.strip():
        raise CriteriaError(f"git tag {tag!r} has no message (an annotated tag with the SHA-256 is required)")
    want = parse_tag_message(msg.stdout.decode("utf-8", "replace"), path)

    blob = _git(root, "show", f"{tag}:{path}")
    if blob.returncode != 0:
        raise CriteriaError(f"{path} is not in tag {tag!r}: {blob.stderr.decode(errors='replace').strip()}")
    if lf_sha256(blob.stdout) != want["primary"]:
        raise CriteriaError(f"SHA-256 mismatch: {path} in tag {tag!r} hashes to {lf_sha256(blob.stdout)}, the tag message "
                            f"records {want['primary']}")

    checked = {path: want["primary"], **want["secondary"]}
    for rel, sha in checked.items():
        f = root / rel
        if not f.is_file():
            raise CriteriaError(f"hashed file {rel} is missing from the working tree")
        have = lf_sha256(f.read_bytes())
        if have != sha:
            raise CriteriaError(f"SHA-256 mismatch: working file {rel} hashes to {have}, the tag {tag!r} records {sha} "
                                "(edited since the freeze; a change of a frozen file needs a decision-log entry)")
    st = _git(root, "status", "--porcelain", "--untracked-files=all", "--", *checked)
    if st.returncode != 0:
        raise CriteriaError(f"git status failed: {st.stderr.decode(errors='replace').strip()}")
    if st.stdout.strip():
        raise CriteriaError("dirty hashed file(s), a ramp run starts from a clean tree: "
                            + "; ".join(l.strip() for l in st.stdout.decode().splitlines()))
    return {"sha256": want["primary"], "tag": tag, "commit": commit, "secondary": want["secondary"], "path": path}


def load_frozen_criteria(root=None, tag: str = TAG, path: str = CRITERIA_PATH) -> tuple[dict, dict]:
    """(criteria dict, verification info). The dict is parsed from the verified blob of the tag, not from the working file."""
    import yaml
    info = verify_frozen_criteria(root, tag, path)
    root = Path(root) if root is not None else repo_root()
    blob = _git(root, "show", f"{tag}:{path}").stdout
    return yaml.safe_load(lf_bytes(blob).decode("utf-8")), info


def is_frozen_criteria_path(criteria_file) -> bool:
    """True if a config's robustness.criteria_file names the frozen criteria file."""
    if not criteria_file:
        return False
    p = Path(criteria_file)
    try:
        p = p.resolve().relative_to(repo_root())
    except (ValueError, OSError):
        pass
    return p.as_posix() == CRITERIA_PATH


def require_frozen_for_config(cfg: dict, root=None) -> dict | None:
    """The runner's gate: a config that names the frozen criteria file runs only if the freeze verifies.

    Configs with another criteria file (A0, A1, A2, A4 stay on configs/replication.yaml, H-2) or none are not touched.
    """
    if not is_frozen_criteria_path(cfg["robustness"]["criteria_file"]):
        return None
    return verify_frozen_criteria(root)
