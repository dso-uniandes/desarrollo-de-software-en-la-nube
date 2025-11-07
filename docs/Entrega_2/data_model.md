# Modelo de Datos

El modelo de datos de **ANB Rising Stars Showcase** se mantiene estable respecto a la primera entrega.  
En esta fase, las entidades siguen representando la gestión de **usuarios**, **videos** y **votos**,  
pero la base de datos ahora se encuentra **desplegada en Amazon RDS (PostgreSQL)**, garantizando disponibilidad y persistencia en la nube.

---

## 📘 Entidades principales

| Entidad | Descripción | Atributos principales |
|----------|--------------|----------------------|
| **User** | Representa a los jugadores registrados en la plataforma. | id, first_name, last_name, email, password, city, country |
| **Video** | Contiene la información de los videos subidos por los jugadores. | id, title, original_url, processed_url, status, uploaded_at, processed_at, user_id |
| **Vote** | Registra los votos emitidos por usuarios sobre los videos. | id, user_id, video_id, vote_type, created_at |

---

## 🔗 Relaciones entre entidades

- Un **User** puede subir varios **Videos** (`1..*`).
- Un **User** puede emitir varios **Votes** (`1..*`).
- Un **Video** puede recibir múltiples **Votes**, pero un **User** solo puede votar una vez por el mismo video (`UNIQUE(user_id, video_id)`).

---

## 🧱 Diagrama Entidad-Relación (ERD)

El siguiente diagrama muestra las entidades principales y sus relaciones, reflejando las claves primarias (PK), foráneas (FK) y restricciones.

<img alt="data_model" src="https://github.com/user-attachments/assets/3247f93b-d83a-4996-a85b-59145b31cb6a" />

