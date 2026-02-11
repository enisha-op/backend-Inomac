from flask import Flask
from flask_cors import CORS
from database import db
from config import Config
from routes.public_routes import public_bp 
from routes.admin_routes import admin_bp
from models.user import User
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # --- CONFIGURACIÓN DE CORS ---
    CORS(app, resources={r"/api/*": {"origins": [
        "https://www.inomac.com.pe",
        "http://localhost:3000"
    ]}}) 
    
    db.init_app(app)

    # Registro de Blueprints
    app.register_blueprint(public_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    with app.app_context():
        db.create_all() 
        
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin = User(
                username='admin',
                email='admin@gmail.com'
            )
            admin.set_password('admin123') 
            db.session.add(admin)
            db.session.commit()
            print(">>> Base de datos inicializada y usuario admin creado.")
        
    return app

# --- ESTA LÍNEA ES LA CLAVE PARA RAILWAY ---
# Al ponerla aquí, gunicorn puede encontrar "app" al hacer "app:app"
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)