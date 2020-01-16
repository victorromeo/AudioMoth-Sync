from enum import Enum, unique

@unique
class iostate(Enum):
    Input = 0
    Output = 1
    Float = -1