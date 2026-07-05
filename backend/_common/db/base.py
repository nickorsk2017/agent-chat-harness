"""SQLAlchemy 2.x declarative base shared by all ORM models."""

from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Common declarative base for every microservice's ORM models."""
