from enum import Enum

class ModelType(Enum):
  POTHOLE="Pot_Hole"
  WASTE="Waste"
  NONE = "None"

def ModelTypeToStr(Type : ModelType):
  match Type:
    case ModelType.POTHOLE : return "PotHole"
    case ModelType.WASTE : return "Waste"
    case ModelType.NONE : return "None"
