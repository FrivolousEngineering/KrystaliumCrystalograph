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

    vulgarity = Column(String, nullable=False)

    # A sample is depleted if it was used to create a Refined Krystalium. From that point on, it can no longer
    # be used to create new samples.
    depleted = Column(Boolean, default=False)


class RefinedKrystalium(Base):
    __tablename__ = "refined_krystalium"

    id = Column(Integer, primary_key=True, index=True)
    rfid_id = Column(String, unique=True)

    # Although these are technically enums, we just validate
    primary_action = Column(String, nullable=False)
    primary_target = Column(String, nullable=False)

    secondary_action = Column(String, nullable=False)
    secondary_target = Column(String, nullable=False)

    purity = Column(String, nullable=False)


class BloodSample(Base):
    __tablename__ = "blood_sample"

    id = Column(Integer, primary_key = True, index = True)
    rfid_id = Column(String, unique = True)

    origin = Column(String, nullable = False)
    strength = Column(Integer, nullable = False)

    action = Column(String, nullable = False)
    target = Column(String, nullable = False)
