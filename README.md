# 🏀 ANB - Cloud Project

Este proyecto implementa una API REST con **FastAPI** que permite subir archivos a **AWS S3 Bucket**, autenticarse mediante JWT y manejar una base de datos PostgreSQL

## 👥 Integrantes del Equipo 8

| Nombre | Correo Uniandes |
|--------|-----------------|
| Jonatan Hernandez Rubio | je.hernandezr@uniandes.edu.co |
| Fernando Parra Villarreal | f.parrav@uniandes.edu.co |
| Daniel Serna Osorio | d.sernao@uniandes.edu.co |
| Harold Virgüez Engativa | h.virgueze@uniandes.edu.co |

## Entregas

### 📋 Entrega 1 - Desarrollo Local
- [Documentación técnica](./docs/Entrega_1/) - Arquitectura, modelo de datos y despliegue
- [Video de sustentación](./sustentacion/Entrega_1/sustentacion.md)
- [Plan de Capacidad](./capacity-planning/plan_de_pruebas.md) 

### ☁️ Entrega 2 - Migración AWS
- [Documentación técnica](./docs/Entrega_2/) - Arquitectura AWS
- [Análisis de capacidad](./capacity-planning/Entrega_2/pruebas_de_carga_entrega2.md) - Pruebas de estrés
- [Reporte SonarQube](./docs/Entrega_2/SonarQube_analysis/) - Análisis de calidad
- [Video de sustentación](./sustentacion/Entrega_1/sustentacion.md)

