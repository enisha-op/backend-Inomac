from flask import Blueprint, jsonify, request, current_app
from database import db
from models.quote import Quote
from models.truck import Truck
from sqlalchemy import func, or_
from werkzeug.utils import secure_filename
import os
import cloudinary.uploader

admin_bp = Blueprint('admin', __name__)

# --- RUTAS DE ESTADÍSTICAS ---

@admin_bp.route('/stats', methods=['GET'])
def get_dashboard_stats():
    try:
        total_quotes = Quote.query.count()
        enterprise_count = Quote.query.filter(Quote.ruc.isnot(None), Quote.ruc != '').count()
        
        # OBTENER TODOS LOS MODELOS PARA DESGLOSARLOS
        all_quotes = Quote.query.with_entities(Quote.model_interested).all()
        
        model_counts = {}
        for q in all_quotes:
            # Separar por coma, limpiar espacios y contar individualmente
            models = [m.strip() for m in q.model_interested.split(',')]
            for model in models:
                if model:
                    model_counts[model] = model_counts.get(model, 0) + 1

        # Convertir a formato compatible con Recharts del Front
        chart_data = [{"name": name, "total": total} for name, total in model_counts.items()]

        # Tendencia mensual
        trend_stats = db.session.query(
            func.date_format(Quote.created_at, '%Y-%m').label('month'),
            func.count(Quote.id)
        ).group_by('month').order_by('month').all()
        
        line_chart_data = [{"month": t[0], "total": t[1]} for t in trend_stats]

        return jsonify({
            "total": total_quotes,
            "enterprises": enterprise_count,
            "chartData": chart_data,
            "lineChartData": line_chart_data,
            "status": "success"
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- RUTAS DE COTIZACIONES ---

@admin_bp.route('/quotes', methods=['GET'])
def get_quotes():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', None)
    search_query = request.args.get('search', None)
    per_page = 10
    
    query = Quote.query
    if status_filter and status_filter != 'Todos':
        query = query.filter_by(status=status_filter)
    if search_query:
        search_all = f"%{search_query}%"
        query = query.filter(or_(
            Quote.fullname.like(search_all), 
            Quote.ruc.like(search_all), 
            Quote.email.like(search_all)
        ))
        
    pagination = query.order_by(Quote.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        "quotes": [q.to_dict() for q in pagination.items],
        "total_pages": pagination.pages,
        "current_page": pagination.page
    }), 200

@admin_bp.route('/quotes/<int:quote_id>/status', methods=['PATCH'])
def update_quote_status(quote_id):
    data = request.json
    new_status = data.get('status')
    quote = Quote.query.get_or_404(quote_id)
    if new_status in ['Pendiente', 'Contactado', 'Vendido']:
        quote.status = new_status
        db.session.commit()
        return jsonify({"message": "Estado actualizado"}), 200
    return jsonify({"error": "Estado no válido"}), 400

@admin_bp.route('/quotes/<int:quote_id>/amounts', methods=['PATCH'])
def update_quote_amounts(quote_id):
    try:
        data = request.json
        quote = Quote.query.get_or_404(quote_id)
        
        # Nota: Aquí guardamos el total_amount general enviado por el front
        quote.total_amount = data.get('total_amount', quote.total_amount)
        
        # Si decides guardar cantidad y precio unitario del primer modelo (simple)
        # o manejar un JSON de items, puedes hacerlo aquí:
        items = data.get('items', [])
        if items:
            # Guardamos los valores del primer item por compatibilidad con tu modelo Quote
            quote.quantity = items[0].get('quantity', quote.quantity)
            quote.unit_price = items[0].get('unit_price', quote.unit_price)

        db.session.commit()
        return jsonify({"message": "Montos y cantidades actualizados correctamente"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# --- RUTAS DE CAMIONES (INVENTARIO) ---

@admin_bp.route('/trucks', methods=['POST'])
def create_truck():
    try:
        name = request.form.get('name')
        price = request.form.get('price')
        short_specs = request.form.get('short_specs')
        
        file_img = request.files.get('image_front')
        file_pdf = request.files.get('pdf_file')

        img_url = ""
        pdf_url = ""

        # SUBIDA DE IMAGEN
        if file_img:
            upload_result = cloudinary.uploader.upload(file_img, folder="inomac/trucks")
            img_url = upload_result['secure_url']

        # SUBIDA DE PDF (Corrección de descarga)
        if file_pdf:
            # Usamos use_filename y resource_type="raw" para archivos no-imagen
            pdf_result = cloudinary.uploader.upload(
                file_pdf, 
                folder="inomac/pdfs", 
                resource_type="raw",
                use_filename=True,
                unique_filename=True
            )
            pdf_url = pdf_result['secure_url']

        new_truck = Truck(
            name=name,
            price=price,
            short_specs=short_specs,
            image_front=img_url,
            pdf_spec_sheet=pdf_url,
            motor=request.form.get('motor'),
            torque=request.form.get('torque'),
            transmission=request.form.get('transmission'),
            traction=request.form.get('traction')
        )

        db.session.add(new_truck)
        db.session.commit()
        return jsonify({"message": "Camión registrado", "truck": new_truck.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/trucks/<int:truck_id>', methods=['PUT'])
def update_truck(truck_id):
    try:
        truck = Truck.query.get_or_404(truck_id)
        truck.name = request.form.get('name', truck.name)
        truck.price = request.form.get('price', truck.price)
        truck.short_specs = request.form.get('short_specs', truck.short_specs)
        truck.motor = request.form.get('motor', truck.motor)
        truck.torque = request.form.get('torque', truck.torque)
        truck.transmission = request.form.get('transmission', truck.transmission)
        truck.traction = request.form.get('traction', truck.traction)

        file_img = request.files.get('image_front')
        file_pdf = request.files.get('pdf_file')

        if file_img:
            upload_result = cloudinary.uploader.upload(file_img, folder="inomac/trucks")
            truck.image_front = upload_result['secure_url']

        if file_pdf:
            pdf_result = cloudinary.uploader.upload(
                file_pdf, 
                folder="inomac/pdfs", 
                resource_type="raw",
                use_filename=True,
                unique_filename=True
            )
            truck.pdf_spec_sheet = pdf_result['secure_url']

        db.session.commit()
        return jsonify({"message": "Unidad actualizada"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
    

@admin_bp.route('/trucks/<int:truck_id>', methods=['DELETE'])
def delete_truck(truck_id):
    try:
        truck = Truck.query.get_or_404(truck_id)
        db.session.delete(truck)
        db.session.commit()
        return jsonify({"message": "Unidad eliminada"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/trucks', methods=['GET'])
def get_all_trucks():
    trucks = Truck.query.order_by(Truck.created_at.desc()).all()
    return jsonify([t.to_dict() for t in trucks]), 200


#login
from models.user import User

@admin_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    # Buscamos por el username 'admin'
    user = User.query.filter_by(username=data.get('username')).first()
    
    if user and user.check_password(data.get('password')):
        return jsonify({"status": "success", "message": "Acceso concedido"}), 200
    
    return jsonify({"error": "Credenciales inválidas"}), 401


# --- RECURSOS UNIFICADOS DE COTIZACIONES Y CLIENTES ---

@admin_bp.route('/quotes', methods=['GET'])
def get_all_quotes():
    """Ruta única para obtener leads. Soporta filtros por estado, búsqueda y tipo."""
    try:
        page = request.args.get('page', 1, type=int)
        status_filter = request.args.get('status', None)
        search_query = request.args.get('search', None)
        # Nuevo filtro: si 'only_manual' es true, solo trae los creados desde el panel
        only_manual = request.args.get('manual', 'false').lower() == 'true'
        
        per_page = request.args.get('per_page', 15, type=int)
        query = Quote.query
        
        # Filtro por Procedencia (Manual vs Web)
        if only_manual:
            query = query.filter(Quote.model_interested == "REGISTRO MANUAL (ADMIN)")
        
        # Filtro por Estado
        if status_filter and status_filter != 'Todos':
            query = query.filter_by(status=status_filter)
            
        # Buscador global (Nombre, RUC, Email)
        if search_query:
            search_all = f"%{search_query}%"
            query = query.filter(or_(
                Quote.fullname.like(search_all), 
                Quote.ruc.like(search_all), 
                Quote.email.like(search_all)
            ))
            
        pagination = query.order_by(Quote.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            "quotes": [q.to_dict() for q in pagination.items],
            "total_pages": pagination.pages,
            "current_page": pagination.page
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/quotes/<int:quote_id>', methods=['PUT', 'DELETE'])
def manage_quote(quote_id):
    """CRUD unificado para editar o eliminar cualquier registro (Manual o Web)"""
    quote = Quote.query.get_or_404(quote_id)
    
    if request.method == 'PUT':
        try:
            data = request.json
            quote.fullname = data.get('name', quote.fullname)
            quote.email = data.get('email', quote.email)
            quote.phone = data.get('phone', quote.phone)
            quote.ruc = data.get('ruc', quote.ruc)
            quote.message = data.get('message', quote.message)
            quote.status = data.get('status', quote.status)
            
            db.session.commit()
            return jsonify({"message": "Registro actualizado correctamente"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    if request.method == 'DELETE':
        try:
            db.session.delete(quote)
            db.session.commit()
            return jsonify({"message": "Registro eliminado del sistema"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500
        



# CREAR COTI
@admin_bp.route('/quotes/manual', methods=['POST'])
def create_manual_quote():
    try:
        data = request.json
        # Buscamos los datos del cliente ya registrado
        customer = Quote.query.get(data.get('customer_id'))
        if not customer:
            return jsonify({"error": "Cliente no encontrado"}), 404

        # Creamos una NUEVA fila en la tabla quotes basada en ese cliente
        new_quote = Quote(
            fullname=customer.fullname,
            email=customer.email,
            phone=customer.phone,
            ruc=customer.ruc,
            model_interested=data.get('model'),
            message=f"Cotización manual creada desde el panel. Ref: {customer.id}",
            status='Pendiente',
            quantity=data.get('quantity', 1),
            unit_price=data.get('unit_price', 0),
            total_amount=data.get('total_amount', 0)
        )

        db.session.add(new_quote)
        db.session.commit()
        return jsonify({"message": "Cotización creada con éxito"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500