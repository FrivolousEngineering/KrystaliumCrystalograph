from sqlalchemy.orm import Session

from . import models, schemas


def getSamples(db: Session):
    return db.query(models.KrystaliumSample).all()


def createSample(db: Session, sample: schemas.KrystaliumSampleCreate):
    # Just unpack all of it, we don't use any diffrent names, and DRY is a thing y'all.
    db_sample = models.KrystaliumSample(**sample.__dict__)
    db.add(db_sample)
    db.commit()
    db.refresh(db_sample)
    return db_sample


def getSampleByRFID(db: Session, rfid_id: str):
    return db.query(models.KrystaliumSample).filter(models.KrystaliumSample.rfid_id == rfid_id).first()

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