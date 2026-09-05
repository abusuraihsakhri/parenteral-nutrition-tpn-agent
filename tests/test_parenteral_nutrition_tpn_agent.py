"""
Automated Pytest Test Suite for Parenteral Nutrition Tpn Agent.
Domain: Gastroenterology & Hepatology Systems
Standard: AASLD / ACG / Chicago Classification v4.0
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.base import PHIGuard, AuditLogger, SecurityException
from agents.models import SystemTaskPayload, UrgencyLevel, SystemIntegrityStatus
from agents.workers import InvariantQCWorker, SafetyEscalationWorker, ProtocolConformanceWorker
from agents.supervisor import SystemSupervisor
from cli import main


def test_phi_guard_enforcement():
    with pytest.raises(SecurityException):
        PHIGuard.assert_no_phi("Patient MRN-994827 blood culture positive for Staphylococcus")

    # Clean text passes
    PHIGuard.assert_no_phi("Analytical assay specimen KEY-001 optimal")


def test_specialized_workers():
    # Worker 1: QC Invariant
    p1 = SystemTaskPayload(task_id="T1", target_identifier="KEY-01", primary_metric=35.0)
    alerts1 = InvariantQCWorker.evaluate(p1)
    assert len(alerts1) == 1
    assert alerts1[0].urgency == UrgencyLevel.ELEVATED

    # Worker 2: Safety
    p2 = SystemTaskPayload(task_id="T2", target_identifier="KEY-02", primary_metric=10.0, is_critical_flag=True)
    alerts2 = SafetyEscalationWorker.evaluate(p2)
    assert len(alerts2) == 1
    assert alerts2[0].urgency == UrgencyLevel.CRITICAL_STAT

    # Worker 3: Protocol Conformance
    p3 = SystemTaskPayload(task_id="T3", target_identifier="KEY-03", primary_metric=10.0, status_descriptor="DISCORDANT_ANOMALY")
    alerts3 = ProtocolConformanceWorker.evaluate(p3)
    assert len(alerts3) == 1


def test_supervisor_consensus_and_audit():
    supervisor = SystemSupervisor(model_provider="mock")
    payload = SystemTaskPayload(
        task_id="TASK-PROD-01",
        target_identifier="KEY-PROD-01",
        primary_metric=12.0,
        secondary_metric=4.0,
        status_descriptor="NOMINAL"
    )
    dossier = supervisor.process_task(payload)
    assert dossier.overall_urgency == UrgencyLevel.ROUTINE
    assert dossier.integrity_status == SystemIntegrityStatus.VALIDATED
    assert dossier.audit_hash != ""

    # Verify cryptographic audit trail
    assert AuditLogger.verify_integrity() is True

    # CLI tests
    assert main(["audit", "--task-id", "CLI-TEST-01"]) == 0
    assert main(["chat", "Explain", "specifications"]) == 0
    assert main(["verify-audit"]) == 0


# --- New validation tests ---

def test_payload_rejects_empty_task_id():
    with pytest.raises(ValueError):
        SystemTaskPayload(task_id="", target_identifier="KEY-01", primary_metric=10.0)


def test_payload_rejects_whitespace_only_identifiers():
    with pytest.raises(ValueError):
        SystemTaskPayload(task_id="   ", target_identifier="KEY-01", primary_metric=10.0)


def test_payload_rejects_nan_metrics():
    with pytest.raises(ValueError):
        SystemTaskPayload(task_id="T1", target_identifier="KEY-01", primary_metric=float("nan"))


def test_payload_strips_whitespace():
    p = SystemTaskPayload(task_id="  T1  ", target_identifier="  KEY-01  ", primary_metric=10.0, status_descriptor="  NOMINAL  ")
    assert p.task_id == "T1"
    assert p.target_identifier == "KEY-01"
    assert p.status_descriptor == "NOMINAL"


def test_payload_max_length_enforced():
    with pytest.raises(ValueError):
        SystemTaskPayload(task_id="T" * 200, target_identifier="KEY-01", primary_metric=10.0)


def test_payload_valid_input():
    p = SystemTaskPayload(task_id="TASK-001", target_identifier="KEY-001", primary_metric=25.5, secondary_metric=10.0)
    assert p.task_id == "TASK-001"
    assert p.primary_metric == 25.5
    assert p.secondary_metric == 10.0


def test_batch_missing_file_returns_error():
    result = main(["batch", "-i", "nonexistent_file_xyz.csv"])
    assert result == 1


def test_phi_redaction():
    redacted = PHIGuard.redact_phi("Contact patient at 555-123-4567 or MRN-12345678")
    assert "555-123-4567" not in redacted
    assert "MRN-12345678" not in redacted
    assert "[REDACTED_IDENTIFIER]" in redacted
