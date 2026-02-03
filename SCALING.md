# Scaling Strategies

To evolve this solution from a prototype to a production-scale system handling high volumes and diverse document types, I recommend the following strategies:

## 1. Asynchronous & Distributed Processing
**Current State**: Thread-based background processing in Flask.
**Scale Problem**: Heavy load will starve the web server (GIL contention, memory limits).
**Solution**:
*   **Queue System**: Introduce **Redis** or **RabbitMQ**.
*   **Worker Pool**: Use **Celery** or **Dramatiq** to offload processing to separate worker nodes.
*   **Benefit**: The API remains responsive. You can horizontally scale the number of workers independently of the web tier.

## 2. Database Evolution
**Current State**: SQLite (single file).
**Scale Problem**: Concurrency locks, no replication, limited size.
**Solution**:
*   **Migrate to PostgreSQL**. It handles concurrent writes robustly and supports JSONB for storing parsed extraction results flexibly.
*   **Read Replicas**: For high read volume (Dashboard/Reporting), verify via read replicas.

## 3. Storage
**Current State**: Local file system.
**Scale Problem**: Cannot scale across multiple web servers (files are local).
**Solution**:
*   **Object Storage**: Use **AWS S3**, **Google Cloud Storage**, or **Azure Blob Storage**.
*   The API uploads to S3 and passes the S3 Key to the worker. The worker reads safely from S3.

## 4. LLM Optimization & Cost
**Current State**: OpenAI GPT-4o-mini (Vision).
**Scale Problem**: High cost per page, latency varies.
**Solution**:
*   **Model Routing**: Use cheaper/faster models (e.g., local layoutLM, OCR-only) for simple documents, and Route to GPT-4o only for complex ones.
*   **Caching**: Hash the document (SHA256). If the same doc is uploaded twice, return the cached extraction.
*   **Batching**: If real-time isn't required, process in nightly batches to avoid rate limits.

## 5. Deployment & Infrastructure
**Current State**: Docker Compose (Single node).
**Scale Problem**: Single point of failure.
**Solution**:
*   **Kubernetes (K8s)**: Orchestrate containers.
*   **Auto-scaling**: Scale backend pods on CPU, and Worker pods on Queue Length (KEDA).

## 6. Observability
*   **Tracing**: Implement OpenTelemetry to trace requests from API -> Queue -> Worker -> LLM -> DB.
*   **Metrics**: Monitor "Extraction Success Rate", "Average Processing Time", and "LLM Token Usage".
