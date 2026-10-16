"""Modelo de dados para itens da despensa."""
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class PantryItem:
    """Representa um ingrediente na despensa do utilizador."""
    id: int
    name: str
    quantity: float
    unit: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    @property
    def display_quantity(self) -> str:
        """Formata a quantidade para exibição (remove zeros desnecessários)."""
        if self.quantity == int(self.quantity):
            return f"{int(self.quantity)} {self.unit}"
        return f"{self.quantity:.1f} {self.unit}"

    def __str__(self) -> str:
        return f"{self.name} — {self.display_quantity}"
