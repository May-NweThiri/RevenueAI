FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && grep -v "^pandasai==" requirements.txt > /tmp/req_base.txt \
    && pip install --no-cache-dir -r /tmp/req_base.txt \
    && pip install --no-cache-dir pandasai==2.3.2 --no-deps

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
