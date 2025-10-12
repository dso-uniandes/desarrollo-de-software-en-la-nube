# 🏀 NAB - Cloud Project

Este proyecto implementa una API REST con **FastAPI** que permite subir archivos a **Backblaze B2** (servicio compatible con S3), autenticarse mediante JWT y manejar una base de datos MySQL o SQLite según el entorno.

---

## 🚀 Características principales

* Upload de archivos directamente a **Backblaze B2 Cloud Storage**
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
* **Cuenta en Backblaze B2** con credenciales válidas
* **Acceso al bucket creado en B2**

---

## 🧩 Configuración del entorno

Crea un archivo llamado `.env` en la raíz del proyecto con el siguiente contenido:

```dotenv
# Estado del entorno
ENV_STATE=dev

# Base de datos de prod 
PROD_DATABASE_URL=anb-database.csxqmc4ywsa4.us-east-1.rds.amazonaws.com

# Credenciales de Backblaze B2
PROD_B2_KEY_ID=003579b919866a70000000001
PROD_B2_APPLICATION_KEY=K003SlZHT3Rr3ztIUNbPkFUF0Ue6PvU
PROD_B2_BUCKET_NAME=ANBbucket
```

---

## ▶️ Ejecución local

1. Instala dependencias:

   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
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
