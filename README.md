# Sistema de Alquiler de Autos

## Configuración del Entorno de Desarrollo

### Requisitos Previos
- Python 3.8 o superior
- MongoDB
- Git

### Configuración Inicial

1. Clonar el repositorio:
```bash
git clone <https://github.com/kevincj2415/Alquiler_Autos>
cd mi-alquiler-autos
```

2. Ejecutar el script de configuración:
```powershell
.\scripts\dev_setup.ps1
```

Este script realizará:
- Crear directorios necesarios
- Configurar entorno virtual
- Instalar dependencias
- Crear archivo .env
- Ejecutar pruebas iniciales

### Estructura del Proyecto
```
mi-alquiler-autos/
├── app.py              # Aplicación principal
├── config/             # Configuraciones
├── frontend/           # Archivos frontend
├── tests/              # Pruebas
├── logs/               # Archivos de log
├── scripts/            # Scripts de utilidad
├── manage.py           # Comandos de gestión
└── requirements.txt    # Dependencias
```

### Comandos Útiles

1. Iniciar servidor de desarrollo:
```bash
python app.py
```

2. Ejecutar pruebas:
```bash
python manage.py test
```

3. Verificar calidad del código:
```bash
python manage.py lint
```

4. Limpiar archivos temporales:
```bash
python manage.py clean
```

### Desarrollo

1. Siempre trabaja en el entorno virtual:
```bash
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

2. Instalar nuevas dependencias:
```bash
pip install <paquete>
pip freeze > requirements.txt
```

3. Antes de commit:
- Ejecutar pruebas
- Verificar código con flake8
- Actualizar documentación si es necesario

### Documentación
- [Documentación de Pruebas](documentacion_pruebas.md)
- [Documentación de Optimizaciones](documentacion_optimizacion.md)

### Contacto
Para dudas o sugerencias, contactar a:
- Kevin y Jairo
