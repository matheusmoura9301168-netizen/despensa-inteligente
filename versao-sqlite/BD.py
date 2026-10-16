"""
╔══════════════════════════════════════════════════════════════════════╗
║                    BD.py                                             ║
║                                                                      ║
║  Este ficheiro trata de TUDO o que tem a ver com a base de dados.   ║
║                                                                      ║
║  GLOSSÁRIO DE TERMOS TÉCNICOS USADOS NESTE FICHEIRO:                 ║
║    - dataclass: Decorador do Python que automatiza a criação de      ║
║                 classes de dados, gerando a função construtora       ║
║                 __init__ de forma automática.                        ║
║    - __init__: O "construtor" de uma classe. É a função inicial que  ║
║                define as variáveis de um objeto quando ele é criado. ║
║    - PRAGMA: Comandos de configuração específicos do SQLite para     ║
║              gerir definições internas e otimizar performance.       ║
║    - WAL: Write-Ahead Logging. Um modo de diário rápido do SQLite    ║
║           que permite leituras e escritas simultâneas rápidas.       ║
║    - SQL: A linguagem padrão para gerir e manipular bases de dados.  ║
║                                                                      ║
║  Está organizado em 3 partes:                                        ║
║                                                                      ║
║  PARTE 1 — MODELOS DE DADOS                                          ║
║    Define a "forma" dos dados: o que é um ingrediente,              ║
║    o que é uma receita, o que é uma sugestão de receita.            ║
║                                                                      ║
║  PARTE 2 — CONEXÃO                                                   ║
║    Funções para abrir e fechar o ficheiro despensa.db (SQLite).     ║
║    O SQLite é uma base de dados que funciona como um ficheiro normal ║
║    — não precisa de servidor nem de Docker!                          ║
║                                                                      ║
║  PARTE 3 — MIGRAÇÕES E RECEITAS DE EXEMPLO                          ║
║    Na 1ª execução do programa: cria as tabelas e insere receitas.   ║
╚══════════════════════════════════════════════════════════════════════╝
"""

# ── Importações de bibliotecas do Python ───────────────────────────────────
#
# sqlite3    → biblioteca para trabalhar com bases de dados SQLite.
#              Já vem incluída no Python — não precisa de instalar nada!
#
# dataclass  → decorator (marcação) que transforma uma classe simples numa
#              classe de dados.Ex: @property é um decorator nativo do Python (definido em builtins.pyi).
#              Ele transforma este método num atributo calculado.
#              Gera automaticamente __init__, __repr__, etc.
#
# field      → usado dentro de @dataclass para configurar campos especiais,
#              como valores padrão que são calculados no momento da criação.
#
# List       → usado para dizer ao Python que uma variável é uma "lista de X".
#              Ex: List[str] = lista de textos, List[int] = lista de números.
#
# Path       → facilita a construção de caminhos de ficheiros de forma
#              compatível com Windows, Mac e Linux.
#
# datetime   → para trabalhar com datas e horas (quando o ingrediente foi
#              adicionado, quando foi modificado, etc.)

import sqlite3
from dataclasses import dataclass, field
from typing import List
from pathlib import Path
from datetime import datetime


# ── Localização do ficheiro da base de dados ───────────────────────────────
#
# __file__  → caminho deste ficheiro (BD.py)
# .resolve() → transforma em caminho absoluto (ex: C:/Users/.../BD.py)
# .parent   → sobe uma pasta (vai para a pasta do projeto)
# / "despensa.db" → junta com o nome do ficheiro da base de dados
#
# Resultado: o ficheiro despensa.db fica na pasta raiz do projeto.
# Se não existir, o SQLite cria-o automaticamente na primeira execução.

CAMINHO_BASE_DADOS = Path(__file__).resolve().parent / "despensa.db"


# ───────────────────────────────────────────────────────────────────────────────────────────
# PARTE 1 — MODELOS DE DADOS
#
# Um "modelo" é como um formulário em branco que define que campos existem.
# Por exemplo, o modelo ItemDespensa tem os campos: nome, quantidade, unidade.
#
# @dataclass é uma forma rápida de criar estes "formulários" em Python.
# Em vez de escrever __init__ manualmente, o Python faz isso por nós.
# ───────────────────────────────────────────────────────────────────────────────────────────


@dataclass
class ItemDespensa:
    """
    Representa um ingrediente guardado na despensa do utilizador.

    Cada campo corresponde a uma coluna na tabela 'despensa' do SQLite.

    Exemplo de uso:
        item = ItemDespensa(id=1, nome="Ovos", quantidade=6, unidade="unidades")
        print(item.quantidade_formatada)  # → "6 unidades"
        print(item)                       # → "Ovos — 6 unidades"
    """

    id: int           # Número único gerado automaticamente pelo SQLite (chave primária)
    nome: str         # Nome do ingrediente, ex: "Farinha", "Ovos", "Sal"
    quantidade: float # Quantidade disponível; float permite números decimais (ex: 0.5 kg)
    unidade: str      # Unidade de medida, ex: "g", "kg", "ml", "unidades"

    # Os campos abaixo têm valores padrão: são preenchidos automaticamente
    # com a data/hora atual quando um ItemDespensa é criado.
    # field(default_factory=datetime.now) significa: "chama datetime.now()
    # cada vez que um novo item é criado" (não partilha a mesma data entre itens)
    criado_em: datetime = field(default_factory=datetime.now)
    atualizado_em: datetime = field(default_factory=datetime.now)

    @property
    def quantidade_formatada(self) -> str:
        """
        Propriedade que devolve a quantidade num formato legível.
        O -> é usado para indicar o tipo de retorno da função (type hint).
        @property significa que podemos aceder como se fosse um campo normal
        (item.quantidade_formatada), mas o Python executa este código automaticamente.

        Exemplos:
          500.0  → "500 g"   (remove o ".0" desnecessário)
          2.5    → "2.5 kg"  (mantém o decimal quando é necessário)
        """
        if self.quantidade == int(self.quantidade):
            # int(500.0) == 500.0 → True → mostra "500 g" sem decimal
            return f"{int(self.quantidade)} {self.unidade}"
        # Caso contrário, mostra com 1 casa decimal
        return f"{self.quantidade:.1f} {self.unidade}"

    def __str__(self) -> str:
        """
        Define o que aparece quando fazemos print(item) ou str(item).
        Ex: print(ItemDespensa(..., nome="Ovos", ...)) → "Ovos — 6 unidades"
        """
        return f"{self.nome} — {self.quantidade_formatada}"


@dataclass
class IngredienteReceita:
    """
    Representa um ingrediente dentro de uma receita específica.

    Diferença de ItemDespensa:
      - ItemDespensa → o que o utilizador TEM em casa
      - IngredienteReceita → o que uma receita PRECISA

    Cada receita tem vários IngredienteReceita associados (relação 1 para muitos).
    """

    id: int                # Identificador único deste ingrediente na tabela
    id_receita: int        # A qual receita este ingrediente pertence (chave estrangeira)
    nome_ingrediente: str  # Nome do ingrediente, ex: "bacalhau desfiado"
    quantidade: float | None  # Pode ser None se a receita não especificar quantidade
    unidade: str | None       # Pode ser None se não houver unidade definida
    opcional: bool = False    # True = ingrediente é opcional (ex: para enfeitar)

    @property
    def exibir(self) -> str:
        """
        Devolve o ingrediente formatado para mostrar ao utilizador.

        Exemplos:
          400 g bacalhau desfiado
          3 dentes alho
          1 ramo salsa (opcional)
        """
        partes = []

        # Adiciona a quantidade se existir
        if self.quantidade is not None:
            # Se for número inteiro, mostra sem decimais: 3.0 → "3"
            if self.quantidade == int(self.quantidade):
                partes.append(str(int(self.quantidade)))
            else:
                partes.append(f"{self.quantidade:.1f}")

        # Adiciona a unidade se existir
        if self.unidade:
            partes.append(self.unidade)

        # Adiciona o nome do ingrediente
        partes.append(self.nome_ingrediente)

        # Junta tudo com espaço e acrescenta "(opcional)" se necessário
        sufixo = " (opcional)" if self.opcional else ""
        return " ".join(partes) + sufixo


@dataclass
class Receita:
    """
    Representa uma receita completa, com todos os seus detalhes.

    Contém informações como o título, tempo de preparação, dificuldade,
    instruções passo a passo, e a lista de ingredientes necessários.
    """

    id: int              # Identificador único da receita
    titulo: str          # Nome da receita, ex: "Bacalhau à Brás"
    descricao: str       # Breve descrição do prato
    categoria: str       # Tipo de prato, ex: "Prato Principal", "Sopa", "Sobremesa"
    dificuldade: str     # "Fácil", "Médio" ou "Difícil"
    tempo_preparo: int   # Minutos de preparação (lavar, cortar, marinar, etc.)
    tempo_cozedura: int  # Minutos de cozedura (forno, fogão, etc.)
    porcoes: int         # Número de pessoas que a receita serve
    instrucoes: str      # Modo de preparo, com os passos separados por "\n"

    # Lista de ingredientes — começa vazia e é preenchida ao carregar da BD.
    # field(default_factory=list) cria uma lista nova para cada receita (não partilhada).
    ingredientes: List[IngredienteReceita] = field(default_factory=list)

    @property
    def tempo_total(self) -> int:
        """Devolve o tempo total = preparação + cozedura, em minutos."""
        return self.tempo_preparo + self.tempo_cozedura

    @property
    def tempo_total_formatado(self) -> str:
        """
        Devolve o tempo total num formato legível.
        Exemplos:
          25  → "25 min"
          90  → "1h 30min"
          60  → "1h"
        """
        total = self.tempo_total
        if total >= 60:
            horas = total // 60       # Divisão inteira: 90 // 60 = 1 hora
            minutos = total % 60      # Resto: 90 % 60 = 30 minutos
            return f"{horas}h {minutos:02d}min" if minutos else f"{horas}h"
        return f"{total} min"

    @property
    def ingredientes_obrigatorios(self) -> List[IngredienteReceita]:
        """
        Devolve apenas os ingredientes obrigatórios (não opcionais).
        São estes que são usados para calcular a % de compatibilidade.
        """
        return [i for i in self.ingredientes if not i.opcional]

    @property
    def emoji_dificuldade(self) -> str:
        """Devolve um círculo colorido consoante a dificuldade da receita."""
        mapeamento = {"Fácil": "🟢", "Médio": "🟡", "Difícil": "🔴"}
        return mapeamento.get(self.dificuldade, "⚪")

    @property
    def emoji_categoria(self) -> str:
        """Devolve um emoji representativo da categoria da receita."""
        mapeamento = {
            "Prato Principal": "🍽️",
            "Sopa": "🥣",
            "Entrada": "🥗",
            "Sobremesa": "🍰",
            "Pequeno-Almoço": "☕",
            "Lanche": "🥪",
            "Acompanhamento": "🥦",
        }
        return mapeamento.get(self.categoria, "🍴")


