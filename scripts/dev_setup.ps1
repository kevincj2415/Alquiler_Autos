# Script de configuración del entorno de desarrollo
Write-Host "Configurando entorno de desarrollo..." -ForegroundColor Green

# Crear directorios necesarios
$directories = @(
    "logs",
    "frontend/static/uploads/cars",
    "tests/integration",
    "tests/unit"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force
        Write-Host "Creado directorio: $dir" -ForegroundColor Yellow
    }
}

# Verificar entorno virtual
if (-not (Test-Path ".venv")) {
    Write-Host "Creando entorno virtual..." -ForegroundColor Yellow
    python -m venv .venv
    Write-Host "Entorno virtual creado" -ForegroundColor Green
}

# Activar entorno virtual
Write-Host "Activando entorno virtual..." -ForegroundColor Yellow
.\.venv\Scripts\Activate

# Instalar dependencias
Write-Host "Instalando dependencias..." -ForegroundColor Yellow
pip install -r requirements.txt

# Crear archivo .env si no existe
if (-not (Test-Path ".env")) {
    Write-Host "Creando archivo .env..." -ForegroundColor Yellow
    @"
# Configuración del entorno
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=dev_secret_key_change_this_in_production
MONGODB_URI=mongodb+srv://kevincj2415:e2BhakVv76vBMD7f@cluster0.hb2dv.mongodb.net/alquiler_coches

# Configuración de caché
CACHE_TYPE=simple
CACHE_DEFAULT_TIMEOUT=300

# Configuración de logging
LOG_LEVEL=DEBUG
"@ | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "Archivo .env creado" -ForegroundColor Green
}

# Ejecutar pruebas
Write-Host "Ejecutando pruebas..." -ForegroundColor Yellow
python manage.py test

# Verificar calidad del código
Write-Host "Verificando calidad del código..." -ForegroundColor Yellow
python manage.py lint

Write-Host "¡Configuración completada!" -ForegroundColor Green
Write-Host @"

Para iniciar el servidor de desarrollo:
1. Asegúrate de estar en el entorno virtual (.venv)
2. Ejecuta: python app.py

Para ejecutar pruebas:
- python manage.py test

Para verificar el código:
- python manage.py lint

Para limpiar archivos temporales:
- python manage.py clean

"@ -ForegroundColor Cyan
