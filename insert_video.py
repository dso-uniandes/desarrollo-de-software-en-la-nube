import asyncio
from datetime import datetime
from storeapi.database import database, video_table, vote_table
from sqlalchemy import Table, Column, Integer, String, MetaData

# Define la tabla de usuarios si no está definida
metadata = MetaData()

user_table = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
)

async def insert_users_and_videos_with_votes():
    # Conectar a la base de datos
    await database.connect()

    try:
        # Lista de usuarios a insertar
        users = [
            {"id": 1, "name": "Usuario 1"},
            {"id": 2, "name": "Usuario 2"},
            {"id": 3, "name": "Usuario 3"},
        ]

        # Insertar usuarios
        await database.execute_many(user_table.insert(), users)
        print("Usuarios insertados correctamente.")

        # Lista de videos a insertar
        videos = [
            {
                "user_id": 1,
                "title": "Video 1",
                "original_url": "https://example.com/video1.mp4",
                "processed_url": None,
                "status": "uploaded",
                "uploaded_at": datetime.now(),
                "processed_at": None,
            },
            {
                "user_id": 2,
                "title": "Video 2",
                "original_url": "https://example.com/video2.mp4",
                "processed_url": None,
                "status": "uploaded",
                "uploaded_at": datetime.now(),
                "processed_at": None,
            },
            {
                "user_id": 3,
                "title": "Video 3",
                "original_url": "https://example.com/video3.mp4",
                "processed_url": None,
                "status": "uploaded",
                "uploaded_at": datetime.now(),
                "processed_at": None,
            },
        ]

        # Insertar videos y obtener sus IDs
        video_ids = []
        for video in videos:
            query = video_table.insert().values(**video).returning(video_table.c.id)
            video_id = await database.execute(query)
            video_ids.append(video_id)

        print(f"Videos insertados con IDs: {video_ids}")

        # Insertar votos para los videos
        votes = []
        for video_id in video_ids:
            # Generar votos para cada video
            for user_id in range(1, 6):  # 5 votos por video
                votes.append({
                    "video_id": video_id,
                    "user_id": user_id,
                    "created_at": datetime.now(),
                })

        # Insertar los votos en la base de datos
        await database.execute_many(vote_table.insert(), votes)

        print(f"Votos insertados para los videos: {len(votes)} votos en total")

    except Exception as e:
        print(f"Error al insertar usuarios, videos o votos: {e}")

    finally:
        # Desconectar de la base de datos
        await database.disconnect()

# Ejecutar el script
if __name__ == "__main__":
    asyncio.run(insert_users_and_videos_with_votes())