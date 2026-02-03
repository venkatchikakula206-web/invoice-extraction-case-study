from pydantic import BaseModel, Field
from typing import List, Optional

class LineItem(BaseModel):
    item_number: Optional[str] = None
    description: str
    qty: float
    unit_price: float
    line_total: float

class ExtractedInvoice(BaseModel):
    invoice_number: Optional[str] = None
    purchase_order_number: Optional[str] = None
    order_date: Optional[str] = None   # ISO date
    due_date: Optional[str] = None
    ship_date: Optional[str] = None
    salesperson: Optional[str] = None
    ship_via: Optional[str] = None
    terms: Optional[str] = None

    subtotal: Optional[float] = None
    tax_rate: Optional[float] = None
    tax_amt: Optional[float] = None
    freight: Optional[float] = None
    total_due: Optional[float] = None
    currency: Optional[str] = None

    bill_to_name: Optional[str] = None
    ship_to_name: Optional[str] = None

    items: List[LineItem] = Field(default_factory=list)
    confidence: Optional[float] = None
    warnings: List[str] = Field(default_factory=list)

class DocumentStatus(BaseModel):
    id: int
    filename: str
    status: str
    error: Optional[str] = None
    extracted: Optional[ExtractedInvoice] = None
    sales_order_id: Optional[int] = None
