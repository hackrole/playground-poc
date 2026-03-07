# LLM Correctness Evaluation PoC

A FastAPI-based RESTful API service for evaluating LLM model correctness.

## Overview

This project provides a simple PoC for LLM correctness evaluation with the following features:
- File upload to S3/MinIO with content-addressable storage (file hash as key)
- Concurrent evaluation with configurable parallelism
- Global rate limiting using token bucket algorithm

## APIs

### 1. Upload File

**Endpoint:** `POST /upload`

Upload a CSV file to S3/MinIO. The file is stored with its hash as the key.

**Request:**
- `file`: CSV file object

**Response:**
- `signed_url`: Short-lived URL to access the uploaded file

### 2. Run Evaluation

**Endpoint:** `POST /evaluate`

Trigger an LLM evaluation job.

**Request:**
```json
{
  "model_name": "string",
  "concurrent": 1,
  "signed_url": "string"
}
```

**Response:**
- `result_url`: S3 signed URL pointing to the result CSV file

### 3. Get Result

**Endpoint:** `GET /result/{job_id}`

Poll for evaluation results.

**Response:**
- Job status and result file URL when complete

## Rate Limiting

- **Per-request concurrency**: Configurable via the `concurrent` parameter
- **Global rate limit**: Token bucket algorithm with in-memory thread-safe implementation

## Development

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager

### Setup

```bash
uv sync
```

### Run Application

```bash
uv run uvicorn playground:app --reload
```

### Run Tests

```bash
uv run pytest tests
```

### Linting & Type Checking

```bash
uv run ruff check .
uv run mypy .
```

## Docker

Start local MinIO container and FastAPI service:

```bash
docker-compose up -d
```

Access the API documentation at `http://localhost:8000/docs`.

## Project Structure

```
playground-poc/
├── playground/          # Main application code
│   ├── __init__.py
│   └── ...
├── tests/               # Test suite
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

## Tech Stack

- **Framework**: FastAPI
- **Storage**: MinIO (S3-compatible)
- **Package Manager**: uv
- **Linter**: ruff
- **Type Checker**: mypy
