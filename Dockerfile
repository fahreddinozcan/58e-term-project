# FROM python:alpine

# WORKDIR /app

# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# COPY app/ app/

# EXPOSE 8080

# CMD ["python", "app/app.py"]


FROM python:3.8.5-slim

USER root

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Installing vulnerable packages for demonstration
RUN pip install \
    flask==1.0.0 \
    requests==2.20.0 \
    urllib3==1.24.1 \
    Pillow==7.1.0 \
    cryptography==3.2.0 \
    jinja2==2.10.1

COPY app/ app/

EXPOSE 8080

CMD ["python", "app/app.py"]
