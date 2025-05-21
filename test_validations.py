import requests
import json

BASE_URL = "http://localhost:5700"

def test_password_mismatch():
    data = {
        "tipo_usuario": "usuario",
        "nombre": "Test User",
        "correo": "test@example.com",
        "contraseña1": "test123",
        "contraseña2": "test456"
    }
    response = requests.post(f"{BASE_URL}/sitio/registrarUsuario", data=data)
    print("Test 1 - Contraseñas diferentes:")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}\n")

def test_duplicate_email():
    # Primer registro
    data = {
        "tipo_usuario": "usuario",
        "nombre": "Test User",
        "correo": "duplicate@example.com",
        "contraseña1": "test123",
        "contraseña2": "test123"
    }
    response1 = requests.post(f"{BASE_URL}/sitio/registrarUsuario", data=data)
    print("Test 2.1 - Primer registro con email:")
    print(f"Status Code: {response1.status_code}")
    print(f"Response: {response1.text}\n")
    
    # Intento duplicado
    response2 = requests.post(f"{BASE_URL}/sitio/registrarUsuario", data=data)
    print("Test 2.2 - Intento de registro con email duplicado:")
    print(f"Status Code: {response2.status_code}")
    print(f"Response: {response2.text}\n")

def test_duplicate_document():
    # Primer registro de socio
    data = {
        "tipo_usuario": "socio",
        "nombre": "Test Socio",
        "correo": "socio@example.com",
        "contraseña1": "test123",
        "contraseña2": "test123",
        "tipo_documento": "cc",
        "numero_documento": "123456789",
        "direccion": "Test Address"
    }
    response1 = requests.post(f"{BASE_URL}/sitio/registrarUsuario", data=data)
    print("Test 3.1 - Primer registro de socio:")
    print(f"Status Code: {response1.status_code}")
    print(f"Response: {response1.text}\n")
    
    # Intento con documento duplicado
    data["correo"] = "otro@example.com"  # Cambiamos el correo pero mantenemos el mismo documento
    response2 = requests.post(f"{BASE_URL}/sitio/registrarUsuario", data=data)
    print("Test 3.2 - Intento de registro con documento duplicado:")
    print(f"Status Code: {response2.status_code}")
    print(f"Response: {response2.text}\n")

if __name__ == "__main__":
    print("Iniciando pruebas de validación...\n")
    test_password_mismatch()
    test_duplicate_email()
    test_duplicate_document()
    print("Pruebas completadas.")
