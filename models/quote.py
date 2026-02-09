from database import db
from datetime import datetime

class Quote(db.Model):
    __tablename__ = 'quotes'
    
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    ruc = db.Column(db.String(11), nullable=True)
    model_interested = db.Column(db.String(1000), nullable=False)
    message = db.Column(db.Text)
    status = db.Column(db.Enum('Pendiente', 'Contactado', 'Vendido'), default='Pendiente')
    
    # Campos para cotización con montos
    quantity = db.Column(db.Integer, default=1)
    unit_price = db.Column(db.Numeric(20, 2), nullable=True)
    total_amount = db.Column(db.Numeric(20, 2), nullable=True)
    
    # Relación con Truck (usamos string 'Truck' para evitar importación circular)
    truck_id = db.Column(db.Integer, db.ForeignKey('trucks.id'), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.fullname,
            "email": self.email,
            "phone": self.phone,
            "ruc": self.ruc,
            "model": self.model_interested,
            "message": self.message,
            "status": self.status,
            "quantity": self.quantity,
            "unit_price": float(self.unit_price) if self.unit_price else 0,
            "total": float(self.total_amount) if self.total_amount else 0,
            "truck_id": self.truck_id,
            "date": self.created_at.strftime("%Y-%m-%d %H:%M")
        }