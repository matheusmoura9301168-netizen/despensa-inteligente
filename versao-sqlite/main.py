"""
________________________________________________________________________
║                         main.py                                      ║
║                                                                      ║
║  PONTO DE ENTRADA DA APLICAÇÃO                                       ║
║                                                                      ║
║  Este é o ÚNICO ficheiro que você precisa de executar:               ║
║    → python main.py                                                  ║
║                                                                      ║
║  O que este ficheiro faz:                                            ║
║    1. Configura a codificação UTF-8 (suporte a emojis no Windows)    ║
║    2. Importa as funções necessárias dos outros ficheiros            ║
║    3. Verifica/cria a base de dados (despensa.db)                    ║
║    4. Cria as tabelas e insere as receitas de exemplo                ║
║    5. Abre a janela gráfica                                          ║
║                                                                      ║
║  Estrutura do projeto (apenas 4 ficheiros Python!):                  ║
║    main.py        → este ficheiro (ponto de entrada)                 ║
║    BD.py → modelos, conexão SQLite, tabelas e receitas               ║
║    servicos.py    → lógica: gerir despensa e sugerir receitas        ║
║    telas.py       → toda a interface gráfica (janelas, botões, etc)  ║
────────────────────────────────────────────────────────────────────────
"""

# ── Importações de bibliotecas do sistema ──────────────────────────────────
#
# sys → permite interagir com o interpretador Python
#       Usado aqui para: configurar encoding e terminar o programa (sys.exit)
#
# os  → permite interagir com o sistema operativo
#       Usado aqui para: adicionar a pasta actual ao caminho de importação

import sys
import os

# ── Corrigir problema de emojis na consola do Windows ─────────────────────
#
# O Windows usa por padrão a codificação "cp1252" que não suporta emojis (🍽️, ✅, etc.)
# Esta verificação força UTF-8, que suporta todos os caracteres Unicode.
#
# sys.stdout → saída padrão (o que aparece na consola com print())
# sys.stderr → saída de erros (mensagens de erro do Python)
# .encoding  → devolve a codificação actual (ex: "cp1252" ou "utf-8")
# .reconfigure() → muda a codificação sem reiniciar o programa
# errors='replace' → se um caracter não couber, substitui por "?" em vez de dar erro

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# ── Garantir que a pasta do projecto está no caminho de importação ─────────
#
# sys.path → lista de pastas onde o Python procura módulos para importar
# sys.path.insert(0, ...) → adiciona a nossa pasta na primeira posição
#
# __file__           → caminho deste ficheiro (main.py)
# os.path.abspath()  → transforma em caminho absoluto
# os.path.dirname()  → obtém a pasta que contém o ficheiro
#
# Isto garante que os outros ficheiros (BD.py, servicos.py, telas.py)
# são encontrados independentemente de onde o programa é executado.

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── Importações dos nossos módulos ────────────────────────────────────────
#
# Importamos apenas as funções que este ficheiro precisa directamente.
# O resto é tratado internamente por cada módulo.

from BD import verificar_base_dados, executar_migracoes
from telas import JanelaPrincipal


def iniciar():
    """
    Função principal — orquestra todo o arranque da aplicação.

    É como o "director de orquestra": não toca instrumentos,
    mas garante que cada músico (módulo) entra na hora certa.
    """

    # ── Mensagem de boas-vindas ────────────────────────────────────────
    print("─" * 55)
    print("   Despensa Inteligente — Versão SQLite")
    print("   Organiza a tua cozinha sem esforço!")
    print("─" * 55)
    print()

    # ── Passo 1: Verificar a base de dados ────────────────────────────
    # verificar_base_dados() tenta abrir/criar o ficheiro despensa.db
    # Para SQLite, isto raramente falha (a não ser que não haja permissão de escrita)
    print("[1/3] A verificar a base de dados...")
    if not verificar_base_dados():
        print()
        print("ERRO: Não foi possível abrir a base de dados.")
        print("Verifique se tem permissão de escrita nesta pasta.")
        print("Tente executar como administrador ou mude a pasta do projecto.")
        sys.exit(1)  # sys.exit(1) termina o programa com código de erro (1 = erro)

    # ── Passo 2: Criar tabelas e inserir receitas de exemplo ──────────
    # executar_migracoes() é segura para correr várias vezes:
    # - Só cria tabelas se ainda não existirem
    # - Só insere receitas se a tabela estiver vazia
    print("[2/3] A preparar as tabelas e receitas...")
    try:
        executar_migracoes()
    except Exception as erro:
        # Se algo correr mal durante as migrações, mostramos o erro e saímos
        print(f"ERRO nas migrações: {erro}")
        sys.exit(1)

    # ── Passo 3: Abrir a janela gráfica ───────────────────────────────
    # JanelaPrincipal() cria toda a interface gráfica
    # .iniciar() abre a janela e mantém-na aberta até o utilizador fechar
    print("[3/3] A abrir a interface gráfica...")
    janela = JanelaPrincipal()
    janela.iniciar()  # Bloqueia aqui até a janela ser fechada

    # Esta linha só é executada depois de fechar a janela
    print("Programa terminado. Ate a proxima!")


# ── Ponto de entrada Python ───────────────────────────────────────────────
#
# __name__ é uma variável especial do Python:
#   - Vale "__main__" quando executamos ESTE ficheiro directamente
#   - Vale o nome do módulo quando outro ficheiro importa este
#
# Esta verificação garante que iniciar() só é chamada quando fazemos:
#   python main.py
#
# Se outro ficheiro fizesse "import main", a função NÃO seria chamada.
# Isto é uma boa prática em Python.

if __name__ == "__main__":
    iniciar()
