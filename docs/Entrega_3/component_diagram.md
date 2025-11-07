# Diagrama de Componentes

Este diagrama muestra la arquitectura actualizada de la aplicación **ANB Rising Stars Showcase**, ya desplegada en **AWS**.  
En esta entrega se incorporaron mejoras importantes enfocadas en **escalabilidad**, **balanceo de carga** y **almacenamiento en la nube**, reemplazando el antiguo servidor NFS por **Amazon S3** y agregando un **Auto Scaling Group** con balanceador para la capa web.

---

## ⚙️ Descripción general de los componentes

| Componente | Tipo | Descripción |
|-------------|------|-------------|
| **Application Load Balancer (ALB)** | Balanceador de carga | Es el punto de entrada de la aplicación. Recibe todas las peticiones y las reparte entre las instancias del grupo de Auto Scaling. Maneja el tráfico HTTP/HTTPS. |
| **Auto Scaling Group (Web Layer)** | Capa web escalable | Contiene las instancias **EC2** donde corre la API `storeapi` (FastAPI). Puede aumentar o disminuir el número de instancias automáticamente según la carga del sistema. Cada instancia se comunica con **S3** y **RDS**. |
| **WorkerServer (EC2)** | Procesamiento de videos | Ejecuta el **Worker Consumer**, encargado de procesar los videos subidos por los usuarios. Obtiene las tareas desde **Kafka**, descarga los videos desde **S3**, los procesa y sube el resultado procesado al mismo bucket. |
| **Amazon S3 (Object Storage)** | Almacenamiento en la nube | Reemplaza el antiguo FileServer (NFS). Guarda los videos subidos y los procesados en carpetas separadas (`/videos/uploaded` y `/videos/processed`). Es accesible tanto desde la capa web como desde el Worker. |
| **Kafka (Broker de Mensajería)** | Cola de tareas | Se encarga de manejar la comunicación asíncrona entre la API y el Worker. Permite que las tareas se ejecuten en segundo plano sin afectar el rendimiento del sistema. |
| **Amazon RDS (PostgreSQL)** | Base de datos | Guarda toda la información estructurada del sistema: usuarios, videos, votos y estados de procesamiento. Es utilizada tanto por la API como por el Worker. |
| **Amazon CloudWatch** | Monitoreo | Se encarga de recopilar métricas del ALB y las instancias EC2. Con esas métricas se activan las políticas de autoescalado cuando aumenta el tráfico o la carga de CPU. |
| **Jugador / Jurado** | Actores externos | Son los usuarios finales que interactúan con la app: suben videos, los ven y votan, a través del balanceador de carga. |

---

## 🔄 Flujo de comunicación

1. El **Jugador o Jurado** accede a la aplicación desde el navegador y sus peticiones llegan al **Application Load Balancer (ALB)**.  
2. El **ALB** distribuye las solicitudes entre las instancias del **Auto Scaling Group**, donde corre la API FastAPI (`storeapi`).  
3. Cuando se sube un video, la API lo guarda en **S3** y crea una tarea en **Kafka** para que el **Worker** la procese.  
4. El **WorkerServer** descarga el video original desde **S3**, aplica los procesos (recorte, marca de agua, etc.) y vuelve a subir el video procesado a la carpeta correspondiente.  
5. Luego el **Worker** actualiza en **RDS** el estado del video a “procesado”.  
6. **CloudWatch** monitorea constantemente las métricas de las instancias y del ALB, y si detecta un aumento de carga, dispara el **autoescalado** para añadir más instancias.  

---

## ⚡ Cambios frente a la entrega anterior

| Cambio | Descripción |
|--------|--------------|
| **Escalabilidad automática (Auto Scaling Group)** | Se reemplazó el único servidor web por un grupo de instancias que se escalan automáticamente según el tráfico. |
| **Balanceador de carga (ALB)** | Se agregó un **Application Load Balancer** para manejar las conexiones externas y distribuir las peticiones, eliminando la necesidad de usar Nginx dentro de las instancias. |
| **Migración de NFS a S3** | Se eliminó el FileServer y se migró todo el almacenamiento de archivos a **Amazon S3**, lo que mejora la disponibilidad y evita depender de una sola máquina. |
| **Monitoreo con CloudWatch** | Se integró **Amazon CloudWatch** para registrar métricas de rendimiento y activar automáticamente el escalado de las instancias. |
| **Simplificación del WebServer** | Ahora las instancias del Auto Scaling Group ejecutan únicamente **FastAPI con Uvicorn**, ya que el ALB actúa como proxy inverso. |

En resumen, la arquitectura pasó de un despliegue estático a uno totalmente **escalable y desacoplado**, soportado en servicios gestionados de AWS.  
Con el uso de **S3, ALB y Auto Scaling**, el sistema ahora puede manejar más usuarios concurrentes, mantener buen rendimiento y reducir los puntos únicos de falla.

---

## 🖼️ Diagrama de Componentes

<img alt="diagrama-componentes" src="https://github.com/user-attachments/assets/e792b527-e5f6-4a9f-b23a-f15709849fa0" />