### ☁️ Entrega 3 - Load balancer/ auto scaling
---
- [Documentación técnica](./docs/Entrega_3/) - Arquitectura AWS
- [Análisis de capacidad](./capacity-planning/Entrega_3/pruebas_de_carga_entrega3.md) - Pruebas de estrés
- [Reporte SonarQube](./docs/Entrega_3/SonarQube_analysis/) - Análisis de calidad
- [Video de sustentación](./sustentacion/Entrega_1/sustentacion.md)
- [Video de sustentación 2](https://uniandes-my.sharepoint.com/:v:/g/personal/f_parrav_uniandes_edu_co/EUEUS4CKdkpOmMDBeM1LfdABDajq83a5hs1O8ri2SFNadA?e=KWPA1f)

### ☁️ Entrega 4 - Escalabilidad en la Capa Worker
---
- [Documentación técnica](./docs/Entrega_4/) - Arquitectura AWS
- [Análisis de capacidad](./capacity-planning/Entrega_4/pruebas_de_carga_entrega4.md) - Pruebas de estrés
- [Video Sustentacion](https://uniandes-my.sharepoint.com/:v:/g/personal/d_sernao_uniandes_edu_co/IQDnhMwaJqqEQI-PzO-blM7KAdGrP7bUP5jcnuss5W7x3vU?nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJPbmVEcml2ZUZvckJ1c2luZXNzIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXciLCJyZWZlcnJhbFZpZXciOiJNeUZpbGVzTGlua0NvcHkifX0&e=YGMlPa)

### ☁️ Entrega 5 - PAAS Capa Web y Worker
---
- [Documentación técnica](./docs/Entrega_5/) - Arquitectura AWS 
- [Análisis de capacidad](./capacity-planning/pruebas_de_carga_entrega5.md) - Pruebas de estrés
- [Video Sustentacion](https://uniandes-my.sharepoint.com/:v:/g/personal/d_sernao_uniandes_edu_co/IQDnhMwaJqqEQI-PzO-blM7KAdGrP7bUP5jcnuss5W7x3vU?nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJPbmVEcml2ZUZvckJ1c2luZXNzIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXciLCJyZWZlcnJhbFZpZXciOiJNeUZpbGVzTGlua0NvcHkifX0&e=YGMlPa)

---

## 🚦 Inicio Rápido

### Para ejecutar la aplicación:
```bash
# Opción 1: Docker Compose (Recomendado)
docker compose up -d
# Acceder: http://localhost/docs

# Opción 2: Desarrollo Local
# Ver sección "Ejecución en Desarrollo Local"
```

### Para ejecutar tests:
```bash
# Tests unitarios (pytest)
ENV_STATE=test TEST_DATABASE_URL="postgresql+asyncpg://postgres:password@localhost:5432/test_db" python -m pytest storeapi/tests/ -v

# Tests de integración (Newman)
newman run collections/Cloud-ANB.postman_collection.json --environment collections/postman_environment.json
```

---

## 🚀 Características principales

* Upload de archivos directamente a **AWS Cloud Storage**
* Soporte para entornos **test**, **dev** y **prod**
* Configuración basada en **Pydantic Settings** y **dotenv (.env)**
* Conexión a base de datos **PostgreSQL** vía **SQLAlchemy ORM**
* Tests automáticos con `pytest` y `pytest-asyncio`

---

## ⚙️ Requisitos previos

* **Python 3.13**
* **PostgreSQL** (para entorno de desarrollo)
* **Docker Desktop**
* **Cuenta en AWS** con credenciales válidas
* **Acceso al bucket creado en AWS S3**

---

## 🐳 Configuración de PostgreSQL con Docker

### Levantar PostgreSQL con Docker
Ejecuta el siguiente comando para levantar PostgreSQL:

```bash
docker run --name postgres-anb -e POSTGRES_PASSWORD=password -e POSTGRES_DB=dev_db -p 5432:5432 -d postgres:15
```

### Verificar que PostgreSQL esté corriendo
```bash
docker ps
```

Deberías ver el contenedor `postgres-anb` corriendo en el puerto 5432.

---

## 🧩 Configuración del entorno

Crea un archivo llamado `.env` en la raíz del proyecto con el siguiente contenido:

```dotenv
# Estado del entorno (dev, test, prod)
ENV_STATE=dev

# Base de datos PostgreSQL local (Docker)
DEV_DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/dev_db

# Base de datos de test
TEST_DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/test_db

# Base de datos de prod 
PROD_DATABASE_URL=anb-database.csxqmc4ywsa4.us-east-1.rds.amazonaws.com

# Credenciales de AWS S3
DEV_AWS_BUCKET_NAME=anb-s3-bucket
DEV_AWS_REGION=us-east-1
DEV_AWS_ACCESS_KEY_ID=tu_access_key
DEV_AWS_SECRET_ACCESS_KEY=tu_secret_key

# Kafka (Message Broker)
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_GROUP_ID=video_tasks_group

# Redis (Caché - opcional)
REDIS_URL=redis://localhost:6379
RANKING_CACHE_TTL=300

# Almacenamiento local de videos
UPLOADED_FOLDER=videos/uploaded
PROCESSED_FOLDER=videos/processed

# Configuración del servidor
APP_HOST=0.0.0.0
APP_PORT=8000
```

---

## 🧪 Tests Automatizados (pytest)

### Requisitos
- PostgreSQL corriendo (contenedor Docker standalone)
- Python 3.13 con dependencias instaladas

### 1. Levantar PostgreSQL para Tests
```bash
# Levantar PostgreSQL standalone (si no está corriendo)
docker run --name postgres-anb -e POSTGRES_PASSWORD=password -e POSTGRES_DB=dev_db -p 5432:5432 -d postgres:15

# Verificar que esté corriendo
docker ps
```

### 2. Ejecutar Tests con pytest

#### Tests básicos
```bash
# Todos los tests (PowerShell)
$env:ENV_STATE="test"; $env:TEST_DATABASE_URL="postgresql+asyncpg://postgres:password@localhost:5432/test_db"; python -m pytest storeapi/tests/ -v

# Tests básicos (Bash/zsh)
ENV_STATE=test TEST_DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/test_db python -m pytest storeapi/tests/ -v
```

#### Tests con salida detallada
```bash
# PowerShell
$env:ENV_STATE="test"; $env:TEST_DATABASE_URL="postgresql+asyncpg://postgres:password@localhost:5432/test_db"; python -m pytest storeapi/tests/ -v --tb=short

# Bash/zsh
ENV_STATE=test TEST_DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/test_db python -m pytest storeapi/tests/ -v --tb=short
```

#### Tests específicos
```bash
# Test de un módulo específico (PowerShell)
$env:ENV_STATE="test"; $env:TEST_DATABASE_URL="postgresql+asyncpg://postgres:password@localhost:5432/test_db"; python -m pytest storeapi/tests/routers/test_user.py -v

# Test de un módulo específico (Bash/zsh)
ENV_STATE=test TEST_DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/test_db python -m pytest storeapi/tests/routers/test_user.py -v

# Test específico por nombre
ENV_STATE=test TEST_DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/test_db python -m pytest storeapi/tests/routers/test_user.py::test_create_user -v
```

### ℹ️ Características de los Tests
- ✅ **Base de datos separada**: Usa `test_db` (aislada de desarrollo)
- ✅ **Rollback automático**: Los datos se limpian después de cada test
- ✅ **Tests asíncronos**: Utilizan `pytest-asyncio`
- ✅ **Cobertura completa**: Autenticación, usuarios, videos, votos, ranking

---

## 🐳 Ejecución con Docker Compose (Recomendado)

### 1. Configurar archivo .env
Asegúrate de tener un archivo `.env` en la raíz con la siguiente configuración mínima:

```dotenv
# Estado del entorno
ENV_STATE=dev

# AWS S3 (usar credenciales locales para desarrollo)
DEV_AWS_BUCKET_NAME=anb-local-bucket
DEV_AWS_REGION=us-east-1
DEV_AWS_ACCESS_KEY_ID=test_key
DEV_AWS_SECRET_ACCESS_KEY=test_secret

# Kafka (no es necesario configurar, Docker Compose lo maneja)
# DEV_DATABASE_URL se configura automáticamente en docker-compose.yml
```

### 2. Levantar todos los servicios

```bash
# Levantar toda la infraestructura
docker compose up -d

# Ver logs en tiempo real (opcional)
docker compose logs -f

# Verificar estado de servicios
docker compose ps
```

**Servicios levantados:**
- 🗄️ **PostgreSQL** (puerto 5432)
- 🌐 **StoreAPI** (expuesto internamente en puerto 8000)
- 🔄 **Nginx** (puerto 80) - Proxy reverso
- 📨 **Kafka** (puerto 9092) - Message broker
- ⚙️ **Worker** - Procesamiento de videos con FFmpeg
- 💾 **Redis** (puerto 6379) - Caché

### 3. Verificar que los servicios estén listos

```bash
# Verificar todos los contenedores
docker compose ps

# Salida esperada:
# NAME          STATUS          PORTS
# database      Up (healthy)    0.0.0.0:5432->5432/tcp
# storeapi      Up              8000/tcp
# proxy         Up              0.0.0.0:80->80/tcp
# kafka         Up (healthy)    0.0.0.0:9092->9092/tcp
# worker        Up              
# redis         Up              0.0.0.0:6379->6379/tcp

# Ver logs de un servicio específico
docker compose logs storeapi --tail 50
docker compose logs worker --tail 50
```

### 4. Acceder a la API

🌐 **API**: [http://localhost/docs](http://localhost/docs)  
🔗 **Endpoints**:
- `http://localhost/api/auth/login`
- `http://localhost/api/videos/upload`
- `http://localhost/api/ranking`

### 5. Ejecutar Tests con Newman (Docker Compose)

**Prerequisitos:**
```bash
# Instalar Newman si no lo tienes
npm install -g newman

# Verificar instalación
newman --version
```

**Ejecutar tests:**
```bash
# Ejecutar toda la colección de tests
newman run collections/Cloud-ANB.postman_collection.json --environment collections/postman_environment.json
```

**Resultados esperados:**
Al ejecutar los tests exitosamente, deberías ver:
- **25 requests ejecutados** ✅
- **22 test scripts ejecutados** ✅  
- **26 pre-request scripts ejecutados** ✅
- **61 de 61 assertions pasaron** ✅ (100% de éxito)

**Nota importante:**
- Los tests incluyen un delay de 10 segundos para esperar que los videos se procesen
- El worker de Kafka debe estar corriendo para que los videos se procesen correctamente
- Los tests de votación requieren que los videos estén en estado "processed"

---

## ▶️ Ejecución en Desarrollo Local (Sin Docker Compose)

Para desarrollo local con más control y debugging.

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Levantar servicios individuales

#### PostgreSQL
```bash
docker run --name postgres-anb -e POSTGRES_PASSWORD=password -e POSTGRES_DB=dev_db -p 5432:5432 -d postgres:15
```

#### Kafka (opcional, si necesitas procesamiento de videos)
```bash
docker run --name kafka-dev -p 9092:9092 -e KAFKA_ENABLE_KRAFT=yes -e KAFKA_CFG_NODE_ID=1 -e KAFKA_CFG_PROCESS_ROLES=broker,controller -e KAFKA_CFG_CONTROLLER_QUORUM_VOTERS=1@localhost:9093 -e KAFKA_CFG_LISTENERS=PLAINTEXT://:9092,CONTROLLER://:9093 -e KAFKA_CFG_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092 -e KAFKA_CFG_CONTROLLER_LISTENER_NAMES=CONTROLLER bitnamilegacy/kafka:4.0.0-debian-12-r10
```

### 3. Configurar variables de entorno

**PowerShell:**
```powershell
$env:ENV_STATE="dev"
$env:DEV_DATABASE_URL="postgresql+asyncpg://postgres:password@localhost:5432/dev_db"
$env:DEV_AWS_ACCESS_KEY_ID="test_key"
$env:DEV_AWS_SECRET_ACCESS_KEY="test_secret"
$env:DEV_AWS_BUCKET_NAME="test_bucket"
$env:DEV_AWS_REGION="us-east-1"
$env:KAFKA_BOOTSTRAP_SERVERS="localhost:9092"
```

**Bash/zsh:**
```bash
export ENV_STATE=dev
export DEV_DATABASE_URL="postgresql+asyncpg://postgres:password@localhost:5432/dev_db"
export DEV_AWS_ACCESS_KEY_ID="test_key"
export DEV_AWS_SECRET_ACCESS_KEY="test_secret"
export DEV_AWS_BUCKET_NAME="test_bucket"
export DEV_AWS_REGION="us-east-1"
export KAFKA_BOOTSTRAP_SERVERS="localhost:9092"
```

### 4. Ejecutar el API

**PowerShell:**
```powershell
$env:ENV_STATE="dev"; $env:DEV_DATABASE_URL="postgresql+asyncpg://postgres:password@localhost:5432/dev_db"; python -m uvicorn storeapi.main:app --reload --host 0.0.0.0 --port 8000
```

**Bash/zsh:**
```bash
ENV_STATE=dev DEV_DATABASE_URL="postgresql+asyncpg://postgres:password@localhost:5432/dev_db" python -m uvicorn storeapi.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Ejecutar el Worker (opcional, en otra terminal)

**PowerShell:**
```powershell
$env:ENV_STATE="dev"; $env:DEV_DATABASE_URL="postgresql+asyncpg://postgres:password@localhost:5432/dev_db"; $env:KAFKA_BOOTSTRAP_SERVERS="localhost:9092"; python -m message_broker.worker
```

**Bash/zsh:**
```bash
ENV_STATE=dev DEV_DATABASE_URL="postgresql+asyncpg://postgres:password@localhost:5432/dev_db" KAFKA_BOOTSTRAP_SERVERS="localhost:9092" python -m message_broker.worker
```

### 6. Acceder a la documentación

🌐 **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)

**Nota importante**: 
- En desarrollo local, el API corre directamente en el **puerto 8000** (sin proxy)
- Con Docker Compose, se accede a través de Nginx en el **puerto 80**: [http://localhost/docs](http://localhost/docs)
- El servidor creará automáticamente las tablas en PostgreSQL al iniciar

---

## 📁 Estructura del Proyecto

```
desarrollo-de-software-en-la-nube/
├── 📂 storeapi/                         # API REST - FastAPI
│   ├── main.py                          # Punto de entrada de la aplicación
│   ├── database.py                      # Configuración de SQLAlchemy
│   ├── security.py                      # Autenticación JWT
│   ├── 📂 routers/                      # Endpoints de la API
│   │   ├── user.py                      # Auth (login, signup)
│   │   ├── video.py                     # Upload, stream, list, delete
│   │   ├── vote.py                      # Sistema de votación
│   │   └── ranking.py                   # Rankings por ciudad
│   ├── 📂 models/                       # Modelos SQLAlchemy (ORM)
│   │   ├── user.py                      # Tabla users
│   │   ├── video.py                     # Tabla videos
│   │   ├── vote.py                      # Tabla votes
│   │   └── ranking.py                   # Vista ranking
│   └── 📂 tests/                        # Tests unitarios (pytest)
│       ├── conftest.py                  # Fixtures
│       ├── test_security.py             # Tests de JWT
│       └── routers/                     # Tests de endpoints
│
├── 📂 message_broker/                   # Sistema de cola de mensajes
│   ├── client.py                        # Cliente Kafka producer
│   ├── tasks_dispatcher.py              # Encolador de tareas
│   └── worker.py                        # Consumer - Procesa videos
│
├── 📂 utils/                            # Utilidades compartidas
│   ├── config.py                        # Configuración (Pydantic)
│   ├── cache.py                         # Cliente Redis
│   ├── logging_conf.py                  # Logging estructurado
│   ├── ffmpeg.py                        # Procesamiento con FFmpeg
│   └── 📂 s3/
│       ├── s3.py                        # Cliente AWS S3
│       └── s3_local.py                  # Storage local (desarrollo)
│
├── 📂 capacity-planning/                # Plan de análisis de capacidad
│   ├── Makefile                         # Comandos para pruebas
│   ├── plan_de_pruebas.md               # Plan de pruebas Entrega 1
│   ├── pruebas_de_carga_entrega5.md     # Análisis de capacidad Entrega 5
│   ├── 📂 Entrega_2/                     # Entrega 2
│   │   ├── pruebas_de_carga_entrega2.md # Análisis de capacidad
│   │   ├── resultados/                  # Resultados de pruebas
│   │   └── resultados_entrega_2/        # Análisis de capacidad
│   ├── 📂 Entrega_3/                     # Entrega 3
│   │   ├── pruebas_de_carga_entrega3.md # Análisis de capacidad
│   │   └── resultados_entrega_3/       # Resultados de pruebas
│   └── 📂 Entrega_4/                     # Entrega 4
│       ├── plan_de_pruebas.md           # Plan de pruebas
│       ├── pruebas_de_carga_entrega4.md # Análisis de capacidad
│       └── postman/                      # Tests de integración (Newman)
│
├── 📂 docs/                             # Documentación técnica
│   ├── 📂 Entrega_1/
│   │   ├── data_model.md                # Modelo de datos (ERD)
│   │   ├── component_diagram.md         # Arquitectura
│   │   ├── process_flow.md              # Flujo de procesamiento
│   │   └── deployment.md                # Guía de despliegue
│   ├── 📂 Entrega_2/
│   │   ├── component_diagram.md         # Arquitectura AWS
│   │   ├── data_model.md                # Modelo de datos actualizado
│   │   ├── validate_endpoints.md        # Validación de endpoints
│   │   └── 📂 SonarQube_analysis/        # Análisis de calidad de código
│   │       ├── sonar_analysis.md        # Reporte de análisis
│   │       └── sonar_issues_fixed.md    # Issues corregidos
│   ├── 📂 Entrega_3/
│   │   ├── component_diagram.md         # Arquitectura AWS
│   │   ├── data_model.md                # Modelo de datos
│   │   ├── process_flow.md              # Flujo de procesamiento
│   │   └── 📂 SonarQube_analysis/        # Análisis de calidad de código
│   └── 📂 Entrega_4/
│       ├── component_diagram.md         # Arquitectura AWS
│       ├── data_model.md                # Modelo de datos
│       └── process_flow.md              # Flujo de procesamiento
│
├── 📂 sustentacion/                     # Videos de sustentación
│   └── 📂 Entrega_1/
│       └── sustentacion.md              # Documento con enlace al video
│
├── 📂 collections/                      # Colecciones Postman (UI)
│   ├── Cloud-ANB.postman_collection.json
│   └── postman_environment.json
│
├── 📂 videos/                           # Almacenamiento local de videos
│   ├── uploaded/                        # Videos subidos (originales)
│   └── processed/                       # Videos procesados (con branding)
│
├── 📂 img/
│   └── logo_nba.png                     # Logo para intro/outro de videos
│
├── 🐳 docker-compose.yml                # Orquestación de servicios
├── 🐳 api.Dockerfile                    # Imagen del API (FastAPI)
├── 🐳 worker.Dockerfile                 # Imagen del worker (FFmpeg)
├── 🐳 ffmpegpy.Dockerfile               # Base con FFmpeg + Python
├── � nginx.conf                        # Configuración Nginx (proxy)
├── � Makefile                          # Comandos Docker Compose (raíz)
├── � monitor.sh                        # Script de monitoreo de recursos
├── � requirements.txt                  # Dependencias Python
├── � .env                              # Variables de entorno (crear)
└── 📖 README.md                         # Este archivo
```

### Descripción de Servicios (Docker Compose)

| Servicio | Puerto | Descripción | Tecnología |
|----------|--------|-------------|------------|
| **nginx** | 80 | Proxy reverso y balanceador | Nginx |
| **storeapi** | 8000 (interno) | API REST principal | FastAPI + Python 3.11 |
| **worker** | - | Procesador asíncrono de videos | Python 3.11 + FFmpeg |
| **db** | 5432 | Base de datos relacional | PostgreSQL 15 |
| **kafka** | 9092 | Message broker para tareas | Apache Kafka (KRaft) |
| **redis** | 6379 | Caché para ranking | Redis 7 |

### Flujo de Datos

1. **Upload**: Cliente → Nginx (80) → StoreAPI → S3/Local + Kafka
2. **Procesamiento**: Kafka → Worker → FFmpeg → S3/Local → DB (update status)
3. **Consultas**: Cliente → Nginx → StoreAPI → Redis (cache) / DB → Response

---
