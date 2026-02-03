from __future__ import annotations
import os
import pandas as pd
from sqlalchemy import select, func

from .db import get_session_factory
from .models import SalesOrderHeader, SalesOrderDetail

DEFAULT_XLSX_CANDIDATES = [
    "/mnt/data/Case Study Data.xlsx",
    "../Case Study Data.xlsx",
]

def maybe_seed_from_excel(app):
    settings = app.config["SETTINGS"]
    xlsx = settings.case_study_xlsx_path

    if not xlsx:
        for c in DEFAULT_XLSX_CANDIDATES:
            if os.path.exists(c):
                xlsx = c
                break

    if not xlsx or not os.path.exists(xlsx):
        return

    sess_factory = get_session_factory(settings)
    with sess_factory() as db:
        count = db.execute(select(func.count()).select_from(SalesOrderHeader)).scalar_one()
        if count and count > 0:
            return

    _seed(xlsx, settings)

def _seed(xlsx_path: str, settings):
    sess_factory = get_session_factory(settings)

    hdr = pd.read_excel(xlsx_path, sheet_name="SalesOrderHeader")
    dtl = pd.read_excel(xlsx_path, sheet_name="SalesOrderDetail")

    # Normalize datetimes
    for col in ["OrderDate", "DueDate", "ShipDate"]:
        hdr[col] = pd.to_datetime(hdr[col], errors="coerce")

    with sess_factory() as db:
        # Insert headers
        headers = []
        for _, r in hdr.iterrows():
            headers.append(SalesOrderHeader(
                SalesOrderID=int(r["SalesOrderID"]),
                RevisionNumber=_int_or_none(r.get("RevisionNumber")),
                OrderDate=_dt_or_none(r.get("OrderDate")),
                DueDate=_dt_or_none(r.get("DueDate")),
                ShipDate=_dt_or_none(r.get("ShipDate")),
                Status=_int_or_none(r.get("Status")),
                OnlineOrderFlag=bool(r.get("OnlineOrderFlag")) if r.get("OnlineOrderFlag") is not None else None,
                SalesOrderNumber=_str_or_none(r.get("SalesOrderNumber")),
                PurchaseOrderNumber=_str_or_none(r.get("PurchaseOrderNumber")),
                AccountNumber=_str_or_none(r.get("AccountNumber")),
                CustomerID=_int_or_none(r.get("CustomerID")),
                SalesPersonID=_int_or_none(r.get("SalesPersonID")),
                TerritoryID=_int_or_none(r.get("TerritoryID")),
                BillToAddressID=_int_or_none(r.get("BillToAddressID")),
                ShipToAddressID=_int_or_none(r.get("ShipToAddressID")),
                ShipMethodID=_int_or_none(r.get("ShipMethodID")),
                CreditCardID=_int_or_none(r.get("CreditCardID")),
                CreditCardApprovalCode=_str_or_none(r.get("CreditCardApprovalCode")),
                CurrencyRateID=_int_or_none(r.get("CurrencyRateID")),
                SubTotal=_float_or_none(r.get("SubTotal")),
                TaxAmt=_float_or_none(r.get("TaxAmt")),
                Freight=_float_or_none(r.get("Freight")),
                TotalDue=_float_or_none(r.get("TotalDue")),
            ))
        db.bulk_save_objects(headers)

        # Insert details
        details = []
        for _, r in dtl.iterrows():
            details.append(SalesOrderDetail(
                SalesOrderDetailID=int(r["SalesOrderDetailID"]),
                SalesOrderID=int(r["SalesOrderID"]),
                CarrierTrackingNumber=_str_or_none(r.get("CarrierTrackingNumber")),
                OrderQty=int(r.get("OrderQty")) if not pd.isna(r.get("OrderQty")) else 0,
                ProductID=_int_or_none(r.get("ProductID")),
                SpecialOfferID=_int_or_none(r.get("SpecialOfferID")),
                UnitPrice=float(r.get("UnitPrice")) if not pd.isna(r.get("UnitPrice")) else 0.0,
                UnitPriceDiscount=_float_or_none(r.get("UnitPriceDiscount")),
                LineTotal=float(r.get("LineTotal")) if not pd.isna(r.get("LineTotal")) else 0.0,
            ))
        db.bulk_save_objects(details)

        db.commit()

def _str_or_none(v):
    import pandas as pd
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    s = str(v).strip()
    return s if s else None

def _int_or_none(v):
    import pandas as pd
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    try:
        return int(v)
    except Exception:
        return None

def _float_or_none(v):
    import pandas as pd
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    try:
        return float(v)
    except Exception:
        return None

def _dt_or_none(v):
    import pandas as pd
    if v is None or pd.isna(v):
        return None
    return v.to_pydatetime() if hasattr(v, "to_pydatetime") else v
