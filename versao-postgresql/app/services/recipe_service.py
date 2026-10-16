"""
Serviço de sugestão de receitas.
Normaliza nomes de ingredientes e calcula compatibilidade com a despensa.
"""
import unicodedata
from typing import List, Tuple
from app.database.connection import get_connection, release_connection
from app.models.recipe import Recipe, RecipeIngredient, RecipeSuggestion
from app.models.ingredient import PantryItem


# ---------------------------------------------------------------------------
# Helpers de normalização
# ---------------------------------------------------------------------------

def _normalize(text: str) -> str:
    """
    Converte texto para minúsculas, remove acentos e espaços extra.
    Facilita a comparação entre ingredientes da despensa e das receitas.
    """
    nfkd = unicodedata.normalize("NFKD", text.lower().strip())
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def _ingredient_matches(pantry_name: str, recipe_name: str) -> bool:
    """
    Verifica se um ingrediente da despensa corresponde a um da receita.
    Usa correspondência por substring nos dois sentidos para máxima flexibilidade.
    Exemplos:
      "frango" corresponde a "peito de frango"
      "batata" corresponde a "batata palha"
      "queijo mozzarella" corresponde a "mozzarella"
    """
    p = _normalize(pantry_name)
    r = _normalize(recipe_name)

    # Correspondência exata
    if p == r:
        return True

    # Correspondência por palavras individuais (≥ 1 palavra em comum com peso)
    pantry_words = set(p.split())
    recipe_words = set(r.split())

    # Remove palavras muito genéricas/curtas (artigos, preposições)
    stop_words = {"de", "do", "da", "em", "com", "a", "o", "e", "um", "uma"}
    pantry_words -= stop_words
    recipe_words -= stop_words

    if not pantry_words or not recipe_words:
        return p in r or r in p

    # Interseção de palavras significativas
    common = pantry_words & recipe_words
    if common:
        # Exige que pelo menos 1 palavra significativa seja comum
        # E que não seja tão genérico (ex: "sal" não pode casar com "salsa")
        # Para evitar falsos positivos, a palavra mais longa deve ter ≥ 4 chars
        significant = [w for w in common if len(w) >= 4]
        if significant:
            return True
        # Para palavras curtas, usa correspondência exata
        if common and all(pw in recipe_words for pw in pantry_words):
            return True

    # Fallback: substring
    return p in r or r in p


# ---------------------------------------------------------------------------
# Funções principais
# ---------------------------------------------------------------------------

def _get_all_recipes_with_ingredients() -> List[Recipe]:
    """Carrega todas as receitas com os seus ingredientes da BD."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Carregar receitas
            cur.execute(
                "SELECT id, title, description, category, difficulty, "
                "prep_time, cook_time, servings, instructions "
                "FROM recipes ORDER BY title"
            )
            recipe_rows = cur.fetchall()

            recipes = {}
            for r in recipe_rows:
                recipe = Recipe(
                    id=r[0], title=r[1], description=r[2] or "",
                    category=r[3] or "", difficulty=r[4] or "Médio",
                    prep_time=r[5] or 0, cook_time=r[6] or 0,
                    servings=r[7] or 4, instructions=r[8] or "",
                )
                recipes[r[0]] = recipe

            # Carregar todos os ingredientes de uma vez
            cur.execute(
                "SELECT id, recipe_id, ingredient_name, quantity, unit, optional "
                "FROM recipe_ingredients ORDER BY recipe_id, id"
            )
            ing_rows = cur.fetchall()

        for row in ing_rows:
            ri = RecipeIngredient(
                id=row[0], recipe_id=row[1], ingredient_name=row[2],
                quantity=float(row[3]) if row[3] else None,
                unit=row[4], optional=row[5],
            )
            if ri.recipe_id in recipes:
                recipes[ri.recipe_id].ingredients.append(ri)

        return list(recipes.values())
    finally:
        release_connection(conn)


def get_suggestions(
    pantry_items: List[PantryItem],
    only_complete: bool = False,
) -> List[RecipeSuggestion]:
    """
    Calcula sugestões de receitas com base nos ingredientes disponíveis na despensa.

    Args:
        pantry_items: Lista de ingredientes disponíveis.
        only_complete: Se True, retorna apenas receitas com 100% de compatibilidade.

    Returns:
        Lista de RecipeSuggestion ordenada por compatibilidade decrescente.
    """
    recipes = _get_all_recipes_with_ingredients()
    pantry_names = [item.name for item in pantry_items]

    suggestions: List[RecipeSuggestion] = []

    for recipe in recipes:
        required = recipe.required_ingredients
        if not required:
            continue

        available = []
        missing = []

        for ing in required:
            matched = any(
                _ingredient_matches(p_name, ing.ingredient_name)
                for p_name in pantry_names
            )
            if matched:
                available.append(ing.ingredient_name)
            else:
                missing.append(ing.ingredient_name)

        pct = (len(available) / len(required)) * 100 if required else 0.0

        if only_complete and pct < 100:
            continue

        suggestions.append(
            RecipeSuggestion(
                recipe=recipe,
                compatibility_pct=round(pct, 1),
                available_ingredients=available,
                missing_ingredients=missing,
            )
        )

    # Ordenar por compatibilidade decrescente, depois por título
    suggestions.sort(key=lambda s: (-s.compatibility_pct, s.recipe.title))
    return suggestions


def get_recipe_by_id(recipe_id: int) -> Recipe | None:
    """Carrega uma receita completa por ID."""
    all_recipes = _get_all_recipes_with_ingredients()
    for r in all_recipes:
        if r.id == recipe_id:
            return r
    return None
