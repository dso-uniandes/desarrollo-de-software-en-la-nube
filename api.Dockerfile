FROM python:3.13-slim

WORKDIR /app

# Layer 1: Install dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt


# Layer 2: Copy application code
COPY . /app







