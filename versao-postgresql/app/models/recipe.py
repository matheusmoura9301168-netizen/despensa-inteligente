"""Modelos de dados para receitas e sugestões."""
from dataclasses import dataclass, field
from typing import List


@dataclass
class RecipeIngredient:
    """Ingrediente de uma receita."""
    id: int
    recipe_id: int
    ingredient_name: str
    quantity: float | None
    unit: str | None
    optional: bool = False

    @property
    def display(self) -> str:
        """Exibição amigável do ingrediente."""
        parts = []
        if self.quantity is not None:
            qty = int(self.quantity) if self.quantity == int(self.quantity) else f"{self.quantity:.1f}"
            parts.append(str(qty))
        if self.unit:
            parts.append(self.unit)
        parts.append(self.ingredient_name)
        suffix = " (opcional)" if self.optional else ""
        return " ".join(parts) + suffix


@dataclass
class Recipe:
    """Receita completa."""
    id: int
    title: str
    description: str
    category: str
    difficulty: str
    prep_time: int
    cook_time: int
    servings: int
    instructions: str
    ingredients: List[RecipeIngredient] = field(default_factory=list)

    @property
    def total_time(self) -> int:
        return self.prep_time + self.cook_time

    @property
    def total_time_display(self) -> str:
        total = self.total_time
        if total >= 60:
            h = total // 60
            m = total % 60
            return f"{h}h {m:02d}min" if m else f"{h}h"
        return f"{total} min"

    @property
    def required_ingredients(self) -> List[RecipeIngredient]:
        """Apenas ingredientes obrigatórios."""
        return [i for i in self.ingredients if not i.optional]

    @property
    def difficulty_emoji(self) -> str:
        mapping = {"Fácil": "🟢", "Médio": "🟡", "Difícil": "🔴"}
        return mapping.get(self.difficulty, "⚪")

    @property
    def category_emoji(self) -> str:
        mapping = {
            "Prato Principal": "🍽️",
            "Sopa": "🥣",
            "Entrada": "🥗",
            "Sobremesa": "🍰",
            "Pequeno-Almoço": "☕",
            "Lanche": "🥪",
            "Acompanhamento": "🥦",
        }
        return mapping.get(self.category, "🍴")


@dataclass
class RecipeSuggestion:
    """Receita com informação de compatibilidade com a despensa."""
    recipe: Recipe
    compatibility_pct: float          # 0.0 a 100.0
    available_ingredients: List[str]  # nomes dos ingredientes disponíveis
    missing_ingredients: List[str]    # nomes dos ingredientes em falta

    @property
    def is_complete(self) -> bool:
        """True se todos os ingredientes obrigatórios estiverem disponíveis."""
        return self.compatibility_pct >= 100.0

    @property
    def compatibility_color(self) -> str:
        """Cor da barra de progresso baseada na compatibilidade."""
        if self.compatibility_pct >= 100:
            return "#10b981"   # verde esmeralda
        elif self.compatibility_pct >= 60:
            return "#f59e0b"   # âmbar
        elif self.compatibility_pct >= 30:
            return "#f97316"   # laranja
        return "#ef4444"       # vermelho
