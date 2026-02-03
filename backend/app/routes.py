from __future__ import annotations
import json
import os
import time
from flask import Blueprint, current_app, request, Response

from .schemas import DocumentStatus, ExtractedInvoice
from .services import (
    create_document, get_document, update_sales_order_from_payload,
    list_orders, get_order
)
from .events import subscribe, unsubscribe

api = Blueprint("api", __name__)

# Supported MIME types for document extraction
SUPPORTED_MIME_TYPES = {
    "application/pdf",
    "image/png", "image/jpeg", "image/jpg", "image/gif",
    "image/webp", "image/tiff", "image/bmp"
}

@api.post("/documents")
def upload_document():
    settings = current_app.config["SETTINGS"]
    if "file" not in request.files:
        return {"error": "missing file"}, 400

    f = request.files["file"]
    if not f.filename:
        return {"error": "missing filename"}, 400

    file_bytes = f.read()
    max_bytes = settings.max_upload_mb * 1024 * 1024
    if len(file_bytes) > max_bytes:
        return {"error": f"file too large (>{settings.max_upload_mb}MB)"}, 413

    content_type = f.mimetype or "application/octet-stream"
    
    # Check for PDF by magic bytes (more reliable than MIME type)
    is_pdf = file_bytes[:4] == b"%PDF" or content_type == "application/pdf"
    is_image = content_type.startswith("image/")
    
    if not is_pdf and not is_image:
        return {
            "error": f"Unsupported file type: {content_type}. Please upload a PDF or image file (PNG, JPEG, GIF, WEBP, TIFF, BMP)."
        }, 415

    doc_id = create_document(settings, f.filename, content_type, file_bytes)
    return {"document_id": doc_id}, 201

@api.get("/documents/<int:doc_id>")
def get_document_status(doc_id: int):
    settings = current_app.config["SETTINGS"]
    doc = get_document(settings, doc_id)
    if not doc:
        return {"error": "not found"}, 404

    extracted = None
    if doc.extracted_json:
        extracted = ExtractedInvoice.model_validate_json(doc.extracted_json)

    payload = DocumentStatus(
        id=doc.id,
        filename=doc.filename,
        status=doc.status,
        error=doc.error,
        extracted=extracted,
        sales_order_id=doc.sales_order_id
    ).model_dump()
    return payload

@api.get("/documents/<int:doc_id>/events")
def document_events(doc_id: int):
    # Server-Sent Events stream for live UI updates
    q = subscribe(doc_id)

    def gen():
        try:
            yield "event: status\ndata: " + json.dumps({"status": "connected"}) + "\n\n"
            while True:
                event = q.get()
                yield f"event: {event.get('type','message')}\n"
                yield "data: " + json.dumps(event) + "\n\n"
        except GeneratorExit:
            pass
        finally:
            unsubscribe(doc_id, q)

    return Response(gen(), mimetype="text/event-stream", headers={
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no"
    })

@api.put("/documents/<int:doc_id>/save")
def save_extracted(doc_id: int):
    settings = current_app.config["SETTINGS"]
    payload = request.get_json(force=True, silent=False)
    try:
        sales_order_id = update_sales_order_from_payload(settings, doc_id, payload)
        return {"sales_order_id": sales_order_id}, 200
    except Exception as e:
        return {"error": str(e)}, 400

@api.get("/orders")
def orders():
    settings = current_app.config["SETTINGS"]
    limit = int(request.args.get("limit", "50"))
    rows = list_orders(settings, limit=limit)
    return {
        "orders": [
            {
                "SalesOrderID": r.SalesOrderID,
                "SalesOrderNumber": r.SalesOrderNumber,
                "OrderDate": r.OrderDate.isoformat() if r.OrderDate else None,
                "SubTotal": r.SubTotal,
                "TaxAmt": r.TaxAmt,
                "Freight": r.Freight,
                "TotalDue": r.TotalDue,
            } for r in rows
        ]
    }

@api.get("/orders/<int:sales_order_id>")
def order_detail(sales_order_id: int):
    settings = current_app.config["SETTINGS"]
    header = get_order(settings, sales_order_id)
    if not header:
        return {"error": "not found"}, 404
    return {
        "header": {
            "SalesOrderID": header.SalesOrderID,
            "SalesOrderNumber": header.SalesOrderNumber,
            "PurchaseOrderNumber": header.PurchaseOrderNumber,
            "OrderDate": header.OrderDate.isoformat() if header.OrderDate else None,
            "DueDate": header.DueDate.isoformat() if header.DueDate else None,
            "ShipDate": header.ShipDate.isoformat() if header.ShipDate else None,
            "SubTotal": header.SubTotal,
            "TaxAmt": header.TaxAmt,
            "Freight": header.Freight,
            "TotalDue": header.TotalDue,
        },
        "details": [
            {
                "SalesOrderDetailID": d.SalesOrderDetailID,
                "OrderQty": d.OrderQty,
                "UnitPrice": d.UnitPrice,
                "LineTotal": d.LineTotal,
            } for d in header.details
        ]
    }
