# 🏀 ANB - Cloud Project

Este proyecto implementa una API REST con **FastAPI** que permite subir archivos a **AWS S3 Bucket**, autenticarse mediante JWT y manejar una base de datos PostgreSQL

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
```

---

## ▶️ Ejecución local

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Configurar variables de entorno
Asegúrate de que tu archivo `.env` esté configurado correctamente (ver sección anterior).

### 3. Ejecutar el servidor FastAPI
```bash
# Con variables de entorno (PowerShell)
$env:ENV_STATE="dev"; $env:DEV_DATABASE_URL="postgresql+asyncpg://postgres:password@localhost:5432/dev_db"; python -m uvicorn storeapi.main:app --reload --host 0.0.0.0 --port 8000

# Con archivo .env configurado
python -m uvicorn storeapi.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Acceder a la documentación
🌐  [http://localhost:8000/docs](http://localhost:8000/docs)

**Nota**: El servidor creará automáticamente las tablas en PostgreSQL al iniciar.

---

## 🧪 Ejecutar Tests Asíncronos

### Requisitos para los tests
Los tests requieren que PostgreSQL esté corriendo (usando Docker) y que las variables de entorno estén configuradas.

### Comandos para ejecutar tests

#### 1. Tests básicos (PowerShell)
```bash
# Configurar entorno de test y ejecutar
$env:ENV_STATE="test"; $env:TEST_DATABASE_URL="postgresql+asyncpg://postgres:password@localhost:5432/test_db"; python -m pytest storeapi/tests/ -v
```

#### 2. Tests con salida detallada
```bash
# Con información detallada de cada test
$env:ENV_STATE="test"; $env:TEST_DATABASE_URL="postgresql+asyncpg://postgres:password@localhost:5432/test_db"; python -m pytest storeapi/tests/ -v --tb=short
```

#### 3. Tests específicos
```bash
# Ejecutar solo tests de un módulo específico
$env:ENV_STATE="test"; $env:TEST_DATABASE_URL="postgresql+asyncpg://postgres:password@localhost:5432/test_db"; python -m pytest storeapi/tests/routers/test_user.py -v

# Ejecutar un test específico
$env:ENV_STATE="test"; $env:TEST_DATABASE_URL="postgresql+asyncpg://postgres:password@localhost:5432/test_db"; python -m pytest storeapi/tests/routers/test_user.py::test_create_user -v
```

### ⚠️ Notas importantes sobre los tests

1. **Base de datos de test**: Los tests usan una base de datos separada (`test_db`) que se crea automáticamente
2. **Rollback automático**: Los tests están configurados para hacer rollback automático de los datos
3. **Tests asíncronos**: Todos los tests son asíncronos y usan `pytest-asyncio`
4. **Docker requerido**: PostgreSQL debe estar corriendo en Docker para que los tests funcionen

---

## 🚀 Ejecutar Tests con Newman (Postman CLI)

### Requisitos para Newman
- **Newman instalado**: `npm install -g newman`
- **Servidor corriendo**: FastAPI debe estar ejecutándose en `http://localhost:8000`
- **PostgreSQL corriendo**: Docker container `postgres-anb` debe estar activo
- **Kafka corriendo**: Para el procesamiento asíncrono de videos
- **Worker corriendo**: Para procesar los videos subidos

### Procedimiento Completo para Ejecutar Tests

#### 1. Configuración Inicial
Asegúrate de que todos los servicios estén corriendo:

```bash
# 1. Verificar que PostgreSQL esté corriendo
docker ps

# 2. Verificar que el contenedor postgres-anb esté activo
docker logs postgres-anb
```

#### 2. Configuración de Variables de Entorno
Configura las variables de entorno necesarias para el desarrollo:

```bash
# Variables de entorno para desarrollo (PowerShell)
$env:ENV_STATE="dev"
$env:DEV_DATABASE_URL="postgresql+asyncpg://postgres:password@localhost:5432/dev_db"
$env:DEV_AWS_ACCESS_KEY_ID="test_key"
$env:DEV_AWS_SECRET_ACCESS_KEY="test_secret"
$env:DEV_AWS_BUCKET_NAME="test_bucket"
$env:DEV_AWS_REGION="us-east-1"
$env:KAFKA_BOOTSTRAP_SERVERS="localhost:9092"
```

#### 3. Levantar el Servidor FastAPI
```bash
# Iniciar el servidor FastAPI con todas las variables de entorno
$env:ENV_STATE="dev"; $env:DEV_DATABASE_URL="postgresql+asyncpg://postgres:password@localhost:5432/dev_db"; $env:DEV_AWS_ACCESS_KEY_ID="test_key"; $env:DEV_AWS_SECRET_ACCESS_KEY="test_secret"; $env:DEV_AWS_BUCKET_NAME="test_bucket"; $env:DEV_AWS_REGION="us-east-1"; $env:KAFKA_BOOTSTRAP_SERVERS="localhost:9092"; python -m uvicorn storeapi.main:app --reload --host 0.0.0.0 --port 8000
```

#### 4. Levantar el Worker de Procesamiento
En una terminal separada, inicia el worker que procesa los videos:

```bash
# Iniciar el worker de Kafka para procesamiento de videos
$env:ENV_STATE="dev"; $env:DEV_DATABASE_URL="postgresql+asyncpg://postgres:password@localhost:5432/dev_db"; $env:DEV_AWS_ACCESS_KEY_ID="test_key"; $env:DEV_AWS_SECRET_ACCESS_KEY="test_secret"; $env:DEV_AWS_BUCKET_NAME="test_bucket"; $env:DEV_AWS_REGION="us-east-1"; $env:KAFKA_BOOTSTRAP_SERVERS="localhost:9092"; python -m message_broker.worker
```

#### 5. Verificar que los Servicios Estén Funcionando
- **FastAPI**: Debe estar disponible en `http://localhost:8000`
- **Worker**: Debe mostrar logs de conexión a la base de datos y Kafka
- **PostgreSQL**: Debe estar corriendo en el puerto 5432

#### 6. Ejecutar Tests con Newman
```bash
# Ejecutar toda la colección de tests
newman run collections/Cloud-ANB.postman_collection.json --environment collections/postman_environment.json
```

### ⚠️ Notas Importantes sobre los Tests

1. **Procesamiento Asíncrono**: Los tests incluyen un delay de 10 segundos para esperar que los videos se procesen
2. **Worker Requerido**: El worker de Kafka debe estar corriendo para que los videos se procesen correctamente
3. **Base de Datos**: Los tests crean usuarios y videos de prueba que se almacenan en la base de datos
4. **Votación**: Los tests de votación requieren que los videos estén en estado "processed"
5. **Autenticación**: Los tests manejan automáticamente la autenticación JWT

### 🔧 Solución de Problemas

#### Si los tests fallan:
1. **Verificar que el worker esté corriendo**: Debe mostrar logs de procesamiento de videos
2. **Verificar la base de datos**: Los videos deben cambiar de estado "uploaded" a "processed"
3. **Verificar Kafka**: El worker debe conectarse correctamente a Kafka
4. **Verificar el logo**: El archivo `img/logo_nba.png` debe existir para el procesamiento

#### Logs esperados del Worker:
```
2025-10-18 22:21:09 - INFO - databases - Connected to database postgresql+asyncpg://postgres:********@localhost:5432/dev_db
2025-10-18 22:21:09 - INFO - worker - Database connection established.
2025-10-18 22:21:13 - INFO - worker - Received message: {"video_id": 54, "user_id": 49, "task_id": "..."}
2025-10-18 22:21:13 - INFO - worker - Processing video: {...}
```

### 📊 Resultados Esperados
Al ejecutar los tests exitosamente, deberías ver:
- **25 requests ejecutados** ✅
- **22 test scripts ejecutados** ✅  
- **26 pre-request scripts ejecutados** ✅
- **61 de 61 assertions pasaron** ✅ (100% de éxito)

---

## ⚙️ Comandos útiles

### Docker
```bash
# Ver contenedores corriendo
docker ps

# Ver logs del contenedor PostgreSQL
docker logs postgres-anb

# Conectar a PostgreSQL desde terminal
docker exec -it postgres-anb psql -U postgres

# Detener el contenedor
docker stop postgres-anb

# Iniciar el contenedor
docker start postgres-anb

# Eliminar el contenedor
docker rm postgres-anb
```

---

## 📁 Estructura del proyecto

```
fastApi/
├── storeapi/                    # Aplicación principal
│   ├── __init__.py
│   ├── main.py                  # Punto de entrada FastAPI
│   ├── config.py                # Configuración con Pydantic
│   ├── database.py              # Configuración de base de datos
│   ├── security.py              # Autenticación JWT
│   ├── routers/                 # Endpoints de la API
│   │   ├── user.py             # Gestión de usuarios
│   │   ├── post.py             # Posts y comentarios
│   │   ├── video.py            # Upload y procesamiento de videos
│   │   ├── vote.py             # Sistema de votos
│   │   └── ranking.py          # Rankings y estadísticas
│   ├── models/                  # Modelos de datos
│   │   ├── user.py
│   │   ├── post.py
│   │   ├── video.py
│   │   ├── vote.py
│   │   └── ranking.py
│   ├── tests/                   # Tests unitarios
│   │   ├── conftest.py         # Configuración de pytest
│   │   ├── test_security.py    # Tests de autenticación
│   │   └── routers/            # Tests de endpoints
│   └── libs/                    # Utilidades
│       ├── cache.py
│       └── s3/                  # Integración con AWS S3
├── requirements.txt             # Dependencias Python
├── .env                        # Variables de entorno (crear)
└── README.md                   # Este archivo
```

---
