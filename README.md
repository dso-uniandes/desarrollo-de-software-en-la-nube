# 🏀 ANB - Cloud Project

Este proyecto implementa una API REST con **FastAPI** que permite subir archivos a **AWS S3 Bucket**, autenticarse mediante JWT y manejar una base de datos PostgreSQL o SQLite según el entorno.

---

## 🚀 Características principales

* Upload de archivos directamente a **AWS Cloud Storage**
* Soporte para entornos **test**, **dev** y **prod**
* Configuración basada en **Pydantic Settings** y **dotenv (.env)**
* Conexión a base de datos vía **SQLAlchemy**:
  * **PostgreSQL**: Dev and Prod
  * **SQLite**: Test
* Tests automáticos con `pytest` y `pytest-asyncio`

---

## ⚙️ Requisitos previos

* **Python 3.11.14**
* **PostgreSQL** (para entorno de desarrollo)
* **Cuenta en AWS** con credenciales válidas
* **Acceso al bucket creado en AWS S3**

---

## 🧩 Configuración del entorno

Crea un archivo llamado `.env` en la raíz del proyecto con el siguiente contenido:

```dotenv
# Estado del entorno
ENV_STATE=dev

# Base de datos de prod 
PROD_DATABASE_URL=anb-database.csxqmc4ywsa4.us-east-1.rds.amazonaws.com

# Credenciales de AWS S3
DEV_AWS_BUCKET_NAME=anb-s3-bucket
DEV_AWS_REGION=us-east-1
```

---

## ▶️ Ejecución local

1. Instala dependencias:

   ```bash
   pip install -r requirements.txt
   ```

2. Ejecuta el servidor FastAPI:

   ```bash
   uvicorn storeapi.main:app --reload
   ```

3. Accede a la documentación interactiva (Swagger UI):

   🌐  [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## ⚙️ Comandos útiles

* Ejecutar tests:

  ```bash
  pytest
  ```
