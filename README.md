# LLM Correctness Evaluation PoC

A FastAPI-based RESTful API service for evaluating LLM model correctness.

## Overview

This project provides a simple PoC for LLM correctness evaluation with the following features:
- File upload to S3/MinIO with content-addressable storage (file hash as key)
- Concurrent evaluation with configurable parallelism
- Global rate limiting using token bucket algorithm
- Support for multiple LLM providers (OpenAI, Anthropic, Ollama)

## APIs

### 1. Upload File

**Endpoint:** `POST /upload`

Upload a CSV file to S3/MinIO. The file is stored with its hash as the key.

**Request:**
- `file`: CSV file object

**Response:**
```json
{
  "signed_url": "https://..."
}
```

### 2. Run Evaluation

**Endpoint:** `POST /evaluate`

Trigger an LLM evaluation job.

**Request:**
```json
{
  "model_name": "gpt-4o",
  "concurrent": 1,
  "signed_url": "https://..."
}
```

**Response:**
```json
{
  "result_url": "https://..."
}
```

### 3. Health Check

**Endpoint:** `GET /health`

Check if the service is running.

**Response:**
```json
{
  "status": "healthy"
}
```

## Supported Models

| Provider   | Model Name                    |
|------------|-------------------------------|
| OpenAI     | `gpt-4o`                      |
| OpenAI     | `gpt-4o-mini`                  |
| Anthropic  | `claude-3.5-sonnet-20241022`  |
| Anthropic  | `claude-3-haiku-20240307`     |
| Ollama     | `llama3.2:latest`              |
| Ollama     | `mistral`                     |

## CSV Formats

### Input CSV Format

The input CSV must contain the following columns:

| Column       | Description                      |
|--------------|----------------------------------|
| `id`         | Unique identifier for the row   |
| `query`      | The question or task to evaluate |
| `ground_truth`| The expected correct answer     |

Example:
```csv
id,query,ground_truth
1,What is 2+2?,4
2,What is the capital of France?,Paris
3,What color is the sky?,Blue
```

### Output CSV Format

The evaluation result CSV contains:

| Column        | Description                                      |
|---------------|-------------------------------------------------|
| `id`          | Same as input                                   |
| `query`       | Same as input                                   |
| `ground_truth`| Same as input                                   |
| `result`      | The model's response                            |
| `correct`     | Boolean indicating correctness                  |
| `score`       | Float between 0 and 1                           |
| `feedback`    | Explanation of the evaluation                  |

## Rate Limiting

- **Per-request concurrency**: Configurable via the `concurrent` parameter (1-10)
- **Global rate limit**: Token bucket algorithm with in-memory thread-safe implementation
  - `TOKEN_BUCKET_CAPACITY`: Maximum tokens in the bucket (default: 100)
  - `TOKEN_BUCKET_REFILL_RATE`: Tokens added per second (default: 10)

## Configuration

Environment variables for configuration:

| Variable                        | Description                          | Default                    |
|---------------------------------|--------------------------------------|----------------------------|
| `PLAYGROUND_APP_ENV`            | Application environment              | `development`              |
| `PLAYGROUND_LOG_LEVEL`          | Logging level                       | `INFO`                     |
| `PLAYGROUND_TOKEN_BUCKET_CAPACITY` | Token bucket capacity           | `100`                      |
| `PLAYGROUND_TOKEN_BUCKET_REFILL_RATE` | Token bucket refill rate     | `10`                       |
| `PLAYGROUND_S3_ENDPOINT_URL`    | S3/MinIO endpoint URL               | None                       |
| `PLAYGROUND_S3_ACCESS_KEY`      | S3 access key                       | None                       |
| `PLAYGROUND_S3_SECRET_KEY`      | S3 secret key                       | None                       |
| `PLAYGROUND_S3_REGION_NAME`     | S3 region name                     | `us-east-1`                |
| `PLAYGROUND_S3_BUCKET_NAME`     | S3 bucket name                      | `playground`               |
| `PLAYGROUND_SIGNED_URL_EXPIRY`  | Signed URL expiry in seconds       | `3600`                     |
| `PLAYGROUND_OPENAI_API_KEY`     | OpenAI API key                      | None                       |
| `PLAYGROUND_ANTHROPIC_API_KEY`  | Anthropic API key                   | None                       |

## Development

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager
- [Docker](https://www.docker.com/) and Docker Compose (for MinIO)

### Setup

```bash
uv sync
```

### Local Development with Ollama

If using Ollama models, pull the required model first:

```bash
# Pull llama3.2 model for local evaluation
ollama pull llama3.2:latest

# Or pull mistral
ollama pull mistral
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
├── playground/              # Main application code
│   ├── __init__.py         # Package exports
│   ├── app.py              # FastAPI application factory
│   ├── config.py           # Configuration management
│   ├── constants.py        # Constants and enumerations
│   ├── prompts.py          # LLM prompts
│   ├── schemas.py          # Data schemas
│   ├── tasks.py            # Background tasks
│   ├── utils.py            # Utility functions and rate limiter
│   ├── clients/
│   │   └── s3_client.py    # S3/MinIO client
│   ├── routers/
│   │   ├── __init__.py     # Router exports
│   │   ├── evaluation.py   # Evaluation endpoint
│   │   └── upload.py       # Upload endpoint
│   └── service/
│       ├── __init__.py
│       └── evaluation.py   # Evaluation business logic
├── tests/                  # Test suite
│   ├── conftest.py         # Pytest fixtures
│   ├── test_evaluation.py
│   └── test_upload.py
├── docs/                   # Documentation
├── docker-compose.yml      # Docker compose configuration
├── pyproject.toml          # Project configuration
└── README.md               # Project README
```

## Tech Stack

- **Framework**: FastAPI
- **LLM Providers**: OpenAI, Anthropic, Ollama
- **Storage**: MinIO (S3-compatible)
- **Package Manager**: uv
- **Linter**: ruff
- **Type Checker**: mypy
- **Testing**: pytest
