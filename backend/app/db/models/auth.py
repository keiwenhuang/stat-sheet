from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from backend.app.db.database import Base
from backend.app.db.models.base import BaseMixin, TimestampMixin


# Association table for many-to-many relationship between users and roles
user_role = Table(
    "user_role",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("user.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("role.id"), primary_key=True),
)


class User(Base, BaseMixin, TimestampMixin):
    """User model for authentication"""

    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)

    # Relationships
    roles = relationship("Role", secondary=user_role, back_populates="users")
    stat_lines = relationship("StatLine", back_populates="entered_by_user")


class Role(Base, BaseMixin, TimestampMixin):
    """Role model for role-based access control"""

    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))

    # Relationships
    users = relationship("User", secondary=user_role, back_populates="roles")
