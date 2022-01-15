import enum
import sqlalchemy as db
from sqlalchemy.orm import column_property, relationship
from sqlalchemy.sql.expression import false
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import BigInteger, DateTime, Enum, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy_json import mutable_json_type

from api.database import Base


class ImportStatus(enum.Enum):
    pending = "pending"
    complete = "complete"
    failed = "failed"


class ProspectsFile(Base):
    """ProspectsFiles Table"""

    __tablename__ = "prospects_files"

    id = Column(BigInteger, primary_key=True, autoincrement=True, unique=True)
    file_address = Column(String, index=True, nullable=False)
    file_rows = Column(BigInteger)
    total_data_rows = Column(BigInteger)
    status = Column(Enum(ImportStatus), nullable=false)
    user_id = Column(BigInteger, ForeignKey("users.id"))

    user = relationship("User", back_populates="prospects_files")

    prospects = relationship("Prospect", back_populates="prospects_file")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"{self.id}"
