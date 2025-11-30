# Diagrama de Componentes

Este diagrama muestra la arquitectura actualizada de la aplicación **ANB Rising Stars Showcase**, ahora desplegada en **AWS** sobre un modelo **PaaS / serverless**.  
En esta entrega se reemplazaron el **Application Load Balancer (ALB)**, los **Auto Scaling Groups** y las instancias **EC2** por funciones **AWS Lambda** orquestadas a través de **API Gateway** y **Amazon SQS**, manteniendo **Amazon S3** como almacenamiento de objetos y **Amazon RDS (PostgreSQL)** como base de datos relacional.  
El objetivo principal es reducir la carga operativa de administración de servidores y aprovechar el escalado automático administrado por la plataforma.

---

## ⚙️ Descripción general de los componentes

| Componente | Tipo | Descripción |
|-----------|------|-------------|
| **AWS API Gateway** | Gateway HTTP administrado | Punto de entrada público. Recibe todas las peticiones HTTP/HTTPS y las enruta hacia las funciones **AWS Lambda Web**. Gestiona rutas, validación básica y límites de tasa. |
| **AWS Lambda Web** | Capa web serverless | Conjunto de funciones Lambda donde se ejecuta la API `storeapi` (FastAPI). Atiende los endpoints de autenticación, gestión de videos, consulta y votación. Genera URLs prefirmadas para carga de videos en S3 y publica mensajes en **SQS** para el procesamiento asíncrono. |
| **AWS Lambda Worker** | Capa de procesamiento serverless | Funciones Lambda disparadas por **Amazon SQS**. Consumen mensajes de la cola, descargan el video desde **S3**, ejecutan el pipeline de procesamiento (recorte, resolución, marca de agua, eliminación de audio), suben el video procesado a S3 y actualizan el estado en **RDS**. |
| **Amazon SQS (video-processing-queue)** | Cola de tareas | Recibe las solicitudes de procesamiento de video que envía la capa web (Lambda Web). Desacopla completamente la recepción de la carga de usuarios del procesamiento en segundo plano. |
| **Amazon SQS (DLQ)** | Cola de errores | Almacena mensajes que no pudieron ser procesados exitosamente tras los reintentos configurados. Permite inspeccionar y reprocesar casos problemáticos sin bloquear la cola principal. |
| **Amazon S3 (Object Storage)** | Almacenamiento en la nube | Almacena los videos originales y los videos procesados, en prefijos separados como `/videos/uploaded` y `/videos/processed`. Es accedido tanto por la capa web (para generar presigned URLs) como por la capa worker durante el procesamiento. |
| **Amazon RDS (PostgreSQL)** | Base de datos relacional | Almacena la información estructurada del sistema: usuarios, videos, votos y estados de procesamiento. Es consumida por **Lambda Web** (para exponer datos a la API) y por **Lambda Worker** (para actualizar estados de los videos). |
| **Amazon CloudWatch + Alarms** | Monitoreo y observabilidad | Centraliza métricas e indicadores de **Lambda**, **API Gateway**, **SQS** y **RDS**. Permite crear alarmas sobre errores, tiempos de respuesta, tamaño de cola y concurrencia, facilitando la operación del sistema. |
| **IAM Role (LabRole / Roles para Lambda)** | Seguridad | Conjunto de roles y policies que otorgan a las funciones Lambda y servicios involucrados permisos mínimos para acceder a **S3**, **SQS** y **RDS**, siguiendo el principio de mínimo privilegio. |
| **Jugador / Jurado** | Actores externos | Usuarios finales de la plataforma que interactúan con la aplicación para registrarse, subir videos, visualizarlos y votar, consumiendo la API a través de **API Gateway**. |

---

## 🔄 Flujo de comunicación

