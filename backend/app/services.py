from __future__ import annotations
import json
import os
import threading
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from .config import Settings
from .db import get_session_factory
from .events import publish
from .models import Document, SalesOrderHeader, SalesOrderDetail
from .schemas import ExtractedInvoice
from .doc_utils import normalize_to_png_bytes
from .llm.factory import get_extractor

_executor_lock = threading.Lock()
_executor_started = False

def _start_background_once():
    global _executor_started
    with _executor_lock:
        if not _executor_started:
            _executor_started = True

def create_document(settings: Settings, filename: str, content_type: str, file_bytes: bytes) -> int:
    _start_background_once()
    sess_factory = get_session_factory(settings)

    storage_path = os.path.join(settings.upload_dir, f"{int(datetime.utcnow().timestamp())}_{filename}")
    os.makedirs(settings.upload_dir, exist_ok=True)
    with open(storage_path, "wb") as f:
        f.write(file_bytes)

    with sess_factory() as db:
        doc = Document(filename=filename, content_type=content_type, storage_path=storage_path, status="uploaded")
        db.add(doc)
        db.commit()
        db.refresh(doc)

    # start async processing
    t = threading.Thread(target=_process_document, args=(settings, doc.id), daemon=True)
    t.start()
    return doc.id

def get_document(settings: Settings, doc_id: int) -> Document | None:
    sess_factory = get_session_factory(settings)
    with sess_factory() as db:
        return db.get(Document, doc_id)

def update_document_extracted(settings: Settings, doc_id: int, extracted: ExtractedInvoice):
    sess_factory = get_session_factory(settings)
    with sess_factory() as db:
        doc = db.get(Document, doc_id)
        if not doc:
            return
        doc.extracted_json = extracted.model_dump_json()
        doc.status = "extracted"
        db.commit()

def save_to_sales_orders(settings: Settings, doc_id: int, extracted: ExtractedInvoice) -> int:
    sess_factory = get_session_factory(settings)
    with sess_factory() as db:
        doc = db.get(Document, doc_id)
        if not doc:
            raise ValueError("Document not found")

        # Create header (let SalesOrderID autoincrement beyond seeded max)
        header = SalesOrderHeader(
            RevisionNumber=1,
            OrderDate=_parse_dt(extracted.order_date),
            DueDate=_parse_dt(extracted.due_date),
            ShipDate=_parse_dt(extracted.ship_date),
            Status=5,  # shipped/complete (demo)
            OnlineOrderFlag=False,
            SalesOrderNumber=extracted.invoice_number,
            PurchaseOrderNumber=extracted.purchase_order_number,
            SubTotal=extracted.subtotal,
            TaxAmt=extracted.tax_amt,
            Freight=extracted.freight,
            TotalDue=extracted.total_due,
        )
        db.add(header)
        db.flush()  # obtains SalesOrderID if autogen

        # Create details
        for li in extracted.items:
            detail = SalesOrderDetail(
                SalesOrderID=header.SalesOrderID,
                OrderQty=int(li.qty),
                UnitPrice=float(li.unit_price),
                UnitPriceDiscount=0.0,
                LineTotal=float(li.line_total),
            )
            db.add(detail)

        doc.sales_order_id = header.SalesOrderID
        doc.status = "saved"
        db.commit()
        return header.SalesOrderID

def update_sales_order_from_payload(settings: Settings, doc_id: int, payload: dict) -> int:
    extracted = ExtractedInvoice.model_validate(payload)
    update_document_extracted(settings, doc_id, extracted)
    return save_to_sales_orders(settings, doc_id, extracted)

def list_orders(settings: Settings, limit: int = 50):
    sess_factory = get_session_factory(settings)
    with sess_factory() as db:
        rows = db.execute(select(SalesOrderHeader).order_by(SalesOrderHeader.SalesOrderID.desc()).limit(limit)).scalars().all()
        return rows

def get_order(settings: Settings, sales_order_id: int):
    sess_factory = get_session_factory(settings)
    with sess_factory() as db:
        header = db.get(SalesOrderHeader, sales_order_id)
        if not header:
            return None
        # load details
        _ = header.details
        return header

def _process_document(settings: Settings, doc_id: int):
    sess_factory = get_session_factory(settings)
    publish(doc_id, {"type": "status", "status": "processing"})
    with sess_factory() as db:
        doc = db.get(Document, doc_id)
        if not doc:
            return
        doc.status = "processing"
        db.commit()

    try:
        with open(doc.storage_path, "rb") as f:
            raw = f.read()
        png = normalize_to_png_bytes(raw, doc.content_type)

        publish(doc_id, {"type": "status", "status": "calling_llm"})
        extractor = get_extractor(settings)
        extracted = extractor.extract(png)

        update_document_extracted(settings, doc_id, extracted)
        publish(doc_id, {"type": "extracted", "data": extracted.model_dump()})
        publish(doc_id, {"type": "status", "status": "extracted"})

    except Exception as e:
        with sess_factory() as db:
            doc = db.get(Document, doc_id)
            if doc:
                doc.status = "failed"
                doc.error = str(e)
                db.commit()
        publish(doc_id, {"type": "error", "message": str(e)})

def _parse_dt(s: str | None):
    if not s:
        return None
    # Accept YYYY-MM-DD or ISO datetime
    try:
        return datetime.fromisoformat(s.replace("Z",""))
    except Exception:
        try:
            return datetime.strptime(s, "%Y-%m-%d")
        except Exception:
            return None
