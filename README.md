# Project

## Context

This is a Fastapi Restful API Service, which aim at provide a simple LLM Correctness evaluation PoC.

It should only contains Three API:

- Upload_file API: accept csv file object and upload to s3 or local minio with key be seted as file hash, then return a signed url.
- Evaluation API: accept model_name, concurrent (int) and signed_url, return a s3 signed url which will point to the result csv file, You can then waiting for the result file exists and download it.

We main desing a concurrent limit for each evaluation (which can be set in client request).

Also a global TokenBucket RateLimit to limit whole Request Rate, general this shuold be done on LLM Gateway or using external Redis service as lock.
But here we will using a memory thread safe lock to simply our system design.

## Usage

### run app

```
uv run uvicorn playground:app
```

### Run Unittest

```
uv run pytest tests
```

### using docker-compose
using docker-compose to run a local minio container to serve as s3 alternative, and the fastapi with swagger as UI to end user.

## Design

- All code shuold be stay into playground python pacakge, all test code should be into tests package.
- Use uv as package manager, use ruff as format and lint, use mypy as typing checking.

