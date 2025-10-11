# 🧠 FastAPI Tutorial – Cloud Storage Integration

Este proyecto implementa una API REST con **FastAPI** que permite subir archivos a **Backblaze B2** (servicio compatible con S3), autenticarse mediante JWT y manejar una base de datos MySQL o SQLite según el entorno.

---

## 🚀 Características principales

* Upload de archivos directamente a **Backblaze B2 Cloud Storage**
* Soporte para entornos **dev**, **test** y **prod**
* Configuración basada en **Pydantic Settings** y **dotenv (.env)**
* Conexión a base de datos vía SQLAlchemy (MySQL o SQLite)
* Tests automáticos con `pytest` y `pytest-asyncio`

---

## ⚙️ Requisitos previos

* **Python 3.11+**
* **MySQL** (para entorno de desarrollo)
* **Cuenta en Backblaze B2** con credenciales válidas
* **Acceso al bucket creado en B2**

---

## 🧩 Configuración del entorno

Crea un archivo llamado `.env` en la raíz del proyecto con el siguiente contenido:

```bash
# Estado del entorno
ENV_STATE=dev

# Base de datos de desarrollo
DEV_DATABASE_URL=sqlite:///data.db
# o para MySQL:
# DEV_DATABASE_URL=mysql+aiomysql://test_user:test_pass@localhost/test_db

# Credenciales de Backblaze B2
DEV_B2_KEY_ID=003579b919866a70000000001
DEV_B2_APPLICATION_KEY=K003SlZHT3Rr3ztIUNbPkFUF0Ue6PvU
DEV_B2_BUCKET_NAME=ANBbucket
```

📘 **Nota:**
El `DEV_B2_BUCKET_NAME` debe coincidir exactamente con el nombre de tu bucket creado en Backblaze B2.

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

   👉 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🧮 Comandos útiles

* Ejecutar tests:

  ```bash
  pytest
  ```

---

## ☁️ Backblaze B2 Setup (opcional)

1. Ingresa a tu cuenta en [Backblaze B2](https://www.backblaze.com/b2/cloud-storage.html)
2. Crea un bucket público o privado
3. Genera una **Application Key** con permisos:

   * `listFiles`, `writeFiles`, `deleteFiles`
   * `listBuckets`, `readBuckets`
4. Copia los valores `KeyID`, `ApplicationKey` y `BucketName` al archivo `.env`
