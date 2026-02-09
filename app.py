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
    # Permitimos tanto tu entorno local como el dominio oficial de INOMAC
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
        
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@gmail.com'
            )
            admin.set_password('admin123') 
            
            db.session.add(admin)
            db.session.commit()
            print(">>> Base de datos inicializada y usuario admin creado.")
        
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)