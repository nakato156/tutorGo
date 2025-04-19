from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import py_eureka_client.eureka_client as eureka_client
from contextlib import asynccontextmanager

# Modelo
class Alumno(BaseModel):
    nombre: str
    correo: str
    contrasena: str

alumnos_registrados = []

@asynccontextmanager
async def lifespan(*args, **kwargs):
    # Esto se ejecuta al iniciar la app
    await eureka_client.stop_async()
    await eureka_client.init_async(
        eureka_server="http://localhost:8099/eureka",
        app_name="STUDENT-SERVICE",
        instance_port=8089,
    )
    yield
    

app = APIRouter(prefix="/api/student", lifespan=lifespan)

@app.post("/registrar")
def registrar_alumno(alumno: Alumno):
    if not alumno.nombre or not alumno.correo or not alumno.contrasena:
        return JSONResponse(
            content={
                "error": "Todos los campos son obligatorios"
            },
            status_code=400
        )
    
    if any(a["correo"] == alumno.correo for a in alumnos_registrados):
        return JSONResponse(
            content={
                "error": "El correo ya está registrado"
            },
            status_code=400
        )

    alumno_data = {
        "id": len(alumnos_registrados) + 1,
        "nombre": alumno.nombre,
        "correo": alumno.correo,
        "contrasena": alumno.contrasena
    }

    alumnos_registrados.append(alumno_data)
    return {"mensaje": "Alumno registrado exitosamente", "alumno": alumno_data}

@app.post("/login")
def login_alumno(alumno: Alumno):   
    alumno_encontrado = next((a for a in alumnos_registrados if a["correo"] == alumno.correo), None)

    if alumno_encontrado is None:
        return JSONResponse(
            content={
                "error": "Alumno no encontrado"
            },
            status_code=404
        )

    if alumno_encontrado["contrasena"] != alumno.contrasena:
        return JSONResponse(
            content={
                "error": "Contraseña incorrecta"
            },
            status_code=401
        )

    return {"mensaje": "Login exitoso", "alumno": alumno_encontrado}