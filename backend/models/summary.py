import enum
import uuid

from sqlalchemy import Enum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class SummaryLevel(str, enum.Enum):
    CHUNK = "chunk"
    CHAPTER = "chapter"
    BOOK = "book"


class Summary(Base):
    __tablename__ = "summaries"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    level: Mapped[SummaryLevel] = mapped_column(
        Enum(SummaryLevel, name="summary_level"),
        nullable=False,
        index=True,
    )
    reference_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    summary: Mapped[str] = mapped_column(Text, nullable=False)

