from flask import Flask, jsonify, render_template, request, redirect, url_for, flash,session, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from flask_mail import Mail, Message
from flask_migrate import Migrate
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from Usuario import Usuario
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
    'idOrga' : "",
    'tipoUs' : ""
    }

app = Flask(__name__, template_folder='frontend/templates', static_folder='frontend/static')

cliente = MongoClient("mongodb+srv://kevincj2415:e2BhakVv76vBMD7f@cluster0.hb2dv.mongodb.net/")
app.db = cliente.test

app.jinja_env.globals.update(generar_codigo_seguro=generar_codigo_seguro)


@app.route('/')
def inicio():
    return render_template('sitio/Inicio.html')

@app.route('/sesion')
def session():
    return render_template('sitio/inicio_sesion.html') 

@app.route('/contraseñaErrada')
def contraseñaErrada():
    return render_template('sitio/contraseñaErrada.html')

@app.route('/correoErrado')
def correoErrado():
    return render_template('sitio/correoErrado.html')

@app.route('/registrarUsuario')
def registroUsuario():
    return render_template('sitio/RegistroUsuario.html')

@app.route('/sitio/registrarUsuario', methods = ['POST'])
def registrarUsuario():
    nombre = request.form['nombre']
    correo = request.form['correo']
    contraseña = request.form['contraseña']
    tipo = request.form['tipo']
    pedidos = 0
    usuario = {'nombre':nombre, 'correo':correo, 'contraseña':contraseña, 'tipo':tipo, 'pedidos':pedidos}
    usuario = Usuario(usuario)
    usuario.set_password(contraseña)
    idc = generar_codigo_seguro()
    idOrga = status['idOrga']
    data = {'idc':idc, 'idOrga':idOrga, 'stockMin':0, 'stockMax':1000, 'email':"", 'sms':0, 'reabastecimiento':"Deshabilitado"}
    app.db.configuracion.insert_one(data)
    return redirect('/inicioSesion')
    
@app.route('/sitio/iniciarSesion', methods = ['POST'])
def iniciarSesion():
    global status
    correo = request.form['email']
    contraseña = request.form['password']
    user = app.db.Usuarios.find_one({'idCreador': status['idUsuario']})
    
    # Verificar si el usuario fue encontrado
    if user is None:
        return redirect('/correoErrado')

    # Crear objeto Usuario
    usuario = Usuario(user)
    
    # Verificar si la contraseña es correcta
    if not usuario.check_password(contraseña):
        return redirect('/contraseñaErrada')
    else:
    # Si la contraseña es correcta iniciar secion
        status['secionIniciada'] = True
        status['idUsuario'] = user['ID']
        status['nombre'] = usuario.nombre
        status['correo'] = usuario.correo
        status['tipo'] = usuario.tipo
        status['pedidos'] = usuario.pedidos
        com = app.db.Comunidad.find_one({'idCreador': status['idUsuario']})
        if com != None:
            status['idOrga'] = com['ido']
        else:
            status['idOrga'] = ''
        print(status['idOrga'])
        return redirect('/inventario')



if __name__ == '__main__':
    app.run(debug = True, port=5700)