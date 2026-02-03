# Task: Migrate to Anthropic & Fix Docker

## Plan
- [/] **Explain JSON Schema**: Clarify to the user why the manual JSON dictionary was removed (replaced by Pydantic auto-generation).
- [/] **Backend: Anthropic Integration**
    - [/] Update `backend/requirements.txt` to include `anthropic`.
    - [/] Update `backend/app/config.py` to load `ANTHROPIC_API_KEY` and `LLM_PROVIDER`.
    - [/] Create `backend/app/llm/anthropic_provider.py` implementing `extract` using `anthropic` SDK and `ExtractedInvoice` schema.
    - [/] Update `backend/app/llm/factory.py` to support `anthropic` provider.
- [/] **Docker Fixes** (from previous request)
    - [x] Update `frontend/Dockerfile` to accept build args.
    - [x] Update `docker-compose.yml` to pass correct environment variables.
- [x] **Verification**
    - [x] Rebuild Docker images.
    - [x] Verify Backend starts with Anthropic config.
    - [x] Update `WALKTHROUGH.md` with new instructions.