@dataclass
class SugestaoReceita:
    """
    Combina uma receita com a informação de compatibilidade com a despensa.

    Quando o utilizador pede sugestões, o programa compara cada receita
    com os ingredientes disponíveis e cria um SugestaoReceita para cada uma,
    com a percentagem de compatibilidade e a lista de ingredientes em falta.

    Exemplo:
        - Receita: "Bacalhau à Brás" (precisa de 10 ingredientes)
        - Despensa: tem 7 desses ingredientes
        - percentagem_compatibilidade = 70.0%
        - ingredientes_disponiveis = ["bacalhau", "ovos", "cebola", ...]
        - ingredientes_em_falta = ["azeitonas", "salsa", "batata palha"]
    """

    receita: Receita                      # A receita em questão
    percentagem_compatibilidade: float    # De 0.0 a 100.0 — quanto % da receita a despensa cobre
    ingredientes_disponiveis: List[str]   # Nomes dos ingredientes que JÁ estão na despensa
    ingredientes_em_falta: List[str]      # Nomes dos ingredientes que FALTAM

    @property
    def e_completa(self) -> bool:
        """
        Devolve True se TODOS os ingredientes obrigatórios estiverem disponíveis.
        (percentagem == 100%)
        """
        return self.percentagem_compatibilidade >= 100.0

    @property
    def cor_compatibilidade(self) -> str:
        """
        Devolve uma cor em formato hexadecimal para representar visualmente
        a compatibilidade. Usado na barra de progresso dos cards de receitas.

        100%      → verde esmeralda  (#10b981)
        60%–99%  → âmbar/laranja   (#f59e0b)
        30%–59%  → laranja         (#f97316)
        0%–29%   → vermelho        (#ef4444)
        """
        if self.percentagem_compatibilidade >= 100:
            return "#10b981"  # Verde — tens tudo!
        elif self.percentagem_compatibilidade >= 60:
            return "#f59e0b"  # Âmbar — falta pouco
        elif self.percentagem_compatibilidade >= 30:
            return "#f97316"  # Laranja — falta bastante
        return "#ef4444"      # Vermelho — falta muito


# ───────────────────────────────────────────────────────────────────────────────────────────
# PARTE 2 — CONEXÃO COM A BASE DE DADOS
#
# O SQLite é uma base de dados que vive num único ficheiro (despensa.db).
# Para ler ou escrever dados, precisamos primeiro de "abrir" o ficheiro
# (obter_conexao) e no fim "fechá-lo" (fechar_conexao).
#
# É como abrir e fechar um livro: abrimos para ler/escrever e fechamos
# quando acabamos para não deixar o ficheiro bloqueado.
# ───────────────────────────────────────────────────────────────────────────────────────────


def obter_conexao() -> sqlite3.Connection:
    """
    Abre e devolve uma conexão com a base de dados SQLite.

    O que é uma "conexão"? É como abrir um canal de comunicação entre
    o programa Python e o ficheiro despensa.db. Através deste canal,
    podemos enviar comandos SQL (SELECT, INSERT, UPDATE, DELETE).

    Configurações aplicadas:
      - PRAGMA foreign_keys = ON  → garante que as ligações entre tabelas
        funcionam corretamente (ex: ao apagar uma receita, os seus ingredientes
        também são apagados automaticamente).

      - PRAGMA journal_mode = WAL → melhora a performance ao permitir leituras
        e escritas simultâneas sem bloquear o ficheiro.

      - check_same_thread=False   → permite usar a mesma conexão em diferentes
        partes do programa (necessário para aplicações gráficas com Tkinter).
    """
    # sqlite3.connect() abre o ficheiro. Se não existir, cria-o automaticamente!
    conexao = sqlite3.connect(str(CAMINHO_BASE_DADOS), check_same_thread=False)

    # PRAGMA são comandos de configuração do SQLite (não são SQL standard)
    # * PRAGMA: Instruções internas para configurar e afinar a base de dados.
    conexao.execute("PRAGMA foreign_keys = ON")   # Activar chaves estrangeiras
    # * WAL (Write-Ahead Logging): Um modo rápido que grava dados num diário à parte para evitar lentidão.
    conexao.execute("PRAGMA journal_mode = WAL")  # Modo de escrita mais eficiente

    return conexao


def fechar_conexao(conexao: sqlite3.Connection) -> None:
    """
    Fecha a conexão com a base de dados.

    Deve ser sempre chamada depois de terminarmos as operações com a BD.
    Funciona como o "guardar e fechar" de um documento.

    O bloco try/except garante que se já estiver fechada (ou der erro),
    o programa não cai — simplesmente ignora o erro.
    """
    try:
        conexao.close()
    except Exception:
        pass  # Se já estiver fechada, não faz nada


def verificar_base_dados() -> bool:
    """
    Verifica se é possível abrir a base de dados SQLite.

    Para o SQLite, esta função é muito simples: como o ficheiro é criado
    automaticamente, raramente falha. Serve sobretudo para confirmar que
    temos permissão de escrita na pasta do projeto.

    Devolve:
        True  → base de dados acessível
        False → erro ao tentar abrir (ex: sem permissão de escrita)
    """
    try:
        conexao = obter_conexao()
        fechar_conexao(conexao)
        print(f"Base de dados pronta: {CAMINHO_BASE_DADOS.name}")
        return True
    except Exception as erro:
        print(f"Erro ao abrir base de dados: {erro}")
        return False


# ───────────────────────────────────────────────────────────────────────────────────────────
# PARTE 3 — MIGRAÇÕES E RECEITAS DE EXEMPLO
#
# "Migração" é o processo de preparar a base de dados para uso:
#   1. Criar as tabelas (se ainda não existirem)
#   2. Inserir dados de exemplo (apenas na primeira execução)
#
# O que é uma tabela? É como uma folha de cálculo: tem colunas (campos)
# e linhas (registos). Cada base de dados pode ter várias tabelas.
#
# As nossas tabelas:
#   - despensa      → ingredientes do utilizador
#   - receitas      → as 20 receitas pré-carregadas
#   - ingredientes_receita → ingredientes de cada receita
# ───────────────────────────────────────────────────────────────────────────────────────────

# SQL para criar as 3 tabelas.
# "IF NOT EXISTS" significa: só cria se ainda não existir — seguro de correr várias vezes.
# Os tipos de dados SQLite são mais simples que o PostgreSQL:
#   INTEGER          → número inteiro
#   REAL             → número decimal (equivale a DECIMAL/FLOAT)
#   TEXT             → texto (equivale a VARCHAR)
#   DATETIME         → data e hora
#   PRIMARY KEY AUTOINCREMENT → o SQLite atribui o ID automaticamente, a começar em 1
#   REFERENCES       → ligação a outra tabela (chave estrangeira)
#   ON DELETE CASCADE → se a receita for apagada, os seus ingredientes também são

SQL_CRIAR_TABELAS = """
CREATE TABLE IF NOT EXISTS despensa (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    nome         TEXT    NOT NULL,
    quantidade   REAL    NOT NULL DEFAULT 1,
    unidade      TEXT    NOT NULL DEFAULT 'unidades',
    criado_em    DATETIME DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS receitas (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo       TEXT NOT NULL,
    descricao    TEXT,
    categoria    TEXT,
    dificuldade  TEXT DEFAULT 'Médio',
    tempo_preparo  INTEGER DEFAULT 0,
    tempo_cozedura INTEGER DEFAULT 0,
    porcoes      INTEGER DEFAULT 4,
    instrucoes   TEXT
);

CREATE TABLE IF NOT EXISTS ingredientes_receita (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    id_receita       INTEGER REFERENCES receitas(id) ON DELETE CASCADE,
    nome_ingrediente TEXT NOT NULL,
    quantidade       REAL,
    unidade          TEXT,
    opcional         INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_despensa_nome ON despensa(nome COLLATE NOCASE);
CREATE INDEX IF NOT EXISTS idx_ing_receita   ON ingredientes_receita(id_receita);
"""

# ── Lista de 20 receitas de exemplo ───────────────────────────────────────
# Cada receita é um dicionário Python com os campos da tabela "receitas"
# e uma lista de "ingredientes" para a tabela "ingredientes_receita".
#
# Formato de cada ingrediente: (nome, quantidade, unidade, opcional)
#   opcional = 0 → obrigatório
#   opcional = 1 → opcional (apenas para enfeitar ou melhorar o sabor)

