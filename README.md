# Arcane Docs - Secure PDF Manager

A secure, high-aesthetic web application for managing and viewing PDF documents without allowing downloads.

## Features
- **Admin Panel**: Upload, Edit, Delete PDFs.
- **User Panel**: Read-only access to documents.
- **Secure Viewing**: 
  - content extracted to HTML (no PDF file access).
  - Right-click disabled.
  - Printing disabled.
  - Copy-paste disabled.
- **Tech Stack**: Flask, PostgreSQL, PyMuPDF, Docker.

## Setup & Run

### Prerequisites
- Docker & Docker Compose

### Steps
1. **Build and Run**:
   ```bash
   docker-compose up --build
   ```
   
2. **Access the App**:
   Open [http://localhost:5000](http://localhost:5000)

3. **Create Accounts**:
   - Go to **Register**.
   - Create a **User** account (just fill username/password).
   - Create an **Admin** account by entering the secret code: `admin123`.

## Architecture
- **Backend**: Flask app serving HTML templates.
- **Database**: PostgreSQL storing User `role` and Document `content_html`.
- **PDF Processing**: `fitz` (PyMuPDF) extracts text blocks and images (converted to Base64) to create a seamless HTML representation.

## Troubleshooting
- If DB connection fails initially, wait a few seconds for Postgres to initialize; the container is set to restart.
