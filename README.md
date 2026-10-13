# Parenteral Nutrition TPN Agent

An educational, non-prescriptive parenteral-nutrition macronutrient **energy-balance calculator**, with an older experimental agent-audit demonstration retained for compatibility.

**Not a clinical prescribing system.** No clinical validation is established. Do not use the calculations or legacy alert thresholds to prescribe PN, assess metabolic risk, or make patient-care decisions.

## Browser application

Open `web/index.html` in a modern browser. The calculator runs locally with JavaScript; no Python runtime, backend, account, telemetry, or internet access is required.

The inputs are **clinician-selected numerical values**, not recommended targets:

- Body weight (kg)
- Daily energy target (kcal/day)
- Amino acids (g/day)
- 20% intravenous lipid emulsion (mL/day)

It reports the resulting amino-acid, lipid, and dextrose energy contributions; lipid mass; remaining dextrose (g/day); and dextrose glucose infusion rate (mg/kg/min). Values that would require negative dextrose or contain invalid/non-finite numbers are rejected.

### Explicit energy conventions

| Component | Assumption |
|---|---|
| Intravenous dextrose | 3.4 kcal/g |
| Amino acids | 4 kcal/g |
| **Illustrative** 20% intravenous lipid emulsion | 2 kcal/mL; 0.2 g lipid/mL |
| Glucose infusion rate | Dextrose mg ÷ weight kg ÷ 1,440 minutes |

Lipid energy density varies with formulation. Verify the actual manufacturer's labeling. These arithmetic conversions **do not** calculate protein needs, caloric requirements, lipid eligibility, fluid balance, glucose tolerance, electrolyte or micronutrient requirements, PN osmolarity, vascular access suitability, or refeeding prevention.

## Python installation and CLI

Python 3.9 or newer is required.

```bash
python -m pip install -e ".[api,test]"
parenteral-nutrition-tpn-engine calculate \
  --weight-kg 70 --energy-kcal 2000 \
  --amino-acids-g 90 --lipid-20pct-ml 250
```

The deterministic Python function can also be imported:

```python
from parenteral_nutrition_tpn_agent.calculator import calculate_macronutrients

result = calculate_macronutrients(70, 2000, 90, 250)
print(result["dextrose_g"])
```

Run the local API and browser app together:

```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/` for the browser interface. `POST /api/macronutrients` accepts the four named numeric inputs and returns the energy breakdown. `GET /health` provides service status.

For a static-only local server, use `python -m http.server 8001 --directory web`.

## Legacy demonstration components

The original `agents/`, `parenteral_nutrition_tpn_agent/agents.py`, `tpn_prescriber.py`, and `enrichment.py` modules remain available so existing scripts and tests are not needlessly broken. Their numeric thresholds and discordance indicators are generic demonstration rules, **not validated ASPEN, ESPEN, NICE, or clinical PN algorithms**, notwithstanding historic descriptions embedded in legacy code.

Existing audit/chat CLI commands and `POST /api/audit`, `POST /api/chat`, `GET /api/audit/logs`, and `GET /metrics` continue to exist for demonstration and testing only. The mock chat does not provide verified clinical reasoning, and the audit service is not a clinical monitoring solution.

## Privacy and security

The browser calculator performs arithmetic in-memory and does not send, store, or export data. It has no fields for personal identifiers. The optional FastAPI backend processes client-supplied data; legacy audit routes maintain an in-memory event trail and are **not** designed for protected health information. Regex-based identifier checks cannot guarantee de-identification or regulatory compliance. Do not input or transmit patient data into this demonstration.

An HMAC-SHA256 chain protects recorded audit event metadata from undetected modification while the application is running; audit records are **not persisted across restarts**. For a consistent signing key set `AUDIT_SECRET_KEY` securely in the environment. This is not an immutable or externally anchored audit system.

## Testing and deployment

```bash
python -m pytest -q
node --test tests-js/*.test.cjs
python -m pip check
```

The GitHub Actions CI workflow tests supported Python versions, the HTTP API, HMAC tamper detection, and browser calculations. A separate Pages workflow publishes the static `web/` directory when GitHub Pages is enabled for Actions deployment. Docker is also available:

```bash
docker compose up --build
```

Browsers: recent Chrome, Firefox, Safari, and Edge supporting standard ES2015+ JavaScript and the Fetch-free DOM API. The browser calculator does not run Python; no Pyodide is needed.

## License

MIT. See [LICENSE](LICENSE).