RECEITAS_EXEMPLO = [
    # ── Receitas Portuguesas ─────────────────────────────────────────────
    {
        "titulo": "Bacalhau à Brás",
        "descricao": "Clássico português com bacalhau desfiado, batata palha crocante e ovos mexidos cremosos.",
        "categoria": "Prato Principal", "dificuldade": "Médio",
        "tempo_preparo": 20, "tempo_cozedura": 25, "porcoes": 4,
        "instrucoes": (
            "1. Demolhe o bacalhau de véspera, trocando a água várias vezes. Escorra e desfie em lascas.\n"
            "2. Descasque e corte as cebolas em meias-luas finas.\n"
            "3. Aqueça o azeite e refogue a cebola e o alho em lume médio até dourar.\n"
            "4. Adicione o bacalhau desfiado e salteie por 3 minutos.\n"
            "5. Junte a batata palha e misture bem.\n"
            "6. Bata os ovos com sal e pimenta. Adicione e mexa em lume baixo.\n"
            "7. Retire quando os ovos estiverem cremosos.\n"
            "8. Sirva com salsa picada e azeitonas pretas."
        ),
        "ingredientes": [
            ("bacalhau desfiado", 400, "g", 0), ("batata palha", 200, "g", 0),
            ("ovos", 4, "unidades", 0), ("cebola", 2, "unidades", 0),
            ("alho", 3, "dentes", 0), ("azeite", 4, "colheres de sopa", 0),
            ("salsa", 1, "ramo", 1), ("azeitonas pretas", 50, "g", 1),
            ("sal", 1, "pitada", 0), ("pimenta preta", 1, "pitada", 0),
        ],
    },
    {
        "titulo": "Caldo Verde",
        "descricao": "Sopa tradicional portuguesa com couve-galega, linguiça e batata cremosa.",
        "categoria": "Sopa", "dificuldade": "Fácil",
        "tempo_preparo": 15, "tempo_cozedura": 30, "porcoes": 6,
        "instrucoes": (
            "1. Descasque e corte as batatas em cubos. Pique a cebola e o alho.\n"
            "2. Refogue a cebola e o alho no azeite por 5 minutos.\n"
            "3. Adicione as batatas e cubra com água. Cozinhe até ficarem macias.\n"
            "4. Triture a sopa até ficar cremosa.\n"
            "5. Junte a linguiça em rodelas e ferva 5 minutos.\n"
            "6. Adicione a couve em juliana fina e cozinhe mais 4 minutos.\n"
            "7. Tempere com sal e regue com azeite antes de servir."
        ),
        "ingredientes": [
            ("couve-galega", 300, "g", 0), ("batata", 4, "unidades", 0),
            ("linguiça", 150, "g", 0), ("cebola", 1, "unidades", 0),
            ("alho", 2, "dentes", 0), ("azeite", 3, "colheres de sopa", 0),
            ("sal", 1, "pitada", 0), ("caldo de legumes", 1500, "ml", 1),
        ],
    },
    {
        "titulo": "Frango Assado com Batatas",
        "descricao": "Frango assado no forno com batatas e alho, marinado em vinho branco e pimentão.",
        "categoria": "Prato Principal", "dificuldade": "Médio",
        "tempo_preparo": 20, "tempo_cozedura": 75, "porcoes": 4,
        "instrucoes": (
            "1. Misture alho picado, pimentão doce, sumo de limão, azeite, sal e pimenta.\n"
            "2. Barre o frango com esta mistura. Marine 30 minutos.\n"
            "3. Pré-aqueça o forno a 200°C.\n"
            "4. Coloque o frango numa assadeira e regue com vinho branco.\n"
            "5. Disponha as batatas em quartos à volta do frango.\n"
            "6. Leve ao forno 75 minutos, regando a cada 20 minutos.\n"
            "7. Pronto quando a pele estiver dourada e crocante."
        ),
        "ingredientes": [
            ("frango inteiro", 1500, "g", 0), ("batata", 800, "g", 0),
            ("alho", 6, "dentes", 0), ("limão", 1, "unidades", 0),
            ("azeite", 5, "colheres de sopa", 0), ("vinho branco", 150, "ml", 0),
            ("pimentão doce", 2, "colheres de chá", 0),
            ("sal", 1, "pitada", 0), ("pimenta preta", 1, "pitada", 0),
        ],
    },
    {
        "titulo": "Arroz de Tomate",
        "descricao": "Acompanhamento simples e saboroso com tomate fresco, cebola e azeite.",
        "categoria": "Acompanhamento", "dificuldade": "Fácil",
        "tempo_preparo": 5, "tempo_cozedura": 20, "porcoes": 4,
        "instrucoes": (
            "1. Pique a cebola e o alho finamente.\n"
            "2. Refogue no azeite até ficarem translúcidos.\n"
            "3. Adicione o tomate picado e cozinhe 5 minutos.\n"
            "4. Junte o arroz e mexa 1 minuto para tostar.\n"
            "5. Adicione água quente (dobro do volume do arroz) e sal.\n"
            "6. Cozinhe em lume baixo com tampa por 18 minutos.\n"
            "7. Repouso de 5 minutos antes de servir."
        ),
        "ingredientes": [
            ("arroz", 300, "g", 0), ("tomate", 3, "unidades", 0),
            ("cebola", 1, "unidades", 0), ("alho", 2, "dentes", 0),
            ("azeite", 3, "colheres de sopa", 0),
            ("sal", 1, "pitada", 0), ("pimenta preta", 1, "pitada", 0),
        ],
    },
    {
        "titulo": "Bifanas",
        "descricao": "Sanduíche portuguesa com carne de porco marinada em vinho e especiarias.",
        "categoria": "Lanche", "dificuldade": "Fácil",
        "tempo_preparo": 15, "tempo_cozedura": 15, "porcoes": 4,
        "instrucoes": (
            "1. Marine a carne em vinho branco, alho, pimentão, louro, sal e pimenta por 1 hora.\n"
            "2. Aqueça azeite numa frigideira em lume alto.\n"
            "3. Frite as bifanas escorridas, 2-3 minutos de cada lado.\n"
            "4. Adicione a marinada e deixe reduzir.\n"
            "5. Sirva dentro de pão regado com o molho."
        ),
        "ingredientes": [
            ("carne de porco em bifanas", 500, "g", 0), ("vinho branco", 200, "ml", 0),
            ("alho", 4, "dentes", 0), ("pimentão doce", 1, "colher de chá", 0),
            ("louro", 2, "folhas", 0), ("sal", 1, "pitada", 0),
            ("pimenta preta", 1, "pitada", 0), ("pão de bolo", 4, "unidades", 0),
            ("azeite", 2, "colheres de sopa", 0),
        ],
    },
    {
        "titulo": "Açorda Alentejana",
        "descricao": "Sopa de pão alentejana com ovos escalfados, coentros frescos e alho.",
        "categoria": "Prato Principal", "dificuldade": "Fácil",
        "tempo_preparo": 10, "tempo_cozedura": 15, "porcoes": 4,
        "instrucoes": (
            "1. Pise o alho com sal grosso num almofariz até formar pasta.\n"
            "2. Corte o pão em fatias e distribua nos pratos.\n"
            "3. Ferva água com azeite e alho pisado por 5 minutos.\n"
            "4. Escalde os ovos no líquido (3-4 min para gema mole).\n"
            "5. Retire os ovos e verta o caldo sobre o pão.\n"
            "6. Coloque os ovos por cima e salpique com coentros frescos."
        ),
        "ingredientes": [
            ("pão alentejano duro", 300, "g", 0), ("ovos", 4, "unidades", 0),
            ("alho", 4, "dentes", 0), ("coentros", 1, "ramo", 0),
            ("azeite", 5, "colheres de sopa", 0), ("sal grosso", 1, "colher de chá", 0),
        ],
    },
    {
        "titulo": "Arroz de Frango",
        "descricao": "Arroz caldoso com frango desfiado, refogado de cebola e especiarias.",
        "categoria": "Prato Principal", "dificuldade": "Médio",
        "tempo_preparo": 15, "tempo_cozedura": 40, "porcoes": 4,
        "instrucoes": (
            "1. Coza o frango em água com sal, cebola e louro por 30 min. Reserve o caldo.\n"
            "2. Desfie o frango e reserve.\n"
            "3. Refogue cebola e alho no azeite. Adicione tomate e cozinhe 5 min.\n"
            "4. Junte o arroz, mexa 1 min, adicione o caldo (2,5x o arroz).\n"
            "5. Adicione o frango e cozinhe 15 minutos em lume médio.\n"
            "6. Sirva com salsa picada."
        ),
        "ingredientes": [
            ("frango", 600, "g", 0), ("arroz", 300, "g", 0),
            ("cebola", 1, "unidades", 0), ("alho", 3, "dentes", 0),
            ("tomate", 2, "unidades", 0), ("azeite", 3, "colheres de sopa", 0),
            ("louro", 1, "folha", 0), ("sal", 1, "pitada", 0),
            ("salsa", 1, "ramo", 1),
        ],
    },
    {
        "titulo": "Sopa de Feijão com Chouriço",
        "descricao": "Sopa rica e reconfortante com feijão vermelho, chouriço e legumes.",
        "categoria": "Sopa", "dificuldade": "Fácil",
        "tempo_preparo": 10, "tempo_cozedura": 40, "porcoes": 6,
        "instrucoes": (
            "1. Refogue cebola e alho no azeite até dourar.\n"
            "2. Adicione chouriço em rodelas e salteie 2 minutos.\n"
            "3. Junte cenoura e batata em cubos. Cubra com caldo.\n"
            "4. Cozinhe 20 minutos, adicione o feijão e ferva mais 10 min.\n"
            "5. Corrija o sal e sirva com pão."
        ),
        "ingredientes": [
            ("feijão vermelho", 400, "g", 0), ("chouriço", 150, "g", 0),
            ("cenoura", 2, "unidades", 0), ("batata", 2, "unidades", 0),
            ("cebola", 1, "unidades", 0), ("alho", 2, "dentes", 0),
            ("azeite", 3, "colheres de sopa", 0),
            ("caldo de legumes", 1500, "ml", 0), ("sal", 1, "pitada", 0),
        ],
    },
    # ── Receitas Internacionais ──────────────────────────────────────────
    {
        "titulo": "Massa Bolonhesa",
        "descricao": "Clássico molho à bolonhesa com carne picada, tomate e ervas.",
        "categoria": "Prato Principal", "dificuldade": "Médio",
        "tempo_preparo": 15, "tempo_cozedura": 45, "porcoes": 4,
        "instrucoes": (
            "1. Refogue cebola e alho no azeite até dourar.\n"
            "2. Adicione carne picada e cozinhe em lume alto até tostar.\n"
            "3. Regue com vinho tinto e deixe evaporar.\n"
            "4. Adicione tomate pelado, louro, sal e pimenta.\n"
            "5. Cozinhe em lume baixo 30-40 minutos.\n"
            "6. Coza o esparguete e sirva com o molho e parmesão."
        ),
        "ingredientes": [
            ("esparguete", 400, "g", 0), ("carne picada", 500, "g", 0),
            ("tomate pelado", 400, "g", 0), ("cebola", 1, "unidades", 0),
            ("alho", 3, "dentes", 0), ("vinho tinto", 150, "ml", 0),
            ("azeite", 3, "colheres de sopa", 0), ("louro", 1, "folha", 0),
            ("parmesão ralado", 50, "g", 1),
            ("sal", 1, "pitada", 0), ("pimenta preta", 1, "pitada", 0),
        ],
    },
    {
        "titulo": "Risotto de Cogumelos",
        "descricao": "Risotto cremoso italiano com cogumelos frescos e parmesão.",
        "categoria": "Prato Principal", "dificuldade": "Médio",
        "tempo_preparo": 10, "tempo_cozedura": 35, "porcoes": 4,
        "instrucoes": (
            "1. Mantenha o caldo quente numa panela separada.\n"
            "2. Refogue cebola na manteiga. Adicione cogumelos e alho por 5 min.\n"
            "3. Junte o arroz arbóreo e mexa 1 minuto.\n"
            "4. Adicione o vinho branco e mexa até absorver.\n"
            "5. Adicione o caldo concha a concha, mexendo sempre (20-25 min).\n"
            "6. Retire do lume, misture manteiga e parmesão. Tempere e sirva."
        ),
        "ingredientes": [
            ("arroz arbóreo", 320, "g", 0), ("cogumelos", 300, "g", 0),
            ("cebola", 1, "unidades", 0), ("alho", 2, "dentes", 0),
            ("vinho branco", 150, "ml", 0), ("caldo de legumes", 1200, "ml", 0),
            ("manteiga", 50, "g", 0), ("parmesão ralado", 80, "g", 0),
            ("sal", 1, "pitada", 0), ("pimenta preta", 1, "pitada", 0),
        ],
    },
    {
        "titulo": "Omelete de Queijo",
        "descricao": "Omelete fofa e dourada com queijo derretido. Pronto em 10 minutos.",
        "categoria": "Pequeno-Almoço", "dificuldade": "Fácil",
        "tempo_preparo": 5, "tempo_cozedura": 8, "porcoes": 1,
        "instrucoes": (
            "1. Bata os ovos com sal e pimenta.\n"
            "2. Derreta manteiga numa frigideira antiaderente em lume médio.\n"
            "3. Adicione os ovos. Quando as bordas solidificarem, puxe-as para o centro.\n"
            "4. Quando quase cozida, distribua o queijo ralado.\n"
            "5. Dobre ao meio e sirva imediatamente."
        ),
        "ingredientes": [
            ("ovos", 3, "unidades", 0), ("queijo", 50, "g", 0),
            ("manteiga", 15, "g", 0), ("sal", 1, "pitada", 0),
            ("pimenta preta", 1, "pitada", 0),
        ],
    },
    {
        "titulo": "Salada César",
        "descricao": "Salada clássica com alface romana, frango grelhado e croutons.",
        "categoria": "Entrada", "dificuldade": "Fácil",
        "tempo_preparo": 20, "tempo_cozedura": 15, "porcoes": 2,
        "instrucoes": (
            "1. Grelhe o frango temperado com sal, pimenta e azeite (6-7 min/lado).\n"
            "2. Corte em fatias e reserve.\n"
            "3. Torre cubos de pão no forno a 180°C por 10 minutos.\n"
            "4. Misture a alface rasgada com o molho César.\n"
            "5. Adicione frango, croutons e parmesão. Sirva de imediato."
        ),
        "ingredientes": [
            ("alface romana", 1, "unidades", 0), ("peito de frango", 200, "g", 0),
            ("parmesão", 40, "g", 0), ("pão", 2, "fatias", 0),
            ("molho césar", 4, "colheres de sopa", 0),
            ("azeite", 2, "colheres de sopa", 0),
            ("limão", 1, "unidades", 1),
            ("sal", 1, "pitada", 0), ("pimenta preta", 1, "pitada", 0),
        ],
    },
    {
        "titulo": "Frango à Parmesão",
        "descricao": "Peito de frango empanado com molho de tomate e mozzarella derretida.",
        "categoria": "Prato Principal", "dificuldade": "Médio",
        "tempo_preparo": 20, "tempo_cozedura": 25, "porcoes": 2,
        "instrucoes": (
            "1. Aplane os peitos de frango.\n"
            "2. Empane: farinha → ovo batido → pão ralado.\n"
            "3. Frite em azeite quente 3-4 min de cada lado até dourar.\n"
            "4. Coloque numa assadeira, cubra com molho de tomate e mozzarella.\n"
            "5. Polvilhe com parmesão e leve ao forno 200°C por 10-15 min."
        ),
        "ingredientes": [
            ("peito de frango", 400, "g", 0), ("farinha", 80, "g", 0),
            ("ovos", 2, "unidades", 0), ("pão ralado", 100, "g", 0),
            ("molho de tomate", 200, "ml", 0), ("queijo mozzarella", 150, "g", 0),
            ("parmesão ralado", 50, "g", 0), ("azeite", 4, "colheres de sopa", 0),
            ("sal", 1, "pitada", 0), ("pimenta preta", 1, "pitada", 0),
        ],
    },
    {
        "titulo": "Guacamole",
        "descricao": "Molho mexicano cremoso com abacate, tomate, limão e coentros.",
        "categoria": "Entrada", "dificuldade": "Fácil",
        "tempo_preparo": 15, "tempo_cozedura": 0, "porcoes": 4,
        "instrucoes": (
            "1. Extraia a polpa dos abacates e esmague com um garfo.\n"
            "2. Pique tomate (sem sementes) e cebola finamente.\n"
            "3. Misture tudo com coentros picados.\n"
            "4. Tempere com sumo de limão, sal e pimenta.\n"
            "5. Sirva imediatamente com nachos ou palitos de legumes."
        ),
        "ingredientes": [
            ("abacate", 2, "unidades", 0), ("tomate", 1, "unidades", 0),
            ("cebola", 0.5, "unidades", 0), ("limão", 1, "unidades", 0),
            ("coentros", 0.5, "ramo", 0),
            ("sal", 1, "pitada", 0), ("pimenta preta", 1, "pitada", 0),
        ],
    },
    {
        "titulo": "Pizza Margherita",
        "descricao": "Pizza italiana clássica com molho de tomate, mozzarella e manjericão.",
        "categoria": "Prato Principal", "dificuldade": "Médio",
        "tempo_preparo": 30, "tempo_cozedura": 25, "porcoes": 4,
        "instrucoes": (
            "1. Dissolva o fermento em água morna. Aguarde 10 min.\n"
            "2. Misture com farinha, sal e azeite. Amasse 10 min. Deixe levedar 1h.\n"
            "3. Pré-aqueça o forno ao máximo (250°C+).\n"
            "4. Estenda a massa, espalhe o molho e distribua a mozzarella.\n"
            "5. Leve ao forno 10-12 min até a base estar crocante.\n"
            "6. Retire e coloque manjericão fresco por cima."
        ),
        "ingredientes": [
            ("farinha de trigo", 400, "g", 0), ("fermento seco", 7, "g", 0),
            ("molho de tomate", 200, "ml", 0), ("queijo mozzarella", 250, "g", 0),
            ("azeite", 3, "colheres de sopa", 0), ("sal", 1, "colher de chá", 0),
            ("açúcar", 1, "colher de chá", 0), ("manjericão", 1, "ramo", 1),
        ],
    },
    {
        "titulo": "Sopa de Legumes",
        "descricao": "Sopa nutritiva e colorida com cenoura, batata e courgette.",
        "categoria": "Sopa", "dificuldade": "Fácil",
        "tempo_preparo": 10, "tempo_cozedura": 25, "porcoes": 4,
        "instrucoes": (
            "1. Corte cenoura, batata e courgette em cubos.\n"
            "2. Refogue cebola e alho no azeite 3 min.\n"
            "3. Adicione cenoura, batata e caldo. Cozinhe 15 min.\n"
            "4. Adicione courgette e cozinhe mais 5 min.\n"
            "5. Triture parcialmente e tempere com sal e pimenta."
        ),
        "ingredientes": [
            ("cenoura", 3, "unidades", 0), ("batata", 2, "unidades", 0),
            ("courgette", 1, "unidades", 0), ("cebola", 1, "unidades", 0),
            ("alho", 2, "dentes", 0), ("caldo de legumes", 1200, "ml", 0),
            ("azeite", 2, "colheres de sopa", 0),
            ("sal", 1, "pitada", 0), ("pimenta preta", 1, "pitada", 0),
        ],
    },
    {
        "titulo": "Panquecas",
        "descricao": "Panquecas fofas americanas, perfeitas com mel ou fruta fresca.",
        "categoria": "Pequeno-Almoço", "dificuldade": "Fácil",
        "tempo_preparo": 10, "tempo_cozedura": 15, "porcoes": 4,
        "instrucoes": (
            "1. Misture os ingredientes secos (farinha, fermento, açúcar, sal).\n"
            "2. Misture os líquidos (ovos, leite, manteiga derretida).\n"
            "3. Una os dois e misture sem bater em excesso.\n"
            "4. Cozinhe colheradas em frigideira com manteiga em lume médio.\n"
            "5. Vire quando aparecerem bolhas (2-3 min). Cozinhe mais 1-2 min."
        ),
        "ingredientes": [
            ("farinha", 200, "g", 0), ("ovos", 2, "unidades", 0),
            ("leite", 250, "ml", 0), ("manteiga", 30, "g", 0),
            ("açúcar", 30, "g", 0), ("fermento em pó", 10, "g", 0),
            ("sal", 1, "pitada", 0),
        ],
    },
    {
        "titulo": "Brownie de Chocolate",
        "descricao": "Brownie denso e húmido com chocolate negro. Uma sobremesa irresistível.",
        "categoria": "Sobremesa", "dificuldade": "Médio",
        "tempo_preparo": 15, "tempo_cozedura": 30, "porcoes": 12,
        "instrucoes": (
            "1. Pré-aqueça o forno a 175°C. Unte uma forma retangular.\n"
            "2. Derreta chocolate e manteiga em banho-maria.\n"
            "3. Adicione açúcar, depois os ovos um a um.\n"
            "4. Adicione farinha e cacau. Misture delicadamente.\n"
            "5. Leve ao forno 25-30 min (interior deve ficar húmido).\n"
            "6. Arrefeça completamente antes de cortar."
        ),
        "ingredientes": [
            ("chocolate negro", 200, "g", 0), ("manteiga", 115, "g", 0),
            ("ovos", 3, "unidades", 0), ("açúcar", 200, "g", 0),
            ("farinha", 65, "g", 0), ("cacau em pó", 30, "g", 0),
        ],
    },
    {
        "titulo": "Wrap de Atum",
        "descricao": "Wrap rápido com atum, salada e maionese. Pronto em 10 minutos.",
        "categoria": "Lanche", "dificuldade": "Fácil",
        "tempo_preparo": 10, "tempo_cozedura": 0, "porcoes": 2,
        "instrucoes": (
            "1. Misture o atum escorrido com maionese e umas gotas de limão.\n"
            "2. Coloque alface na base da tortilha.\n"
            "3. Adicione tomate em cubos e o atum com maionese.\n"
            "4. Enrole firmemente e corte ao meio na diagonal."
        ),
        "ingredientes": [
            ("atum em lata", 160, "g", 0), ("tortilha", 2, "unidades", 0),
            ("alface", 50, "g", 0), ("tomate", 1, "unidades", 0),
            ("maionese", 2, "colheres de sopa", 0),
            ("limão", 0.5, "unidades", 1),
            ("sal", 1, "pitada", 0), ("pimenta preta", 1, "pitada", 0),
        ],
    },
    {
        "titulo": "Tacos de Frango",
        "descricao": "Tacos mexicanos com frango temperado, salsa fresca e queijo.",
        "categoria": "Prato Principal", "dificuldade": "Médio",
        "tempo_preparo": 20, "tempo_cozedura": 15, "porcoes": 4,
        "instrucoes": (
            "1. Corte o frango em tiras e tempere com cominho, pimentão, sal e pimenta.\n"
            "2. Grelhe em frigideira quente com azeite por 5-7 min.\n"
            "3. Aqueça as tortilhas na frigideira seca 30 seg/lado.\n"
            "4. Monte: alface + frango + tomate + cebola + queijo.\n"
            "5. Adicione creme azedo e sirva com fatias de limão."
        ),
        "ingredientes": [
            ("peito de frango", 500, "g", 0), ("tortilha", 8, "unidades", 0),
            ("alface", 100, "g", 0), ("tomate", 2, "unidades", 0),
            ("cebola", 0.5, "unidades", 0), ("limão", 1, "unidades", 0),
            ("cominho", 1, "colher de chá", 0), ("pimentão", 1, "colher de chá", 0),
            ("azeite", 2, "colheres de sopa", 0),
            ("queijo ralado", 80, "g", 1), ("creme azedo", 100, "ml", 1),
            ("coentros", 0.5, "ramo", 1),
            ("sal", 1, "pitada", 0), ("pimenta preta", 1, "pitada", 0),
        ],
    },
    # ── 20 RECEITAS BÁSICAS ADICIONAIS ─────────────────────────────────────────
    {
        "titulo": "Arroz Branco Simples",
        "descricao": "Arroz branco soltinho, o acompanhamento básico perfeito para qualquer refeição.",
        "categoria": "Acompanhamento", "dificuldade": "Fácil",
        "tempo_preparo": 5, "tempo_cozedura": 15, "porcoes": 4,
        "instrucoes": "1. Pique o alho e refogue-o no azeite quente até dourar.\n2. Adicione o arroz e mexa bem por 1 minuto.\n3. Adicione a água a ferver e o sal.\n4. Coza em lume brando com o tacho semi-tapado por 15 minutos até a água secar.",
        "ingredientes": [
            ("arroz", 200, "g", 0), ("agua", 400, "ml", 0),
            ("alho", 1, "dentes", 0), ("azeite", 1, "colheres de sopa", 0),
            ("sal", 1, "pitada", 0)
        ]
    },
    {
        "titulo": "Massa Alho e Óleo",
        "descricao": "Uma refeição rápida e deliciosa com ingredientes simples que todos têm em casa.",
        "categoria": "Prato Principal", "dificuldade": "Fácil",
        "tempo_preparo": 5, "tempo_cozedura": 10, "porcoes": 2,
        "instrucoes": "1. Coza a massa em água com sal abundante.\n2. Enquanto isso, doure os dentes de alho laminados no azeite sem queimar.\n3. Escorra a massa e misture-a diretamente no azeite com alho.\n4. Polvilhe com salsa picada e sirva.",
        "ingredientes": [
            ("esparguete", 200, "g", 0), ("alho", 4, "dentes", 0),
            ("azeite", 3, "colheres de sopa", 0), ("salsa", 1, "ramo", 1),
            ("sal", 1, "pitada", 0)
        ]
    },
    {
        "titulo": "Sopa de Alho-Francês",
        "descricao": "Sopa reconfortante e cremosa, ideal para dias mais frios.",
        "categoria": "Sopa", "dificuldade": "Fácil",
        "tempo_preparo": 10, "tempo_cozedura": 20, "porcoes": 4,
        "instrucoes": "1. Corte a cebola, a batata e o alho-francês em pedaços.\n2. Refogue a cebola e o alho-francês no azeite por 5 minutos.\n3. Junte a batata e a água quente. Tempere com sal e coza até que a batata esteja tenra.\n4. Triture a sopa com a varinha mágica até obter um creme liso.",
        "ingredientes": [
            ("alho-frances", 2, "unidades", 0), ("batata", 3, "unidades", 0),
            ("cebola", 1, "unidades", 0), ("azeite", 2, "colheres de sopa", 0),
            ("agua", 1000, "ml", 0), ("sal", 1, "pitada", 0)
        ]
    },
    {
        "titulo": "Ovos Mexidos com Tomate",
        "descricao": "Ovos mexidos simples enriquecidos com tomate fresco suculento.",
        "categoria": "Lanche", "dificuldade": "Fácil",
        "tempo_preparo": 5, "tempo_cozedura": 8, "porcoes": 2,
        "instrucoes": "1. Pique o tomate e refogue-o na manteiga até que amacie ligeiramente.\n2. Bata os ovos com sal e pimenta.\n3. Verta os ovos sobre o tomate e coza em lume brando mexendo sempre até ao ponto desejado.",
        "ingredientes": [
            ("ovos", 4, "unidades", 0), ("tomate", 1, "unidades", 0),
            ("manteiga", 1, "colheres de sopa", 0), ("sal", 1, "pitada", 0),
            ("pimenta preta", 1, "pitada", 1)
        ]
    },
    {
        "titulo": "Puré de Batata Caseiro",
        "descricao": "Puré de batata cremoso e aveludado com um toque de noz-moscada.",
        "categoria": "Acompanhamento", "dificuldade": "Fácil",
        "tempo_preparo": 10, "tempo_cozedura": 20, "porcoes": 4,
        "instrucoes": "1. Descasque e coza as batatas em água com sal.\n2. Escorra as batatas e esmague-as ainda quentes.\n3. Junte a manteiga, o leite quente e tempere com noz-moscada.\n4. Mexa vigorosamente até ficar cremoso.",
        "ingredientes": [
            ("batata", 800, "g", 0), ("leite", 150, "ml", 0),
            ("manteiga", 50, "g", 0), ("sal", 1, "pitada", 0),
            ("noz-moscada", 1, "pitada", 1)
        ]
    },
    {
        "titulo": "Atum com Grão de Bico",
        "descricao": "Uma salada fria de preparação super rápida e nutritiva.",
        "categoria": "Prato Principal", "dificuldade": "Fácil",
        "tempo_preparo": 10, "tempo_cozedura": 0, "porcoes": 2,
        "instrucoes": "1. Escorra o atum e o grão de bico enlatado.\n2. Pique a cebola, o alho e o ovo cozido.\n3. Misture tudo numa taça.\n4. Tempere com azeite, vinagre, sal e salsa picada.",
        "ingredientes": [
            ("grao de bico cozido", 400, "g", 0), ("atum em lata", 2, "unidades", 0),
            ("ovo cozido", 1, "unidades", 1), ("cebola", 0.5, "unidades", 0),
            ("azeite", 2, "colheres de sopa", 0), ("vinagre", 1, "colheres de sopa", 0),
            ("salsa", 1, "ramo", 1)
        ]
    },
    {
        "titulo": "Sopa de Cenoura Macia",
        "descricao": "Sopa de cenoura simples, doce e cremosa, óptima para iniciar qualquer refeição.",
        "categoria": "Sopa", "dificuldade": "Fácil",
        "tempo_preparo": 10, "tempo_cozedura": 20, "porcoes": 4,
        "instrucoes": "1. Descasque as cenouras e a batata cortando-as em pedaços.\n2. Leve a cozer com a cebola cortada em água temperada com sal.\n3. Adicione o azeite e triture tudo muito bem após a cozedura.",
        "ingredientes": [
            ("cenoura", 4, "unidades", 0), ("batata", 2, "unidades", 0),
            ("cebola", 1, "unidades", 0), ("azeite", 2, "colheres de sopa", 0),
            ("sal", 1, "pitada", 0)
        ]
    },
    {
        "titulo": "Sandes de Fiambre e Queijo Grelhada",
        "descricao": "A famosa tosta mista rápida e crocante feita na frigideira.",
        "categoria": "Lanche", "dificuldade": "Fácil",
        "tempo_preparo": 5, "tempo_cozedura": 5, "porcoes": 1,
        "instrucoes": "1. Barre um pouco de manteiga na parte externa de cada fatia de pão.\n2. Recheie com queijo e fiambre.\n3. Grelhe numa frigideira quente até dourar de ambos os lados e o queijo derreter.",
        "ingredientes": [
            ("pao", 2, "fatias", 0), ("queijo", 1, "fatias", 0),
            ("fiambre", 1, "fatias", 0), ("manteiga", 10, "g", 0)
        ]
    },
    {
        "titulo": "Salada de Tomate e Pepino",
        "descricao": "Salada fresca de verão bem temperada, tipicamente portuguesa.",
        "categoria": "Entrada", "dificuldade": "Fácil",
        "tempo_preparo": 10, "tempo_cozedura": 0, "porcoes": 2,
        "instrucoes": "1. Lave e corte os tomates em gomos e o pepino em rodelas.\n2. Adicione a cebola cortada em meias-luas finas.\n3. Tempere com sal, azeite, vinagre e orégãos.",
        "ingredientes": [
            ("tomate", 2, "unidades", 0), ("pepino", 1, "unidades", 0),
            ("cebola", 0.5, "unidades", 0), ("azeite", 2, "colheres de sopa", 0),
            ("vinagre", 1, "colheres de sopa", 0), ("oregaos", 1, "pitada", 1)
        ]
    },
    {
        "titulo": "Couve Salteada com Alho",
        "descricao": "Acompanhamento verde rápido, saudável e rico em sabor.",
        "categoria": "Acompanhamento", "dificuldade": "Fácil",
        "tempo_preparo": 5, "tempo_cozedura": 10, "porcoes": 2,
        "instrucoes": "1. Lave bem as folhas de couve e corte-as em tiras finas.\n2. Numa frigideira com azeite, doure os dentes de alho picados.\n3. Adicione a couve e salteie até murchar e ficar macia mas firme. Tempere com sal.",
        "ingredientes": [
            ("couve", 300, "g", 0), ("alho", 2, "dentes", 0),
            ("azeite", 2, "colheres de sopa", 0), ("sal", 1, "pitada", 0)
        ]
    },
    {
        "titulo": "Creme de Abóbora",
        "descricao": "Uma sopa aveludada, de cor vibrante e sabor ligeiramente adocicado.",
        "categoria": "Sopa", "dificuldade": "Fácil",
        "tempo_preparo": 10, "tempo_cozedura": 20, "porcoes": 4,
        "instrucoes": "1. Descasque a abóbora e as batatas, cortando em cubos.\n2. Coza em água quente com a cebola e sal.\n3. Adicione azeite e triture até ficar homogéneo.",
        "ingredientes": [
            ("abobora", 600, "g", 0), ("batata", 2, "unidades", 0),
            ("cebola", 1, "unidades", 0), ("azeite", 2, "colheres de sopa", 0),
            ("sal", 1, "pitada", 0)
        ]
    },
    {
        "titulo": "Cogumelos Salteados",
        "descricao": "Cogumelos frescos salteados com alho e azeite, perfeitos como entrada.",
        "categoria": "Entrada", "dificuldade": "Fácil",
        "tempo_preparo": 5, "tempo_cozedura": 10, "porcoes": 2,
        "instrucoes": "1. Limpe e lamine os cogumelos.\n2. Numa frigideira, aqueça o azeite e doure ligeiramente o alho.\n3. Junte os cogumelos e salteie em lume forte por 8 minutos até dourar. Tempere com sal e salsa.",
        "ingredientes": [
            ("cogumelos frescos", 250, "g", 0), ("alho", 2, "dentes", 0),
            ("azeite", 2, "colheres de sopa", 0), ("salsa", 1, "ramo", 1),
            ("sal", 1, "pitada", 0)
        ]
    },
    {
        "titulo": "Ervilhas com Ovo Escalfado",
        "descricao": "Um prato tradicional do dia a dia, reconfortante e rico.",
        "categoria": "Prato Principal", "dificuldade": "Fácil",
        "tempo_preparo": 10, "tempo_cozedura": 20, "porcoes": 2,
        "instrucoes": "1. Refogue cebola e alho no azeite. Adicione cubos de bacon.\n2. Junte as ervilhas e um pouco de água. Tape e cozinhe por 10 minutos.\n3. Abra pequenos espaços nas ervilhas e parta os ovos lá dentro.\n4. Tape e deixe cozer os ovos em lume brando até escalfarem.",
        "ingredientes": [
            ("ervilhas", 300, "g", 0), ("ovos", 2, "unidades", 0),
            ("bacon", 50, "g", 1), ("cebola", 0.5, "unidades", 0),
            ("azeite", 2, "colheres de sopa", 0), ("sal", 1, "pitada", 0)
        ]
    },
    {
        "titulo": "Batatas a Murro Simples",
        "descricao": "Batatas assadas esmagadas e regadas generosamente com azeite e alho.",
        "categoria": "Acompanhamento", "dificuldade": "Fácil",
        "tempo_preparo": 5, "tempo_cozedura": 30, "porcoes": 4,
        "instrucoes": "1. Lave bem as batatas pequenas com pele e coza com sal.\n2. Coloque-as num tabuleiro e dê um pequeno murro em cada uma para rachar.\n3. Espalhe alho picado por cima e regue generosamente com azeite.\n4. Leve ao forno a 200°C por 15 minutos até dourarem.",
        "ingredientes": [
            ("batata pequena", 800, "g", 0), ("alho", 4, "dentes", 0),
            ("azeite", 100, "ml", 0), ("sal", 1, "colher de sopa", 0)
        ]
    },
    {
        "titulo": "Frittata de Legumes",
        "descricao": "Omelete de forno italiana, ideal para usar sobras de vegetais.",
        "categoria": "Prato Principal", "dificuldade": "Fácil",
        "tempo_preparo": 10, "tempo_cozedura": 15, "porcoes": 3,
        "instrucoes": "1. Salteie os legumes (ex: tomate, espinafres) numa frigideira com azeite.\n2. Bata os ovos com sal e pimenta e verta sobre os legumes.\n3. Cozinhe por 5 minutos no fogão e leve ao forno pré-aquecido a 180°C por 10 minutos para dourar o topo.",
        "ingredientes": [
            ("ovos", 6, "unidades", 0), ("tomate", 1, "unidades", 1),
            ("espinafres", 100, "g", 1), ("azeite", 1, "colheres de sopa", 0),
            ("sal", 1, "pitada", 0)
        ]
    },
    {
        "titulo": "Cuscuz Rápido",
        "descricao": "Cuscuz hidratado super veloz com pequenos cubos de vegetais.",
        "categoria": "Acompanhamento", "dificuldade": "Fácil",
        "tempo_preparo": 5, "tempo_cozedura": 5, "porcoes": 2,
        "instrucoes": "1. Ferva a água com uma pitada de sal e um fio de azeite.\n2. Verta a água a ferver sobre o cuscuz numa taça e tape por 5 minutos.\n3. Solte o cuscuz com um garfo e misture o tomate picado e os orégãos.",
        "ingredientes": [
            ("cuscuz", 150, "g", 0), ("agua", 150, "ml", 0),
            ("tomate", 1, "unidades", 1), ("azeite", 1, "colheres de sopa", 0),
            ("sal", 1, "pitada", 0)
        ]
    },
    {
        "titulo": "Pescada Cozida com Legumes",
        "descricao": "Uma refeição leve, simples, saudável e tradicional portuguesa.",
        "categoria": "Prato Principal", "dificuldade": "Fácil",
        "tempo_preparo": 10, "tempo_cozedura": 15, "porcoes": 2,
        "instrucoes": "1. Descasque as batatas e as cenouras cortando-as em rodelas grossas.\n2. Leve-as a cozer num tacho com água e sal.\n3. A meio da cozedura (cerca de 8 minutos depois), junte as postas de pescada.\n4. Escorra e sirva regado com azeite.",
        "ingredientes": [
            ("postas de pescada", 2, "unidades", 0), ("batata", 2, "unidades", 0),
            ("cenoura", 1, "unidades", 0), ("azeite", 2, "colheres de sopa", 0),
            ("sal", 1, "pitada", 0)
        ]
    },
    {
        "titulo": "Sopa de Lentilhas",
        "descricao": "Sopa proteica e reconfortante muito rápida usando lentilhas vermelhas.",
        "categoria": "Sopa", "dificuldade": "Fácil",
        "tempo_preparo": 10, "tempo_cozedura": 20, "porcoes": 4,
        "instrucoes": "1. Refogue cebola, alho e cenoura cortada no azeite.\n2. Adicione as lentilhas vermelhas bem lavadas e o tomate pelado.\n3. Cubra com água ou caldo de legumes quente, tempere com sal e coza por 20 minutos até as lentilhas estarem tenras.",
        "ingredientes": [
            ("lentilhas vermelhas", 200, "g", 0), ("cenoura", 1, "unidades", 0),
            ("tomate pelado", 200, "g", 0), ("cebola", 1, "unidades", 0),
            ("azeite", 2, "colheres de sopa", 0), ("sal", 1, "pitada", 0)
        ]
    },
    {
        "titulo": "Pão de Alho Caseiro",
        "descricao": "Pão torrado estaladiço besuntado com uma pasta de alho e manteiga.",
        "categoria": "Lanche", "dificuldade": "Fácil",
        "tempo_preparo": 5, "tempo_cozedura": 8, "porcoes": 3,
        "instrucoes": "1. Misture a manteiga amolecida com o alho picado e salsa.\n2. Faça cortes no pão sem o fatiar totalmente.\n3. Espalhe a pasta de manteiga de alho nos cortes do pão.\n4. Leve ao forno a 180°C por 8 minutos até dourar e ficar crocante.",
        "ingredientes": [
            ("pao baguette", 1, "unidades", 0), ("manteiga", 50, "g", 0),
            ("alho", 3, "dentes", 0), ("salsa", 1, "ramo", 1)
        ]
    },
    {
        "titulo": "Limonada com Hortelã",
        "descricao": "Bebida refrescante e cítrica excelente para acompanhar refeições quentes.",
        "categoria": "Lanche", "dificuldade": "Fácil",
        "tempo_preparo": 5, "tempo_cozedura": 0, "porcoes": 4,
        "instrucoes": "1. Esprema o sumo dos limões.\n2. Numa jarra misture o sumo, a água e o açúcar até dissolver.\n3. Adicione folhas de hortelã fresca e gelo antes de servir.",
        "ingredientes": [
            ("limao", 3, "unidades", 0), ("agua", 1000, "ml", 0),
            ("acucar", 4, "colheres de sopa", 0), ("hortela", 1, "ramo", 1)
        ]
    },

    # ── 10 RECEITAS AVANÇADAS ADICIONAIS ───────────────────────────────────────
    {
        "titulo": "Arroz de Marisco",
        "descricao": "Clássico arroz caldoso português rico em marisco, coentros e limão.",
        "categoria": "Prato Principal", "dificuldade": "Difícil",
        "tempo_preparo": 25, "tempo_cozedura": 25, "porcoes": 4,
        "instrucoes": "1. Coza as cascas e cabeças do camarão para fazer o caldo de marisco.\n2. Faça um refogado rico com azeite, cebola, alho, tomate picado e pimento.\n3. Adicione o arroz carolino e regue gradualmente com o caldo quente.\n4. Junte o camarão descascado, amêijoas e mexilhões a meio da cozedura.\n5. Sirva caldoso com muitos coentros frescos e sumo de limão.",
        "ingredientes": [
            ("camarao", 400, "g", 0), ("ameijoas", 300, "g", 0),
            ("mexilhao", 300, "g", 0), ("arroz carolino", 300, "g", 0),
            ("cebola", 1, "unidades", 0), ("alho", 3, "dentes", 0),
            ("tomate", 2, "unidades", 0), ("pimento", 0.5, "unidades", 1),
            ("coentros", 1, "ramo", 0), ("limao", 0.5, "unidades", 1),
            ("azeite", 3, "colheres de sopa", 0), ("sal", 1, "pitada", 0)
        ]
    },
    {
        "titulo": "Bacalhau com Natas",
        "descricao": "Bacalhau desfiado cremoso cozinhado no forno com batatas fritas e bechamel caseiro.",
        "categoria": "Prato Principal", "dificuldade": "Difícil",
        "tempo_preparo": 30, "tempo_cozedura": 30, "porcoes": 6,
        "instrucoes": "1. Desfie e refogue o bacalhau com cebola às rodelas e alho em azeite.\n2. Adicione as batatas fritas em cubos pequenos.\n3. Faça um molho bechamel caseiro derretendo manteiga com farinha e adicionando leite aos poucos.\n4. Envolva o bacalhau, batatas e bechamel com as natas.\n5. Coloque tudo num tabuleiro, cubra com queijo ralado e leve a gratinar no forno.",
        "ingredientes": [
            ("bacalhau desfiado", 500, "g", 0), ("batata frita em cubos", 400, "g", 0),
            ("leite", 500, "ml", 0), ("manteiga", 40, "g", 0),
            ("farinha de trigo", 40, "g", 0), ("natas", 200, "ml", 0),
            ("cebola", 2, "unidades", 0), ("queijo ralado", 100, "g", 1),
            ("sal", 1, "pitada", 0)
        ]
    },
    {
        "titulo": "Carne de Porco à Alentejana",
        "descricao": "Mistura singular de cubos de porco fritos com amêijoas frescas e coentros.",
        "categoria": "Prato Principal", "dificuldade": "Difícil",
        "tempo_preparo": 30, "tempo_cozedura": 20, "porcoes": 4,
        "instrucoes": "1. Marine a carne de porco cortada em cubos com vinho branco, massa de pimentão, alho e sal durante 4 horas.\n2. Frite a carne marinada na banha de porco quente até dourar.\n3. Adicione o molho da marinada e deixe apurar.\n4. Junte as amêijoas limpas, tape e cozinhe até abrirem.\n5. Sirva com batatas fritas aos cubos polvilhado com coentros.",
        "ingredientes": [
            ("carne de porco", 800, "g", 0), ("ameijoas", 500, "g", 0),
            ("massa de pimentao", 2, "colheres de sopa", 0), ("vinho branco", 150, "ml", 0),
            ("alho", 4, "dentes", 0), ("banha de porco", 2, "colheres de sopa", 0),
            ("batata frita em cubos", 500, "g", 0), ("coentros", 1, "ramo", 0)
        ]
    },
    {
        "titulo": "Feijoada à Transmontana",
        "descricao": "Feijoada rica e consistente à base de carnes de porco e enchidos tradicionais.",
        "categoria": "Prato Principal", "dificuldade": "Difícil",
        "tempo_preparo": 40, "tempo_cozedura": 60, "porcoes": 6,
        "instrucoes": "1. Coza as carnes de porco e os enchidos em água temperada.\n2. Retire e corte em pedaços pequenos.\n3. Faça um refogado com azeite, cebola, alho e tomate.\n4. Adicione o feijão cozido, a couve lombarda e a cenoura.\n5. Junte as carnes cozidas e o caldo destas. Cozinhe em lume brando até apurar.",
        "ingredientes": [
            ("feijao encarnado cozido", 800, "g", 0), ("orelha de porco", 300, "g", 0),
            ("entrecosto", 400, "g", 0), ("chourico", 1, "unidades", 0),
            ("morcela", 1, "unidades", 0), ("couve lombarda", 0.5, "unidades", 0),
            ("cenoura", 2, "unidades", 0), ("tomate", 2, "unidades", 0),
            ("sal", 1, "pitada", 0)
        ]
    },
    {
        "titulo": "Polvo à Lagareiro",
        "descricao": "Polvo cozido e depois assado no forno regado com azeite aromatizado com alho.",
        "categoria": "Prato Principal", "dificuldade": "Difícil",
        "tempo_preparo": 20, "tempo_cozedura": 50, "porcoes": 4,
        "instrucoes": "1. Coza o polvo numa panela de pressão com uma cebola inteira por 35 minutos.\n2. Coloque as batatas pequenas no forno com pele e sal grosso.\n3. Disponha o polvo num tabuleiro de forno, cerque com as batatas levemente esmagadas.\n4. Cubra com lâminas de alho picado e regue generosamente com azeite.\n5. Asse a 200°C por 15 minutos até alourar.",
        "ingredientes": [
            ("polvo", 1200, "g", 0), ("batata pequena", 800, "g", 0),
            ("alho", 6, "dentes", 0), ("azeite", 200, "ml", 0),
            ("cebola", 1, "unidades", 0), ("sal grosso", 1, "colher de sopa", 0)
        ]
    },
    {
        "titulo": "Vitela Assada no Forno",
        "descricao": "Assado tenro de vitela temperado com especiarias e vinho branco acompanhado de batatas.",
        "categoria": "Prato Principal", "dificuldade": "Difícil",
        "tempo_preparo": 20, "tempo_cozedura": 90, "porcoes": 6,
        "instrucoes": "1. Barre a carne com uma mistura de alho, sal, pimentão, louro e azeite.\n2. Deixe marinar por 2 horas.\n3. Coloque no forno a 180°C com vinho branco e cebola.\n4. Junte as batatas e as cenouras a meio da cozedura e vá regando com o próprio molho até a carne ficar tenra.",
        "ingredientes": [
            ("carne de vitela para assar", 1200, "g", 0), ("batata", 800, "g", 0),
            ("cenoura", 2, "unidades", 0), ("vinho branco", 200, "ml", 0),
            ("alho", 5, "dentes", 0), ("azeite", 50, "ml", 0),
            ("pimentao doce", 1, "colher de sopa", 0), ("sal", 1, "pitada", 0)
        ]
    },
    {
        "titulo": "Caldeirada de Peixe",
        "descricao": "Gisado tradicional de peixe fresco em camadas de cebola, pimentos e batatas.",
        "categoria": "Prato Principal", "dificuldade": "Difícil",
        "tempo_preparo": 25, "tempo_cozedura": 30, "porcoes": 4,
        "instrucoes": "1. Num tacho largo, disponha em camadas alternadas: cebola, alho, pimento, batata e peixe variado.\n2. Regue cada camada com tomate picado, azeite, vinho branco e uma pitada de sal.\n3. Leve a cozinhar em lume brando com o tacho tapado para libertar os sumos.\n4. Sirva quando a batata estiver macia, decorado com salsa.",
        "ingredientes": [
            ("peixe variado em postas", 800, "g", 0), ("batata", 4, "unidades", 0),
            ("pimento", 1, "unidades", 0), ("cebola", 2, "unidades", 0),
            ("tomate", 2, "unidades", 0), ("vinho branco", 100, "ml", 0),
            ("azeite", 4, "colheres de sopa", 0), ("salsa", 1, "ramo", 1)
        ]
    },
    {
        "titulo": "Lasanha de Carne Caseira",
        "descricao": "Lasagna clássica italiana com massa fresca, ragú de carne e bechamel.",
        "categoria": "Prato Principal", "dificuldade": "Difícil",
        "tempo_preparo": 30, "tempo_cozedura": 40, "porcoes": 6,
        "instrucoes": "1. Prepare o ragú de carne picada com cebola, alho, cenoura picada e molho de tomate.\n2. Prepare o molho bechamel.\n3. Num prato de forno, intercale folhas de massa, molho de carne e bechamel.\n4. Termine com queijo mozzarella e leve ao forno a 180°C por 30 minutos.",
        "ingredientes": [
            ("placas de massa lasanha", 12, "unidades", 0), ("carne picada", 600, "g", 0),
            ("molho de tomate", 400, "g", 0), ("leite", 400, "ml", 0),
            ("farinha de trigo", 30, "g", 0), ("manteiga", 30, "g", 0),
            ("queijo mozzarella", 200, "g", 0), ("sal", 1, "pitada", 0)
        ]
    },
    {
        "titulo": "Ramen Caseiro de Porco",
        "descricao": "Sopa de noodles japonesa com caldo de ossos de porco cozinhado lentamente.",
        "categoria": "Prato Principal", "dificuldade": "Difícil",
        "tempo_preparo": 40, "tempo_cozedura": 120, "porcoes": 3,
        "instrucoes": "1. Cozinhe lentamente os ossos e carnes de porco com gengibre e alho para formar um caldo rico.\n2. Coza os ovos mantendo a gema mole (6 minutos) e marine-os em molho de soja.\n3. Coza os noodles em água.\n4. Monte as taças: noodles no fundo, caldo de porco bem quente, fatias de carne, ovo marinado cortado ao meio e cebolinho fresco.",
        "ingredientes": [
            ("noodles para ramen", 300, "g", 0), ("carne de porco", 400, "g", 0),
            ("ovos", 3, "unidades", 0), ("molho de soja", 50, "ml", 0),
            ("gengibre fresco", 10, "g", 0), ("cebolinho", 1, "ramo", 0),
            ("alho", 3, "dentes", 0), ("sal", 1, "pitada", 0)
        ]
    },
    {
        "titulo": "Paella Valenciana",
        "descricao": "Prato festivo espanhol de arroz açafrão com marisco, lulas e frango.",
        "categoria": "Prato Principal", "dificuldade": "Difícil",
        "tempo_preparo": 30, "tempo_cozedura": 30, "porcoes": 6,
        "instrucoes": "1. Doure pedaços de frango e lulas numa paellera larga com azeite.\n2. Adicione cebola picada, pimento e alho.\n3. Junte o arroz e o açafrão.\n4. Adicione o caldo de marisco quente e coza sem mexer.\n5. Coloque camarões e mexilhões decorando o topo e coza até que o caldo seque totalmente.",
        "ingredientes": [
            ("arroz bombra", 400, "g", 0), ("camarao", 300, "g", 0),
            ("mexilhao", 300, "g", 0), ("lulas", 200, "g", 0),
            ("peito de frango", 200, "g", 0), ("acafrao", 1, "pitada", 0),
            ("pimento", 1, "unidades", 0), ("caldo de marisco", 1000, "ml", 0),
            ("azeite", 3, "colheres de sopa", 0), ("sal", 1, "pitada", 0)
        ]
    },

    # ── 10 DOCES ADICIONAIS ───────────────────────────────────────────────────
    {
        "titulo": "Pastéis de Nata Caseiros",
        "descricao": "O doce nacional português mais famoso com massa folhada estaladiça e creme rico.",
        "categoria": "Sobremesa", "dificuldade": "Difícil",
        "tempo_preparo": 30, "tempo_cozedura": 15, "porcoes": 12,
        "instrucoes": "1. Forre forminhas de metal com a massa folhada enrolada fina.\n2. Ferva o leite com canela e casca de limão.\n3. Faça uma calda com água e açúcar. Junte ao leite e depois à farinha diluída.\n4. Incorpore as gemas de ovo batidas no creme morno.\n5. Verta nas formas e asse a 250°C (temperatura máxima do forno) por 10 minutos.",
        "ingredientes": [
            ("massa folhada", 1, "unidades", 0), ("gemas de ovo", 6, "unidades", 0),
            ("leite", 500, "ml", 0), ("acucar", 250, "g", 0),
            ("farinha de trigo", 40, "g", 0), ("canela em pau", 1, "unidades", 1),
            ("limao", 1, "unidades", 1), ("agua", 150, "ml", 0)
        ]
    },
    {
        "titulo": "Arroz Doce Cremoso",
        "descricao": "Arroz doce à moda antiga com gema de ovo e pó de canela para desenhar.",
        "categoria": "Sobremesa", "dificuldade": "Médio",
        "tempo_preparo": 10, "tempo_cozedura": 35, "porcoes": 6,
        "instrucoes": "1. Coza o arroz em água com sal e a casca de limão.\n2. Quando a água secar, adicione o leite morno gradualmente mexendo sempre.\n3. Junte o açúcar e mexa por mais 5 minutos.\n4. Retire do lume e junte lentamente as gemas de ovo mexendo bem para não cozerem.\n5. Sirva polvilhado com canela em pó.",
        "ingredientes": [
            ("arroz", 150, "g", 0), ("leite", 1000, "ml", 0),
            ("acucar", 150, "g", 0), ("gemas de ovo", 3, "unidades", 0),
            ("limao", 1, "unidades", 1), ("canela em po", 1, "colher de sopa", 1),
            ("sal", 1, "pitada", 0)
        ]
    },
    {
        "titulo": "Mousse de Chocolate Tradicional",
        "descricao": "Mousse de chocolate caseira, leve, fofa e muito escura.",
        "categoria": "Sobremesa", "dificuldade": "Médio",
        "tempo_preparo": 15, "tempo_cozedura": 5, "porcoes": 6,
        "instrucoes": "1. Derreta o chocolate negro com a manteiga em banho-maria.\n2. Junte as gemas de ovo ao chocolate derretido morno mexendo rapidamente.\n3. Bata as claras em castelo bem firme.\n4. Envolva as claras em castelo delicadamente na mistura de chocolate.\n5. Verta em taças e refrigere por pelo menos 4 horas.",
        "ingredientes": [
            ("chocolate negro", 200, "g", 0), ("ovos", 6, "unidades", 0),
            ("manteiga", 50, "g", 0), ("acucar", 100, "g", 1)
        ]
    },
    {
        "titulo": "Bolo de Bolacha",
        "descricao": "Sobremesa tradicional portuguesa em camadas de bolacha Maria embebida em café e creme de manteiga.",
        "categoria": "Sobremesa", "dificuldade": "Médio",
        "tempo_preparo": 25, "tempo_cozedura": 0, "porcoes": 8,
        "instrucoes": "1. Bata a manteiga com o açúcar em pó e a gema de ovo até obter um creme esbranquiçado.\n2. Prepare o café forte e deixe-o arrefecer.\n3. Passe as bolachas Maria rapidamente pelo café morno.\n4. Intercale camadas de bolacha e creme de manteiga.\n5. Cubra tudo com o creme restante e decore com bolacha ralada fina.",
        "ingredientes": [
            ("bolacha maria", 2, "pacote", 0), ("manteiga", 250, "g", 0),
            ("acucar em po", 200, "g", 0), ("gemas de ovo", 1, "unidades", 1),
            ("cafe forte preparado", 250, "ml", 0)
        ]
    },
    {
        "titulo": "Tarte de Maçã Rápida",
        "descricao": "Tarte fina de massa folhada coberta com fatias finas de maçã e geleia.",
        "categoria": "Sobremesa", "dificuldade": "Fácil",
        "tempo_preparo": 15, "tempo_cozedura": 25, "porcoes": 6,
        "instrucoes": "1. Estenda a massa folhada numa tarteira.\n2. Descasque e fatie as maçãs finamente, dispondo em círculos sobre a massa.\n3. Polvilhe com açúcar e canela.\n4. Leve ao forno a 190°C até a massa dourar.\n5. Pincele com geleia de pêssego/açúcar ainda quente para dar brilho.",
        "ingredientes": [
            ("massa folhada", 1, "unidades", 0), ("maca", 3, "unidades", 0),
            ("acucar", 30, "g", 0), ("canela em po", 1, "colher de cha", 0),
            ("geleia para pincelar", 2, "colheres de sopa", 1)
        ]
    },
    {
        "titulo": "Bolo de Laranja Húmido",
        "descricao": "Bolo caseiro perfumado muito fofo regado com calda de laranja fresca.",
        "categoria": "Sobremesa", "dificuldade": "Fácil",
        "tempo_preparo": 15, "tempo_cozedura": 40, "porcoes": 8,
        "instrucoes": "1. Bata o açúcar com a manteiga. Adicione os ovos um a um.\n2. Misture a raspa e o sumo de laranja.\n3. Incorpore a farinha de trigo e o fermento em pó.\n4. Asse a 180°C por 40 minutos. Regue com sumo de laranja quente logo ao retirar do forno.",
        "ingredientes": [
            ("laranja", 2, "unidades", 0), ("farinha de trigo", 250, "g", 0),
            ("acucar", 200, "g", 0), ("ovos", 4, "unidades", 0),
            ("manteiga", 100, "g", 0), ("fermento em po", 1, "colher de sopa", 0)
        ]
    },
    {
        "titulo": "Panna Cotta de Morango",
        "descricao": "Sobremesa italiana de natas cozidas gelificadas acompanhada de molho de morango.",
        "categoria": "Sobremesa", "dificuldade": "Médio",
        "tempo_preparo": 15, "tempo_cozedura": 10, "porcoes": 4,
        "instrucoes": "1. Hidrate as folhas de gelatina em água fria.\n2. Aqueça as natas, o leite e o açúcar até quase ferver.\n3. Dissolva a gelatina espremida na mistura morna.\n4. Distribua por copos e refrigere por 4 horas.\n5. Cubra com morangos reduzidos a puré com um pouco de açúcar.",
        "ingredientes": [
            ("natas", 400, "ml", 0), ("leite", 100, "ml", 0),
            ("acucar", 80, "g", 0), ("gelatina em folha", 3, "unidades", 0),
            ("morangos", 200, "g", 0)
        ]
    },
    {
        "titulo": "Serradura",
        "descricao": "Sobremesa clássica de Macau e muito popular em Portugal com bolacha esmagada e natas.",
        "categoria": "Sobremesa", "dificuldade": "Fácil",
        "tempo_preparo": 15, "tempo_cozedura": 0, "porcoes": 4,
        "instrucoes": "1. Triture as bolachas Maria até ficarem como serradura fina.\n2. Bata as natas bem frias até ficarem firmes.\n3. Junte o leite condensado às natas batidas mexendo delicadamente.\n4. Em copos individuais, intercale camadas de bolacha triturada e creme.\n5. Termine com uma camada de bolacha e guarde no frio por 2 horas.",
        "ingredientes": [
            ("natas", 400, "ml", 0), ("leite condensado", 200, "g", 0),
            ("bolacha maria", 150, "g", 0)
        ]
    },
    {
        "titulo": "Salada de Fruta Fresca",
        "descricao": "Uma sobremesa saudável e leve com frutas frescas da época.",
        "categoria": "Sobremesa", "dificuldade": "Fácil",
        "tempo_preparo": 10, "tempo_cozedura": 0, "porcoes": 4,
        "instrucoes": "1. Descasque e corte todas as frutas em cubos pequenos.\n2. Coloque-as numa taça grande.\n3. Verta o sumo de laranja sobre as frutas para não oxidarem e adicione folhas de hortelã fresca.",
        "ingredientes": [
            ("maca", 1, "unidades", 0), ("banana", 1, "unidades", 0),
            ("laranja", 2, "unidades", 0), ("abacaxi", 200, "g", 1),
            ("morangos", 100, "g", 1), ("hortela", 1, "ramo", 1)
        ]
    },
    {
        "titulo": "Bolo de Caneca de Chocolate",
        "descricao": "Bolo individual ultra rápido feito no microondas em apenas 2 minutos.",
        "categoria": "Sobremesa", "dificuldade": "Fácil",
        "tempo_preparo": 3, "tempo_cozedura": 2, "porcoes": 1,
        "instrucoes": "1. Junte todos os ingredientes secos diretamente numa caneca grande.\n2. Adicione o ovo, o leite e o óleo mexendo muito bem com um garfo.\n3. Leve ao microondas na potência máxima por 1 minuto e 30 segundos.\n4. Sirva morno.",
        "ingredientes": [
            ("farinha de trigo", 4, "colheres de sopa", 0), ("acucar", 3, "colheres de sopa", 0),
            ("cacau em po", 2, "colheres de sopa", 0), ("ovos", 1, "unidades", 0),
            ("leite", 3, "colheres de sopa", 0), ("oleo", 2, "colheres de sopa", 0),
            ("fermento em po", 1, "pitada", 0)
        ]
    }
]


