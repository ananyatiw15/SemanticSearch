FROM python:3.11-slim

RUN apt-get update && apt-get install -y gcc libssl-dev

WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --upgrade --no-cache-dir -r requirements.txt

COPY embedding.py /app/embedding.py
COPY sf-class2-root.crt /app/sf-class2-root.crt

CMD ["python", "/app/embedding.py"]
