import argparse
import os
from datetime import date
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

SAMPLES = [
    {
        "template": "classic",
        "invoice_number": "SO-DEMO-1001",
        "date": "2026-01-30",
        "customer": "Acme Retail LLC",
        "ship_to": "Acme Retail LLC",
        "items": [
            {"desc": "Product XYZ", "qty": 15, "unit": 150.00},
            {"desc": "Product ABC", "qty": 1, "unit": 75.00},
        ],
        "tax_rate": 0.06875,
        "freight": 0.00,
        "terms": "Net 30",
        "ship_via": "UPS Ground",
        "salesperson": "Demo Rep",
    },
    {
        "template": "minimal",
        "invoice_number": "SO-DEMO-1002",
        "date": "2026-01-30",
        "customer": "Bluebird Foods Inc",
        "ship_to": "Bluebird Foods Warehouse",
        "items": [
            {"desc": "Organic Granola Bars (Case)", "qty": 8, "unit": 42.50},
            {"desc": "Assorted Snacks Pack", "qty": 3, "unit": 19.99},
        ],
        "tax_rate": 0.0825,
        "freight": 12.95,
        "terms": "Due on receipt",
        "ship_via": "FedEx",
        "salesperson": "A. Patel",
    },
    {
        "template": "boxed",
        "invoice_number": "SO-DEMO-1003",
        "date": "2026-01-29",
        "customer": "Sunrise Hardware",
        "ship_to": "Sunrise Hardware - Dock 2",
        "items": [
            {"desc": "Steel Screws 2in (1000ct)", "qty": 2, "unit": 58.00},
            {"desc": "Wood Drill Bits Set", "qty": 5, "unit": 24.25},
            {"desc": "Measuring Tape 25ft", "qty": 10, "unit": 9.99},
        ],
        "tax_rate": 0.0725,
        "freight": 24.50,
        "terms": "Net 15",
        "ship_via": "DHL",
        "salesperson": "S. Kim",
    },
]

def money(x): 
    return f"{x:,.2f}"

def calc_totals(sample):
    subtotal = sum(it["qty"] * it["unit"] for it in sample["items"])
    tax = subtotal * sample["tax_rate"]
    total = subtotal + tax + sample["freight"]
    return subtotal, tax, total

def draw_classic(c, s):
    w, h = letter
    c.setFont("Helvetica-Bold", 20)
    c.drawRightString(w - 0.75*inch, h - 0.75*inch, "INVOICE")
    c.setFont("Helvetica", 10)
    c.drawString(0.75*inch, h - 0.85*inch, "Demo Company Inc.")
    c.drawString(0.75*inch, h - 1.05*inch, "123 Demo Street, San Jose, CA 95112")
    c.drawString(0.75*inch, h - 1.25*inch, "Phone: (555) 000-0000")

    c.setFont("Helvetica-Bold", 10)
    c.drawString(w - 2.5*inch, h - 1.1*inch, "DATE")
    c.drawString(w - 1.4*inch, h - 1.1*inch, s["date"])
    c.drawString(w - 2.5*inch, h - 1.3*inch, "INVOICE #")
    c.drawString(w - 1.4*inch, h - 1.3*inch, s["invoice_number"])

    c.setFont("Helvetica-Bold", 10)
    c.drawString(0.75*inch, h - 1.75*inch, "BILL TO:")
    c.setFont("Helvetica", 10)
    c.drawString(0.75*inch, h - 1.95*inch, s["customer"])

    c.setFont("Helvetica-Bold", 10)
    c.drawString(3.75*inch, h - 1.75*inch, "SHIP TO:")
    c.setFont("Helvetica", 10)
    c.drawString(3.75*inch, h - 1.95*inch, s["ship_to"])

    c.setFont("Helvetica-Bold", 9)
    c.drawString(0.75*inch, h - 2.4*inch, "SALESPERSON:")
    c.setFont("Helvetica", 9)
    c.drawString(1.75*inch, h - 2.4*inch, s["salesperson"])
    c.setFont("Helvetica-Bold", 9)
    c.drawString(3.75*inch, h - 2.4*inch, "SHIP VIA:")
    c.setFont("Helvetica", 9)
    c.drawString(4.55*inch, h - 2.4*inch, s["ship_via"])
    c.setFont("Helvetica-Bold", 9)
    c.drawString(5.95*inch, h - 2.4*inch, "TERMS:")
    c.setFont("Helvetica", 9)
    c.drawString(6.45*inch, h - 2.4*inch, s["terms"])

    # Table header
    y = h - 2.85*inch
    c.setFont("Helvetica-Bold", 10)
    c.rect(0.75*inch, y, w-1.5*inch, 0.3*inch, stroke=1, fill=0)
    c.drawString(0.85*inch, y + 0.1*inch, "DESCRIPTION")
    c.drawRightString(w - 2.6*inch, y + 0.1*inch, "QTY")
    c.drawRightString(w - 1.6*inch, y + 0.1*inch, "UNIT PRICE")
    c.drawRightString(w - 0.85*inch, y + 0.1*inch, "TOTAL")

    c.setFont("Helvetica", 10)
    y -= 0.35*inch
    for it in s["items"]:
        line_total = it["qty"]*it["unit"]
        c.drawString(0.85*inch, y, it["desc"])
        c.drawRightString(w - 2.6*inch, y, str(it["qty"]))
        c.drawRightString(w - 1.6*inch, y, money(it["unit"]))
        c.drawRightString(w - 0.85*inch, y, money(line_total))
        y -= 0.25*inch

    subtotal, tax, total = calc_totals(s)
    y -= 0.25*inch
    c.setFont("Helvetica-Bold", 10)
    c.drawRightString(w - 1.6*inch, y, "SUBTOTAL")
    c.setFont("Helvetica", 10)
    c.drawRightString(w - 0.85*inch, y, money(subtotal))
    y -= 0.2*inch
    c.setFont("Helvetica-Bold", 10)
    c.drawRightString(w - 1.6*inch, y, f"TAX ({s['tax_rate']*100:.3f}%)")
    c.setFont("Helvetica", 10)
    c.drawRightString(w - 0.85*inch, y, money(tax))
    y -= 0.2*inch
    c.setFont("Helvetica-Bold", 10)
    c.drawRightString(w - 1.6*inch, y, "FREIGHT")
    c.setFont("Helvetica", 10)
    c.drawRightString(w - 0.85*inch, y, money(s["freight"]))
    y -= 0.25*inch
    c.setFont("Helvetica-Bold", 11)
    c.drawRightString(w - 1.6*inch, y, "TOTAL DUE")
    c.drawRightString(w - 0.85*inch, y, money(total))

