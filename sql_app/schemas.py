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
    gas: str = "Mind"
    solid: str = "Solid"
    liquid: str = "Solid"
    energy: str = "Energy"
    light: str = "Light"
    sound: str = "Sound"


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


class KrystaliumSampleCreate(KrystaliumSampleBase):
    pass


class KrystaliumSample(KrystaliumSampleBase):
    id: int
    class Config:
        orm_mode = True