def executar_migracoes() -> None:
    """
    Prepara a base de dados para uso:
      1. Cria as tabelas (se ainda não existirem)
      2. Insere as 20 receitas de exemplo (apenas se a tabela estiver vazia)

    Esta função é segura para correr várias vezes: o SQL usa "IF NOT EXISTS"
    e verificamos se já existem receitas antes de inserir.
    """
    conexao = obter_conexao()
    try:
        cursor = conexao.cursor()
        print("A criar tabelas...")

        # Executamos cada comando SQL separadamente.
        # O split(";") divide o texto em comandos individuais
        # (o SQLite não aceita múltiplos comandos de uma vez).
        for comando in SQL_CRIAR_TABELAS.strip().split(";"):
            comando = comando.strip()
            if comando:  # Ignora linhas vazias
                cursor.execute(comando)

        conexao.commit()  # Guarda as alterações no ficheiro
        print("Tabelas criadas com sucesso.")

        _inserir_receitas_exemplo(conexao)

    finally:
        # O bloco finally garante que a conexão é sempre fechada,
        # mesmo que ocorra um erro a meio da função.
        fechar_conexao(conexao)


def _inserir_receitas_exemplo(conexao: sqlite3.Connection) -> None:
    """
    Insere as 20 receitas de exemplo se a tabela 'receitas' estiver vazia.

    O prefixo _ (underscore) indica que esta é uma função "interna" —
    só deve ser chamada dentro deste ficheiro, não por outros módulos.

    Como funciona a inserção:
      1. Insere os dados da receita na tabela 'receitas'
      2. Obtém o ID gerado automaticamente pelo SQLite (cursor.lastrowid)
      3. Insere cada ingrediente na tabela 'ingredientes_receita',
         ligando-o à receita pelo ID
    """
    cursor = conexao.cursor()

    # Verifica se já existem receitas para não inserir duplicados
    cursor.execute("SELECT COUNT(*) FROM receitas")
    total_existente = cursor.fetchone()[0]  # fetchone() obtém a primeira linha do resultado

    if total_existente > 0:
        # Já foram inseridas anteriormente
        print(f"Já existem {total_existente} receitas na base de dados.")
        return

    print("A inserir 20 receitas de exemplo...")

    for receita in RECEITAS_EXEMPLO:
        # INSERT INTO insere uma nova linha na tabela.
        # Os ? são "marcadores de posição" — o SQLite substitui-os pelos valores
        # da lista seguinte, protegendo contra SQL injection.
        cursor.execute(
            """
            INSERT INTO receitas
                (titulo, descricao, categoria, dificuldade,
                 tempo_preparo, tempo_cozedura, porcoes, instrucoes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                receita["titulo"], receita["descricao"], receita["categoria"],
                receita["dificuldade"], receita["tempo_preparo"],
                receita["tempo_cozedura"], receita["porcoes"], receita["instrucoes"],
            ),
        )

        # cursor.lastrowid → devolve o ID que o SQLite atribuiu à linha
        # que acabámos de inserir. Usamos este ID para associar os ingredientes.
        id_receita = cursor.lastrowid

        # Insere cada ingrediente desta receita
        for ingrediente in receita["ingredientes"]:
            # ingrediente é um tuple: (nome, quantidade, unidade, opcional)
            cursor.execute(
                """
                INSERT INTO ingredientes_receita
                    (id_receita, nome_ingrediente, quantidade, unidade, opcional)
                VALUES (?, ?, ?, ?, ?)
                """,
                (id_receita, ingrediente[0], ingrediente[1], ingrediente[2], ingrediente[3]),
            )

    # commit() guarda TODAS as inserções no ficheiro de uma vez.
    # É mais eficiente do que fazer commit após cada inserção.
    conexao.commit()
    print(f"{len(RECEITAS_EXEMPLO)} receitas inseridas com sucesso!")
