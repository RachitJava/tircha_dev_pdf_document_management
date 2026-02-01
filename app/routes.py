import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, make_response
from app import bcrypt, jwt
from app.json_db import db
from app.pdf_processor import process_pdf
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity, 
    set_access_cookies, unset_jwt_cookies, verify_jwt_in_request, get_jwt
)
import bleach
from functools import wraps

main = Blueprint('main', __name__)

# --- Custom Decorators ---
def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("role") not in ["ADMIN", "SUPERUSER"]:
                flash('Access denied.', 'danger')
                return redirect(url_for('main.user_list'))
            return fn(*args, **kwargs)
        return decorator
    return wrapper

# --- Context Processor for Templates ---
@main.context_processor
def inject_user():
    try:
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
        theme_color = db.get_setting("theme_color", "#3495eb")
        pdf_header_color = db.get_setting("pdf_header_color", "#1e293b")
        if identity:
            user = db.get_user_by_username(identity)
            return {'current_user': user, 'theme_color': theme_color, 'pdf_header_color': pdf_header_color}
        return {'current_user': None, 'theme_color': theme_color, 'pdf_header_color': pdf_header_color}
    except:
        return {'current_user': None, 'theme_color': "#3495eb", 'pdf_header_color': "#1e293b"}

# --- Routes ---

@main.route('/')
def index():
    return redirect(url_for('main.login'))

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # All new registrations are 'USER' by default. Admin is pre-seeded.
        role = 'USER'
            
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Check if exists
        if db.get_user_by_username(username):
            flash('Username already exists.', 'danger')
        else:
            db.add_user(username=username, password_hash=hashed_pw, role=role)
            flash('Account created! Please login.', 'success')
            return redirect(url_for('main.login'))
            
    return render_template('auth.html', mode='register')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = db.get_user_by_username(username)
        
        if user and bcrypt.check_password_hash(user.password_hash, password):
            # Create JWT
            access_token = create_access_token(identity=user.username, additional_claims={"role": user.role})
            
            if user.role in ['ADMIN', 'SUPERUSER']:
                next_page = url_for('main.admin_list')
            else:
                next_page = url_for('main.user_list')
                
            resp = make_response(redirect(next_page))
            set_access_cookies(resp, access_token)
            return resp
        else:
            flash('Login Unsuccessful. Check username and password', 'danger')
            
    return render_template('auth.html', mode='login')

@main.route('/logout')
def logout():
    resp = make_response(redirect(url_for('main.login')))
    unset_jwt_cookies(resp)
    flash('You have been logged out.', 'info')
    return resp

# --- Admin Routes ---

@main.route('/admin/list')
@admin_required()
def admin_list():
    query = request.args.get('q')
    docs = db.get_documents(query=query)
    return render_template('admin_dashboard.html', docs=docs)

@main.route('/admin/upload', methods=['GET', 'POST'])
@admin_required()
def upload():
    if request.method == 'POST':
        file = request.files.get('file')
        title = bleach.clean(request.form.get('title', ''))
        description = bleach.clean(request.form.get('description', ''))
        
        if not title:
            flash('Title is required', 'warning')
            return redirect(request.url)
            
        if not file or file.filename == '':
            flash('No selected file', 'warning')
            return redirect(request.url)
            
        # Security: Check file size and type on server side
        # 16MB limit
        MAX_CONTENT_LENGTH = 16 * 1024 * 1024
        file.seek(0, os.SEEK_END)
        file_length = file.tell()
        file.seek(0)
        
        if file_length > MAX_CONTENT_LENGTH:
            flash('File too large. Maximum size is 16MB.', 'danger')
            return redirect(request.url)

        if file and (file.filename.lower().endswith('.pdf') or file.mimetype == 'application/pdf'):
            try:
                # Read content once
                file_content = file.read()
                content_html, pdf_base64 = process_pdf(file_content)
                db.add_document(title=title, description=description, content_html=content_html, pdf_base64=pdf_base64)
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return {"status": "success"}, 200
                
                flash('Document uploaded and processed successfully!', 'success')
                return redirect(url_for('main.admin_list'))
            except Exception as e:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return {"error": str(e)}, 500
                flash(f'Error processing PDF: {str(e)}', 'danger')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return {"error": "Invalid file type. Only PDF allowed."}, 400
            flash('Invalid file type. Only PDF allowed.', 'danger')
            
    return render_template('upload.html')

