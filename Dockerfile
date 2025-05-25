# SECURE CONFIGURATION - This will PASS container scanning
FROM python:alpine
RUN adduser --disabled-password --gecos '' appuser
USER appuser
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ app/
EXPOSE 8080

# VULNERABLE CONFIGURATION - Uncomment to FAIL container scanning
# Use a vulnerable base image with root user and install vulnerable packages
# FROM python:3.7-slim
# WORKDIR /app
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt \
#     && pip install django==2.2.0 flask==0.12.2 requests==2.19.1 cryptography==2.1.4
# COPY app/ app/
# EXPOSE 8080
CMD ["python", "app/app.py"]