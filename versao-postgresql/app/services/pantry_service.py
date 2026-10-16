"""
Serviço CRUD para a despensa do utilizador.
"""
from typing import List, Optional
from app.database.connection import get_connection, release_connection
from app.models.ingredient import PantryItem


def get_all_items() -> List[PantryItem]:
    """Retorna todos os ingredientes da despensa ordenados por nome."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, name, quantity, unit, created_at, updated_at "
                "FROM pantry_items ORDER BY LOWER(name)"
            )
            rows = cur.fetchall()
        return [PantryItem(id=r[0], name=r[1], quantity=float(r[2]),
                           unit=r[3], created_at=r[4], updated_at=r[5])
                for r in rows]
    finally:
        release_connection(conn)


def search_items(query: str) -> List[PantryItem]:
    """Pesquisa ingredientes pelo nome."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, name, quantity, unit, created_at, updated_at "
                "FROM pantry_items "
                "WHERE LOWER(name) LIKE LOWER(%s) "
                "ORDER BY LOWER(name)",
                (f"%{query}%",),
            )
            rows = cur.fetchall()
        return [PantryItem(id=r[0], name=r[1], quantity=float(r[2]),
                           unit=r[3], created_at=r[4], updated_at=r[5])
                for r in rows]
    finally:
        release_connection(conn)


def add_item(name: str, quantity: float, unit: str) -> PantryItem:
    """Adiciona um novo ingrediente à despensa."""
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO pantry_items (name, quantity, unit) "
                    "VALUES (%s, %s, %s) RETURNING id, created_at, updated_at",
                    (name.strip(), quantity, unit),
                )
                row = cur.fetchone()
        return PantryItem(id=row[0], name=name.strip(), quantity=quantity,
                          unit=unit, created_at=row[1], updated_at=row[2])
    finally:
        release_connection(conn)


def update_item(item_id: int, name: str, quantity: float, unit: str) -> Optional[PantryItem]:
    """Atualiza um ingrediente existente."""
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE pantry_items "
                    "SET name=%s, quantity=%s, unit=%s, updated_at=CURRENT_TIMESTAMP "
                    "WHERE id=%s RETURNING id, created_at, updated_at",
                    (name.strip(), quantity, unit, item_id),
                )
                row = cur.fetchone()
        if row is None:
            return None
        return PantryItem(id=row[0], name=name.strip(), quantity=quantity,
                          unit=unit, created_at=row[1], updated_at=row[2])
    finally:
        release_connection(conn)


def delete_item(item_id: int) -> bool:
    """Remove um ingrediente da despensa."""
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM pantry_items WHERE id=%s", (item_id,))
                return cur.rowcount > 0
    finally:
        release_connection(conn)


def item_exists(name: str, exclude_id: Optional[int] = None) -> bool:
    """Verifica se já existe um ingrediente com este nome."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            if exclude_id:
                cur.execute(
                    "SELECT 1 FROM pantry_items WHERE LOWER(name)=LOWER(%s) AND id != %s",
                    (name, exclude_id),
                )
            else:
                cur.execute(
                    "SELECT 1 FROM pantry_items WHERE LOWER(name)=LOWER(%s)",
                    (name,),
                )
            return cur.fetchone() is not None
    finally:
        release_connection(conn)
