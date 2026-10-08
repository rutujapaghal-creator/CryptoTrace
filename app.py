import os
import json
import sqlite3
import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from ved.database.db import get_connection, init_db
from ved.database.seed_data import seed_database
from ved.core.validation import detect_and_validate_wallet
from ved.core.tracing import TracingEngine
from ved.services.ncrp_service import NCRPService
from ved.services.report_service import ReportService
from ved.services.watchtower import WatchtowerService

app = FastAPI(
    title="Project VED",
    description="Virtual Evidence & Attribution Directorate - Crypto Fraud Attribution System",
    version="2.4.0"
)

seed_database()

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")

if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR, exist_ok=True)
if not os.path.exists(TEMPLATES_DIR):
    os.makedirs(TEMPLATES_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

class TraceRequest(BaseModel):
    wallet_address: str
    chain: Optional[str] = None
    max_hops: Optional[int] = 8
    complaint_category: Optional[str] = "INVESTMENT_FRAUD"

class IngestComplaintRequest(BaseModel):
    source: str = "NCRP"
    acknowledgement_no: str
    victim_name: str
    victim_city: str
    victim_state: str
    fraud_category: str
    suspect_wallet: str
    amount_inr: float
    token_symbol: str = "USDT"
    victim_tx_hash: Optional[str] = None

class FreezeNoticeRequest(BaseModel):
    case_number: str
    investigator_name: str
    io_unit: str
    vasp_hit: dict
    victim_loss_inr: float
    evidence_hash: str
    trace_payload: dict

@app.get("/", response_class=HTMLResponse)
def index_page():
    index_file = os.path.join(TEMPLATES_DIR, "index.html")
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Project VED UI Initializing...</h1>"

@app.get("/api/stats")
def get_stats():
    conn = get_connection()
    try:
        wt = WatchtowerService(conn)
        return wt.get_system_stats()
    finally:
        conn.close()

@app.post("/api/validate-address")
def validate_address_endpoint(req: dict):
    address = req.get("address", "")
    return detect_and_validate_wallet(address)

@app.post("/api/trace")
def execute_trace(req: TraceRequest):
    address = req.wallet_address.strip()
    val = detect_and_validate_wallet(address)
    if not val["valid"]:
        raise HTTPException(status_code=400, detail=val.get("error", "Invalid blockchain address format"))

    detected_chain = val["chain"]
    chain = req.chain or detected_chain

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT case_number, total_victims, primary_fraud_category, total_loss_inr FROM cases WHERE LOWER(primary_wallet) = LOWER(?)", (address,))
        case_row = cur.fetchone()
        
        complaints_count = case_row["total_victims"] if case_row else 1
        complaint_category = case_row["primary_fraud_category"] if case_row else req.complaint_category

        tracer = TracingEngine(conn)
        trace_result = tracer.trace_wallet(
            seed_wallet=address,
            chain=chain,
            max_hops=req.max_hops or 8,
            complaints_count=complaints_count,
            complaint_category=complaint_category
        )

        trace_result["address_validation"] = val
        trace_result["linked_case"] = dict(case_row) if case_row else None
        return trace_result
    finally:
        conn.close()

@app.get("/api/cases")
def list_cases():
    conn = get_connection()
    try:
        ncrp = NCRPService(conn)
        return ncrp.list_cases()
    finally:
        conn.close()

@app.get("/api/cases/{case_id}")
def get_case_details(case_id: str):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM cases WHERE case_id = ?", (case_id,))
        case = cur.fetchone()
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")

        cur.execute("SELECT * FROM complaints WHERE case_cluster_id = ? ORDER BY complaint_timestamp DESC", (case_id,))
        complaints = [dict(r) for r in cur.fetchall()]

        return {
            "case": dict(case),
            "complaints": complaints
        }
    finally:
        conn.close()

@app.get("/api/complaints")
def list_complaints(limit: int = 50):
    conn = get_connection()
    try:
        ncrp = NCRPService(conn)
        return ncrp.list_recent_complaints(limit=limit)
    finally:
        conn.close()

@app.post("/api/complaints/ingest")
def ingest_complaint(req: IngestComplaintRequest):
    conn = get_connection()
    try:
        ncrp = NCRPService(conn)
        res = ncrp.ingest_complaint(
            source=req.source,
            acknowledgement_no=req.acknowledgement_no,
            victim_name=req.victim_name,
            victim_city=req.victim_city,
            victim_state=req.victim_state,
            fraud_category=req.fraud_category,
            suspect_wallet=req.suspect_wallet,
            amount_inr=req.amount_inr,
            token_symbol=req.token_symbol,
            victim_tx_hash=req.victim_tx_hash
        )
        if not res["success"]:
            raise HTTPException(status_code=400, detail=res["error"])
        return res
    finally:
        conn.close()

@app.get("/api/vasps")
def list_vasps():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT address, chain, entity_name, entity_type, fiu_registered,
                   jurisdiction, nodal_officer_email, nodal_portal_url, notes
            FROM entity_labels
            ORDER BY fiu_registered DESC, entity_name ASC
        """)
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()

@app.get("/api/alerts")
def list_alerts(limit: int = 20):
    conn = get_connection()
    try:
        wt = WatchtowerService(conn)
        return wt.get_active_alerts(limit=limit)
    finally:
        conn.close()

@app.post("/api/freeze-notice")
def generate_freeze_notice(req: FreezeNoticeRequest):
    notice = ReportService.generate_freeze_notice_bnss106(
        case_number=req.case_number,
        investigator_name=req.investigator_name,
        io_unit=req.io_unit,
        vasp_hit=req.vasp_hit,
        victim_loss_inr=req.victim_loss_inr,
        evidence_hash=req.evidence_hash,
        trace_payload=req.trace_payload
    )
    return notice

@app.post("/api/bsa-certificate")
def generate_bsa_certificate(req: dict):
    cert = ReportService.generate_bsa_section63_certificate(
        case_number=req.get("case_number", "VED-MH-2026-0841"),
        investigator_name=req.get("investigator_name", "Investigating Officer"),
        io_unit=req.get("io_unit", "State Cyber Cell"),
        evidence_hash=req.get("evidence_hash", ""),
        trace_payload=req.get("trace_payload", {})
    )
    return cert

@app.get("/api/dossier/{case_id}", response_class=HTMLResponse)
def view_full_dossier(case_id: str):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM cases WHERE case_id = ?", (case_id,))
        case = cur.fetchone()
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")

        tracer = TracingEngine(conn)
        trace_res = tracer.trace_wallet(
            seed_wallet=case["primary_wallet"],
            chain=case["chain"],
            complaints_count=case["total_victims"],
            complaint_category=case["primary_fraud_category"]
        )

        top_hit = trace_res["vasp_attribution"][0] if trace_res["vasp_attribution"] else {
            "vasp_name": "Target VASP", "deposit_address": "N/A", "amount": 0, "token_symbol": "USDT", "confidence_pct": 90
        }

        freeze_notice = ReportService.generate_freeze_notice_bnss106(
            case_number=case["case_number"],
            investigator_name=case["lead_investigator"],
            io_unit=case["io_unit"],
            vasp_hit=top_hit,
            victim_loss_inr=case["total_loss_inr"],
            evidence_hash=trace_res["sha256_evidence_hash"],
            trace_payload=trace_res
        )

        bsa_cert = ReportService.generate_bsa_section63_certificate(
            case_number=case["case_number"],
            investigator_name=case["lead_investigator"],
            io_unit=case["io_unit"],
            evidence_hash=trace_res["sha256_evidence_hash"],
            trace_payload=trace_res
        )

        html = ReportService.generate_html_dossier(
            case_info=dict(case),
            trace_payload=trace_res,
            freeze_notice=freeze_notice,
            bsa_cert=bsa_cert
        )
        return html
    finally:
        conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("ved.app:app", host="127.0.0.1", port=8000, reload=True)
