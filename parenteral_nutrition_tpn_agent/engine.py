"""
Clinical Algorithmic Engine & Guideline Rules for TPN-Prescriber: Total Parenteral Nutrition (TPN) Macro/Micro & Refeeding Agent.
Domain: Clinical Nutrition
Scope: synthetic demonstration thresholds; not clinical guidance
"""
import math
from typing import Dict, Any, List, Optional
from .models import ClinicalCasePayload, AgentAlert, UrgencyLevel, ClinicalIntegrityStatus


class ClinicalDomainEngine:
    GUIDELINE = "Synthetic demonstration only; not clinical guidance"
    PRIMARY_BASELINE_LIMIT = 20.0
    SECONDARY_ALERT_LIMIT = 10.0

    @classmethod
    def evaluate_primary_index(cls, value: float) -> Optional[Dict[str, Any]]:
        if value > cls.PRIMARY_BASELINE_LIMIT:
            return {
                "title": "Primary Metric Threshold Exceeded",
                "finding": f"Observed value ({value:.2f}) exceeds synthetic demonstration limit ({cls.PRIMARY_BASELINE_LIMIT:.1f}).",
                "recommendation": "Review synthetic input; do not use this output for patient care.",
            }
        return None

    @classmethod
    def evaluate_secondary_kinetics(cls, value: float, is_stat: bool) -> Optional[Dict[str, Any]]:
        if value > cls.SECONDARY_ALERT_LIMIT or is_stat:
            return {
                "title": "STAT Kinetic Escalation Triggered",
                "finding": f"Kinetic parameter ({value:.2f}) with STAT={is_stat} requires prioritized supervision.",
                "recommendation": "Demonstration-only STAT flag; no real-world notification is initiated.",
            }
        return None

    @classmethod
    def evaluate_biomarker_concordance(cls, status_flag: str, biomarkers: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        status_upper = str(status_flag).upper()
        if "DISCORDANT" in status_upper or "EQUIVOCAL" in status_upper or "MUTANT" in status_upper:
            return {
                "title": "Phenotypic / Biomarker Discordance Identified",
                "finding": f"Status flag '{status_flag}' indicates divergence from standard diagnostic concordance.",
                "recommendation": f"Review the synthetic status flag; no clinical testing recommendation is made.",
            }
        return None