1. El **Jugador/Jurado** realiza una solicitud HTTP hacia la API (por ejemplo, carga de video, consulta de rankings o emisión de voto), que ingresa por **AWS API Gateway**.  
2. **API Gateway** enruta la solicitud a la función correspondiente en **AWS Lambda Web**, de acuerdo con el endpoint definido (e.g. `/api/videos/upload`, `/api/public/rankings`).  
3. Para la carga de videos, la función **Lambda Web**:
   - Valida la autenticación y los parámetros de la solicitud.  
   - Registra o actualiza la metadata del video en **Amazon RDS**.  
   - Genera una **URL prefirmada de S3** para que el cliente suba el archivo directamente al bucket.  
   - Publica un mensaje en **Amazon SQS (video-processing-queue)** indicando el identificador del video y la ubicación en S3.  
4. Cuando hay mensajes disponibles en la cola, **Amazon SQS** dispara la ejecución de **AWS Lambda Worker**, que:
   - Lee el mensaje y obtiene la referencia al archivo de entrada en **S3**.  
   - Descarga el video, ejecuta el procesamiento (recorte a 30s, ajuste de resolución, marca de agua, eliminación de audio, etc.).  
   - Sube el video procesado a la carpeta correspondiente en **S3** (por ejemplo, `/videos/processed`).  
   - Actualiza el estado del video en **RDS** de `uploaded` a `processed`.  
5. Si una tarea de procesamiento falla repetidamente, el mensaje es redirigido a **Amazon SQS (DLQ)** para análisis posterior, sin afectar el flujo normal de la cola principal.  
6. **CloudWatch** recopila métricas de **Lambda**, **API Gateway**, **SQS** y **RDS**, permitiendo configurar alarmas sobre errores, latencias, concurrencia y tamaño de las colas para soporte operativo y capacidad.  
7. Los usuarios consultan nuevamente la API (vía API Gateway → Lambda Web) para obtener el listado de sus videos, los detalles de procesamiento o el ranking actualizado, apoyándose en la información almacenada en **RDS** y los objetos en **S3**.

---

## ⚡ Cambios frente a la entrega anterior

| Cambio | Descripción |
|--------|-------------|
| **EC2 + ALB → API Gateway + Lambda** | Se eliminaron las instancias EC2, el Application Load Balancer y los Auto Scaling Groups. La capa web ahora corre completamente en **AWS Lambda**, expuesta mediante **API Gateway**, con escalamiento administrado por la plataforma. |
| **Workers EC2 → Lambda Worker** | Los workers de procesamiento ya no se ejecutan en EC2. Las tareas ahora son manejadas por funciones **AWS Lambda Worker** disparadas por eventos de **SQS**, simplificando la configuración de escalamiento y mantenimiento. |
| **Autoscaling manual → Concurrencia administrada** | Se reemplazan las políticas explícitas de Auto Scaling por el modelo de **concurrencia automática de Lambda**, donde el proveedor escala horizontalmente el número de ejecuciones concurrentes según la demanda. |
| **Arquitectura 100% PaaS** | La solución deja de depender de servidores gestionados por el equipo y se apoya en servicios administrados (Lambda, API Gateway, SQS, S3, RDS), cumpliendo con los requisitos de la entrega de **despliegue en PaaS**. |
| **Menor complejidad operativa** | Desaparecen tareas como administración de AMIs, parches de sistema operativo, configuración de health checks de ALB y capacity planning detallado de instancias. El foco se centra en la lógica de negocio y no en la infraestructura. |
| **Modelo de costos por uso** | La facturación pasa de ser principalmente por tiempo de ejecución de instancias EC2 a un esquema basado en número de invocaciones y tiempo de ejecución de **Lambda**, además de uso de S3, RDS y SQS, lo cual es más eficiente para cargas variables. |

En resumen, la arquitectura evolucionó desde un modelo basado en servidores (IaaS con EC2 + ALB + ASG) hacia un modelo **completamente serverless**, donde **Lambda Web**, **Lambda Worker**, **API Gateway**, **SQS**, **S3** y **RDS** trabajan de forma integrada para soportar la concurrencia de usuarios, simplificar el despliegue y reducir la carga operativa del equipo.

---

## 🖼️ Diagrama de Componentes
<img alt="image" src="https://github.com/user-attachments/assets/30f48b71-b306-42d3-bb82-cb81df24ceae" />