def draw_minimal(c, s):
    w, h = letter
    c.setFont("Helvetica-Bold", 18)
    c.drawString(0.75*inch, h - 0.9*inch, "Invoice")
    c.setFont("Helvetica", 10)
    c.drawString(0.75*inch, h - 1.2*inch, f"Invoice #: {s['invoice_number']}")
    c.drawString(0.75*inch, h - 1.4*inch, f"Date: {s['date']}")
    c.drawString(0.75*inch, h - 1.6*inch, f"Billed To: {s['customer']}")
    c.drawString(0.75*inch, h - 1.8*inch, f"Ship To: {s['ship_to']}")
    c.drawString(0.75*inch, h - 2.0*inch, f"Terms: {s['terms']}   Ship Via: {s['ship_via']}   Sales: {s['salesperson']}")

    y = h - 2.5*inch
    c.setFont("Helvetica-Bold", 10)
    c.drawString(0.75*inch, y, "Item")
    c.drawRightString(w - 3.0*inch, y, "Qty")
    c.drawRightString(w - 2.0*inch, y, "Unit")
    c.drawRightString(w - 0.75*inch, y, "Total")
    y -= 0.2*inch
    c.line(0.75*inch, y, w - 0.75*inch, y)
    y -= 0.25*inch
    c.setFont("Helvetica", 10)
    for it in s["items"]:
        c.drawString(0.75*inch, y, it["desc"])
        c.drawRightString(w - 3.0*inch, y, str(it["qty"]))
        c.drawRightString(w - 2.0*inch, y, money(it["unit"]))
        c.drawRightString(w - 0.75*inch, y, money(it["qty"]*it["unit"]))
        y -= 0.25*inch

    subtotal, tax, total = calc_totals(s)
    y -= 0.2*inch
    c.setFont("Helvetica-Bold", 10)
    c.drawRightString(w - 2.0*inch, y, "Subtotal")
    c.setFont("Helvetica", 10)
    c.drawRightString(w - 0.75*inch, y, money(subtotal))
    y -= 0.2*inch
    c.setFont("Helvetica-Bold", 10)
    c.drawRightString(w - 2.0*inch, y, f"Tax ({s['tax_rate']*100:.2f}%)")
    c.setFont("Helvetica", 10)
    c.drawRightString(w - 0.75*inch, y, money(tax))
    y -= 0.2*inch
    c.setFont("Helvetica-Bold", 10)
    c.drawRightString(w - 2.0*inch, y, "Freight")
    c.setFont("Helvetica", 10)
    c.drawRightString(w - 0.75*inch, y, money(s["freight"]))
    y -= 0.3*inch
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(w - 2.0*inch, y, "TOTAL DUE")
    c.drawRightString(w - 0.75*inch, y, money(total))

