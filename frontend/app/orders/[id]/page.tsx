"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

const BACKEND = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

type OrderHeader = {
  SalesOrderID: number;
  SalesOrderNumber: string | null;
  PurchaseOrderNumber: string | null;
  OrderDate: string | null;
  DueDate: string | null;
  ShipDate: string | null;
  SubTotal: number | null;
  TaxAmt: number | null;
  Freight: number | null;
  TotalDue: number | null;
};

type OrderDetail = {
  SalesOrderDetailID: number;
  OrderQty: number;
  UnitPrice: number;
  LineTotal: number;
};

type OrderData = {
  header: OrderHeader;
  details: OrderDetail[];
};

export default function OrderDetailPage() {
  const params = useParams();
  const id = params.id;
  const [data, setData] = useState<OrderData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${BACKEND}/api/orders/${id}`)
      .then((r) => r.json())
      .then((d) => {
        if (d.error) {
          setError(d.error);
        } else {
          setData(d);
        }
        setLoading(false);
      })
      .catch((e) => {
        setError(String(e));
        setLoading(false);
      });
  }, [id]);

  if (loading) {
    return (
      <div className="card p-12 animate-fade-in">
        <div className="flex flex-col items-center justify-center space-y-4">
          <div className="w-12 h-12 spinner" />
          <p className="text-sm text-gray-500">Loading order details...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6 animate-fade-in">
        <div className="p-4 bg-red-50 border border-red-200 rounded-xl">
          <div className="flex items-center space-x-3">
            <svg className="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p className="text-sm text-red-700">{error}</p>
          </div>
        </div>
        <a href="/orders" className="btn-secondary inline-flex">
          ← Back to Orders
        </a>
      </div>
    );
  }

  if (!data) return null;

  const { header, details } = data;

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <a 
            href="/orders" 
            className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </a>
          <div>
            <div className="flex items-center space-x-3">
              <h1 className="text-2xl font-bold text-gray-900">
                Order #{header.SalesOrderID}
              </h1>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                Saved
              </span>
            </div>
            <p className="mt-1 text-sm text-gray-500">
              {header.SalesOrderNumber ? `Invoice: ${header.SalesOrderNumber}` : "No invoice number"}
            </p>
          </div>
        </div>
      </div>

      {/* Order Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <SummaryCard
          label="Subtotal"
          value={formatCurrency(header.SubTotal)}
          icon={
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
            </svg>
          }
        />
        <SummaryCard
          label="Tax"
          value={formatCurrency(header.TaxAmt)}
          icon={
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
          }
        />
        <SummaryCard
          label="Freight"
          value={formatCurrency(header.Freight)}
          icon={
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
            </svg>
          }
        />
        <SummaryCard
          label="Total Due"
          value={formatCurrency(header.TotalDue)}
          highlight
          icon={
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          }
        />
      </div>

      {/* Order Details Card */}
      <div className="card">
        <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
          <h2 className="text-lg font-semibold text-gray-900">Order Information</h2>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <InfoItem label="Order Number" value={header.SalesOrderNumber} />
            <InfoItem label="PO Number" value={header.PurchaseOrderNumber} />
            <InfoItem label="Order Date" value={formatDate(header.OrderDate)} />
            <InfoItem label="Due Date" value={formatDate(header.DueDate)} />
            <InfoItem label="Ship Date" value={formatDate(header.ShipDate)} />
          </div>
        </div>
      </div>

      {/* Line Items Card */}
      <div className="card">
        <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
          <h2 className="text-lg font-semibold text-gray-900">Line Items</h2>
          <p className="text-sm text-gray-500">{details.length} item(s)</p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Detail ID
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Quantity
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Unit Price
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Line Total
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 bg-white">
              {details.map((detail) => (
                <tr key={detail.SalesOrderDetailID} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800">
                      {detail.SalesOrderDetailID}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-right">
                    {detail.OrderQty}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-right">
                    {formatCurrency(detail.UnitPrice)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 text-right">
                    {formatCurrency(detail.LineTotal)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Actions */}
      <div className="flex justify-between">
        <a href="/orders" className="btn-secondary">
          ← Back to Orders
        </a>
        <a href="/upload" className="btn-primary">
          Upload New Invoice
        </a>
      </div>
    </div>
  );
}

function SummaryCard({ 
  label, 
  value, 
  icon, 
  highlight = false 
}: { 
  label: string; 
  value: string; 
  icon: React.ReactNode;
  highlight?: boolean;
}) {
  return (
    <div className={`card p-4 ${highlight ? "ring-2 ring-blue-500 ring-offset-2" : ""}`}>
      <div className="flex items-center space-x-3">
        <div className={`p-2 rounded-lg ${highlight ? "bg-blue-100 text-blue-600" : "bg-gray-100 text-gray-500"}`}>
          {icon}
        </div>
        <div>
          <p className="text-xs font-medium text-gray-500 uppercase tracking-wider">{label}</p>
          <p className={`text-lg font-semibold ${highlight ? "text-blue-600" : "text-gray-900"}`}>{value}</p>
        </div>
      </div>
    </div>
  );
}

function InfoItem({ label, value }: { label: string; value: string | null }) {
  return (
    <div>
      <p className="text-xs font-medium text-gray-500 uppercase tracking-wider">{label}</p>
      <p className="mt-1 text-sm text-gray-900">{value || "—"}</p>
    </div>
  );
}

function formatDate(dateStr: string | null): string | null {
  if (!dateStr) return null;
  try {
    const date = new Date(dateStr);
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  } catch {
    return dateStr.slice(0, 10);
  }
}

function formatCurrency(value: number | null): string {
  if (value === null || value === undefined) return "—";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(value);
}
