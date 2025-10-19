# Despliegue e Infraestructura

Este documento describe la infraestructura de despliegue de la aplicación **ANB Rising Stars Showcase**, implementada con **Docker Compose** para garantizar portabilidad, consistencia y facilidad de replicación en distintos entornos.

---

## Infraestructura general

El sistema se compone de múltiples servicios que trabajan de forma orquestada para habilitar el flujo completo de la aplicación: autenticación, carga de videos, procesamiento asíncrono, almacenamiento y exposición pública.

### Servicios principales

| Servicio | Imagen / Dockerfile | Rol principal | Dependencias |
|-----------|---------------------|----------------|---------------|
| **storeapi** | `api.Dockerfile` | Backend principal basado en FastAPI. Expone la API REST, maneja autenticación y encola tareas. | Kafka, PostgreSQL |
| **worker** | `worker.Dockerfile` | Servicio asíncrono que procesa videos (recorte, marca de agua, resolución). | Kafka, PostgreSQL |
| **db** | `postgres:15` | Base de datos relacional para almacenar usuarios, videos y votos. | — |
| **kafka** | `bitnamilegacy/kafka:4.0.0` | Broker de mensajería que gestiona las tareas en el tópico `video_tasks`. | — |
| **nginx** | `nginx:latest` | Proxy inverso que recibe las peticiones HTTP y las redirige al backend. | storeapi |


---

### Configuración de entorno

La configuración del entorno del proyecto se documentó en el archivo `README.md`, donde se especifican detalladamente las variables necesarias para ejecutar la aplicación en local mediante Docker Compose. 
En dicho archivo se incluyen instrucciones explícitas para crear el archivo `.env` en la raíz del proyecto, junto con los pasos a seguir, ejemplos de contenido y la documentación de cada variable requerida.