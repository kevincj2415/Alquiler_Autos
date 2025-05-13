from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class Socio(UserMixin):
    def __init__(self,socio:dict):
        self.id = socio.get('ID') 
        self.nombre = socio.get('nombre', '')
        self.correo = socio.get('correo', '')
        self.contraseña = socio.get('contraseña', '')
        self.direccion = socio.get('direccion', '')
        self.numero_documento = socio.get('numero_documento')
        self.tipo_documento = socio.get('tipo_documento')
        self.imagen = socio.get('imagen', "")
        
    def set_password(self, password):
        self.contraseña = generate_password_hash(password)
        return self.contraseña

    def check_password(self, password):
        return check_password_hash(self.contraseña, password)
    
    def __repr__(self):
        return '<User {}>'.format(self.correo)
    
    

        