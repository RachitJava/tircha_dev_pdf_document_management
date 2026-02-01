import os
from datetime import datetime
from app import db as sqlalchemy_db
from app.models import User, Document, Setting
from sqlalchemy import or_

class DatabaseBridge:
    def __init__(self):
        pass

    def get_user_by_username(self, username):
        return User.query.filter_by(username=username).first()
    
    def get_user_by_id(self, uid):
        return User.query.get(uid)

    def add_user(self, username, password_hash, role='USER'):
        user = User(username=username, password_hash=password_hash, role=role)
        sqlalchemy_db.session.add(user)
        sqlalchemy_db.session.commit()
        return user

    def get_users(self):
        return User.query.all()

    def delete_user(self, user_id):
        user = User.query.get(user_id)
        if user:
            sqlalchemy_db.session.delete(user)
            sqlalchemy_db.session.commit()

    def get_documents(self, query=None, page=1, per_page=10):
        docs_query = Document.query
        if query:
            query_filter = f"%{query}%"
            docs_query = docs_query.filter(or_(
                Document.title.ilike(query_filter),
                Document.description.ilike(query_filter)
            ))
        
        docs_query = docs_query.order_by(Document.id.desc())
        
        # Paginate using SQLAlchemy's paginate
        pagination = docs_query.paginate(page=page, per_page=per_page, error_out=False)
        return pagination

    def delete_document(self, doc_id):
        doc = Document.query.get(doc_id)
        if doc:
            sqlalchemy_db.session.delete(doc)
            sqlalchemy_db.session.commit()

    def get_document_by_id(self, doc_id):
        return Document.query.get(doc_id)

    def add_document(self, title, description, content_html, pdf_base64=None):
        doc = Document(
            title=title, 
            description=description, 
            content_html=content_html, 
            pdf_base64=pdf_base64
        )
        sqlalchemy_db.session.add(doc)
        sqlalchemy_db.session.commit()
        return doc

    def update_document(self, doc_id, **kwargs):
        doc = Document.query.get(doc_id)
        if doc:
            if 'title' in kwargs: doc.title = kwargs['title']
            if 'description' in kwargs: doc.description = kwargs['description']
            if 'content_html' in kwargs: doc.content_html = kwargs['content_html']
            if 'pdf_base64' in kwargs: doc.pdf_base64 = kwargs['pdf_base64']
            doc.updated_at = datetime.utcnow()
            sqlalchemy_db.session.commit()
            return doc
        return None

    def get_setting(self, key, default=None):
        setting = Setting.query.filter_by(key=key).first()
        if setting:
            return setting.value
        return default

    def set_setting(self, key, value):
        setting = Setting.query.filter_by(key=key).first()
        if setting:
            setting.value = value
        else:
            setting = Setting(key=key, value=value)
            sqlalchemy_db.session.add(setting)
        sqlalchemy_db.session.commit()

db = DatabaseBridge()
