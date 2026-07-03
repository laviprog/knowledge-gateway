from enum import StrEnum


class BaseEnum(StrEnum):
    """Base Enum for all Enums"""

    @classmethod
    def values(cls) -> list[str]:
        """
        Returns a list of all enum values.
        """
        return [item.value for item in cls]
