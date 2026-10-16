"""
Módulo de conexão à base de dados PostgreSQL.
Suporta retry automático enquanto aguarda o Docker subir.
"""
import os
import time
import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv

# Carregar variáveis de ambiente do .env
load_dotenv()

DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', '5432')),
    'dbname': os.getenv('POSTGRES_DB', 'despensa'),
    'user': os.getenv('POSTGRES_USER', 'despensa_user'),
    'password': os.getenv('POSTGRES_PASSWORD', 'despensa_pass'),
}

_connection_pool: pool.SimpleConnectionPool | None = None


def get_pool() -> pool.SimpleConnectionPool:
    """Retorna (ou cria) o pool de conexões."""
    global _connection_pool
    if _connection_pool is None:
        _connection_pool = pool.SimpleConnectionPool(minconn=1, maxconn=10, **DB_CONFIG)
    return _connection_pool


def get_connection():
    """Obtém uma conexão do pool."""
    return get_pool().getconn()


def release_connection(conn) -> None:
    """Devolve uma conexão ao pool."""
    get_pool().putconn(conn)


def wait_for_db(max_retries: int = 30, delay: float = 2.0) -> bool:
    """
    Aguarda a base de dados ficar disponível.
    Útil quando o PostgreSQL está a subir no Docker.
    """
    print("🔌 A conectar à base de dados...")
    for attempt in range(1, max_retries + 1):
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            conn.close()
            print("✅ Base de dados disponível!")
            return True
        except psycopg2.OperationalError:
            print(f"   ⏳ Aguardando PostgreSQL... ({attempt}/{max_retries})")
            if attempt < max_retries:
                time.sleep(delay)
    print("❌ Não foi possível conectar à base de dados.")
    return False
