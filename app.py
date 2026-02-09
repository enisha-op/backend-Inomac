from flask import Flask
from flask_cors import CORS
from database import db
from config import Config
from routes.public_routes import public_bp 
from routes.admin_routes import admin_bp
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    CORS(app) 
    db.init_app(app)

    # --- CONFIGURACIÓN DE CARPETAS PARA ARCHIVOS ---
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'static/uploads/trucks')

    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # Registro de Blueprints
    app.register_blueprint(public_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    with app.app_context():
        # Esto creará las tablas en Railway automáticamente al subir el código
        db.create_all() 
        
    return app

# IMPORTANTE: Esto es lo que permite que funcione en Local y Railway
if __name__ == '__main__':
    app = create_app()
    # En Railway, la variable PORT es obligatoria. En local, usa el 5000.
    port = int(os.environ.get("PORT", 5000))
    # host='0.0.0.0' es vital para que Railway pueda "ver" tu app
    app.run(host='0.0.0.0', port=port, debug=True)