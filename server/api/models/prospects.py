from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import BigInteger, DateTime, Integer, String

from api.database import Base


class Prospect(Base):
    """Prospects Table"""

    __tablename__ = "prospects"

    id = Column(BigInteger, primary_key=True, autoincrement=True, unique=True)
    email = Column(String, primary_key=True, nullable=False)
    first_name = Column(String, index=True, nullable=False)
    last_name = Column(String, index=True, nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id"), primary_key=True)
    prospects_file_id = Column(BigInteger, ForeignKey("prospects_files.id"))

    user = relationship("User", back_populates="prospects", foreign_keys=[user_id])
    prospects_file = relationship("ProspectsFile", back_populates="prospects")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"{self.id} | {self.email}"
