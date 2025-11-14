# Diagrama de Componentes

Este diagrama muestra la arquitectura actualizada de la aplicación **ANB Rising Stars Showcase**, ya desplegada en **AWS**.  
En esta entrega se incorporaron mejoras importantes enfocadas en **escalabilidad**, **balanceo de carga** y **almacenamiento en la nube**, reemplazando el antiguo servidor NFS por **Amazon S3** y agregando **Auto Scaling Groups** tanto para la capa web como para la de workers.  
Además, se migró la mensajería a **Amazon SQS** con **DLQ** e integración de **CloudWatch Alarms** para tomar acciones sobre la salud y capacidad del sistema.

---

## ⚙️ Descripción general de los componentes

| Componente | Tipo | Descripción |
|-------------|------|-------------|
| **Application Load Balancer (ALB)** | Balanceador de carga | Punto de entrada público. Recibe todas las peticiones y las enruta al **Target Group (Web)**. Termina TLS y maneja tráfico HTTP/HTTPS. |
| **Target Group (Web)** | Grupo de destino | Agrupa las instancias sanas de la capa web y define health checks usados por el ALB y las alarmas. |
| **Auto Scaling Group (Web)** | Capa web escalable | Conjunto de instancias **EC2** que ejecutan la API `storeapi` (FastAPI). Escala en base a métricas (CPU, peticiones por target, errores 5xx) definidas en **CloudWatch Alarms**. Se crea a partir de un **Launch Template (Web)**. |
| **Auto Scaling Group (Workers)** | Capa de procesamiento | Grupo de instancias **EC2** que ejecutan los workers de procesamiento de video (FFmpeg). Escala por profundidad de cola y/o edad de mensajes en **SQS**. Se crea a partir de un **Launch Template (Workers)**. |
| **Amazon SQS (video-processing-queue)** | Cola de tareas | Recibe eventos de procesamiento emitidos por la API. Los workers consumen mensajes de aquí. |
| **Amazon SQS (DLQ)** | Cola de errores | Almacena mensajes que no pudieron ser procesados tras los reintentos, para análisis y reproceso seguro. |
| **Amazon S3 (Object Storage)** | Almacenamiento en la nube | Reemplaza el antiguo FileServer (NFS). Guarda los videos subidos y los procesados en carpetas separadas (`/videos/uploaded` y `/videos/processed`). Es accesible tanto desde la capa web como desde el Worker. |
| **Amazon RDS (PostgreSQL)** | Base de datos | Guarda toda la información estructurada del sistema: usuarios, videos, votos y estados de procesamiento. Es utilizada tanto por la API como por el Worker. |
| **Amazon CloudWatch + Alarms** | Monitoreo y alertas | Recopila métricas del ALB, Target Group, ASG y SQS. Dispara escalado en ambos ASG (Web/Workers) y envía alertas operativas. |
| **IAM Instance Profile (LabRole)** | Seguridad | Rol adjunto a instancias con permisos mínimos necesarios para acceder a **S3**, **SQS** y **RDS**. |
| **Jugador / Jurado** | Actores externos | Son los usuarios finales que interactúan con la app: suben videos, los ven y votan, a través del balanceador de carga. |

---

## 🔄 Flujo de comunicación

1. El **Jugador/Jurado** realiza solicitudes que ingresan por el **ALB** y se enrutan al **Target Group (Web)**.  
2. Las instancias del **ASG Web** (FastAPI) atienden la solicitud. Para subida de video: guardan el archivo en **S3** y publican un mensaje en **SQS (video-processing-queue)**.  
3. El **ASG de Workers** escala según la métrica de cola (mensajes en cola/edad de mensajes). Las instancias consumen mensajes de **SQS**, descargan el video desde **S3**, lo procesan con FFmpeg y suben el resultado a `processed/`.  
4. El estado del procesamiento se registra en **RDS** y se expone a la API para consulta.  
5. Si un mensaje falla repetidamente, se envía a **SQS DLQ** para diagnóstico y eventual reproceso.  
6. **CloudWatch** alimenta políticas de escalado y dispara **Alarms** para disponibilidad, errores y latencias.  
7. Los **IAM Instance Profiles** garantizan que cada instancia tenga exactamente los permisos necesarios (principio de mínimo privilegio).

---

## ⚡ Cambios frente a la entrega anterior

| Cambio | Descripción |
|--------|--------------|
| **ASG Web + Target Group** | La capa web corre en un Auto Scaling Group detrás de un Target Group con health checks, expuesto mediante **ALB**. |
| **ASG para Workers** | Los workers también escalan automáticamente con base en métricas de **SQS** (backlog/age). |
| **Kafka → Amazon SQS + DLQ** | Se reemplazó Kafka por **SQS**, incorporando una **Dead-Letter Queue** para resiliencia y observabilidad. |
| **NFS → S3** | Todo el almacenamiento de archivos se migró a **Amazon S3**, eliminando puntos únicos de falla. |
| **CloudWatch Alarms** | Alarmas para web y workers (CPU, 5xx, UnHealthyHosts, ApproximateNumberOfMessagesVisible, etc.) que gatillan escalado y alertas. |
| **Launch Templates + IAM Roles** | Plantillas de lanzamiento por grupo y roles con permisos mínimos para S3, SQS y RDS. |
| **Simplificación de instancias** | Las instancias web ejecutan **FastAPI con Uvicorn**; el proxy/terminación TLS está en el **ALB**. |

En resumen, la arquitectura evolucionó hacia un modelo **elástico, desacoplado y observable**, soportado íntegramente en servicios gestionados de AWS.  
Con **ALB, ASG (Web/Workers), SQS con DLQ, S3, RDS y CloudWatch**, el sistema soporta mayor concurrencia, reduce MTTR y elimina puntos únicos de falla.

---

## 🖼️ Diagrama de Componentes

<!-- Coloca el archivo del diagrama en la ruta indicada para que se renderice en el README/Docs -->
<img alt="entrega4-component-diagram" src="../../img/entrega4_component_diagram.png" />
