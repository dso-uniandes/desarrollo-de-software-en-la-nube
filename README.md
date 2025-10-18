# 🏀 ANB - Cloud Project

Este proyecto implementa una API REST con **FastAPI** que permite subir archivos a **AWS S3 Bucket**, autenticarse mediante JWT y manejar una base de datos PostgreSQL

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
```bash
docker run --name postgres-test -e POSTGRES_PASSWORD=password -e POSTGRES_DB=test_db -p 5433:5432 -d postgres:15
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
