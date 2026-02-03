# Anthropic Migration & Docker Fixes Implementation Plan

## Goal
1.  Verify usage of Anthropic (Claude 3.5 Sonnet) instead of OpenAI.
2.  Ensure production-ready Docker configuration.

## Explanation: JSON Schema
The user asked about the removed `JSON_SCHEMA`.
*   **Reason**: I replaced the manual dictionary with a Pydantic model (`schemas.py`).
*   **Mechanism**: The new OpenAI `parse` method **automatically generates** the JSON schema from the Pydantic class.
*   **Benefit**: This prevents bugs where the manual dictionary and the validation logic get out of sync.
*   **For Anthropic**: We will generate the schema programmatically using `ExtractedInvoice.model_json_schema()` and pass it to Anthropic's Tool Use API.

## Changes

### 1. Backend Dependencies
*   Add `anthropic` to `backend/requirements.txt`.

### 2. Configuration (`backend/app/config.py`)
*   Add `ANTHROPIC_API_KEY`.
*   Update `LLM_PROVIDER` default or logic.

### 3. Anthropic Provider (`backend/app/llm/anthropic_provider.py`) [NEW]
*   Implement `AnthropicInvoiceExtractor`.
*   Use `client.messages.create` with `tools`.
*   Tool definition will be auto-generated from `ExtractedInvoice`.

### 4. Docker Fixes
*   **Frontend**: Update `Dockerfile` to accept `ARG NEXT_PUBLIC_BACKEND_URL`.
*   **Compose**: Pass `http://localhost:8000` to frontend build args.

## Verification
1.  Install dependencies.
2.  Run backend with `LLM_PROVIDER=anthropic`.
3.  Trigger upload.
4.  Verify extraction works.
