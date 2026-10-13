"""
FastAPI REST API Server for Parenteral Nutrition Tpn Agent.
"""
from pathlib import Path
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from parenteral_nutrition_tpn_agent.calculator import calculate_macronutrients, CalculationError
from .base import AuditLogger, PHIGuard, SecurityException
from .models import SystemTaskPayload, ConsensusDossier
from .supervisor import SystemSupervisor

supervisor = SystemSupervisor(model_provider="mock")

app = FastAPI(
    title="Parenteral Nutrition Tpn Agent API",
    description="Demonstration audit API plus non-prescriptive parenteral nutrition energy arithmetic; not a clinical prescribing system.",
    version="2.1.0",
)


class ChatRequest(BaseModel):
    query: str


class MacronutrientRequest(BaseModel):
    weight_kg: float = Field(gt=0, allow_inf_nan=False)
    energy_kcal: float = Field(gt=0, allow_inf_nan=False)
    amino_acids_g: float = Field(ge=0, allow_inf_nan=False)
    lipid_20pct_ml: float = Field(ge=0, allow_inf_nan=False)


@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "parenteral-nutrition-tpn-agent", "domain": "Non-prescriptive nutrition arithmetic / legacy demonstrations", "validation": "NOT_CLINICALLY_VALIDATED", "version": "2.1.0"}


@app.get("/metrics")
def metrics():
    return {
        "dossiers_processed_total": len(supervisor.dossier_registry),
        "audit_blocks_total": len(AuditLogger.get_trail()),
        "system_status": "DEMONSTRATION_ONLY"
    }


@app.post("/api/audit")
def api_audit(payload: SystemTaskPayload):
    try:
        dossier = supervisor.process_task(payload)
    except SecurityException:
        raise HTTPException(status_code=400, detail="Potential direct identifier detected")
    return dossier.to_dict()


@app.post("/api/macronutrients")
def api_macronutrients(payload: MacronutrientRequest):
    try:
        return calculate_macronutrients(**payload.model_dump())
    except CalculationError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        ans = supervisor.query_supervisory_chat(req.query)
        return {"response": ans}
    except SecurityException:
        raise HTTPException(status_code=400, detail="Potential direct identifier detected")


@app.get("/api/audit/logs")
def api_audit_logs():
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}

# Mount the browser-local calculator after API routes to preserve their precedence.
_static_dir = Path(__file__).resolve().parents[1] / "web"
if _static_dir.is_dir():
    app.mount("/", StaticFiles(directory=str(_static_dir), html=True), name="browser-calculator")
