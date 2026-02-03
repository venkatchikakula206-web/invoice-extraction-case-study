"use client";

import { useEffect, useState, useCallback } from "react";

type LineItem = { 
  item_number?: string | null; 
  description: string; 
  qty: number; 
  unit_price: number; 
  line_total: number; 
};

type Extracted = {
  invoice_number?: string | null;
  purchase_order_number?: string | null;
  order_date?: string | null;
  due_date?: string | null;
  ship_date?: string | null;
  salesperson?: string | null;
  ship_via?: string | null;
  terms?: string | null;
  subtotal?: number | null;
  tax_rate?: number | null;
  tax_amt?: number | null;
  freight?: number | null;
  total_due?: number | null;
  currency?: string | null;
  bill_to_name?: string | null;
  ship_to_name?: string | null;
  items: LineItem[];
  confidence?: number | null;
  warnings: string[];
};

const BACKEND = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

const statusConfig: Record<string, { color: string; bg: string; icon: string; text: string }> = {
  idle: { color: "text-gray-600", bg: "bg-gray-100", icon: "○", text: "Ready to upload" },
  uploading: { color: "text-blue-600", bg: "bg-blue-50", icon: "↑", text: "Uploading..." },
  processing: { color: "text-amber-600", bg: "bg-amber-50", icon: "◐", text: "Processing document..." },
  calling_llm: { color: "text-purple-600", bg: "bg-purple-50", icon: "◑", text: "Analyzing with AI..." },
  extracted: { color: "text-green-600", bg: "bg-green-50", icon: "✓", text: "Extraction complete" },
  saved: { color: "text-green-600", bg: "bg-green-50", icon: "✓", text: "Saved to database" },
  failed: { color: "text-red-600", bg: "bg-red-50", icon: "✕", text: "Processing failed" },
};

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [docId, setDocId] = useState<number | null>(null);
  const [status, setStatus] = useState<string>("idle");
  const [error, setError] = useState<string | null>(null);
  const [extracted, setExtracted] = useState<Extracted | null>(null);
  const [savedOrderId, setSavedOrderId] = useState<number | null>(null);
  const [saving, setSaving] = useState(false);

  const canSave = extracted && docId && !saving && 
    status !== "failed" && status !== "processing" && status !== "calling_llm";

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  }, []);

  async function upload() {
    if (!file) return;
    setError(null);
    setExtracted(null);
    setSavedOrderId(null);
    setStatus("uploading");

    const form = new FormData();
    form.append("file", file);

    try {
      const resp = await fetch(`${BACKEND}/api/documents`, { method: "POST", body: form });
      const data = await resp.json();
      
      if (!resp.ok) {
        setError(data.error || `Upload failed: ${resp.status}`);
        setStatus("failed");
        return;
      }
      
      setDocId(data.document_id);
      setStatus("processing");
    } catch (err) {
      setError("Failed to connect to server");
      setStatus("failed");
    }
  }

  // SSE listener
  useEffect(() => {
    if (!docId) return;
    const es = new EventSource(`${BACKEND}/api/documents/${docId}/events`);
    
    es.addEventListener("status", (e: MessageEvent) => {
      try {
        const msg = JSON.parse(e.data);
        if (msg.status) setStatus(msg.status);
      } catch {}
    });
    
    es.addEventListener("extracted", (e: MessageEvent) => {
      try {
        const msg = JSON.parse(e.data);
        if (msg.data) setExtracted(msg.data);
      } catch {}
    });
    
    es.addEventListener("error", (e: MessageEvent) => {
      try {
        const msg = JSON.parse(e.data);
        setError(msg.message || "Processing failed");
      } catch {}
      setStatus("failed");
    });
    
    return () => es.close();
  }, [docId]);

  function updateField<K extends keyof Extracted>(k: K, v: Extracted[K]) {
    if (!extracted) return;
    setExtracted({ ...extracted, [k]: v });
  }

  function updateItem(idx: number, k: keyof LineItem, v: string | number) {
    if (!extracted) return;
    const items = extracted.items.slice();
    items[idx] = { ...items[idx], [k]: v };
    
    const qty = Number(items[idx].qty || 0);
    const unit = Number(items[idx].unit_price || 0);
    items[idx].line_total = Number.isFinite(qty * unit) ? qty * unit : items[idx].line_total;
    
    const subtotal = items.reduce((s, it) => s + Number(it.line_total || 0), 0);
    const taxRate = Number(extracted.tax_rate || 0);
    const taxAmt = extracted.tax_amt ?? (subtotal * taxRate);
    const freight = Number(extracted.freight || 0);
    const totalDue = subtotal + Number(taxAmt || 0) + freight;
    
    setExtracted({ ...extracted, items, subtotal, tax_amt: taxAmt, total_due: totalDue });
  }

  async function save() {
    if (!docId || !extracted) return;
    setError(null);
    setSaving(true);
    
    try {
      const resp = await fetch(`${BACKEND}/api/documents/${docId}/save`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(extracted),
      });
      const data = await resp.json();
      
      if (!resp.ok) {
        setError(data.error || "Save failed");
        return;
      }
      
      setSavedOrderId(data.sales_order_id);
      setStatus("saved");
    } catch (err) {
      setError("Failed to save");
    } finally {
      setSaving(false);
    }
  }

  function reset() {
    setFile(null);
    setDocId(null);
    setStatus("idle");
    setError(null);
    setExtracted(null);
    setSavedOrderId(null);
  }

  const statusInfo = statusConfig[status] || statusConfig.idle;
  const isProcessing = status === "uploading" || status === "processing" || status === "calling_llm";

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Upload Invoice</h1>
          <p className="mt-1 text-sm text-gray-500">
            Upload a PDF or image to extract invoice data automatically
          </p>
        </div>
        {(extracted || error) && (
          <button onClick={reset} className="btn-secondary">
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Start Over
          </button>
        )}
      </div>

      {/* Upload Area */}
      <div className="card">
        <div className="p-6">
          <div
            className={`relative border-2 border-dashed rounded-xl p-8 text-center transition-all duration-300 ${
              dragActive 
                ? "border-blue-500 bg-blue-50" 
                : file 
                  ? "border-green-300 bg-green-50" 
                  : "border-gray-300 hover:border-gray-400 bg-gray-50"
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <input
              type="file"
              accept="application/pdf,image/png,image/jpeg,image/jpg,image/gif,image/webp,image/tiff,image/bmp"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              disabled={isProcessing}
            />
            
            <div className="space-y-4">
              {file ? (
                <div className="animate-fade-in">
                  <div className="w-16 h-16 mx-auto bg-green-100 rounded-full flex items-center justify-center">
                    <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <p className="mt-4 text-lg font-medium text-gray-900">{file.name}</p>
                  <p className="text-sm text-gray-500">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                </div>
              ) : (
                <>
                  <div className="w-16 h-16 mx-auto bg-gray-100 rounded-full flex items-center justify-center">
                    <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                    </svg>
                  </div>
                  <div>
                    <p className="text-lg font-medium text-gray-900">
                      Drop your invoice here, or <span className="text-blue-600">browse</span>
                    </p>
                    <p className="mt-1 text-sm text-gray-500">
                      Supports PDF, PNG, JPEG, GIF, WEBP, TIFF, BMP
                    </p>
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Status & Action */}
          <div className="mt-6 flex items-center justify-between">
            <div className={`flex items-center space-x-3 px-4 py-2 rounded-lg ${statusInfo.bg}`}>
              {isProcessing ? (
                <div className="w-4 h-4 spinner" />
              ) : (
                <span className={`text-lg ${statusInfo.color}`}>{statusInfo.icon}</span>
              )}
              <span className={`text-sm font-medium ${statusInfo.color}`}>{statusInfo.text}</span>
              {docId && <span className="text-xs text-gray-400">ID: {docId}</span>}
            </div>
            
            <button
              onClick={upload}
              disabled={!file || isProcessing}
              className="btn-primary"
            >
              {isProcessing ? (
                <>
                  <div className="w-4 h-4 spinner mr-2" />
                  Processing...
                </>
              ) : (
                <>
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  Extract Data
                </>
              )}
            </button>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg animate-slide-up">
              <div className="flex items-start space-x-3">
                <svg className="w-5 h-5 text-red-500 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div>
                  <p className="text-sm font-medium text-red-800">Error</p>
                  <p className="text-sm text-red-700">{error}</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Extracted Data */}
      {extracted && (
        <div className="space-y-6 animate-slide-up">
          {/* Success Banner */}
          {savedOrderId && (
            <div className="p-4 bg-green-50 border border-green-200 rounded-xl flex items-center justify-between animate-slide-up">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                  <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <div>
                  <p className="font-medium text-green-800">Saved Successfully!</p>
                  <p className="text-sm text-green-700">Order ID: {savedOrderId}</p>
                </div>
              </div>
              <a 
                href={`/orders/${savedOrderId}`}
                className="btn-primary bg-green-600 hover:bg-green-700"
              >
                View Order →
              </a>
            </div>
          )}

          {/* Invoice Details Card */}
          <div className="card">
            <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
              <h2 className="text-lg font-semibold text-gray-900">Extracted Invoice Data</h2>
              <p className="text-sm text-gray-500">Review and edit the extracted information</p>
            </div>
            
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <InputField label="Invoice #" value={extracted.invoice_number || ""} onChange={(v) => updateField("invoice_number", v)} />
                <InputField label="PO #" value={extracted.purchase_order_number || ""} onChange={(v) => updateField("purchase_order_number", v)} />
                <InputField label="Order Date" value={extracted.order_date || ""} onChange={(v) => updateField("order_date", v)} />
                <InputField label="Due Date" value={extracted.due_date || ""} onChange={(v) => updateField("due_date", v)} />
                <InputField label="Ship Date" value={extracted.ship_date || ""} onChange={(v) => updateField("ship_date", v)} />
                <InputField label="Terms" value={extracted.terms || ""} onChange={(v) => updateField("terms", v)} />
                <InputField label="Ship Via" value={extracted.ship_via || ""} onChange={(v) => updateField("ship_via", v)} />
                <InputField label="Salesperson" value={extracted.salesperson || ""} onChange={(v) => updateField("salesperson", v)} />
                <InputField label="Currency" value={extracted.currency || "USD"} onChange={(v) => updateField("currency", v)} />
                <InputField label="Bill To" value={extracted.bill_to_name || ""} onChange={(v) => updateField("bill_to_name", v)} />
                <InputField label="Ship To" value={extracted.ship_to_name || ""} onChange={(v) => updateField("ship_to_name", v)} />
                <InputField label="Tax Rate (%)" value={(extracted.tax_rate ?? "").toString()} onChange={(v) => updateField("tax_rate", parseFloat(v) || 0)} type="number" />
              </div>
            </div>
          </div>

          {/* Line Items Card */}
          <div className="card">
            <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
              <h2 className="text-lg font-semibold text-gray-900">Line Items</h2>
              <p className="text-sm text-gray-500">{extracted.items.length} item(s) found</p>
            </div>
            
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Qty</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Unit Price</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Line Total</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {extracted.items.map((item, idx) => (
                    <tr key={idx} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4">
                        <input
                          value={item.description}
                          onChange={(e) => updateItem(idx, "description", e.target.value)}
                          className="w-full bg-transparent border-0 focus:ring-0 text-sm text-gray-900"
                        />
                      </td>
                      <td className="px-6 py-4">
                        <input
                          type="number"
                          value={item.qty}
                          onChange={(e) => updateItem(idx, "qty", parseFloat(e.target.value) || 0)}
                          className="w-20 text-right bg-transparent border-0 focus:ring-0 text-sm text-gray-900"
                        />
                      </td>
                      <td className="px-6 py-4">
                        <input
                          type="number"
                          step="0.01"
                          value={item.unit_price}
                          onChange={(e) => updateItem(idx, "unit_price", parseFloat(e.target.value) || 0)}
                          className="w-24 text-right bg-transparent border-0 focus:ring-0 text-sm text-gray-900"
                        />
                      </td>
                      <td className="px-6 py-4 text-right text-sm font-medium text-gray-900">
                        ${item.line_total.toFixed(2)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Totals */}
            <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
              <div className="flex justify-end">
                <div className="w-64 space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Subtotal</span>
                    <span className="font-medium">${(extracted.subtotal || 0).toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Tax</span>
                    <span className="font-medium">${(extracted.tax_amt || 0).toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Freight</span>
                    <span className="font-medium">${(extracted.freight || 0).toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between text-base pt-2 border-t border-gray-300">
                    <span className="font-semibold text-gray-900">Total Due</span>
                    <span className="font-bold text-gray-900">${(extracted.total_due || 0).toFixed(2)}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Warnings */}
          {extracted.warnings?.length > 0 && (
            <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl">
              <div className="flex items-start space-x-3">
                <svg className="w-5 h-5 text-amber-500 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <div>
                  <p className="text-sm font-medium text-amber-800">Warnings</p>
                  <ul className="mt-1 text-sm text-amber-700 list-disc list-inside">
                    {extracted.warnings.map((w, i) => <li key={i}>{w}</li>)}
                  </ul>
                </div>
              </div>
            </div>
          )}

          {/* Save Button */}
          {!savedOrderId && (
            <div className="flex justify-end">
              <button
                onClick={save}
                disabled={!canSave}
                className="btn-primary px-8 py-3 text-base"
              >
                {saving ? (
                  <>
                    <div className="w-5 h-5 spinner mr-2" />
                    Saving...
                  </>
                ) : (
                  <>
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
                    </svg>
                    Save to Database
                  </>
                )}
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function InputField({ 
  label, 
  value, 
  onChange, 
  type = "text" 
}: { 
  label: string; 
  value: string; 
  onChange: (v: string) => void;
  type?: string;
}) {
  return (
    <div>
      <label className="block text-xs font-medium text-gray-500 uppercase tracking-wider mb-1">
        {label}
      </label>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 text-sm"
      />
    </div>
  );
}
