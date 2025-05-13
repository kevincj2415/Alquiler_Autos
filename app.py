from flask import Flask, jsonify, render_template, request, redirect, url_for, flash,session, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from flask_mail import Mail, Message
from flask_migrate import Migrate
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from Usuario import Usuario
from Socio import Socio
from pymongo import MongoClient
import datetime
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import mysql.connector
import datetime
import requests

import secrets
import string

def generar_codigo_seguro(longitud=6):
    caracteres = string.ascii_letters + string.digits
    return ''.join(secrets.choice(caracteres) for _ in range(longitud))


PIXABAY_API_KEY = "47289007-1c84d3d414f613c857c6ded8f"
BASE_URL = "https://api.pexels.com/v1/search"

status = {'secionIniciada' : False,
    'nombre' : "",
    "correo" : "",
    "tipo" : "",
    'pedidos' : 0,
    'idUsuario' : 0,
    'tipoUs' : "",
    'imagen': ""
    }

app = Flask(__name__, template_folder='frontend/templates', static_folder='frontend/static')
app.secret_key = 'kevin_jairo'

cliente = MongoClient("mongodb+srv://kevincj2415:e2BhakVv76vBMD7f@cluster0.hb2dv.mongodb.net/")
app.db = cliente.alquiler_coches

app.jinja_env.globals.update(generar_codigo_seguro=generar_codigo_seguro)


@app.route('/')
def inicio():
    global status
    return render_template('sitio/Inicio.html', status=status)

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
def PanelSocio():
    global status
    if status['secionIniciada'] == True:
        return render_template('control/panel_socio.html')
    else:
        return redirect(url_for('registro'))

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
        return redirect('/')
    else:
        usuario = {'nombre':nombre, 'correo':correo, 'contraseña':contraseña, 'imagen':"usuario.png"}
        usuario = Usuario(usuario)
        passw = usuario.set_password(contraseña)
        idc = generar_codigo_seguro()
        data = {'idc':idc, 'nombre':nombre, 'correo':correo, 'contraseña':passw, 'tipo_usuario': tipo_usuario, 'imagen':"usuario.png"}
        app.db.Users.insert_one(data)
        return redirect('/')
    
@app.route('/sitio/iniciarSesion', methods = ['POST'])
def iniciarSesion():
    global status
    tipo_usuario = request.form['tipo_usuario']
    correo = request.form['correo']
    contraseña = request.form['contraseña']
    
    
    if tipo_usuario == "socio":
        user = app.db.Socios.find_one({'correo': correo})
    
        # Verificar si el usuario fue encontrado
        if user is None:
            flash('No se encontro el socio, intente nuevamente', 'error')
            return redirect('/sesion')

        # Crear objeto Usuario
        socio = Socio(user)
        
        # Verificar si la contraseña es correcta
        if not socio.check_password(contraseña):
            flash('Contraseña incorrecta', 'error')
            return redirect('/sesion')
        else:
        # Si la contraseña es correcta iniciar secion
            status['secionIniciada'] = True
            status['idUsuario'] = user['idc']
            status['nombre'] = socio.nombre
            status['correo'] = socio.correo
            status['tipo'] = "socio"
            status['imagen'] = socio.imagen
            return redirect('/panelSocio')
        
    elif tipo_usuario == "usuario":
        user = app.db.Users.find_one({'correo': correo})
        
        if user is None:
            flash('No se encontro el usuario, intente nuevamente', 'error')
            return redirect('/sesion')

        # Crear objeto Usuario
        usuario = Usuario(user)
        
        # Verificar si la contraseña es correcta
        if not usuario.check_password(contraseña):
            flash('Contraseña incorrecta', 'error')
            return redirect('/sesion')
        else:
        # Si la contraseña es correcta iniciar secion
            status['secionIniciada'] = True
            status['idUsuario'] = user['idc']
            status['nombre'] = usuario.nombre
            status['correo'] = usuario.correo
            status['tipo'] = "usuario"
            status['imagen'] = usuario.imagen
            print(status['imagen'])
            return redirect('/')
        
@app.route('/cerrarSesion')
def cerrarSesion():
    global status
    status = {'secionIniciada' : False,
    'nombre' : "",
    "correo" : "",
    "tipo" : "",
    'pedidos' : 0,
    'idUsuario' : 0,
    'tipoUs' : "",
    'imagen': ""
    }
    return redirect('/')
        



if __name__ == '__main__':
    app.run(debug = True, port=5700)