def draw_boxed(c, s):
    w, h = letter
    c.setFont("Helvetica-Bold", 20)
    c.drawString(0.75*inch, h - 0.85*inch, "SALES INVOICE")
    c.rect(0.75*inch, h - 1.5*inch, w - 1.5*inch, 0.6*inch)
    c.setFont("Helvetica", 10)
    c.drawString(0.85*inch, h - 1.15*inch, f"Invoice: {s['invoice_number']}   Date: {s['date']}")

    c.rect(0.75*inch, h - 2.3*inch, (w - 1.5*inch)/2, 0.7*inch)
    c.rect(0.75*inch + (w - 1.5*inch)/2, h - 2.3*inch, (w - 1.5*inch)/2, 0.7*inch)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(0.85*inch, h - 1.75*inch, "Bill To")
    c.drawString(0.85*inch + (w - 1.5*inch)/2, h - 1.75*inch, "Ship To")
    c.setFont("Helvetica", 10)
    c.drawString(0.85*inch, h - 1.95*inch, s["customer"])
    c.drawString(0.85*inch + (w - 1.5*inch)/2, h - 1.95*inch, s["ship_to"])

    y = h - 3.0*inch
    c.setFont("Helvetica-Bold", 10)
    c.rect(0.75*inch, y, w-1.5*inch, 0.35*inch)
    c.drawString(0.85*inch, y+0.12*inch, "Description")
    c.drawRightString(w - 3.0*inch, y+0.12*inch, "Qty")
    c.drawRightString(w - 2.0*inch, y+0.12*inch, "Unit")
    c.drawRightString(w - 0.85*inch, y+0.12*inch, "Line Total")

    y -= 0.35*inch
    c.setFont("Helvetica", 10)
    for it in s["items"]:
        c.rect(0.75*inch, y, w-1.5*inch, 0.28*inch)
        c.drawString(0.85*inch, y+0.08*inch, it["desc"])
        c.drawRightString(w - 3.0*inch, y+0.08*inch, str(it["qty"]))
        c.drawRightString(w - 2.0*inch, y+0.08*inch, money(it["unit"]))
        c.drawRightString(w - 0.85*inch, y+0.08*inch, money(it["qty"]*it["unit"]))
        y -= 0.28*inch

    subtotal, tax, total = calc_totals(s)
    y -= 0.2*inch
    c.setFont("Helvetica", 10)
    c.drawString(0.75*inch, y, f"Salesperson: {s['salesperson']}   Ship Via: {s['ship_via']}   Terms: {s['terms']}")
    y -= 0.4*inch

    c.setFont("Helvetica-Bold", 10)
    c.drawRightString(w - 2.0*inch, y, "Subtotal")
    c.setFont("Helvetica", 10)
    c.drawRightString(w - 0.85*inch, y, money(subtotal))
    y -= 0.2*inch
    c.setFont("Helvetica-Bold", 10)
    c.drawRightString(w - 2.0*inch, y, f"Tax ({s['tax_rate']*100:.2f}%)")
    c.setFont("Helvetica", 10)
    c.drawRightString(w - 0.85*inch, y, money(tax))
    y -= 0.2*inch
    c.setFont("Helvetica-Bold", 10)
    c.drawRightString(w - 2.0*inch, y, "Freight")
    c.setFont("Helvetica", 10)
    c.drawRightString(w - 0.85*inch, y, money(s["freight"]))
    y -= 0.3*inch
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(w - 2.0*inch, y, "TOTAL DUE")
    c.drawRightString(w - 0.85*inch, y, money(total))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="../samples", help="Output folder for sample invoices")
    args = ap.parse_args()
    out = os.path.abspath(args.out)
    os.makedirs(out, exist_ok=True)

    for s in SAMPLES:
        path = os.path.join(out, f"invoice_{s['template']}_{s['invoice_number']}.pdf")
        c = canvas.Canvas(path, pagesize=letter)
        if s["template"] == "classic":
            draw_classic(c, s)
        elif s["template"] == "minimal":
            draw_minimal(c, s)
        elif s["template"] == "boxed":
            draw_boxed(c, s)
        else:
            draw_classic(c, s)
        c.showPage()
        c.save()
        print("Wrote", path)

if __name__ == "__main__":
    main()
