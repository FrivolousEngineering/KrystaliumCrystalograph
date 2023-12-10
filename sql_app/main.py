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


@app.get("/samples/", response_model = list[schemas.KrystaliumSample])
def read_samples(db: Session = Depends(get_db)):
    """
    Get all known (raw) Krystalium samples
    """
    samples = crud.getSamples(db)
    return samples


@app.post("/samples/", response_model=schemas.KrystaliumSample)
def create_sample(sample: schemas.KrystaliumSampleCreate,  db: Session = Depends(get_db)):
    """
    Add a new (raw) Krystalium sample to the DB.
    """
    db_sample = crud.getSampleByRFID(db, rfid_id=sample.rfid_id)
    if db_sample:
        raise HTTPException(status_code=400, detail="A sample with that RFID id has already been registered")
    return crud.createSample(db=db, sample=sample)
