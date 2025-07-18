from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, session, send_file
from cache_config import init_cache
from logger_config import setup_logger
from werkzeug.utils import secure_filename
import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from pymongo import MongoClient
from functools import wraps
from Usuario import Usuario
from Socio import Socio
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


# Inicializar cache
cache = init_cache(app)

# Configurar logger
logger = setup_logger(app)

# Configuración para subida de archivos
UPLOAD_FOLDER = os.path.join('frontend', 'static', 'uploads', 'cars')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_car_image(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Generar un nombre único para el archivo
        base, ext = os.path.splitext(filename)
        unique_filename = f"{base}_{generar_codigo_seguro()}{ext}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        return os.path.join('uploads', 'cars', unique_filename)
    return None

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'sesion'

# Conexión a MongoDB usando la configuración
cliente = MongoClient(app.config['MONGODB_URI'])
app.db = cliente.alquiler_coches

# Crear índices para optimizar búsquedas
app.db.Users.create_index('correo', unique=True)
app.db.Users.create_index('idc', unique=True)
app.db.Socios.create_index('correo', unique=True)
app.db.Socios.create_index('idc', unique=True)
app.db.Socios.create_index('numero_documento', unique=True)

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
@cache.cached(timeout=300)  # Cache por 5 minutos
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
        # Obtener datos del formulario
        nombre = request.form['nombre']
        tipo = request.form['tipo']
        placa = request.form['placa']
        año = request.form['año']
        color = request.form['color']
        ubicacion = request.form['ubicacion']
        precio = request.form['precio']
        
        # Verificar si la placa ya existe
        carro_existente = app.db.Carros.find_one({'placa': placa})
        if carro_existente:
            flash('Ya existe un carro registrado con esa placa', 'error')
            return redirect('/mis_carros')
        
        # Manejar la imagen
        imagen_path = 'default_car.png'  # Imagen por defecto
        if 'imagen' in request.files:
            file = request.files['imagen']
            if file and file.filename != '':
                saved_path = save_car_image(file)
                if saved_path:
                    imagen_path = saved_path.replace('\\', '/')  # Reemplazar \ por /
                else:
                    flash('Formato de imagen no válido. Se usará una imagen por defecto.', 'warning')
        
        # Preparar datos para MongoDB
        data = {
            'idCarro': generar_codigo_seguro(),
            'idSocio': current_user.id,
            'nombre': nombre,
            'tipo': tipo,
            'placa': placa.upper(),  # Convertir placa a mayúsculas
            'año': año,
            'color': color,
            'ubicacion': ubicacion,
            'precio': precio,
            'disponible': True,
            'ingresos': int(0),
            'imagen': imagen_path,
            'fotos' : [imagen_path, ],
        }
        
        # Guardar en la base de datos
        app.db.Carros.insert_one(data)
        flash('Carro registrado exitosamente', 'success')
        return redirect('/mis_carros')
        
    except Exception as e:
        print(f'Error al registrar el carro: {str(e)}')
        flash(f'Error al registrar el carro: {str(e)}', 'error')
        return redirect('/mis_carros')
    
@app.route('/detalles/<carro_id>')
@login_required
@tipo_required('socio')
def Detalles(carro_id):
    try:
        carro =  app.db.Carros.find_one({"idCarro": carro_id})
        if carro is None:
            flash('Carro no encontrado', 'error')
            return redirect(url_for('PanelSocio'))
        return render_template('control/detalles_carros.html', carro=carro)
    except Exception as e:
        flash('Error al cargar los carros', 'error')
        return redirect(url_for('PanelSocio'))
    
from flask import request, redirect, flash, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os

@app.route('/control/agregarFoto/<carro_id>', methods=['POST'])
@login_required
@tipo_required('socio')
def AgregarFoto(carro_id):
    try:
        # Buscar el carro
        carro = app.db.Carros.find_one({"idCarro": carro_id, "idSocio": current_user.id})
        if carro is None:
            flash("Carro no encontrado o no tienes permiso para modificarlo", "error")
            return redirect(url_for('PanelSocio'))

        # Manejo del archivo
        if 'nueva_foto' not in request.files:
            flash('No se ha subido ninguna imagen', 'error')
            return redirect(url_for('Detalles', carro_id=carro_id))
        
        file = request.files['nueva_foto']
        if file.filename == '':
            flash('No se seleccionó ningún archivo', 'warning')
            return redirect(url_for('Detalles', carro_id=carro_id))
        
        saved_path = save_car_image(file)
        if not saved_path:
            flash('Formato de imagen no válido', 'error')
            return redirect(url_for('Detalles', carro_id=carro_id))

        # Reemplazar \ por / en la ruta
        saved_path = saved_path.replace('\\', '/')

        # Agregar imagen al arreglo de fotos del carro
        fotos_actuales = carro.get('fotos', [])
        if not isinstance(fotos_actuales, list):
            fotos_actuales = []

        fotos_actuales.append(saved_path)

        # Actualizar en la base de datos
        app.db.Carros.update_one(
            {"idCarro": carro_id},
            {"$set": {"fotos": fotos_actuales}}
        )

        flash('Foto agregada exitosamente', 'success')
        return redirect(url_for('Detalles', carro_id=carro_id))

    except Exception as e:
        print(f"Error al agregar la foto: {str(e)}")
        flash("Ocurrió un error al subir la foto", "error")
        return redirect(url_for('Detalles', carro_id=carro_id))
    

@app.route('/control/editarCarro/<carro_id>', methods=['POST'])
@login_required
@tipo_required('socio')
def editarCarro(carro_id):
    try:
        # Obtener el carro original desde la base de datos
        carro = app.db.Carros.find_one({'idCarro': carro_id, 'idSocio': current_user.id})
        if not carro:
            flash('Carro no encontrado o no tienes permiso para editarlo.', 'error')
            return redirect('/mis_carros')

        # Obtener los datos del formulario
        nombre = request.form.get('nombre', carro['nombre'])
        tipo = request.form.get('tipo', carro['tipo'])
        año = request.form.get('año', carro['año'])
        color = request.form.get('color', carro['color'])
        ubicacion = request.form.get('ubicacion', carro['ubicacion'])
        precio = request.form.get('precio', carro['precio'])

        # Si hay una nueva imagen, guardarla
        imagen_path = carro['imagen']
        if 'imagen' in request.files:
            file = request.files['imagen']
            if file and file.filename != '':
                saved_path = save_car_image(file)
                if saved_path:
                    imagen_path = saved_path.replace('\\', '/')
                else:
                    flash('Formato de imagen no válido. Se mantiene la imagen anterior.', 'warning')

        # Actualizar en la base de datos
        app.db.Carros.update_one(
            {'idCarro': carro_id},
            {'$set': {
                'nombre': nombre,
                'tipo': tipo,
                'año': año,
                'color': color,
                'ubicacion': ubicacion,
                'precio': precio,
                'imagen': imagen_path
            }}
        )

        flash('Carro actualizado exitosamente.', 'success')
        return redirect(url_for('Detalles', carro_id=carro_id))

    except Exception as e:
        print(f'Error al editar el carro: {str(e)}')
        flash(f'Ocurrió un error al actualizar el carro: {str(e)}', 'error')
        return redirect('/mis_carros')


@app.route('/control/eliminarCarro/<carro_id>', methods=['POST'])
@login_required
@tipo_required('socio')
def eliminarCarro(carro_id):
    try:
        resultado = app.db.Carros.delete_one({'idCarro': carro_id, 'idSocio': current_user.id})
        if resultado.deleted_count == 1:
            flash('Carro eliminado exitosamente.', 'success')
        else:
            flash('No se encontró el carro o no tienes permisos.', 'error')
    except Exception as e:
        flash(f'Error al eliminar el carro: {str(e)}', 'error')
    
    return redirect('/mis_carros')





@app.route('/lista_carros')
def Lista_carros():
    carros = [carro for carro in app.db.Carros.find()]
    return render_template('sitio/lista_carros.html',carros = carros, status={
        'secionIniciada': current_user.is_authenticated,
        'nombre': current_user.nombre if current_user.is_authenticated else '',
        'correo': current_user.correo if current_user.is_authenticated else '',
        'tipo': current_user.tipo if current_user.is_authenticated else '',
        'imagen': current_user.imagen if current_user.is_authenticated else 'usuario.png',
        'idUsuario': current_user.id if current_user.is_authenticated else 0,
        'pedidos': 0
    })


@app.route('/control/aplicarFiltros', methods=['POST'])
def aplicar_filtros():
    filtro_Tipo = request.form.get('tipo', '')
    filtro_ubicacion = request.form.get('ubicacion', '')
    filtro_precioMin = request.form.get('precioMin', '')
    filtro_precioMax = request.form.get('precioMax', '')
    filtro_color = request.form.get('color', '')
    filtro_marca = request.form.get('marca', '')
    filtro_año = request.form.get('año', '')

    try:
        filtro_precioMin = int(filtro_precioMin)
    except (ValueError, TypeError):
        filtro_precioMin = 0

    try:
        filtro_precioMax = int(filtro_precioMax)
    except (ValueError, TypeError):
        filtro_precioMax = 999999999

    try:
        filtro_año = int(filtro_año)
    except (ValueError, TypeError):
        filtro_año = None

    query = {}
    if filtro_Tipo:
        query['tipo'] = filtro_Tipo
    if filtro_ubicacion:
        query['ubicacion'] = filtro_ubicacion
    if filtro_color:
        query['color'] = filtro_color

    carros = list(app.db.Carros.find(query))
    
    print(f"Consulta: {query}")

    return render_template('sitio/lista_carros.html', carros=carros, status={
        'secionIniciada': current_user.is_authenticated,
        'nombre': current_user.nombre if current_user.is_authenticated else '',
        'correo': current_user.correo if current_user.is_authenticated else '',
        'tipo': current_user.tipo if current_user.is_authenticated else '',
        'imagen': current_user.imagen if current_user.is_authenticated else 'usuario.png',
        'idUsuario': current_user.id if current_user.is_authenticated else 0,
        'pedidos': 0
    })
    
    
@app.route('/ver_detalles/<carro_id>')
def ver_detalles(carro_id):
    carro = app.db.Carros.find_one({"idCarro": carro_id})
    if carro is None:
        flash('Carro no encontrado', 'error')
        return redirect(url_for('Lista_carros'))
    
    return render_template('sitio/ver_detalles.html', carro=carro, status={
        'secionIniciada': current_user.is_authenticated,
        'nombre': current_user.nombre if current_user.is_authenticated else '',
        'correo': current_user.correo if current_user.is_authenticated else '',
        'tipo': current_user.tipo if current_user.is_authenticated else '',
        'imagen': current_user.imagen if current_user.is_authenticated else 'usuario.png',
        'idUsuario': current_user.id if current_user.is_authenticated else 0,
        'pedidos': 0
    })
    
@app.route('/agendar_reserva/<carro_id>', methods=['POST'])
@login_required
def agendar_reserva(carro_id):
    try:
        # Verificar si el usuario está autenticado
        if not current_user.is_authenticated:
            flash('Debes iniciar sesión para hacer una reserva', 'error')
            return redirect(url_for('sesion'))

        # Obtener datos del formulario
        fecha_inicio = request.form.get('inicio')
        fecha_final = request.form.get('fin')

        # Validar fechas
        if not fecha_inicio or not fecha_final:
            flash('Debes proporcionar ambas fechas: inicio y fin.', 'error')
            return redirect(url_for('ver_detalles', carro_id=carro_id))

        try:
            fecha_inicio = datetime.datetime.strptime(fecha_inicio, '%Y-%m-%d')
            fecha_final = datetime.datetime.strptime(fecha_final, '%Y-%m-%d')
            hoy = datetime.datetime.now().date()

            if fecha_inicio.date() < hoy:
                flash('La fecha de inicio no puede ser menor al día de hoy.', 'error')
                return redirect(url_for('ver_detalles', carro_id=carro_id))

            if fecha_inicio >= fecha_final:
                flash('La fecha de inicio debe ser anterior a la fecha final.', 'error')
                return redirect(url_for('ver_detalles', carro_id=carro_id))
        except ValueError:
            flash('Formato de fecha inválido. Usa el formato AAAA-MM-DD.', 'error')
            return redirect(url_for('ver_detalles', carro_id=carro_id))

        # Calcular la cantidad de días de la reserva
        dias_reserva = (fecha_final - fecha_inicio).days

        # Verificar si el carro existe
        carro = app.db.Carros.find_one({"idCarro": carro_id})
        if not carro:
            flash('Carro no encontrado.', 'error')
            return redirect(url_for('Lista_carros'))

        # Crear la reserva
        reserva_data = {
            'idReserva': generar_codigo_seguro(),
            'idCarro': carro_id,
            'idUsuario': current_user.id,
            'fecha_inicio': fecha_inicio,
            'fecha_final': fecha_final,
            'dias_reserva': dias_reserva,
            'estado': "pendiente",
            'carro_nombre': carro.get('nombre', 'Desconocido'),
            'carro_imagen': carro.get('imagen', 'default_car.png')
        }
        app.db.Reservas.insert_one(reserva_data)

        flash(f'Reserva realizada exitosamente por {dias_reserva} días. Está pendiente de confirmación.', 'success')
        return redirect(url_for('Lista_carros'))

    except Exception as e:
        print(f"Error al agendar la reserva: {str(e)}")
        flash('Ocurrió un error al intentar realizar la reserva. Por favor, inténtalo nuevamente.', 'error')
        return redirect(url_for('ver_detalles', carro_id=carro_id))

if __name__ == '__main__':
    app.run(debug = True, port=5700)