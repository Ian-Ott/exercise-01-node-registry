# TODO: Write a production-ready Dockerfile
#
# All of these are tested by the grader:
#
# [ ] Multi-stage build (2+ FROM instructions)
# [ ] Base image: python:3.14-slim (pinned version, no :latest)
# [ ] Copy requirements.txt and pip install BEFORE copying source code (layer caching)
# [ ] Run as a non-root USER
# [ ] EXPOSE 8080
# [ ] HEALTHCHECK instruction
# [ ] No hardcoded secrets (no ENV PASSWORD=..., no ENV SECRET_KEY=...)
# [ ] Final image under 200MB
#
# Start command: uvicorn src.app:app --host 0.0.0.0 --port 8080
#build
FROM python:3.14-slim AS builder
WORKDIR /app
COPY requirements.txt .

RUN pip install --no-cache-dir --only-binary=:all: --prefix=/install -r requirements.txt 

# Runtime 
FROM python:3.14-slim
WORKDIR /app


RUN useradd -m appuser 


COPY --from=builder --chown=appuser:appuser /install/lib/python3.14/site-packages /usr/local/lib/python3.14/site-packages
COPY --from=builder --chown=appuser:appuser /install/bin /usr/local/bin
COPY --chown=appuser:appuser src/ src/

USER appuser
ENV PATH="/usr/local/bin:$PATH"
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')"
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8080"]