from typing import Optional

from sqlalchemy.orm import Session

from . import models, schemas
from .OpposingTraitController import OpposingTraitController

from .schemas import Vulgarity, Target, Action
import random


opposing_targets = OpposingTraitController()
opposing_targets.addPair(Target.mind, Target.flesh)
opposing_targets.addPair(Target.gas, Target.solid)
opposing_targets.addPair(Target.gas, Target.liquid)
opposing_targets.addPair(Target.liquid, Target.gas)

opposing_actions = OpposingTraitController()
opposing_actions.addPair(Action.strengthen, Action.deteriorate)
opposing_actions.addPair(Action.heat, Action.cool)
opposing_actions.addPair(Action.solidify, Action.lighten)

action_list = list(Action)
target_list = list(Target)

def getAllKrystaliumSamples(db: Session):
    return db.query(models.KrystaliumSample).all()


def getAllRefinedKrystalium(db: Session):
    return db.query(models.RefinedKrystalium).all()


def findVulgarity(positive_action, negative_action, positive_target, negative_target, *args, **kwargs) -> Vulgarity:
    target_invariant = positive_target == negative_target
    action_invariant = positive_action == negative_action

    if target_invariant and action_invariant:
        return Vulgarity.precious

    is_action_opposing = opposing_actions.areOpposed(positive_action, negative_action)

    is_target_opposing = opposing_targets.areOpposed(positive_target.value, negative_target)

    if target_invariant or action_invariant:
        # It's semi-precious, but now to figure out if it's high or low!
        if target_invariant:
            return Vulgarity.high_semi_precious if is_action_opposing else Vulgarity.low_semi_precious
        else:
            return Vulgarity.high_semi_precious if is_target_opposing else Vulgarity.low_semi_precious

    if not is_action_opposing and not is_target_opposing:
        return Vulgarity.vulgar

    # Now to find out if it's high or low mundane
    if is_action_opposing and is_target_opposing:
        return Vulgarity.high_mundane

    # Only one left, so it's low mundane
    return Vulgarity.low_mundane


def createSample(db: Session, sample: schemas.KrystaliumSampleCreate):
    # Just unpack all of it, we don't use any diffrent names, and DRY is a thing y'all.
    db_sample = models.KrystaliumSample(**sample.__dict__)
    db_sample.vulgarity = findVulgarity(**sample.__dict__)
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

    positive_sample.depleted = True
    negative_sample.depleted = True

    db.add(db_refined)
    db.commit()
    db.refresh(db_refined)
    return db_refined


def generateOpposingTargetPair():
    print(opposing_targets.getAllKnownTraits())
    value_1 = random.choice(opposing_targets.getAllKnownTraits())
    value_2 = random.choice(opposing_targets.getOpposites(value_1))
    return value_1, value_2


def generateOpposingActionPair():
    value_1 = random.choice(opposing_actions.getAllKnownTraits())
    value_2 = random.choice(opposing_actions.getOpposites(value_1))
    return value_1, value_2


def generateConflictingActionPair():
    # Pick the first value completely random
    value_1 = random.choice(action_list)

    # Create a new candidate list but exclude any possible opposites and the original selected value (as this would
    # make it not conflicting!)
    actions = list(set(action_list) - set(opposing_actions.getOpposites(value_1) + [value_1]))
    value_2 = random.choice(actions)
    return value_1, value_2


def generateConflictingTargetPair():
    # Pick the first value completely random
    value_1 = random.choice(target_list)

    # Create a new candidate list but exclude any possible opposites and the original selected value (as this would
    # make it not conflicting!)
    targets = list(set(target_list) - set(opposing_targets.getOpposites(value_1) + [value_1]))
    value_2 = random.choice(targets)
    return value_1, value_2


def createRandomSample(db: Session, rfid_id: str, vulgarity: Optional[Vulgarity]):
    db_sample = models.KrystaliumSample()
    db_sample.rfid_id = rfid_id

    if vulgarity is None:
        # Completely random
        db_sample.negative_action = random.choice(action_list)
        db_sample.positive_action = random.choice(action_list)

        db_sample.negative_target = random.choice(target_list)
        db_sample.positive_target = random.choice(target_list)
    else:
        if vulgarity == Vulgarity.precious:
            db_sample.negative_action = random.choice(action_list)
            db_sample.positive_action = db_sample.negative_action

            db_sample.negative_target = random.choice(target_list)
            db_sample.positive_target = db_sample.negative_target

        if vulgarity == Vulgarity.high_semi_precious or vulgarity == Vulgarity.low_semi_precious:
            # One of the pairs needs to be the same, randomly decide which one
            action_invariant = bool(random.getrandbits(1))
            if action_invariant:
                db_sample.negative_action = random.choice(action_list)
                db_sample.positive_action = db_sample.negative_action
            else:
                db_sample.negative_target = random.choice(target_list)
                db_sample.positive_target = db_sample.negative_target
            if vulgarity == Vulgarity.high_semi_precious:
                if action_invariant:
                    # We need to generate a target that has an opposite
                    db_sample.negative_target, db_sample.positive_target = generateOpposingTargetPair()
                else:
                    db_sample.negative_action, db_sample.positive_action = generateOpposingActionPair()
            else:
                if action_invariant:
                    db_sample.negative_target, db_sample.positive_target = generateConflictingTargetPair()
                else:
                    db_sample.negative_action, db_sample.positive_action = generateConflictingActionPair()

        if vulgarity == Vulgarity.high_mundane:
            db_sample.negative_target, db_sample.positive_target = generateOpposingTargetPair()
            db_sample.negative_action, db_sample.positive_action = generateOpposingActionPair()
        if vulgarity == vulgarity.low_mundane:
            action_conflicting = bool(random.getrandbits(1))
            if action_conflicting:
                db_sample.negative_action, db_sample.positive_action = generateConflictingActionPair()
                db_sample.negative_target, db_sample.positive_target = generateOpposingTargetPair()
            else:
                db_sample.negative_action, db_sample.positive_action = generateOpposingActionPair()
                db_sample.negative_target, db_sample.positive_target = generateConflictingTargetPair()
        if vulgarity == Vulgarity.vulgar:
            db_sample.negative_target, db_sample.positive_target = generateConflictingTargetPair()
            db_sample.negative_action, db_sample.positive_action = generateConflictingActionPair()

    db_sample.vulgarity = findVulgarity(db_sample.positive_action, db_sample.negative_action, db_sample.positive_target,
                                        db_sample.negative_target)
    if vulgarity:
        assert db_sample.vulgarity == vulgarity, "Calculated vulgarity and provided vulgarity must be the same!"
    db.add(db_sample)
    db.commit()
    db.refresh(db_sample)
    return db_sample


def getSampleByRFID(db: Session, rfid_id: str) -> Optional[models.KrystaliumSample]:
    return db.query(models.KrystaliumSample).filter(models.KrystaliumSample.rfid_id == rfid_id).first()


def getRefineKrystaliumdByRFID(db: Session, rfid_id: str) -> Optional[models.KrystaliumSample]:
    return db.query(models.RefinedKrystalium).filter(models.RefinedKrystalium.rfid_id == rfid_id).first()
