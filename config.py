import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "chave-muito-segura"
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')  # depois trocamos para PostgreSQL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutos
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True  # funciona apenas em HTTPS
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = True
    WTF_CSRF_TIME_LIMIT = 1800  # expiração do token (em segundos)
