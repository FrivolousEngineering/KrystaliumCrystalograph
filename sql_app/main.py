from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def checkUniqueRFID(db, rfid_id: str):
    db_sample = crud.getSampleByRFID(db, rfid_id=rfid_id)
    if db_sample:
        raise HTTPException(status_code=400, detail="A krystalium sample with that RFID id has already been registered")

    # Check if the RFID is already used for a refined Krystalium
    db_refined = crud.getRefineKrystaliumdByRFID(db, rfid_id=rfid_id)
    if db_refined:
        raise HTTPException(status_code=400,
                            detail="A refined krystalium with that RFID id has already been registered")


@app.get("/samples/", response_model=list[schemas.KrystaliumSample])
def get_all_krystalium_samples(db: Session = Depends(get_db)):
    """
    Get all known (raw) Krystalium samples
    """
    return crud.getAllKrystaliumSamples(db)


@app.post("/samples/", response_model=schemas.KrystaliumSample)
def create_krystalium_sample(sample: schemas.KrystaliumSampleCreate, db: Session = Depends(get_db)):
    """
    Add a new (raw) Krystalium sample to the DB.
    """
    # Check if the RFID is already used for a sample
    checkUniqueRFID(db, sample.rfid_id)
    return crud.createSample(db=db, sample=sample)


@app.get("/refined/", response_model=list[schemas.RefinedKrystalium])
def get_all_refined_krystalium(db: Session = Depends(get_db)):
    return crud.getAllRefinedKrystalium(db)


@app.post("/refined/", response_model=schemas.RefinedKrystalium)
def create_refined_krystalium(refined_krystalium: schemas.RefinedKrystaliumCreate, db: Session = Depends(get_db)):
    # Check if the RFID is already used for a sample
    checkUniqueRFID(db, refined_krystalium.rfid_id)
    return crud.createRefinedKrystalium(db=db, refined_krystalium=refined_krystalium)
