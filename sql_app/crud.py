from typing import Optional

from sqlalchemy.orm import Session

from . import models, schemas


def getAllKrystaliumSamples(db: Session):
    return db.query(models.KrystaliumSample).all()


def getAllRefinedKrystalium(db: Session):
    return db.query(models.RefinedKrystalium).all()


def createSample(db: Session, sample: schemas.KrystaliumSampleCreate):
    # Just unpack all of it, we don't use any diffrent names, and DRY is a thing y'all.
    db_sample = models.KrystaliumSample(**sample.__dict__)
    db.add(db_sample)
    db.commit()
    db.refresh(db_sample)
    return db_sample


def createRefinedKrystalium(db: Session, refined_krystalium: schemas.RefinedKrystaliumCreate):
    # Just unpack all of it, we don't use any diffrent names, and DRY is a thing y'all.
    db_refined_krystalium = models.RefinedKrystalium(**refined_krystalium.__dict__)
    db.add(db_refined_krystalium)
    db.commit()
    db.refresh(db_refined_krystalium)
    return db_refined_krystalium


def createRefinedKrystaliumFromSamples(db: Session, positive_sample: models.KrystaliumSample, negative_sample: models.KrystaliumSample, refined_rfid_id: str):
    db_refined = models.RefinedKrystalium()
    db_refined.primary_action = positive_sample.positive_action
    db_refined.primary_target = negative_sample.negative_target

    db_refined.secondary_action = negative_sample.negative_action
    db_refined.secondary_target = positive_sample.positive_target
    db_refined.rfid_id = refined_rfid_id

    db.add(db_refined)
    db.commit()
    db.refresh(db_refined)
    return db_refined


def getSampleByRFID(db: Session, rfid_id: str) -> Optional[models.KrystaliumSample]:
    return db.query(models.KrystaliumSample).filter(models.KrystaliumSample.rfid_id == rfid_id).first()


def getRefineKrystaliumdByRFID(db: Session, rfid_id: str) -> Optional[models.KrystaliumSample]:
    return db.query(models.RefinedKrystalium).filter(models.RefinedKrystalium.rfid_id == rfid_id).first()

"""def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(email=user.email, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()


def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
    db_item = models.Item(**item.dict(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item"""