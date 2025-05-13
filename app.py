from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, session, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from pymongo import MongoClient
from functools import wraps
from Usuario import Usuario
from Socio import Socio
from config import Config
import datetime
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import secrets
import string

def generar_codigo_seguro(longitud=6):
    caracteres = string.ascii_letters + string.digits
    return ''.join(secrets.choice(caracteres) for _ in range(longitud))

BASE_URL = "https://api.pexels.com/v1/search"

app = Flask(__name__, template_folder='frontend/templates', static_folder='frontend/static')
app.config.from_object(Config)

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'sesion'

# Conexión a MongoDB usando la configuración
cliente = MongoClient(app.config['MONGODB_URI'])
app.db = cliente.alquiler_coches

# Clase para manejar usuarios en Flask-Login
class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['idc'])
        self.nombre = user_data['nombre']
        self.correo = user_data['correo']
        self.tipo = user_data['tipo_usuario']
        self.imagen = user_data.get('imagen', 'usuario.png')

@login_manager.user_loader
def load_user(user_id):
    user_data = app.db.Users.find_one({'idc': user_id}) or app.db.Socios.find_one({'idc': user_id})
    if user_data:
        return User(user_data)
    return None

# Decorador personalizado para verificar el tipo de usuario
def tipo_required(tipo):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.tipo != tipo:
                flash('No tienes permiso para acceder a esta página', 'error')
                return redirect(url_for('inicio'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

app.jinja_env.globals.update(generar_codigo_seguro=generar_codigo_seguro)

@app.route('/')
def inicio():
    return render_template('sitio/Inicio.html', status={
        'secionIniciada': current_user.is_authenticated,
        'nombre': current_user.nombre if current_user.is_authenticated else '',
        'correo': current_user.correo if current_user.is_authenticated else '',
        'tipo': current_user.tipo if current_user.is_authenticated else '',
        'imagen': current_user.imagen if current_user.is_authenticated else 'usuario.png',
        'idUsuario': current_user.id if current_user.is_authenticated else 0,
        'pedidos': 0
    })

@app.route('/sesion')
def sesion():
    return render_template('sitio/inicio_sesion.html') 

@app.route('/registro')
def registro():
    return render_template('sitio/registro.html')

@app.route('/registrarUsuario')
def registroUsuario():
    return render_template('sitio/RegistroUsuario.html')

@app.route('/panelSocio')
@login_required
@tipo_required('socio')
def PanelSocio():
    return render_template('control/panel_socio.html')

@app.route('/sitio/registrarUsuario', methods = ['POST'])
def registrarUsuario():
    tipo_usuario = request.form['tipo_usuario']
    nombre = request.form['nombre']
    correo = request.form['correo']
    contraseña = request.form['contraseña1']
    confirmacion = request.form['contraseña2']
    if contraseña != confirmacion:
        flash('Las contraseñas no coinciden', 'error')
        return redirect(url_for('registro'))
    
    correo_usuario =  app.db.Users.find_one({'correo': correo})
    correo_socio = app.db.Socios.find_one({'correo': correo})
    
    if correo_socio:
        flash('El correo ya se encuentra registrado como socio', 'error')
        return redirect(url_for('registro'))
    elif correo_usuario:
        flash('El correo ya se encuentra registrado como usuario', 'error')
        return redirect(url_for('registro'))
    
    if tipo_usuario == "socio":
        tipo_documento = request.form['tipo_documento']
        numero_documento = request.form['numero_documento']
        direccion = request.form['direccion']
        nd = app.db.Socios.find_one({'numero_documento': numero_documento})
        if nd:
            flash('El numero de documento ya se encuentra registrado', 'error')
            return redirect(url_for('registro'))
        socio = {'nombre':nombre, 'correo':correo, 'contraseña':contraseña, 'direccion': direccion,'tipo_documento': tipo_documento, 'numero_documento':numero_documento, 'imagen_perfil': "usuario.png"}
        socio = Socio(socio)
        passw = socio.set_password(contraseña)
        idc = generar_codigo_seguro()
        data = {'idc':idc, 'nombre':nombre, 'correo':correo, 'contraseña':passw, 'direccion': direccion,'tipo_documento': tipo_documento, 'numero_documento':numero_documento, 'tipo_usuario': tipo_usuario, 'imagen_perfil': "usuario.png"}
        app.db.Socios.insert_one(data)
        return redirect('/sesion')
    else:
        usuario = {'nombre':nombre, 'correo':correo, 'contraseña':contraseña, 'imagen':"usuario.png"}
        usuario = Usuario(usuario)
        passw = usuario.set_password(contraseña)
        idc = generar_codigo_seguro()
        data = {'idc':idc, 'nombre':nombre, 'correo':correo, 'contraseña':passw, 'tipo_usuario': tipo_usuario, 'imagen':"usuario.png"}
        app.db.Users.insert_one(data)
        return redirect('/sesion')
    
@app.route('/sitio/iniciarSesion', methods=['POST'])
def iniciarSesion():
    try:
        tipo_usuario = request.form['tipo_usuario']
        correo = request.form['correo']
        contraseña = request.form['contraseña']
        
        if tipo_usuario == "socio":
            user_data = app.db.Socios.find_one({'correo': correo})
            if user_data is None:
                flash('No se encontró el socio, intente nuevamente', 'error')
                return redirect('/sesion')
            
            socio = Socio(user_data)
            if not socio.check_password(contraseña):
                flash('Contraseña incorrecta', 'error')
                return redirect('/sesion')
                
            user = User(user_data)
            login_user(user)
            return redirect('/panelSocio')
            
        elif tipo_usuario == "usuario":
            user_data = app.db.Users.find_one({'correo': correo})
            if user_data is None:
                flash('No se encontró el usuario, intente nuevamente', 'error')
                return redirect('/sesion')
            
            usuario = Usuario(user_data)
            if not usuario.check_password(contraseña):
                flash('Contraseña incorrecta', 'error')
                return redirect('/sesion')
                
            user = User(user_data)
            login_user(user)
            return redirect('/')
            
    except Exception as e:
        flash('Error al iniciar sesión. Por favor, intente nuevamente.', 'error')
        return redirect('/sesion')
        
@app.route('/cerrarSesion')
@login_required
def cerrarSesion():
    logout_user()
    return redirect('/')

@app.route('/mis_carros')
@login_required
@tipo_required('socio')
def mis_carros():
    try:
        mis_carros = [carro for carro in app.db.Carros.find({"idSocio": current_user.id})]
        return render_template('/control/mis_carros.html', mis_carros=mis_carros)
    except Exception as e:
        flash('Error al cargar los carros', 'error')
        return redirect(url_for('inicio'))

@app.route('/control/registrarCarro', methods=['POST'])
@login_required
@tipo_required('socio')
def registrarCarro():
    try:
        nombre = request.form['nombre']
        tipo = request.form['tipo']
        placa = request.form['placa']
        año = request.form['año']
        color = request.form['color']
        ubicacion = request.form['ubicacion']
        imagen = request.form['imagenes']
        
        # Verificar si la placa ya existe
        carro_existente = app.db.Carros.find_one({'placa': placa})
        if carro_existente:
            flash('Ya existe un carro registrado con esa placa', 'error')
            return redirect('/mis_carros')
            
        data = {
            'idSocio': current_user.id,
            'nombre': nombre,
            'tipo': tipo,
            'placa': placa,
            'año': año,
            'color': color,
            'ubicacion': ubicacion,
            'ingresos': int(0),
            'imagen': imagen
        }
        app.db.Carros.insert_one(data)
        flash('Carro registrado exitosamente', 'success')
        return redirect('/mis_carros')
    except Exception as e:
        flash('Error al registrar el carro', 'error')
        return redirect('/mis_carros')



if __name__ == '__main__':
    app.run(debug = True, port=5700)