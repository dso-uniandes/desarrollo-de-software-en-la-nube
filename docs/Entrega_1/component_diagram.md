# Diagrama de Componentes

El siguiente diagrama representa la arquitectura lógica del sistema **ANB Rising Stars Showcase**, mostrando la interacción entre los principales componentes del backend, el procesamiento asíncrono y la persistencia de datos.  

La aplicación sigue un enfoque **basado en microservicios y tareas distribuidas**, desplegada mediante **Docker Compose**.

---

## Descripción general de los componentes

| Componente | Tipo | Descripción |
|-------------|------|--------------|
| **Nginx (Proxy Inverso)** | Servidor web | Redirige las peticiones entrantes hacia la API, mejorando seguridad y rendimiento. |
| **storeapi (FastAPI)** | API REST | Gestiona usuarios, videos y votos; delega las tareas de procesamiento a través del broker de mensajería. |
| **Kafka (Broker de Mensajería)** | Middleware | Encapsula las tareas asíncronas en el tópico `video_tasks`, garantizando comunicación confiable entre API y Worker. |
| **Worker Consumer** | Servicio asíncrono | Procesa los videos (recorte, marca de agua, conversión) y actualiza los estados en la base de datos. |
| **PostgreSQL** | Base de datos | Almacena la información estructurada de usuarios, videos y votos. |
| **Almacenamiento de videos** | Sistema de archivos | Guarda los archivos originales (`/videos/uploaded`) y procesados (`/videos/processed`). |

---

## Diagrama de Componentes

<img width="3084" height="4340" alt="component_diagrama" src="https://github.com/user-attachments/assets/290675c4-7293-4c5a-9459-5928e2a79314" />
