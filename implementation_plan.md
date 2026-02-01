# IMPLEMENATION PLAN - Secure PDF Web Viewer

## 1. Project Setup
- Create directory structure.
- Define `requirements.txt` (Flask, SQLAlchemy, Psycopg2, PyMuPDF, JWT, etc.).
- Create `Dockerfile` and `docker-compose.yml` for App + Postgres.

## 2. Backend - Core & Database
- Initialize Flask app with factory pattern.
- Configure SQLAlchemy with PostgreSQL.
- Create Models:
    - `User`: id, username, password_hash, role.
    - `Document`: id, title, description, content_html, created_at, updated_at.
- Initialize Migrations (or `db.create_all()` for simplicity in this MVP).

## 3. Authentication & Authorization
- Implement JWT handling.
- Create Decorators: `@admin_required`, `@login_required`.
- Routes: `/login`, `/register`, `/logout`.

## 4. PDF Processing (The Core Logic)
- Create `pdf_service.py`:
    - Accept file stream.
    - Validate MIME type and Size.
    - Use `fitz` (PyMuPDF) to iterate pages.
    - Extract text and images.
    - Convert images to base64 `data:image/...` strings.
    - Construct HTML string with styled divs for pages.
    - Sanitize HTML (bleach) to prevent XSS (though we are generating it, good to be safe if we allow bold/italics parsing later).

## 5. Routes & Views
- **Admin**:
    - `/admin/list`: Table view.
    - `/admin/upload`: Form for file upload.
    - `/admin/edit/<id>`: Update metadata or re-upload.
    - `/admin/delete/<id>`: Remove record.
- **User**:
    - `/user/list`: Card view of docs.
    - `/user/read/<id>`: The actual content viewer.

## 6. Frontend - "Beautiful & Premium"
- **CSS Architecture**:
    - Variables for colors (Dark mode/Glassmorphism).
    - Utility classes for layout (Flex/Grid).
    - Animations (Fade in, Slide up).
- **Templates**:
    - `base.html`: Nav, Flash messages, Theme toggle.
    - `auth.html`: Login/Register split or separate.
    - `dashboard.html`: Adaptive for Admin/User.
    - `read_view.html`: The protected content view.
        - **Security**: Disable selection, right-click context menu, print blocking via CSS `@media print { body { display: none; } }`.

## 7. Docker Integration
- Ensure DB persists in a volume.
- App connects using internal docker network.

## 8. Final Polish
- Seed an Admin user if none exists.
- Test PDF rendering.
