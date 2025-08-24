# GPU-ready image (works on CPU too, but heavier). For CPU-only, you can switch to python:3.11-slim and install torch cpu.
FROM pytorch/pytorch:2.3.1-cuda12.1-cudnn8-runtime

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# System deps
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Copy and install Python deps
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY . .

# Expose FastAPI
EXPOSE 8000

# Launch
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
