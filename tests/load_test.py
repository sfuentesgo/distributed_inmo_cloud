import time
import requests
from concurrent.futures import ThreadPoolExecutor

GATEWAY_URL = "http://localhost:8000/inmuebles/publicar"
TOTAL_PETICIONES = 20
HILOS_SIMULACION = 5  # 5 usuarios concurrentes enviando solicitudes

def enviar_publicacion(id_simulada: int):
    payload = {
        "id_inmueble": 100 + id_simulada,
        "titulo": f"Apartamento en Chapinero #{100 + id_simulada}",
        "ciudad": "Bogotá",
        "precio": 450000000.0,
        "imagenes": [
            f"https://storage.compuvivienda.com/img{id_simulada}_1.jpg",
            f"https://storage.compuvivienda.com/img{id_simulada}_2.jpg",
            f"https://storage.compuvivienda.com/img{id_simulada}_3.jpg"
        ]
    }
    
    inicio = time.time()
    try:
        respuesta = requests.post(GATEWAY_URL, json=payload, timeout=10)
        latencia = round((time.time() - inicio) * 1000, 2)  # Latencia en milisegundos
        return {
            "id": id_simulada,
            "status_code": respuesta.status_code,
            "latencia_ms": latencia,
            "exito": respuesta.status_code == 202
        }
    except Exception as error:
        latencia = round((time.time() - inicio) * 1000, 2)
        return {
            "id": id_simulada,
            "status_code": 500,
            "latencia_ms": latencia,
            "exito": False,
            "error": str(error)
        }

def ejecutar_prueba():
    print("============================================================")
    print(f" INICIANDO PRUEBA DE CONCURRENCIA - COMPUVIVIENDA DISTRIBUIDO")
    print(f" Peticiones totales: {TOTAL_PETICIONES} | Usuarios concurrentes: {HILOS_SIMULACION}")
    print("============================================================\n")
    
    tiempo_inicio_total = time.time()
    resultados = []
    
    # Lanzar las peticiones en paralelo simulando usuarios concurrentes
    with ThreadPoolExecutor(max_workers=HILOS_SIMULACION) as ejecutor:
        futuros = [ejecutor.submit(enviar_publicacion, i) for i in range(1, TOTAL_PETICIONES + 1)]
        for futuro in futuros:
            resultados.append(futuro.result())
            
    tiempo_total = round(time.time() - tiempo_inicio_total, 2)
    
    exitosas = sum(1 for r in resultados if r["exito"])
    latencias = [r["latencia_ms"] for r in resultados]
    latencia_promedio = round(sum(latencias) / len(latencias), 2)
    latencia_minima = min(latencias)
    latencia_maxima = max(latencias)
    
    print("\n------------------ RESUMEN DE RESULTADOS ------------------")
    print(f"Peticiones procesadas exitosamente por Gateway: {exitosas}/{TOTAL_PETICIONES}")
    print(f"Tiempo total de ingesta HTTP: {tiempo_total} segundos")
    print(f"Latencia promedio por cliente: {latencia_promedio} ms")
    print(f"Latencia mínima: {latencia_minima} ms | Máxima: {latencia_maxima} ms")
    print("-----------------------------------------------------------\n")

if __name__ == "__main__":
    ejecutar_prueba()