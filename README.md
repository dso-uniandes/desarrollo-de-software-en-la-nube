# 🏀 ANB - Cloud Project

Este proyecto implementa una API REST con **FastAPI** que permite subir archivos a **AWS S3 Bucket**, autenticarse mediante JWT y manejar una base de datos PostgreSQL

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
make newman
```

### Para monitorear recursos:
```bash
./monitor.sh
```

---

## 📘 Documentación del Proyecto

Dentro del repositorio existe una carpeta `/docs/Entrega_1` que contiene toda la documentación técnica de la primera entrega, incluyendo:

- **Modelo de datos (ERD):** `data_model.md`
- **Diagrama de componentes de la arquitectura:** `component_diagram.md`
- **Flujo de procesamiento de videos:** `process_flow.md`
- **Guía de despliegue e infraestructura:** `deployment.md`
- **Colecciones de Postman:** `/collections/`

```
📂 root-folder/
└── 📂 docs/
    └── 📂 Entrega_1/
        ├── data_model.md
        ├── component_diagram.md
        ├── process_flow.md
        ├── deployment.md
        └── sonar_reporte.pdf
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
📚 **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

**Nota**: El servidor creará automáticamente las tablas en PostgreSQL al iniciar.

---

## 📊 Comparación de Enfoques

| Característica | Docker Compose | Desarrollo Local |
|----------------|----------------|------------------|
| **Setup inicial** | Simple (`docker compose up`) | Manual (varios comandos) |
| **Aislamiento** | ✅ Completo | ⚠️ Parcial |
| **Hot reload** | ✅ Sí (con volumes) | ✅ Sí |
| **Debugging** | ⚠️ Requiere attach | ✅ Directo |
| **Recursos** | 🔴 Alto (todos los servicios) | 🟢 Bajo (solo necesarios) |
| **Producción-like** | ✅ Muy similar | ⚠️ Diferente |
| **Recomendado para** | Tests, demos, CI/CD | Desarrollo activo, debugging |

---

## 📁 Estructura del Proyecto

```
proyecto/
├── 📂 storeapi/                     # Aplicación principal API
│   ├── __init__.py
│   ├── main.py                      # Punto de entrada FastAPI
│   ├── database.py                  # Configuración de base de datos
│   ├── security.py                  # Autenticación JWT
│   ├── 📂 routers/                  # Endpoints de la API
│   │   ├── user.py                 # Gestión de usuarios
│   │   ├── video.py                # Upload y streaming de videos
│   │   ├── vote.py                 # Sistema de votos
│   │   └── ranking.py              # Rankings y estadísticas
│   ├── 📂 models/                   # Modelos SQLAlchemy
│   │   ├── user.py
│   │   ├── video.py
│   │   ├── vote.py
│   │   └── ranking.py
│   └── 📂 tests/                    # Tests unitarios
│       ├── conftest.py             # Configuración de pytest
│       ├── test_security.py        # Tests de autenticación
│       └── routers/                # Tests de endpoints
│
├── 📂 message_broker/               # Sistema de mensajería
│   ├── __init__.py
│   ├── client.py                   # Cliente de Kafka
│   ├── tasks_dispatcher.py         # Despachador de tareas
│   └── worker.py                   # Worker de procesamiento
│
├── 📂 utils/                        # Utilidades compartidas
│   ├── __init__.py
│   ├── config.py                   # Configuración global
│   ├── cache.py                    # Gestión de caché Redis
│   ├── logging_conf.py             # Configuración de logs
│   ├── ffmpeg.py                   # Procesamiento de video
│   └── 📂 s3/                       # Integración con S3
│       ├── s3.py                   # Cliente AWS S3
│       └── s3_local.py             # Storage local simulado
│
├── 📂 docs/                         # Documentación técnica
│   └── 📂 Entrega_1/
│       ├── data_model.md
│       ├── component_diagram.md
│       ├── process_flow.md
│       └── deployment.md
│
├── 📂 capacity-planning/            # Análisis de capacidad
│   ├── plan_de_capacidad.md
│   └── 📂 results/                  # Resultados de pruebas
│
├── 📂 postman/                      # Tests de integración
│   ├── collection.json             # Colección Newman
│   ├── environment.json            # Variables de entorno
│   └── report.html                 # Reportes generados
│
├── 📂 collections/                  # Colecciones Postman UI
│   ├── Cloud-ANB.postman_collection.json
│   └── postman_environment.json
│
├── 📂 videos/                       # Almacenamiento local
│   ├── uploaded/                   # Videos originales
│   └── processed/                  # Videos procesados
│
├── 📂 img/                          # Recursos
│   └── logo_nba.png                # Logo para branding
│
├── 🐳 docker-compose.yml            # Orquestación de servicios
├── 🐳 api.Dockerfile                # Imagen del API
├── 🐳 worker.Dockerfile             # Imagen del worker
├── 🐳 ffmpegpy.Dockerfile           # Imagen con FFmpeg
├── 📋 requirements.txt              # Dependencias Python
├── 🔧 .env                          # Variables de entorno (crear)
├── 🔧 nginx.conf                    # Configuración Nginx
├── 📜 Makefile                      # Comandos automatizados
├── 📊 monitor.sh                    # Script de monitoreo
└── 📖 README.md                     # Este archivo
```

### Descripción de Componentes

| Componente | Descripción | Tecnología |
|------------|-------------|------------|
| **StoreAPI** | API REST para gestión de videos, votos y ranking | FastAPI + SQLAlchemy |
| **Message Broker** | Sistema de mensajería asíncrona para tareas | Kafka + Python |
| **Worker** | Procesador de videos con branding y edición | FFmpeg + Python |
| **Database** | Almacenamiento de metadatos | PostgreSQL 15 |
| **Cache** | Caché de ranking y consultas frecuentes | Redis 7 |
| **Nginx** | Proxy reverso y balanceador de carga | Nginx |
| **Storage** | Almacenamiento de archivos de video | S3/Local |

---
