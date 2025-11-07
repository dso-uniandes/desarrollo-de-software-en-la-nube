 # Flujo de Procesos

El siguiente diagrama representa el flujo general de la aplicación **ANB Rising Stars Showcase** en la arquitectura actual desplegada en AWS.  
En esta versión se reemplazó el servidor NFS por **Amazon S3**, y la carga de trabajo de la API se distribuye a través del **Application Load Balancer (ALB)** y un **Auto Scaling Group** con instancias EC2.  
El procesamiento de los videos se sigue manejando de forma asíncrona por medio del **WorkerServer**, que consume tareas desde **Kafka**.

---

## ⚙️ Descripción del flujo

1. El **Jugador o Jurado** realiza una solicitud HTTP/HTTPS (por ejemplo, subir un video).  
2. El **ALB** recibe la petición y la dirige a una instancia disponible dentro del **Auto Scaling Group**, donde se ejecuta la API FastAPI (`storeapi`).  
3. La API guarda el video original en **Amazon S3** (carpeta `/videos/uploaded`) y crea una tarea en **Kafka** para que el Worker la procese.  
4. El **WorkerServer** toma la tarea desde Kafka, descarga el archivo de S3, aplica los pasos de procesamiento (recorte, marca de agua, etc.) y sube el resultado a **S3** (carpeta `/videos/processed`).  
5. El Worker actualiza el estado del video en la base de datos **Amazon RDS (PostgreSQL)**.  
6. **CloudWatch** monitorea las métricas del ALB y de las instancias EC2 para ajustar automáticamente la cantidad de servidores en el Auto Scaling Group según la demanda.

---

## 🧠 Beneficio del nuevo flujo

Este nuevo flujo elimina la dependencia del FileServer, reduce los puntos de falla y permite escalar dinámicamente la capa web, garantizando mejor desempeño incluso con muchos usuarios concurrentes.

---

## 📈 Diagrama del flujo de procesos

<img alt="flujo de procesos" src="https://github.com/user-attachments/assets/b4d18100-ce82-476a-83c2-7cf5a3b54e94" />
