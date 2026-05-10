from datetime import datetime

from sqlalchemy import String, Boolean, Integer, ForeignKey, Text, DateTime, UniqueConstraint, BigInteger
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
import os
from dotenv import load_dotenv

load_dotenv()
engine = create_async_engine(url=os.getenv("PG_URL"))
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    phone_number: Mapped[str] = mapped_column(String(255), nullable=True)
    email_adress: Mapped[str] = mapped_column(String(255), nullable=True)
    email_password: Mapped[str] = mapped_column(String(255), nullable=True)
    include_prompt: Mapped[str] = mapped_column(String(255), nullable=True)
    exclude_prompt: Mapped[str] = mapped_column(String(255), nullable=True)
    save_midle: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    mail_connected: Mapped[bool] = mapped_column(Boolean, nullable=True)
    AI_connected: Mapped[bool] = mapped_column(Boolean, nullable=True)
    last_saved: Mapped[int] = mapped_column(BigInteger, nullable=True)

class Message(Base):
    __tablename__ = 'messages'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.telegram_id', ondelete='CASCADE'))
    uid: Mapped[int] = mapped_column(Integer)
    priority: Mapped[str] = mapped_column(String(50))
    importance_score: Mapped[int] = mapped_column(Integer)
    urgency_score: Mapped[int] = mapped_column(Integer)
    summary: Mapped[str] = mapped_column(Text)
    action_item: Mapped[str] = mapped_column(Text)
    deadline: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())

    __table_args__ = (
        UniqueConstraint('user_id', 'uid', name='_user_email_uid_uc'),
    )


class Consent(Base):
    __tablename__ = 'User_consents'
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    phone_number: Mapped[str] = mapped_column(String(255), nullable=False)
    action: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
    consent_text_version: Mapped[str] = mapped_column(String(255), nullable=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)