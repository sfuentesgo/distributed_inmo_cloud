import os
import json
import redis
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="CompuVivienda Distributed Gateway",
    description="Nodo de ingesta perimetral y desacoplamiento asíncrono",
    version="2.0.0"
)

# Configuración de variables de entorno para comunicación en red entre nodos
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
QUEUE_NAME = "cola_inmuebles_multimedia"

# Cliente de conexión al nodo de mensajería (Broker)
broker_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# Modelo de validación de datos de entrada
class PublicacionInmueble(BaseModel):
    id_inmueble: int
    titulo: str
    ciudad: str
    precio: float
    imagenes: list[str]

@app.get("/")
def estado_nodo():
    return {
        "nodo": "API Gateway (Nodo 1)",
        "estado": "Activo",
        "broker_conectado": f"{REDIS_HOST}:{REDIS_PORT}"
    }

@app.post("/inmuebles/publicar", status_code=202)
def encolar_publicacion(inmueble: PublicacionInmueble):
    """
    Recibe la petición del cliente y la encola de inmediato en el Broker,
    retornando código HTTP 202 Accepted sin bloquear el hilo web.
    """
    try:
        payload = inmueble.model_dump()
        # Encolar la tarea en Redis (RPUSH añade al final de la cola)
        broker_client.rpush(QUEUE_NAME, json.dumps(payload))
        
        return {
            "mensaje": "Publicación recibida y encolada con éxito para procesamiento distribuido",
            "id_inmueble": inmueble.id_inmueble,
            "estado": "En cola de espera",
            "nodo_receptor": "Gateway"
        }
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Fallo de comunicación con el nodo Broker: {str(error)}"
        )