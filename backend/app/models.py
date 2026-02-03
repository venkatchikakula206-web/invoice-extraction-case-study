from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .db import Base

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(255), nullable=False)
    content_type = Column(String(100), nullable=False)
    storage_path = Column(String(500), nullable=False)
    status = Column(String(50), nullable=False, default="uploaded")  # uploaded|processing|extracted|saved|failed
    error = Column(Text, nullable=True)
    extracted_json = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    sales_order_id = Column(Integer, ForeignKey("sales_order_header.SalesOrderID"), nullable=True)
    sales_order = relationship("SalesOrderHeader", back_populates="documents")

class SalesOrderHeader(Base):
    __tablename__ = "sales_order_header"
    SalesOrderID = Column(Integer, primary_key=True)
    RevisionNumber = Column(Integer, nullable=True)
    OrderDate = Column(DateTime, nullable=True)
    DueDate = Column(DateTime, nullable=True)
    ShipDate = Column(DateTime, nullable=True)
    Status = Column(Integer, nullable=True)
    OnlineOrderFlag = Column(Boolean, nullable=True)
    SalesOrderNumber = Column(String(50), nullable=True)
    PurchaseOrderNumber = Column(String(50), nullable=True)
    AccountNumber = Column(String(50), nullable=True)
    CustomerID = Column(Integer, nullable=True)
    SalesPersonID = Column(Integer, nullable=True)
    TerritoryID = Column(Integer, nullable=True)
    BillToAddressID = Column(Integer, nullable=True)
    ShipToAddressID = Column(Integer, nullable=True)
    ShipMethodID = Column(Integer, nullable=True)
    CreditCardID = Column(Integer, nullable=True)
    CreditCardApprovalCode = Column(String(50), nullable=True)
    CurrencyRateID = Column(Integer, nullable=True)
    SubTotal = Column(Float, nullable=True)
    TaxAmt = Column(Float, nullable=True)
    Freight = Column(Float, nullable=True)
    TotalDue = Column(Float, nullable=True)

    details = relationship("SalesOrderDetail", back_populates="header", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="sales_order")

class SalesOrderDetail(Base):
    __tablename__ = "sales_order_detail"
    SalesOrderDetailID = Column(Integer, primary_key=True)
    SalesOrderID = Column(Integer, ForeignKey("sales_order_header.SalesOrderID"), nullable=False)
    CarrierTrackingNumber = Column(String(50), nullable=True)
    OrderQty = Column(Integer, nullable=False)
    ProductID = Column(Integer, nullable=True)
    SpecialOfferID = Column(Integer, nullable=True)
    UnitPrice = Column(Float, nullable=False)
    UnitPriceDiscount = Column(Float, nullable=True)
    LineTotal = Column(Float, nullable=False)

    header = relationship("SalesOrderHeader", back_populates="details")
