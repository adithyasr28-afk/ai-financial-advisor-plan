FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt .
COPY backend/pyproject.toml .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./backend/
COPY fixtures/ ./fixtures/
COPY models/ ./models/
RUN pip install -e ./backend
ENV PYTHONPATH=/app
COPY backend/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

