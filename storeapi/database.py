import databases
import sqlalchemy
import asyncio

from storeapi.config import config

metadata = sqlalchemy.MetaData()

post_table = sqlalchemy.Table(
    "posts",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("body", sqlalchemy.Text),
    sqlalchemy.Column("user_id", sqlalchemy.ForeignKey("users.id"), nullable=False)
)

user_table = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("first_name", sqlalchemy.String(255), nullable=False),
    sqlalchemy.Column("last_name", sqlalchemy.String(255), nullable=False),
    sqlalchemy.Column("email", sqlalchemy.String(255), unique=True, nullable=False),
    sqlalchemy.Column("password", sqlalchemy.String(255), nullable=False),
    sqlalchemy.Column("city", sqlalchemy.String(255), nullable=False),
    sqlalchemy.Column("country", sqlalchemy.String(255), nullable=False),
)

video_table = sqlalchemy.Table(
    "videos",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("user_id", sqlalchemy.ForeignKey("users.id"), nullable=False),
    sqlalchemy.Column("title", sqlalchemy.String(255), nullable=False),
    sqlalchemy.Column("original_url", sqlalchemy.String(500), nullable=False),
    sqlalchemy.Column("processed_url", sqlalchemy.String(500), nullable=True),
    sqlalchemy.Column("status", sqlalchemy.String(50), nullable=False),
    sqlalchemy.Column("uploaded_at", sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column("processed_at", sqlalchemy.DateTime, nullable=True),
)

video_vote_table = sqlalchemy.Table(
    "video_votes",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("video_id", sqlalchemy.ForeignKey("videos.id"), nullable=False),
    sqlalchemy.Column(
        "created_at",
        sqlalchemy.DateTime,
        server_default=sqlalchemy.func.now(),
        nullable=False,
    ),
)

comment_table = sqlalchemy.Table(
    "comments",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("body", sqlalchemy.Text),
    sqlalchemy.Column("post_id", sqlalchemy.ForeignKey("posts.id"), nullable=False),
    sqlalchemy.Column("user_id", sqlalchemy.ForeignKey("users.id"), nullable=False)
)

vote_table = sqlalchemy.Table(
    "votes",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("user_id", sqlalchemy.ForeignKey("users.id"), nullable=False),
    sqlalchemy.Column("video_id", sqlalchemy.ForeignKey("videos.id"), nullable=False),
    sqlalchemy.Column("vote_type", sqlalchemy.String(50), nullable=False),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, default=sqlalchemy.func.now()),
    sqlalchemy.UniqueConstraint("user_id", "video_id", name="unique_user_video_vote")
)

sync_url = config.DATABASE_URL.replace("mysql+aiomysql://", "mysql+pymysql://")
engine = sqlalchemy.create_engine(sync_url)

database = databases.Database(config.DATABASE_URL, force_rollback=config.DB_FORCE_ROLL_BACK)

def create_tables():
    metadata.create_all(engine)

async def create_tables_async():
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, metadata.create_all, engine)
