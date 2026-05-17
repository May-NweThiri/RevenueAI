FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && grep -v "^pandasai==" requirements.txt > /tmp/req_base.txt \
    && pip install --no-cache-dir --no-build-isolation -r /tmp/req_base.txt \
    && pip install --no-cache-dir --no-build-isolation pandasai==2.3.2 --no-deps

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
