import os
import time
import json
import redis
from concurrent.futures import ThreadPoolExecutor

# Configuración de red para conectarse al Broker
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
QUEUE_NAME = "cola_inmuebles_multimedia"

# Cantidad de hilos de trabajo configurables
NUM_THREADS = int(os.getenv("WORKER_THREADS", "1"))

# Conexión al nodo de mensajería (Broker) con timeout extendido
broker_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True,
    socket_timeout=10,
    socket_connect_timeout=10
)

def procesar_inmueble_pesado(datos_tarea: dict):
    """
    Función que ejecuta cada hilo individual: simula el trabajo pesado
    de procesar y redimensionar fotos.
    """
    id_inmueble = datos_tarea.get("id_inmueble")
    titulo = datos_tarea.get("titulo")
    imagenes = datos_tarea.get("imagenes", [])
    
    tiempo_inicio = time.time()
    hora_actual = time.strftime('%H:%M:%S')
    
    print(f"[{hora_actual}] [Hilo en ejecución] Procesando fotos de inmueble #{id_inmueble}: '{titulo}' ({len(imagenes)} imágenes)...", flush=True)
    
    # Simulación de retardo por procesamiento intensivo (1.5 segundos por publicación)
    time.sleep(1.5)
    
    duracion = round(time.time() - tiempo_inicio, 2)
    hora_fin = time.strftime('%H:%M:%S')
    print(f"[{hora_fin}] [Hilo completado] Inmueble #{id_inmueble} procesado exitosamente en {duracion} segundos.\n", flush=True)

def iniciar_nodo_worker():
    """
    Ciclo principal del Nodo Worker: escucha la cola de mensajes
    y reparte el trabajo entre su grupo (pool) de hilos.
    """
    print("============================================================", flush=True)
    print(f"   NODO WORKER INICIADO | Pool de Hilos configurado: {NUM_THREADS}", flush=True)
    print(f"   Escuchando eventos en la cola '{QUEUE_NAME}'...", flush=True)
    print("============================================================\n", flush=True)
    
    with ThreadPoolExecutor(max_workers=NUM_THREADS) as pool_hilos:
        while True:
            try:
                # timeout=0 bloquea de forma limpia e indefinida hasta que entre un mensaje
                tarea_recibida = broker_client.blpop(QUEUE_NAME, timeout=0)
                
                if tarea_recibida:
                    _, contenido_json = tarea_recibida
                    datos_tarea = json.loads(contenido_json)
                    pool_hilos.submit(procesar_inmueble_pesado, datos_tarea)
            except (redis.exceptions.TimeoutError, redis.exceptions.ConnectionError):
                time.sleep(1)
                continue
            except Exception as e:
                print(f"[Error en Worker] {str(e)}", flush=True)
                time.sleep(1)

if __name__ == "__main__":
    iniciar_nodo_worker()