# Document Extraction Project Walkthrough

## Overview
This project is a Document Extraction Application that processes sales invoices. It allows users to:
1.  **Upload** PDF or Image invoices.
2.  **Extract** structured data using **Anthropic Claude 3.5 Sonnet** (or OpenAI GPT-4o-mini).
3.  **Review & Edit** the extracted data in a React UI.
4.  **Save** the data to a local database (SQLite) modeled after `SalesOrderHeader` and `SalesOrderDetail`.

The application demonstrates a modern AI-integrated workflow with real-time feedback.

---

## 1. Prerequisites
Before you start, ensure you have:
*   **Node.js** (v18 or higher) and `npm`.
*   **Python** (3.10 or higher).
*   **API Key**: **REQUIRED** (Anthropic or OpenAI).

---

## 2. Project Structure
The project is split into two parts:

### Backend (`/backend`)
Built with **Flask**. It handles the API, database, and AI processing.
*   `app/routes.py`: Defines API endpoints (Upload, Status, Save).
*   `app/services.py`: Core logic for handling files and database transactions.
*   `app/llm/`: Contains the logic to call OpenAI.
*   `app/models.py`: Defines the Database schema (`Document`, `SalesOrderHeader`, etc.).

### Frontend (`/frontend`)
Built with **Next.js** (React).
*   `app/upload/page.tsx`: The main page where you upload files and see results.
*   `app/orders/page.tsx`: A list of saved orders.

---

## 3. How to Run (Local Mode)

We recommend running locally for development.

### Step A: Setup Backend
1.  Open your terminal and navigate to `backend`:
    ```bash
    cd backend
    ```
2.  Create a virtual environment and install dependencies:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    ```
3.  **Configure Environment**:
    The system needs your API keys. Edit the `.env` file:
    ```bash
    # Ensure this file exists (I created it for you)
    open .env
    ```
    **Add your API Key** (choose one):
    ```bash
    # For Anthropic (Recommended) - used by default
    ANTHROPIC_API_KEY=sk-ant-YOUR-KEY
    LLM_PROVIDER=anthropic

    # OR for OpenAI
    OPENAI_API_KEY=sk-proj-YOUR-KEY
    LLM_PROVIDER=openai
    ```
4.  Start the server:
    ```bash
    python -m app
    ```
    It will run on `http://localhost:8000`.

### Step B: Setup Frontend
1.  Open a **new terminal** tab (do not close the backend).
2.  Navigate to `frontend`:
    ```bash
    cd frontend
    ```
3.  Install dependencies:
    ```bash
    npm install
    ```
4.  Start the UI:
    ```bash
    npm run dev
    ```
    It will run on `http://localhost:3000`.

---

## 4. Verification (Smoke Test)

You can verify the backend is working without using the UI by using `curl`.

1.  **Check Health**:
    ```bash
    curl http://localhost:8000/health
    # Expected output: {"status": "ok"}
    ```

2.  **Upload a Sample Invoice**:
    Run this from the project root:
    ```bash
    curl -F "file=@samples/invoice_minimal_SO-DEMO-1002.pdf" http://localhost:8000/api/documents
    # Expected Output: {"document_id": 1}
    ```

3.  **Check Status**:
    (Replace `1` with the ID from the previous step)
    ```bash
    curl http://localhost:8000/api/documents/1
    ```
    *   If you set your `OPENAI_API_KEY`: You will see valid extracted JSON in the response.
    *   If you did **NOT** set the key: You will see `"status": "failed"` and `"error": "OPENAI_API_KEY is not set"`. This confirms the app is running correctly but blocked by missing credentials.

---

## 5. Docker (Production / Easy Mode)

I have fixed the Docker configuration so you can run the entire stack with one command.

1.  Ensure your `backend/.env` has your API Key.
2.  Run:
    ```bash
    docker compose up --build
    ```
3.  Open `http://localhost:3000`.

---

## 6. Live Demo Flow
1.  Go to `http://localhost:3000/upload` in your browser.
2.  Select `samples/invoice_template_image.png` or one of the PDFs.
3.  Click **Upload & Extract**.
4.  Watch the Real-time status update (Processing -> Calling LLM -> Extracted).
5.  Review the fields. Change "Quantity" or "Description" to see how it works.
6.  Click **Save to DB**.
7.  Click the "View" link to see the saved Order record.

---

## Technical Fixes Applied
I performed several fixes to make this production-ready:
1.  **Fixed Database Session Bug**: The app was crashing with `Instance not bound to Session` errors. I updated `db.py` to keep sessions valid so data can be read safely.
2.  **Updated OpenAI Integration**: The code was using an incorrect/outdated method to call OpenAI. I updated it to use the robust `client.beta.chat.completions.parse` method with Pydantic validation.
3.  **Verified Build**: Confirmed both backend and frontend compile and run.
