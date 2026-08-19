FROM cgr.dev/chainguard/python:latest-dev@sha256:91418fa26adfd56d959d80e5da0d7470b5653e4f00ba698ef5d8212e58e3f7f8 AS builder

ENV PIP_NO_CACHE_DIR=1

USER root
WORKDIR /build

COPY requirements.txt .
RUN python -m venv /venv \
    && /venv/bin/pip install --upgrade pip \
    && /venv/bin/pip install -r requirements.txt

FROM cgr.dev/chainguard/python:latest@sha256:6d71f8dbd199350964ce8b10d50fb9d4d8e2bd50316f3a1821dbdc6eef5252fb

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/venv/bin:$PATH"

WORKDIR /service

COPY --from=builder /venv /venv
COPY --chown=65532:65532 app ./app

USER 65532:65532
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD ["/venv/bin/python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health', timeout=2)"]

ENTRYPOINT ["/venv/bin/python", "-m", "uvicorn"]
CMD ["app.main:app", "--host", "0.0.0.0", "--port", "8080", "--no-server-header"]
