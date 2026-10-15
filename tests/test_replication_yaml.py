"""configs/replication.yaml is frozen (DL-084): LF line endings and a pinned SHA-256."""
from mprsurge import config as C
from mprsurge.provenance import sha256_file

FROZEN_SHA256 = "667d3b788d1c7c5aebc716998d09746b685358f326334aae87591924908819a5"
PATH = C.repo_root() / "configs" / "replication.yaml"


def test_replication_yaml_has_no_cr_byte():
    assert b"\r" not in PATH.read_bytes()


def test_replication_yaml_sha256_is_the_frozen_value():
    # Fails by design if the tolerances change: that needs a new decision-log
    # entry (D34), then an update of this value. Also fails on a CRLF working copy.
    assert sha256_file(PATH) == FROZEN_SHA256
