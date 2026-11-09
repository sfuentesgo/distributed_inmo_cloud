# CompuVivienda - Arquitectura Distribuida entre Hilos y Nodos

Mini proyecto correspondiente a la **Unidad 2: Patrones de diseño y arquitectura** (Actividad 4: *Tejiendo redes: Arquitectura de software entre hilos y nodos*).

## 1. Descripción del Sistema
Evolución de la plataforma CompuVivienda hacia un esquema de arquitectura distribuida para la ingesta y procesamiento asíncrono de publicaciones inmobiliarias con alta carga multimedia. El sistema desacopla la recepción HTTP, la gestión de colas en red y el procesamiento paralelo mediante grupos de hilos de trabajo (*worker pools*).

## 2. Topología de Nodos y Red
El sistema opera sobre tres nodos desacoplados conectados en una red interna privada (`red_distribuida`):
- **Nodo 1: API Gateway (`gateway`):** Servidor HTTP perimetral desarrollado en FastAPI/Uvicorn. Recibe peticiones de los clientes, responde con código `202 Accepted` de forma no bloqueante y deposita tareas en el broker.
- **Nodo 2: Message Broker (`broker`):** Instancia de Redis actuando como cola de mensajería distribuida (`cola_inmuebles_multimedia`).
- **Nodo 3: Worker Service (`worker`):** Servicio consumidor que extrae tareas del broker y ejecuta el procesamiento pesado simulado de imágenes mediante un grupo de hilos concurrentes (`ThreadPoolExecutor`).

## 3. Patrones de Diseño y Arquitectura Aplicados
1. **Asynchronous Request-Reply:** La API responde de inmediato al cliente mientras la tarea pesada se procesa en segundo plano.
2. **Competing Consumers / Queue-Based Load Leveling:** Desacopla la tasa de entrada de peticiones respecto a la velocidad de procesamiento de los workers.
3. **Thread Pool (Worker Pool):** Gestión controlada de hilos concurrentes en el nodo de procesamiento para optimizar el uso de CPU y memoria.

## 4. Instrucciones de Ejecución

### Requisitos
- Docker y Docker Compose
- Python 3.10+ (para lanzar el script de pruebas)

### Paso a paso

1. Construir y levantar la red de contenedores:
   `docker compose up --build`

2. Verificar el estado del Gateway en el navegador o consola:
   `curl http://localhost:8000/`

3. Ejecutar la prueba de concurrencia y métricas en otra terminal:
   `pip install requests`
   `python tests/load_test.py`

## 5. Simulación de Cuello de Botella y Mejora Arquitectónica
- **Escenario 1 (Cuello de Botella):** El worker se inicia con `WORKER_THREADS=1`. Las tareas se encolan secuencialmente generando retraso acumulado en el vaciado de la cola.
- **Escenario 2 (Optimización Concurrente):** Se ajusta la variable de entorno a `WORKER_THREADS=4` en `docker-compose.yml`. Las tareas se reparten entre múltiples hilos en paralelo, reduciendo drásticamente el tiempo total de procesamiento.