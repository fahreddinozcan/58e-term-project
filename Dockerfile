# Original secure image
# FROM python:3.9-slim

FROM python:alpine
RUN adduser --disabled-password --gecos '' appuser
USER appuser
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ app/
EXPOSE 8080
CMD ["python", "app/app.py"]