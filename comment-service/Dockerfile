FROM python:3.11-slim

WORKDIR /app

# Kopiraj requirements pa instaliraj
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install fastapi uvicorn motor pymongo python-jose[cryptography]

# Kopiraj ostatak aplikacije
COPY . /app

# Startaj Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
