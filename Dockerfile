# Original secure image
# FROM python:3.9-slim

# Vulnerable image
FROM python:3.7-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Installing packages with known vulnerabilities to trigger container scanning
RUN pip install django==2.2.0 flask==0.12.2 requests==2.19.1 cryptography==2.1.4

COPY app/ app/

EXPOSE 8080

CMD ["python", "app/app.py"]