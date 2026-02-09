from database import db
from datetime import datetime

class Truck(db.Model):
    __tablename__ = 'trucks'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    short_specs = db.Column(db.String(255))
    price = db.Column(db.Numeric(10, 2), default=0.00)
    
    # Se aumenta a 500 para soportar URLs largas de Cloudinary
    image_front = db.Column(db.String(500))
    image_side = db.Column(db.String(500))
    pdf_spec_sheet = db.Column(db.String(500))
    
    # Detalles técnicos
    motor = db.Column(db.String(150))
    torque = db.Column(db.String(150))
    transmission = db.Column(db.String(150))
    traction = db.Column(db.String(150))
    cabin = db.Column(db.String(150))
    tank_capacity = db.Column(db.String(150))
    brakes = db.Column(db.String(150))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "specs": self.short_specs,
            "price": float(self.price) if self.price else 0.0,
            "img": self.image_front,
            "imgSide": self.image_side,
            "pdf": self.pdf_spec_sheet,
            "details": {
                "motor": self.motor,
                "torque": self.torque,
                "transmision": self.transmission,
                "traccion": self.traction,
                "cabina": self.cabin,
                "tanque": self.tank_capacity,
                "frenos": self.brakes
            },
            "created_at": self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }