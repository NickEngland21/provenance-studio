FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=10000

RUN useradd --create-home --uid 1000 app
WORKDIR /home/app

COPY --chown=app:app pyproject.toml README.md LICENSE SECURITY.md ./
COPY --chown=app:app src ./src

RUN pip install --no-cache-dir ".[production]"

USER app
EXPOSE 10000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import os,urllib.request; urllib.request.urlopen('http://127.0.0.1:'+os.environ.get('PORT','10000')+'/health',timeout=3)"

CMD ["sh", "-c", "provenance-studio-api --workspace /tmp/provenance-studio --host 0.0.0.0 --port ${PORT:-10000}"]
