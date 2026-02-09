import os
from dotenv import load_dotenv

# Solo carga el .env si existe (útil para local)
load_dotenv()

class Config:
    # 1. Intentamos obtener la URL de Railway. 
    # 2. Si no existe, usamos la de tu MySQL local.
    # Nota: Asegúrate de que en local tu base de datos se llame 'inomac_db'
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', 
        'mysql+pymysql://root:@localhost/inomac_db'
    )
    
    # Railway a veces entrega URLs que empiezan con 'mysql://' 
    # pero Flask-SQLAlchemy necesita 'mysql+pymysql://'
    if SQLALCHEMY_DATABASE_URI.startswith("mysql://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("mysql://", "mysql+pymysql://", 1)

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'tu_clave_secreta_provisional')