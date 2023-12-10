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
        raise HTTPException(status_code=400, detail=f"A Krystalium sample with the RFID id [{rfid_id}] has already been registered")

    # Check if the RFID is already used for a refined Krystalium
    db_refined = crud.getRefineKrystaliumdByRFID(db, rfid_id=rfid_id)
    if db_refined:
        raise HTTPException(status_code=400,
                            detail=f"A refined Krystalium with the RFID id [{rfid_id}] has already been registered")


@app.get("/samples/", response_model=list[schemas.KrystaliumSample])
def get_all_krystalium_samples(db: Session = Depends(get_db)):
    """
    Get all known (raw) Krystalium samples
    """
    return crud.getAllKrystaliumSamples(db)


@app.get("/samples/{rfid_id}", response_model=schemas.KrystaliumSample)
def get_krystalium_sample_by_rfid(rfid_id: str, db: Session = Depends(get_db)):
    """
    Get a single raw Krystalium sample by RFID. If it doesn't find anything, you might want to try checking if it's
    refined Krystalium instead!
    """
    db_sample = crud.getSampleByRFID(db, rfid_id=rfid_id)
    if not db_sample:
        raise HTTPException(status_code=404, detail=f"Krystalium Sample with RFID [{rfid_id}] was not found")
    return db_sample


@app.post("/samples/", response_model=schemas.KrystaliumSample)
def create_krystalium_sample(sample: schemas.KrystaliumSampleCreate, db: Session = Depends(get_db)):
    """
    Add a new (raw) Krystalium sample to the DB.
    """
    # Check if the RFID is already used for a sample
    checkUniqueRFID(db, sample.rfid_id)
    return crud.createSample(db=db, sample=sample)


@app.post("/sample/random/", response_model=schemas.KrystaliumSample)
def create_random_krystalium_sample(sample: schemas.RandomKrystaliumSampleCreate, db: Session = Depends(get_db)):
    checkUniqueRFID(db, sample.rfid_id)

    return crud.createRandomSample(db, rfid_id = sample.rfid_id, vulgarity = sample.vulgarity)


@app.get("/refined/", response_model=list[schemas.RefinedKrystalium])
def get_all_refined_krystalium(db: Session = Depends(get_db)):
    """
    Get a list of all known refined Krystalium
    """
    return crud.getAllRefinedKrystalium(db)


@app.get("/refined/{rfid_id}", response_model=schemas.RefinedKrystalium)
def get_refined_krystalium_by_rfid(rfid_id: str, db: Session = Depends(get_db)):
    """
    Get a single refined Krystalium by RFID. If it doesn't find anything, you might want to try checking if it's
    a sample instead!
    """
    db_refined = crud.getRefineKrystaliumdByRFID(db, rfid_id=rfid_id)
    if not db_refined:
        raise HTTPException(status_code=404, detail=f"Refined Krystalium with RFID [{rfid_id}] was not found")
    return db_refined


@app.post("/refined/", response_model=schemas.RefinedKrystalium)
def create_refined_krystalium(refined_krystalium: schemas.RefinedKrystaliumCreate, db: Session = Depends(get_db)):
    # Check if the RFID is already used for a sample
    checkUniqueRFID(db, refined_krystalium.rfid_id)
    return crud.createRefinedKrystalium(db=db, refined_krystalium=refined_krystalium)


@app.post("/refined/create_from_samples/", response_model=schemas.RefinedKrystalium)
def create_refined_crystalium_from_samples(creation_request: schemas.RefinedKrystaliumFromSample, db: Session = Depends(get_db)):
    """
    Combine two raw Krystalium samples into a refined Krystalium sample.

    This can fail in the following situations:

    1. You try to use the exact same sample (so scan same RFID twice)
    2. You use two samples that have the exact same properties
    3. The refined krystalium rfid is already used by something else
    """
    if creation_request.positive_sample_rfid_id == creation_request.negative_sample_rfid_id:
        raise HTTPException(status_code=400,
                            detail=f"You must use different samples")

    db_positive_sample = crud.getSampleByRFID(db, rfid_id=creation_request.positive_sample_rfid_id)
    if not db_positive_sample:
        raise HTTPException(status_code=400, detail=f"Krystalium Sample for the positive slot with RFID [{creation_request.positive_sample_rfid_id}] was not found")

    if db_positive_sample.depleted:
        raise HTTPException(status_code=400, detail=f"The positive sample is depleted, so it can't be used")

    db_negative_sample = crud.getSampleByRFID(db, rfid_id=creation_request.negative_sample_rfid_id)
    if not db_negative_sample:
        raise HTTPException(status_code=400,
                            detail=f"Krystalium Sample for the negative slot with RFID [{creation_request.negative_sample_rfid_id}] was not found")

    if db_negative_sample.depleted:
        raise HTTPException(status_code=400, detail=f"The negative sample is depleted, so it can't be used")

    # Check if the samples are exactly the same (eg have same targets & actions)
    if db_positive_sample.positive_target == db_negative_sample.positive_target and \
            db_positive_sample.negative_target == db_negative_sample.negative_target and \
            db_positive_sample.positive_action == db_negative_sample.positive_action and \
            db_positive_sample.negative_action == db_negative_sample.negative_action:
        raise HTTPException(status_code=400,
                            detail=f"The samples must have at least one property different from eachother")
    # The provided refined Krystalium rfid id must be unique
    checkUniqueRFID(db, creation_request.refined_krystalium_rfid_id)

    # We're good to go!
    return crud.createRefinedKrystaliumFromSamples(db, negative_sample=db_negative_sample, positive_sample=db_positive_sample, refined_rfid_id=creation_request.refined_krystalium_rfid_id)


