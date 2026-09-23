# Runs the app as a Hugging Face Docker Space (or any container host).
#
# Hugging Face serves the container on port 7860 and runs it as user 1000,
# so the app's own folder has to be writable by that user: the SQLite file
# for bookmarks and the downloaded Islam360 index both live under data/.
#
#   ISLAM360_INDEX_TOKEN   — set as a Space secret; the index is fetched from
#                            the private repository named in code at start-up.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

RUN useradd -m -u 1000 app
WORKDIR /home/app/src

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=app:app . .
RUN chown -R app:app /home/app/src
USER app

EXPOSE 7860
HEALTHCHECK --interval=60s --timeout=10s --start-period=40s \
    CMD python -c "import urllib.request,sys;sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:7860/_stcore/health',timeout=5).status==200 else 1)"

CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]
