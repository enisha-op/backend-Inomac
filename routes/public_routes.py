from flask import Blueprint, request, jsonify
from database import db
from models.quote import Quote
# from utils.mailer import send_notification_email # Descomentar cuando configures el mailer

public_bp = Blueprint('public', __name__)

@public_bp.route('/quote', methods=['POST'])
def create_quote():
    try:
        data = request.json

        # Validaciones básicas
        if not data.get('name') or not data.get('email'):
            return jsonify({"error": "Nombre y correo son obligatorios"}), 400

        # Crear nueva instancia del modelo Quote
        new_quote = Quote(
            fullname=data.get('name'),
            email=data.get('email'),
            phone=data.get('phone'),
            ruc=data.get('ruc'), # Capturamos el RUC que viene del front
            model_interested=data.get('model'),
            message=data.get('message')
        )

        # Guardar en MySQL (XAMPP)
        db.session.add(new_quote)
        db.session.commit()

        # Opcional: Enviar correo (puedes configurar esto luego)
        # send_notification_email(new_quote)

        return jsonify({
            "status": "success",
            "message": "Cotización guardada correctamente",
            "id": new_quote.id
        }), 201

    except Exception as e:
        db.session.rollback()
        # Este print es clave para ver si el error es por la longitud del String
        print(f"Error detallado: {str(e)}")
        return jsonify({"error": "No se pudo procesar la cotización"}), 500