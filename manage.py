#!/usr/bin/env python
"""Script para gestionar el entorno de desarrollo"""
import click
import os
import sys
from flask.cli import FlaskGroup
from app import app

def create_app():
    return app

cli = FlaskGroup(create_app=create_app)

@cli.command()
def test():
    """Ejecutar pruebas unitarias"""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

@cli.command()
def create_db():
    """Crear índices y configuraciones iniciales de la base de datos"""
    from app import app
    with app.app_context():
        # Crear índices
        app.db.Users.create_index('correo', unique=True)
        app.db.Users.create_index('idc', unique=True)
        app.db.Socios.create_index('correo', unique=True)
        app.db.Socios.create_index('idc', unique=True)
        app.db.Socios.create_index('numero_documento', unique=True)
        click.echo('Índices creados correctamente')

@cli.command()
def lint():
    """Ejecutar revisión de código con flake8"""
    click.echo('Ejecutando flake8...')
    os.system('flake8 .')

@cli.command()
def clean():
    """Limpiar archivos temporales y caché"""
    click.echo('Limpiando archivos temporales...')
    os.system('find . -type f -name "*.pyc" -delete')
    os.system('find . -type d -name "__pycache__" -delete')
    os.system('find . -type d -name ".pytest_cache" -delete')

if __name__ == '__main__':
    cli()