@main.route('/admin/delete/<int:id>', methods=['POST'])
@admin_required()
def delete_document(id):
    db.delete_document(id)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return {"status": "success"}, 200
    flash('Document deleted.', 'success')
    return redirect(url_for('main.admin_list'))

@main.route('/admin/edit/<int:id>', methods=['GET', 'POST'])
@admin_required()
def edit_document(id):
    doc = db.get_document_by_id(id)
    if not doc:
        flash('Document not found.', 'danger')
        return redirect(url_for('main.admin_list'))

    if request.method == 'POST':
        title = bleach.clean(request.form.get('title', ''))
        description = bleach.clean(request.form.get('description', ''))
        file = request.files.get('file')
        
        if not title:
            flash('Title is required', 'warning')
            return render_template('upload.html', doc=doc)
            
        updates = {
            "title": title,
            "description": description
        }

        if file and file.filename != '':
            # Security: Check file size and type
            MAX_CONTENT_LENGTH = 16 * 1024 * 1024
            file.seek(0, os.SEEK_END)
            file_length = file.tell()
            file.seek(0)
            
            if file_length > MAX_CONTENT_LENGTH:
                flash('File too large. Maximum size is 16MB.', 'danger')
                return render_template('upload.html', doc=doc)

            if file.filename.lower().endswith('.pdf') or file.mimetype == 'application/pdf':
                try:
                    # Process new file
                    file_content = file.read()
                    content_html, pdf_base64 = process_pdf(file_content)
                    updates['content_html'] = content_html
                    updates['pdf_base64'] = pdf_base64
                except Exception as e:
                    flash(f'Error processing new PDF: {str(e)}', 'danger')
                    return render_template('upload.html', doc=doc)
            else:
                flash('Invalid file type. Only PDF allowed.', 'danger')
                return render_template('upload.html', doc=doc)
        
        db.update_document(id, **updates)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return {"status": "success"}, 200
            
        flash('Document updated.', 'success')
        return redirect(url_for('main.admin_list'))
            
    return render_template('upload.html', doc=doc)

@main.route('/admin/users')
@admin_required()
def admin_users():
    users = [u for u in db.get_users() if u.role != 'SUPERUSER']
    return render_template('admin_users.html', users=users)

@main.route('/admin/update_theme', methods=['POST'])
@admin_required()
def update_theme():
    verify_jwt_in_request()
    claims = get_jwt()
    if claims.get("role") not in ["ADMIN", "SUPERUSER"]:
        return {"error": "Unauthorized"}, 403
    
    color = request.json.get('color')
    if color:
        db.set_setting("theme_color", color)
        return {"status": "success"}, 200
    return {"error": "Invalid color"}, 400

@main.route('/admin/update_pdf_header_theme', methods=['POST'])
@admin_required()
def update_pdf_header_theme():
    verify_jwt_in_request()
    claims = get_jwt()
    if claims.get("role") not in ["ADMIN", "SUPERUSER"]:
        return {"error": "Unauthorized"}, 403
    
    color = request.json.get('color')
    if color:
        db.set_setting("pdf_header_color", color)
        return {"status": "success"}, 200
    return {"error": "Invalid color"}, 400

@main.route('/admin/users/add', methods=['POST'])
@admin_required()
def add_user_route():
    username = request.form.get('username')
    password = request.form.get('password')
    role = request.form.get('role', 'USER')
    
    if db.get_user_by_username(username):
        flash('Username already exists.', 'danger')
    else:
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        db.add_user(username, hashed_pw, role)
        flash('User added successfully.', 'success')
    
    return redirect(url_for('main.admin_users'))

@main.route('/admin/users/delete/<int:id>', methods=['POST'])
@admin_required()
def delete_user_route(id):
    # Prevent deleting self
    current_identity = get_jwt_identity()
    user_to_delete = db.get_user_by_id(id)
    
    if user_to_delete and user_to_delete.username == current_identity:
        flash('You cannot delete yourself.', 'danger')
        return redirect(url_for('main.admin_users'))

    db.delete_user(id)
    flash('User deleted.', 'success')
    return redirect(url_for('main.admin_users'))

# --- User Routes ---

@main.route('/user/list')
@jwt_required() # Any logged in user
def user_list():
    page = request.args.get('page', 1, type=int)
    query = request.args.get('q')
    docs = db.get_documents(query=query, page=page, per_page=10)
    return render_template('user_dashboard.html', docs=docs)

@main.route('/user/read/<int:id>')
@jwt_required()
def read_document(id):
    doc = db.get_document_by_id(id)
    if not doc:
        abort(404)
    return render_template('read_view.html', doc=doc)
