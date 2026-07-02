import uuid
from datetime import datetime

from sqlalchemy import DateTime, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class SystemProfile(Base):
    __tablename__ = "system_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    profile_key: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    assistant_name: Mapped[str] = mapped_column(Text, nullable=False)
    assistant_description: Mapped[str] = mapped_column(Text, nullable=False)
    creator_name: Mapped[str] = mapped_column(Text, nullable=False)
    creator_description: Mapped[str] = mapped_column(Text, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
