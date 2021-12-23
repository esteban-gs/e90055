import sqlalchemy as db
from sqlalchemy.orm import column_property, relationship
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import BigInteger, DateTime, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy_json import mutable_json_type

from api.database import Base


class ProspectsFile(Base):
    """ProspectsFiles Table"""

    __tablename__ = "prospects_files"

    id = Column(BigInteger, primary_key=True, autoincrement=True, unique=True)
    fileAddress = Column(String, index=True, nullable=False)
    # JSONB postgres type: https://amercader.net/blog/beware-of-json-fields-in-sqlalchemy/
    preview = Column(mutable_json_type(dbtype=JSONB, nested=True), index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"))

    user = relationship("User", back_populates="prospects_files")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"{self.id}"
