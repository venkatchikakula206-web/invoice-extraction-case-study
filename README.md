# Invoice Extraction App

A production-ready document extraction application that uses AI to extract structured data from sales invoices.

## Features

- **Upload invoices** (PDF or images) via a modern drag-and-drop interface
- **AI-powered extraction** using Anthropic Claude or OpenAI GPT-4o
- **Real-time processing updates** via Server-Sent Events (SSE)
- **Review & edit** extracted data in a clean, professional UI
- **Save to database** (SalesOrderHeader/SalesOrderDetail schema)
- **View orders** with detailed breakdowns

## Tech Stack

- **Frontend**: Next.js 14, React 18, Tailwind CSS
- **Backend**: Flask, SQLAlchemy, Gunicorn (production server)
- **AI**: Anthropic Claude 3.5 Sonnet / OpenAI GPT-4o-mini
- **Database**: SQLite (dev) / PostgreSQL (prod-ready)

---

## Quick Start (Docker)

### Prerequisites
- Docker Desktop installed and running

### 1. Configure API Key

```bash
# Copy the example env file
cp backend/.env.example backend/.env

# Edit backend/.env and add your API key:
# For Anthropic (recommended):
#   ANTHROPIC_API_KEY=sk-ant-...
#   LLM_PROVIDER=anthropic
#
# For OpenAI:
#   OPENAI_API_KEY=sk-proj-...
#   LLM_PROVIDER=openai
```

### 2. Start the Application

```bash
# Use the startup script (kills existing processes automatically)
./start.sh

# Or manually:
docker compose up --build
```

### 3. Open in Browser

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Health Check**: http://localhost:8000/health

### Stop the Application

```bash
docker compose down
```

---

## Local Development

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Add your API key to .env

# Run development server
python -m app
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## Demo Flow

1. **Open** http://localhost:3000/upload
2. **Drag & drop** or browse to select an invoice (PDF or image)
3. **Click "Extract Data"** and watch real-time status updates
4. **Review** the extracted fields - edit if needed
5. **Click "Save to Database"** to persist the order
6. **View the order** in the Orders page

---

## Sample Invoices

The `samples/` folder contains test invoices:

- `invoice_classic_SO-DEMO-1001.pdf` - Classic invoice layout
- `invoice_minimal_SO-DEMO-1002.pdf` - Minimal invoice layout
- `invoice_boxed_SO-DEMO-1003.pdf` - Boxed/table layout
- `sample_invoice.png` - Image format invoice

---

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── llm/           # LLM providers (Anthropic, OpenAI)
│   │   ├── models.py      # Database models
│   │   ├── routes.py      # API endpoints
│   │   ├── services.py    # Business logic
│   │   └── schemas.py     # Pydantic models
│   ├── scripts/           # Utility scripts
│   └── Dockerfile
├── frontend/
│   ├── app/
│   │   ├── upload/        # Upload page
│   │   └── orders/        # Orders pages
│   └── Dockerfile
├── samples/               # Sample invoices
├── docker-compose.yml
├── start.sh              # Production startup script
└── README.md
```

---

## Supported File Types

- **PDF** - Rendered to image for AI processing
- **Images** - PNG, JPEG, GIF, WEBP, TIFF, BMP

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/documents` | Upload a document |
| GET | `/api/documents/:id` | Get document status |
| GET | `/api/documents/:id/events` | SSE stream for updates |
| PUT | `/api/documents/:id/save` | Save extracted data |
| GET | `/api/orders` | List all orders |
| GET | `/api/orders/:id` | Get order details |

---

## Scaling Considerations

See [SCALING.md](./SCALING.md) for production deployment strategies including:
- Queue-based async processing (Celery/Redis)
- Database migration to PostgreSQL
- Object storage for uploads (S3/GCS)
- Kubernetes deployment
- Observability and monitoring

---

## License

MIT
