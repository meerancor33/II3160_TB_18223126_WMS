FROM python:3.11-slim

# Ganti working directory
WORKDIR /app

# Copy dependencies & install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy seluruh project
COPY . .

# Expose port FastAPI
EXPOSE 8000

# Command untuk menjalankan FastAPI
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
