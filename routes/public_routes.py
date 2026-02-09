from flask import Blueprint, request, jsonify
from database import db
from models.quote import Quote
# from utils.mailer import send_notification_email # Descomentar cuando configures el mailer

public_bp = Blueprint('public', __name__)

@public_bp.route('/quote', methods=['POST'])
def create_quote():
    try:
        data = request.json
        if not data.get('name') or not data.get('email'):
            return jsonify({"error": "Nombre y correo son obligatorios"}), 400

        # Mejora: Asegurar que el modelo sea un String si el front manda un Array
        model_val = data.get('model', '')
        if isinstance(model_val, list):
            model_val = ", ".join(model_val)

        new_quote = Quote(
            fullname=data.get('name'),
            email=data.get('email'),
            phone=data.get('phone'),
            ruc=data.get('ruc'), 
            model_interested=model_val, # Guardamos el string procesado
            message=data.get('message')
        )

        db.session.add(new_quote)
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Cotización guardada correctamente",
            "id": new_quote.id
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f"Error en INOMAC (Public Route): {str(e)}") # Log más descriptivo
        return jsonify({"error": "No se pudo procesar la cotización"}), 500