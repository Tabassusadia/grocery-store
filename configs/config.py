class Config:
    SECRET_KEY = 'dbms'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///grocery.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'static/uploads'
