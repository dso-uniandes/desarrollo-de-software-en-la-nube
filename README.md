# 🏀 ANB - Cloud Project

Este proyecto implementa una API REST con **FastAPI** que permite subir archivos a **AWS S3 Bucket**, autenticarse mediante JWT y manejar una base de datos MySQL.

---

## 🚀 Características principales

* Upload de archivos directamente a **AWS Cloud Storage**
* Soporte para entornos **test**, **dev** y **prod**
* Configuración basada en **Pydantic Settings** y **dotenv (.env)**
* Conexión a base de datos **MySQL** vía **SQLAlchemy ORM**
* Tests automáticos con `pytest` y `pytest-asyncio`

---

## ⚙️ Requisitos previos

* **Python 3.13+**
* **Docker Desktop** (para MySQL local)
* **Cuenta en AWS** con credenciales válidas
* **Acceso al bucket creado en AWS S3**

---

## 🐳 Configuración de MySQL con Docker

**IMPORTANTE**: Este proyecto requiere MySQL. Los tests y el servidor necesitan una instancia de MySQL corriendo.

### 1. Instalar Docker Desktop
Descarga e instala [Docker Desktop](https://www.docker.com/products/docker-desktop/) para tu sistema operativo.

### 2. Levantar MySQL con Docker
Ejecuta el siguiente comando para levantar MySQL:

```bash
docker run --name mysql-anb -e MYSQL_ROOT_PASSWORD=password -e MYSQL_DATABASE=dev_db -p 3306:3306 -d mysql:8.0
```

### 3. Verificar que MySQL esté corriendo
```bash
docker ps
```

Deberías ver el contenedor `mysql-anb` corriendo en el puerto 3306.

---

## 🧩 Configuración del entorno

Crea un archivo llamado `.env` en la raíz del proyecto con el siguiente contenido:

```dotenv
# Estado del entorno (dev, test, prod)
ENV_STATE=dev

# Base de datos MySQL local (Docker)
DEV_DATABASE_URL=mysql+aiomysql://root:password@localhost:3306/dev_db

# Base de datos de test (para pytest)
TEST_DATABASE_URL=mysql+aiomysql://root:password@localhost:3306/test_db

# Base de datos de producción
PROD_DATABASE_URL=mysql+aiomysql://usuario:password@anb-database.csxqmc4ywsa4.us-east-1.rds.amazonaws.com:3306/prod_db

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
# Opción 1: Con variables de entorno
$env:ENV_STATE="dev"; $env:DEV_DATABASE_URL="mysql+aiomysql://root:password@localhost:3306/dev_db"; python -m uvicorn storeapi.main:app --reload --host 0.0.0.0 --port 8000

# Opción 2: Si tienes el archivo .env configurado
python -m uvicorn storeapi.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Acceder a la documentación
🌐  [http://localhost:8000/docs](http://localhost:8000/docs)

**Nota**: El servidor creará automáticamente las tablas en MySQL al iniciar.

---

## ⚙️ Comandos útiles

### Ejecutar tests
```bash
# Ejecutar todos los tests
python -m pytest -v

# Ejecutar tests específicos
python -m pytest storeapi/tests/test_security.py -v

# Ejecutar tests con más detalle
python -m pytest -v --tb=short
```

### Gestión de Docker MySQL
```bash
# Ver contenedores corriendo
docker ps

# Parar el contenedor MySQL
docker stop mysql-anb

# Iniciar el contenedor MySQL
docker start mysql-anb

# Ver logs del contenedor
docker logs mysql-anb

# Eliminar el contenedor (si necesitas recrearlo)
docker rm mysql-anb
```

### Verificar conexión a MySQL
```bash
# Conectar a MySQL desde línea de comandos
docker exec -it mysql-anb mysql -u root -p
# Password: password
```

---

## 📋 Estructura del proyecto

```
fastApi/
├── storeapi/
│   ├── database.py          # Configuración MySQL + SQLAlchemy ORM
│   ├── main.py             # Aplicación FastAPI
│   ├── config.py           # Configuración con Pydantic
│   ├── routers/            # Endpoints de la API
│   └── tests/              # Tests con pytest
├── .env                    # Variables de entorno (crear)
├── requirements.txt        # Dependencias Python
└── README.md              # Este archivo
```

---
