from database import db
from datetime import datetime

class Quote(db.Model):
    __tablename__ = 'quotes'
    
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(25), nullable=True) # Aumentado para prefijos internacionales
    ruc = db.Column(db.String(11), nullable=True)
    
    # Este campo servirá para diferenciar: 
    # Si es 'REGISTRO MANUAL (ADMIN)' se trata como un Cliente puro.
    model_interested = db.Column(db.String(1000), nullable=False)
    
    message = db.Column(db.Text, nullable=True)
    status = db.Column(db.Enum('Pendiente', 'Contactado', 'Vendido'), default='Pendiente')
    
    # Precios y cantidades con precisión aumentada (DECIMAL 20,2)
    quantity = db.Column(db.Integer, default=1)
    unit_price = db.Column(db.Numeric(20, 2), nullable=True, default=0.00)
    total_amount = db.Column(db.Numeric(20, 2), nullable=True, default=0.00)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convierte el objeto a diccionario para el Frontend de Next.js"""
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
            "date": self.created_at.strftime("%Y-%m-%d %H:%M")
        }