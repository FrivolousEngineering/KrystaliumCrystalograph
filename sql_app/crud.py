from typing import Optional

from sqlalchemy.orm import Session

from . import models, schemas
from .OpposingTraitController import OpposingTraitController

from .schemas import Vulgarity, Target, Action, Purity
import random


opposing_targets = OpposingTraitController()
opposing_targets.addPair(Target.mind, Target.flesh)
opposing_targets.addPair(Target.flesh, Target.plant)
opposing_targets.addPair(Target.gas, Target.solid)
opposing_targets.addPair(Target.gas, Target.liquid)
opposing_targets.addPair(Target.liquid, Target.gas)
opposing_targets.addPair(Target.krystal, Target.energy)


opposing_actions = OpposingTraitController()
opposing_actions.addPair(Action.expanding, Action.contracting)
opposing_actions.addPair(Action.conducting, Action.insulating)
opposing_actions.addPair(Action.fortifying, Action.deteriorating)
opposing_actions.addPair(Action.creating, Action.destroying)
opposing_actions.addPair(Action.increasing, Action.decreasing)
opposing_actions.addPair(Action.absorbing, Action.releasing)
opposing_actions.addPair(Action.heating, Action.cooling)
opposing_actions.addPair(Action.solidifying, Action.lightening)
opposing_actions.addPair(Action.lightening, Action.encumbering)

action_list = list(Action)
target_list = list(Target)


def getAllKrystaliumSamples(db: Session):
    return db.query(models.KrystaliumSample).all()


def getAllRefinedKrystalium(db: Session):
    return db.query(models.RefinedKrystalium).all()


def findVulgarityFromProperties(positive_action, negative_action, positive_target, negative_target, *args, **kwargs) -> Vulgarity:
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
    db_sample.vulgarity = findVulgarityFromProperties(**sample.__dict__)
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

    db_refined.purity = Purity.getByScore(Vulgarity.getScore(positive_sample.vulgarity) + Vulgarity.getScore(negative_sample.vulgarity))

    db.add(db_refined)
    db.commit()
    db.refresh(db_refined)
    return db_refined


def generateOpposingTargetPair():
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


def createRandomActionPair():
    return random.choice(action_list), random.choice(action_list)


def createRandomTargetPair():
    return random.choice(target_list), random.choice(target_list),


def createInvariantTargetPair():
    result = random.choice(target_list)
    return result, result


def createInvariantActionPair():
    result = random.choice(action_list)
    return result, result


def createRandomRefined(db: Session, rfid_id: str, purity: Optional[Purity]):
    db_refined = models.RefinedKrystalium()

    if purity is None:
        # In order to properly simulate the right distribution of purity, we generate two random samples and combine
        # them.
        positive_sample = _createRandomSample(vulgarity=None)
        negative_sample = _createRandomSample(vulgarity=None)

        db_refined.primary_action = positive_sample.positive_action
        db_refined.primary_target = negative_sample.negative_target
        db_refined.secondary_action = negative_sample.negative_action
        db_refined.secondary_target = positive_sample.positive_target

        db_refined.purity = Purity.getByScore(Vulgarity.getScore(positive_sample.vulgarity) + Vulgarity.getScore(negative_sample.vulgarity))
    else:
        db_refined.primary_action, db_refined.secondary_action = createRandomActionPair()
        db_refined.primary_target, db_refined.secondary_target = createRandomTargetPair()
        db_refined.purity = purity
    db_refined.rfid_id = rfid_id
    db.add(db_refined)
    db.commit()
    return db_refined


