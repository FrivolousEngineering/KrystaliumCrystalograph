from typing import Optional

from pydantic import BaseModel, Field
from enum import Enum


class Action(str, Enum):
    """
    All the actions that a sample of raw Krystalium can have. Each sample of raw Krystalium has two actions;
    One positively charged action and one negatively charged action.

    In the case of refined Krystalium, it no longer has negative / positive charge, only two pairs of actions & targets.
    """
    expanding: str = "Expanding"
    conducting: str = "Conducting"
    deteriorate: str = "Deteriorate"
    creating: str = "Creating"
    increasing: str = "Increasing"
    absorbing: str = "Absorbing"
    solidify: str = "Solidify"
    lighten: str = "Lighten"
    connecting: str = "Connecting"
    encumber: str = "Encumber"
    strengthen: str = "Strengthen"
    heat: str = "Heat"
    cool: str = "Cool"


class Target(str, Enum):
    """
    All the targets that a sample of raw Krystalium can have. Each sample of raw Krystalium has two targets; One positively
    charged target and one negatively charged target.

    In the case of refined Krystalium, it no longer has negative / positive charge, only two pairs of actions & targets.
    """
    flesh: str = "Flesh"
    mind: str = "Mind"
    gas: str = "Gas"
    solid: str = "Solid"
    liquid: str = "Liquid"
    energy: str = "Energy"
    light: str = "Light"
    sound: str = "Sound"


class Vulgarity(str, Enum):
    """
    Vulgarity defines how stable a Krystalium sample is, with precious being most stable and vulgar being the least stable.

    When two traits (action or target) are the same, we call this 'invariant'.

    When two traits (action or target) are somewhat related (mind vs body, solid vs gas) we call it opposing. This is
    less stable than invariant, but more stable than related.

    When two traits (action or target) are not related (not opposing and not the same), we call this conflicted.

    When both pairs are invariant, the substance is precious.
    When one of the pairs is invariant, it's semi-precious. High semi-precious have the other pair opposing, low has
    the other pair conflicting

    When all pairs are conflicting, it's vulgar.

    When there are no invariants, but one or two opposing, it's mundane (two opposing being high, one low)
    """
    precious = "Precious"
    high_semi_precious = "High Semi-Precious"
    low_semi_precious = "Low Semi-Precious"
    high_mundane = "High Mundane"
    low_mundane = "Low Mundane"
    vulgar = "Vulgar"


class KrystaliumSampleBase(BaseModel):
    """
    Represents a raw Krystalium sample. Raw samples don't directly do something, instead they have two sets of actions
    and targets (negative and positive). When two samples are combined, one of the samples is places in the negative
    slot and the other in the positive slot. This will result in two sets of properties;

    The action of the negative is combined with the target of the positive and the target of the negative is combined
    with the action of the positive.
    """
    negative_action: Action = Field(description = "The negative action of the Krystalium sample")
    negative_target: Target = Field(description = "The negative target of the Krystalium sample")
    positive_action: Action = Field(description = "The positive action of the Krystalium sample")
    positive_target: Target = Field(description = "The positive target of the Krystalium sample")
    rfid_id: str = Field(description = "The ID of the physical RFID in the sample")


class RefinedKrystaliumBase(BaseModel):
    """
    Represents refined Krystalium, which are generated by combining two raw krystalium samples.

    When two samples are combined, one of the samples is places in the negative
    slot and the other in the positive slot. This will result in two sets of properties;

    The action of the negative is combined with the target of the positive and the target of the negative is combined
    with the action of the positive.
    """
    primary_action: Action = Field(description="The primary action of the refined Krystalium")
    primary_target: Target = Field(description="The primary target of the refined Krystalium")
    secondary_action: Action = Field(description="The secondary action of the refined Krystalium")
    secondary_target: Target = Field(description="The secondary target of the refined Krystalium")
    rfid_id: str = Field(description="The ID of the physical RFID in the sample")


class RefinedKrystalium(RefinedKrystaliumBase):
    id: int

    class Config:
        orm_mode = True


class RefinedKrystaliumCreate(RefinedKrystaliumBase):
    pass


class KrystaliumSampleCreate(KrystaliumSampleBase):
    pass


class KrystaliumSample(KrystaliumSampleBase):
    id: int
    depleted: bool = Field(description="A Sample is depleted if it has been used to create refined Krystalium. It can no longer be used to create other refined samples")
    vulgarity: Vulgarity = Field()

    class Config:
        orm_mode = True


class RefinedKrystaliumFromSample(BaseModel):
    positive_sample_rfid_id: str
    negative_sample_rfid_id: str
    refined_krystalium_rfid_id: str


class RandomKrystaliumSampleCreate(BaseModel):
    rfid_id: str = Field(description="The ID of the physical RFID in the sample")
    vulgarity: Optional[Vulgarity] = Field(None, description="When set, it will create a sample with the given vulgarity. If not set, it will entirely randomly create one")