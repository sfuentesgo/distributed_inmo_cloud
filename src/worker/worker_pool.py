import os
import time
import json
import redis
from concurrent.futures import ThreadPoolExecutor

# Configuración de red para conectarse al mismo Broker
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
QUEUE_NAME = "cola_inmuebles_multimedia"

# Cantidad de hilos de trabajo configurables
# (Iniciaremos con 1 para generar el cuello de botella y luego aumentaremos a 4 para la mejora)
NUM_THREADS = int(os.getenv("WORKER_THREADS", "1"))

# Conexión al nodo de mensajería (Broker)
broker_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def procesar_inmueble_pesado(datos_tarea: dict):
    """
    Función que ejecuta cada hilo individual: simula el trabajo pesado
    de procesar, redimensionar fotos y guardar en base de datos.
    """
    id_inmueble = datos_tarea.get("id_inmueble")
    titulo = datos_tarea.get("titulo")
    imagenes = datos_tarea.get("imagenes", [])
    
    tiempo_inicio = time.time()
    hora_actual = time.strftime('%H:%M:%S')
    
    print(f"[{hora_actual}] [Hilo en ejecución] Procesando fotos de inmueble #{id_inmueble}: '{titulo}' ({len(imagenes)} imágenes)...")
    
    # Simulación de retardo por procesamiento intensivo (1.5 segundos por publicación)
    time.sleep(1.5)
    
    duracion = round(time.time() - tiempo_inicio, 2)
    hora_fin = time.strftime('%H:%M:%S')
    print(f"[{hora_fin}] [Hilo completado] Inmueble #{id_inmueble} procesado exitosamente en {duracion} segundos.\n")

def iniciar_nodo_worker():
    """
    Ciclo principal del Nodo Worker: escucha la cola de mensajes
    y reparte el trabajo entre su grupo (pool) de hilos.
    """
    print(f"============================================================")
    print(f"   NODO WORKER INICIADO | Pool de Hilos configurado: {NUM_THREADS}")
    print(f"   Escuchando eventos en la cola '{QUEUE_NAME}'...")
    print(f"============================================================\n")
    
    # ThreadPoolExecutor administra los hilos en paralelo
    with ThreadPoolExecutor(max_workers=NUM_THREADS) as pool_hilos:
        while True:
            # blpop espera pacientemente a que llegue una tarea a la cola de Redis
            tarea_recibida = broker_client.blpop(QUEUE_NAME, timeout=5)
            
            if tarea_recibida:
                _, contenido_json = tarea_recibida
                datos_tarea = json.loads(contenido_json)
                
                # Asigna la tarea a un hilo disponible sin congelar el ciclo
                pool_hilos.submit(procesar_inmueble_pesado, datos_tarea)

if __name__ == "__main__":
    iniciar_nodo_worker()