def _createRandomSample(vulgarity: Optional[Vulgarity]) -> models.KrystaliumSample:
    """
    Create a random sample without adding it to the database or comitting it.
    :param vulgarity: The vulgarity of the sample to create.
    :return: The created sample
    """
    db_sample = models.KrystaliumSample()
    match vulgarity:
        case None:
            # Completely random
            db_sample.negative_action, db_sample.positive_action = createRandomActionPair()
            db_sample.negative_target, db_sample.positive_target = createRandomTargetPair()
        case Vulgarity.precious:
            db_sample.negative_action, db_sample.positive_action = createInvariantActionPair()
            db_sample.negative_target, db_sample.positive_target = createInvariantTargetPair()
        case Vulgarity.high_semi_precious | Vulgarity.low_semi_precious:
            # One of the pairs needs to be the same, randomly decide which one
            action_invariant = bool(random.getrandbits(1))
            if action_invariant:
                db_sample.negative_action, db_sample.positive_action = createInvariantActionPair()
            else:
                db_sample.negative_target, db_sample.positive_target = createInvariantTargetPair()
            if vulgarity == Vulgarity.high_semi_precious:
                if action_invariant:
                    db_sample.negative_target, db_sample.positive_target = generateOpposingTargetPair()
                else:
                    db_sample.negative_action, db_sample.positive_action = generateOpposingActionPair()
            else:  # Low semi precious
                if action_invariant:
                    db_sample.negative_target, db_sample.positive_target = generateConflictingTargetPair()
                else:
                    db_sample.negative_action, db_sample.positive_action = generateConflictingActionPair()
        case Vulgarity.high_mundane:
            db_sample.negative_target, db_sample.positive_target = generateOpposingTargetPair()
            db_sample.negative_action, db_sample.positive_action = generateOpposingActionPair()
        case vulgarity.low_mundane:
            # Randomly generate if we want action or target to be conflicting
            action_conflicting = bool(random.getrandbits(1))
            if action_conflicting:
                db_sample.negative_action, db_sample.positive_action = generateConflictingActionPair()
                db_sample.negative_target, db_sample.positive_target = generateOpposingTargetPair()
            else:
                db_sample.negative_action, db_sample.positive_action = generateOpposingActionPair()
                db_sample.negative_target, db_sample.positive_target = generateConflictingTargetPair()
        case Vulgarity.vulgar:
            db_sample.negative_target, db_sample.positive_target = generateConflictingTargetPair()
            db_sample.negative_action, db_sample.positive_action = generateConflictingActionPair()

    db_sample.vulgarity = findVulgarityFromProperties(db_sample.positive_action, db_sample.negative_action,
                                                      db_sample.positive_target,
                                                      db_sample.negative_target)
    if vulgarity is not None:
        assert db_sample.vulgarity == vulgarity, "Calculated vulgarity and provided vulgarity must be the same!"

    return db_sample


def createRandomSample(db: Session, rfid_id: str, vulgarity: Optional[Vulgarity]):
    db_sample = _createRandomSample(vulgarity)
    db_sample.rfid_id = rfid_id

    db.add(db_sample)
    db.commit()
    db.refresh(db_sample)
    return db_sample


def getSampleByRFID(db: Session, rfid_id: str) -> Optional[models.KrystaliumSample]:
    return db.query(models.KrystaliumSample).filter(models.KrystaliumSample.rfid_id == rfid_id).first()


def deleteSampleByRFID(db: Session, rfid_id: str) -> bool:
    """

    :param db:
    :param rfid_id: The RFID id of the sample that needs to be deleted
    :return: True if it was able to delete it, false otherwise
    """
    sample = getSampleByRFID(db, rfid_id)
    if sample:
        db.delete(sample)
        db.commit()
        return True
    return False


def deleteRefinedKrystaliumByRFID(db: Session, rfid_id: str) -> bool:
    """
    :param db:
    :param rfid_id: The RFID id of the refined Krystalium that needs to be deleted
    :return: True if it was able to delete it, false otherwise
    """
    refined = getRefineKrystaliumByRFID(db, rfid_id)
    if refined:
        db.delete(refined)
        db.commit()
        return True
    return False


def getRefineKrystaliumByRFID(db: Session, rfid_id: str) -> Optional[models.KrystaliumSample]:
    return db.query(models.RefinedKrystalium).filter(models.RefinedKrystalium.rfid_id == rfid_id).first()
