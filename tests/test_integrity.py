"""Integrity regression tests for HMAC audit and numerical validation."""
import copy
import pytest

from agents.base import AuditTrail, SecurityException
from agents.models import SystemTaskPayload


def _trail():
    trail = AuditTrail(secret_key="test-secret-0123456789")
    trail.log("worker", "supervisor", "EVALUATED", {"task_id": "SYNTH-001"})
    trail.log("worker", "supervisor", "REVIEWED", {"task_id": "SYNTH-002"})
    return trail


def test_audit_hmac_detects_any_record_tampering():
    for field, corrupted in [
        ("actor", "impersonator"),
        ("event_type", "MODIFIED"),
        ("payload_hash", "f" * 64),
        ("current_hash", "0" * 64),
        ("timestamp", "2000-01-01"),
        ("audit_id", "forged"),
    ]:
        trail = _trail()
        trail.logs[0][field] = corrupted
        assert trail.verify_integrity() is False, field


def test_audit_chain_detects_deletion_and_reordering():
    trail = _trail()
    assert trail.verify_integrity()
    trail.logs.pop(0)
    assert not trail.verify_integrity()

    trail = _trail()
    trail.logs.reverse()
    assert not trail.verify_integrity()


def test_audit_exposed_trail_is_a_copy():
    trail = _trail()
    exposed = trail.get_trail()
    exposed[0]["actor"] = "mutant"
    exposed.pop()
    assert trail.verify_integrity()
    assert len(trail.get_trail()) == 2


def test_audit_rejects_phi_in_actor_fields():
    trail = AuditTrail(secret_key="test-secret-0123456789")
    with pytest.raises(SecurityException):
        trail.log("MRN-123456", "supervisor", "EVALUATED", {"task_id": "SYNTH-001"})
    assert trail.logs == []


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
def test_task_model_rejects_non_finite_primary_and_secondary(bad):
    with pytest.raises(ValueError):
        SystemTaskPayload(task_id="T1", target_identifier="KEY-01", primary_metric=bad)
    with pytest.raises(ValueError):
        SystemTaskPayload(task_id="T1", target_identifier="KEY-01", primary_metric=1, secondary_metric=bad)
