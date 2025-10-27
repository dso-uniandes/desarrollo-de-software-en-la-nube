# Diagrama de Componentes

Este diagrama representa la arquitectura ajustada de la aplicación **ANB Rising Stars Showcase** desplegada en la nube pública de AWS.  
La solución distribuye los componentes en tres instancias EC2 y un servicio RDS, interconectados mediante NFS para compartir los archivos de video.

---

## Descripción general de los componentes

| Componente | Tipo | Descripción |
|-------------|------|-------------|
| **WebServer (EC2)** | Servidor de aplicación | Ejecuta **Nginx** (proxy inverso) y la **API FastAPI** (`storeapi`), expuesta al público. Se comunica con Kafka, RDS y el almacenamiento NFS. |
| **WorkerServer (EC2)** | Servidor de procesamiento | Ejecuta el servicio **Worker Consumer**, encargado de procesar videos y actualizar la base de datos. Se conecta al Broker Kafka, RDS y NFS. |
| **FileServer (EC2)** | Servidor NFS | Almacena los archivos de video originales y procesados (`/videos/uploaded`, `/videos/processed`). Está montado tanto en WebServer como en WorkerServer. |
| **Kafka (Broker de Mensajería)** | Middleware | Gestiona las tareas asíncronas del sistema (tópico `video_tasks`), permitiendo la comunicación entre FastAPI y Worker. |
| **Amazon RDS (PostgreSQL)** | Base de datos | Servicio gestionado de AWS que almacena información estructurada de usuarios, videos y votos. |
| **Jugador / Jurado** | Actores externos | Interactúan con la aplicación web para cargar, procesar y votar videos. |

---

## Flujo de comunicación

1. **Jugador/Jurado** envía peticiones HTTP a Nginx (WebServer).  
2. FastAPI encola tareas de procesamiento en **Kafka**.  
3. **Worker Consumer** (WorkerServer) consume las tareas y procesa los videos almacenados en NFS.  
4. El **Worker** actualiza los estados en **PostgreSQL (RDS)**.  
5. El **NFS** mantiene los archivos accesibles desde ambos servidores.

---

## Diagrama de Componentes

<img width="3204" height="3740" alt="Untitled Diagram drawio" src="https://github.com/user-attachments/assets/dd242582-a9c8-49c7-a81e-2123481ecba4" />
