from dataclasses import dataclass


@dataclass
class PortEntryRequest:
    vessel_uid: int


@dataclass
class PortEntryPermission:
    vessel_uid: int
    avl_dock: str
