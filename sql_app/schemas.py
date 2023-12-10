from pydantic import BaseModel, Field
from enum import Enum


class Action(str, Enum):
    """
    All the actions that a sample of Krystalium can have. Each sample of Krystalium has two actions; One positively
    charged action and one negatively charged action.
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
    All the targets that a sample of Krystalium can have. Each sample of Krystalium has two targets; One positively
    charged target and one negatively charged target.
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

