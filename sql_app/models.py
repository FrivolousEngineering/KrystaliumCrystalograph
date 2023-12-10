from sqlalchemy import Boolean, Column, ForeignKey, Integer, String

from .database import Base


class KrystaliumSample(Base):
    __tablename__ = "krystalium_sample"

    id = Column(Integer, primary_key=True, index=True)
    rfid_id = Column(String, unique=True)

    # Although these are technically enums, we just validate
    negative_action = Column(String, nullable=False)
    negative_target = Column(String, nullable=False)

    positive_action = Column(String, nullable=False)
    positive_target = Column(String, nullable=False)


