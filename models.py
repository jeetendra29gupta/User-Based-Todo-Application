import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.sql import func

load_dotenv()
SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL", "sqlite:///./todo-app.db")
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, echo=False)
Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    fullname = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True, server_default='1')
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    todos = relationship('Todo', back_populates='user', lazy=True)


class Todo(Base):
    __tablename__ = 'todos'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    is_done = Column(Boolean, default=False, server_default='0')
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    is_active = Column(Boolean, default=True, server_default='1')
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship('User', back_populates='todos')


def init_db():
    Base.metadata.create_all(bind=engine)
