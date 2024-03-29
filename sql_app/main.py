import uuid

from fastapi import Depends, FastAPI, HTTPException
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html
)
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine
from .schemas import BadRequestError, NotFoundError

models.Base.metadata.create_all(bind=engine)

# Mount the swagger & redoc stuff locally.
app = FastAPI(docs_url = None, redoc_url= None)
app.mount("/static", StaticFiles(directory="static"), name="static")


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
    db_refined = crud.getRefineKrystaliumByRFID(db, rfid_id=rfid_id)
    if db_refined:
        raise HTTPException(status_code=400,
                            detail=f"A refined Krystalium with the RFID id [{rfid_id}] has already been registered")


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    # This function is required to locally host the swagger API. This means that the docs will work without internet
    # connection
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )


@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    # This function is required to locally host the swagger API. This means that the docs will work without internet
    # connection
    return get_swagger_ui_oauth2_redirect_html()


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    # This function is required to locally host the swagger API. This means that the docs will work without internet
    # connection
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="/static/redoc.standalone.js",
    )


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


@app.delete("/samples/{rfid_id}", responses={404: {"model": NotFoundError}})
def delete_krystalium_sample_by_rfid(rfid_id: str, db: Session = Depends(get_db)):
    """
    Get a single refined Krystalium by RFID. If it doesn't find anything, you might want to try checking if it's
    a sample instead!
    """
    success = crud.deleteSampleByRFID(db, rfid_id=rfid_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Krystalium sample with RFID [{rfid_id}] was not found")


@app.post("/samples/", response_model=schemas.KrystaliumSample, responses={400: {"model": BadRequestError}})
def create_krystalium_sample(sample: schemas.KrystaliumSampleCreate, db: Session = Depends(get_db)):
    """
    Add a new (raw) Krystalium sample to the DB.
    """
    # Check if the RFID is already used for a sample
    checkUniqueRFID(db, sample.rfid_id)
    return crud.createSample(db=db, sample=sample)


@app.post("/sample/random/", response_model=schemas.KrystaliumSample, responses={400: {"model": BadRequestError}})
def create_random_krystalium_sample(sample: schemas.RandomKrystaliumSampleCreate, db: Session = Depends(get_db)):
    """
    Create random raw sample(s) of Krystalium.
    If the num_samples is larger than 1, you can't set the RFID, as each sample needs a unique one. The num_samples
    parameter is just there for debug purposes. If it is set, all the RFID tags will get a random rfid tag.

    If the vulgarity is not set, it will create a completely random sample. If it is set, its guaranteed to create a
    sample of that Vulgarity (or multiple samples if the num samples is set)
    """
    if sample.num_samples > 1 and sample.rfid_id is not None:
        raise HTTPException(status_code=400, detail=f"Impossible to create multiple RFID samples with the same RFID id")

    if sample.num_samples == 1:
        checkUniqueRFID(db, str(sample.rfid_id))
        return crud.createRandomSample(db, rfid_id = str(sample.rfid_id), vulgarity = sample.vulgarity)
    else:
        result = None
        for i in range(0, sample.num_samples):
            result = crud.createRandomSample(db, rfid_id = str(uuid.uuid4()), vulgarity = sample.vulgarity)
        return result


@app.post("/refined/random/", response_model=schemas.RefinedKrystalium, responses={400: {"model": BadRequestError}})
def create_random_refined_krystalium(refined_create: schemas.RandomRefinedKrystaliumCreate, db: Session = Depends(get_db)):
    """
    Create random refined Krystalium.
    If the num_samples is larger than 1, you can't set the RFID, as each sample needs a unique one. The num_samples
    parameter is just there for debug purposes. If it is set, all the RFID tags will get a random rfid tag.

    Note that the random purity is done by creating random samples. This means that a low purity is *much* more common
    than a high one!
    """
    if refined_create.num_samples > 1 and refined_create.rfid_id is not None:
        raise HTTPException(status_code=400, detail=f"Impossible to create multiple refined krystalium with the same RFID id")

    if refined_create.num_samples == 1:
        checkUniqueRFID(db, str(refined_create.rfid_id))
        return crud.createRandomRefined(db, rfid_id = str(refined_create.rfid_id), purity = refined_create.purity)
    else:
        result = None
        for i in range(0, refined_create.num_samples):
            result = crud.createRandomRefined(db, rfid_id = str(uuid.uuid4()), purity = refined_create.purity)
        return result


@app.get("/refined/", response_model=list[schemas.RefinedKrystalium])
def get_all_refined_krystalium(db: Session = Depends(get_db)):
    """
    Get a list of all known refined Krystalium
    """
    return crud.getAllRefinedKrystalium(db)


@app.get("/refined/{rfid_id}", response_model=schemas.RefinedKrystalium, responses={404: {"model": NotFoundError}})
def get_refined_krystalium_by_rfid(rfid_id: str, db: Session = Depends(get_db)):
    """
    Get a single refined Krystalium by RFID. If it doesn't find anything, you might want to try checking if it's
    a sample instead!
    """
    db_refined = crud.getRefineKrystaliumByRFID(db, rfid_id=rfid_id)
    if not db_refined:
        raise HTTPException(status_code=404, detail=f"Refined Krystalium with RFID [{rfid_id}] was not found")
    return db_refined


@app.delete("/refined/{rfid_id}", responses={404: {"model": NotFoundError}})
def delete_refined_krystalium_by_rfid(rfid_id: str, db: Session = Depends(get_db)):
    """
    Get a single refined Krystalium by RFID. If it doesn't find anything, you might want to try checking if it's
    a sample instead!
    """
    success = crud.deleteRefinedKrystaliumByRFID(db, rfid_id=rfid_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Refined Krystalium with RFID [{rfid_id}] was not found")


@app.post("/refined/", response_model=schemas.RefinedKrystalium, responses={400: {"model": BadRequestError}})
def create_refined_krystalium(refined_krystalium: schemas.RefinedKrystaliumCreate, db: Session = Depends(get_db)):
    # Check if the RFID is already used for a sample
    checkUniqueRFID(db, refined_krystalium.rfid_id)
    return crud.createRefinedKrystalium(db=db, refined_krystalium=refined_krystalium)


@app.post("/refined/create_from_samples/", response_model=schemas.RefinedKrystalium, responses={400: {"model": BadRequestError}})
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
                            detail=f"The samples must have at least one property different from each other")
    # The provided refined Krystalium rfid id must be unique
    checkUniqueRFID(db, creation_request.refined_krystalium_rfid_id)

    # We're good to go!
    return crud.createRefinedKrystaliumFromSamples(db, negative_sample=db_negative_sample, positive_sample=db_positive_sample, refined_rfid_id=creation_request.refined_krystalium_rfid_id)


@app.get("/blood", response_model = list[schemas.BloodSample], responses = {400: {"model": BadRequestError}})
def get_all_blood_samples(db: Session = Depends(get_db)):
    """
    Get a list of all blood samples.
    """
    return crud.getAllBloodSamples(db)


@app.post("/blood", response_model = schemas.BloodSample, responses = {400: {"model": BadRequestError}})
def create_blood_sample(sample: schemas.BloodSampleCreate, db: Session = Depends(get_db)):
    """
    Create a new blood sample.
    """
    checkUniqueRFID(db, sample.rfid_id)
    return crud.createBloodSample(db = db, blood_sample = sample)


@app.get("/blood/{rfid_id}", response_model = schemas.BloodSample, responses = {400: {"model": BadRequestError}})
def get_blood_sample_by_rfid(rfid_id: str, db: Session = Depends(get_db)):
    """
    Get a single blood sample by RFID ID.
    """
    return crud.getBloodSampleByRFID(db, rfid_id)


# @app.post("/blood/random", response_model = schemas.BloodSample, responses = {400: {"model": BadRequestError}})
# def create_random_blood_sample(blood_create: schemas.RandomBloodSampleCreate, db: Session = Depends(get_db)):
#     """
#     Create one or more random blood samples.
#     """
