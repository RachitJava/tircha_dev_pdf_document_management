FROM python:3.10-slim

# Install system dependencies required for PyMuPDF and other binary packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose the port the app runs on
EXPOSE 8080

# Environment variables
ENV PORT=8080
ENV FLASK_APP=run.py

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:create_app()"]
