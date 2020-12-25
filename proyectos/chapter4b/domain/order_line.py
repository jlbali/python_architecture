from dataclasses import dataclass

@dataclass(unsafe_hash=True)
class OrderLine:
    ref: str
    sku: str
    qty: int
