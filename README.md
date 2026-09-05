# Parenteral Nutrition TPN Agent

> **Domain:** Gastroenterology, Hepatology & Clinical Nutrition
> **Reference Guidelines & Standards:** AASLD & ACG Clinical Practice Guidelines, ASPEN / ESPEN Parenteral Nutrition Standards

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## What It Does

**Parenteral Nutrition TPN Agent** is an advanced analytical and computational platform implementing TPN Macronutrient, Osmolarity & Refeeding Syndrome Prophylaxis evaluation. It uses a multi-agent architecture to evaluate clinical cases against established guidelines.

---

## Architecture

The project contains two parallel agent implementations:

### 1. Enterprise Agent System (`agents/`)

- **`agents/models.py`** — Pydantic v2 schemas with input validation
- **`agents/base.py`** — Security (PHI guard), HMAC-SHA256 audit trail
- **`agents/supervisor.py`** — Master orchestrator coordinating worker evaluations
- **`agents/workers.py`** — Specialized domain workers (QC, Safety, Protocol Conformance)
- **`agents/api.py`** — FastAPI REST endpoints
- **`agents/metrics.py`** — Prometheus operational metrics
- **`agents/learning.py`** — Bayesian calibration & active learning
- **`agents/streamer.py`** — WebSocket telemetry broadcaster

### 2. Clinical TPN Engine (`parenteral_nutrition_tpn_agent/`)

- **`models.py`** — Clinical data models (dataclass-based)
- **`agents.py`** — Sub-agents: CaloricMacronutrientAgent, RefeedingSyndromeAuditorAgent, OsmolarityPeripheralCentralAgent
- **`engine.py`** — Clinical algorithmic engine with ASPEN/ESPEN guideline rules
- **`server.py`** — FastAPI REST application
- **`cli.py`** — Command-line interface

### 3. Enrichment Module (`enrichment.py`)

- Feature evaluation engines for monitoring, escalation, deployment, audit, workflow integration, predictive analytics, and patient outcomes.

---

## Installation

```bash
# Clone the repository
git clone https://github.com/abusuraihsakhri/parenteral-nutrition-tpn-agent.git
cd parenteral-nutrition-tpn-agent

# Install dependencies
pip install fastapi uvicorn pydantic pytest
```

---

## CLI Quickstart & Usage

### 1. Single Case Evaluation
```bash
python cli.py audit --task-id TASK-001 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
```

### 2. Interactive Chat
```bash
python cli.py chat "What is the system status?"
```

### 3. Batch CSV Processing
```bash
python cli.py batch -i sample.csv -o results.csv
```

### 4. Verify Audit Trail Integrity
```bash
python cli.py verify-audit
```

### 5. Launch REST API Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### Parameter Reference
| Flag | Description | Default |
|:-----|:------------|:--------|
| `--task-id` | Unique task/case identifier | TASK-2026-001 |
| `--target` | Target entity identifier | KEY-TARGET-01 |
| `--primary` | Primary measurement value | 28.5 |
| `--secondary` | Secondary metric value | 14.2 |
| `--critical` | Trigger emergency escalation | False |
| `--status` | Status/phenotype descriptor | DISCORDANT |

---

## REST API Endpoints

| Method | Endpoint | Description |
|:-------|:---------|:------------|
| GET | `/health` | Service health check |
| GET | `/metrics` | Operational metrics |
| POST | `/api/audit` | Submit case for evaluation |
| POST | `/api/chat` | Query supervisory chat |
| GET | `/api/audit/logs` | Retrieve HMAC audit trail |

---

## Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation.
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances, Claude, GPT-4o, and deterministic test mocks.
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics.

### Security Configuration

Set the `AUDIT_SECRET_KEY` environment variable in production to ensure audit trail persistence across restarts:

```bash
# Linux/macOS
export AUDIT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")

# Windows PowerShell
$env:AUDIT_SECRET_KEY = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 64 | % {[char]$_})
```

---

## Testing

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py 1000
```

---

## Container Deployment

```bash
# Build and run with Docker Compose (recommended)
docker-compose up --build

# Or manually
docker build -t parenteral-nutrition-tpn-agent .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY=your-secret-key parenteral-nutrition-tpn-agent
```

---

## License

MIT License. See [LICENSE](LICENSE) for details.
