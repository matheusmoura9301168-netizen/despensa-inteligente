"""
Ponto de entrada da aplicação Despensa Inteligente.
Verifica a conexão com o PostgreSQL (Docker), executa as migrações e inicia a UI.
"""
import sys
import os

# Forçar UTF-8 na consola Windows (suporte a emojis)
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Garantir que o diretório raiz está no sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.connection import wait_for_db
from app.database.migrations import run_migrations
from app.ui.app_window import AppWindow


def main():
    print("=" * 50)
    print("  🍽️  Despensa Inteligente  v1.0.0")
    print("=" * 50)
    print()

    # 1. Aguardar a base de dados ficar disponível
    if not wait_for_db(max_retries=15, delay=2.0):
        print()
        print("❌ ERRO: Não foi possível conectar ao PostgreSQL.")
        print()
        print("  Verifica se o Docker está em execução:")
        print("  → docker-compose up -d")
        print()
        sys.exit(1)

    # 2. Executar migrações (criar tabelas + seed)
    try:
        run_migrations()
    except Exception as e:
        print(f"❌ Erro nas migrações: {e}")
        sys.exit(1)

    print()
    print("🚀 A iniciar a interface gráfica...")
    print()

    # 3. Iniciar a UI
    app = AppWindow()
    app.run()


if __name__ == "__main__":
    main()
