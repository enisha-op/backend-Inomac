import os
from dotenv import load_dotenv
import cloudinary # Importante importar la librería

# Solo carga el .env si existe (útil para local)
load_dotenv()

class Config:
    # --- CONFIGURACIÓN DE BASE DE DATOS ---
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', 
        'mysql+pymysql://root:@localhost/inomac_db'
    )
    
    if SQLALCHEMY_DATABASE_URI.startswith("mysql://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("mysql://", "mysql+pymysql://", 1)

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'tu_clave_secreta_provisional')

    # --- CONFIGURACIÓN DE CLOUDINARY ---
    # Esto inicializa Cloudinary tanto en Local como en Railway
    cloudinary.config( 
        cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"), 
        api_key = os.getenv("CLOUDINARY_API_KEY"), 
        api_secret = os.getenv("CLOUDINARY_API_SECRET"),
        secure = True
    )