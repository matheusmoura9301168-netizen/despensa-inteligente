"""
╔══════════════════════════════════════════════════════════════════════╗
║                       servicos.py                                    ║
║                                                                      ║
║  Este ficheiro contém a "inteligência" da aplicação —               ║
║  as regras de negócio que definem o que o programa faz.             ║
║                                                                      ║
║  GLOSSÁRIO DE TERMOS TÉCNICOS USADOS NESTE FICHEIRO:                 ║
║    - CRUD: Acrónimo de Create (Criar), Read (Ler), Update             ║
║            (Atualizar) e Delete (Apagar). São as quatro operações    ║
║            fundamentais para gerir dados.                            ║
║    - SQL: Structured Query Language (Linguagem de Consulta            ║
║           Estruturada). É a linguagem que usamos para pedir dados ou  ║
║           dar ordens à base de dados.                                ║
║    - commit: Operação que guarda/confirma de forma definitiva as     ║
║              alterações feitas na base de dados (como guardar).       ║
║    - SQLite: O sistema de base de dados leve que guarda tudo num     ║
║              único ficheiro físico no disco rígido.                  ║
║                                                                      ║
║  Está dividido em 2 secções:                                         ║
║                                                                      ║
║  SECÇÃO 1 — GESTÃO DA DESPENSA                                       ║
║    Funções para adicionar, editar, remover e pesquisar              ║
║    ingredientes na despensa do utilizador.                          ║
║                                                                      ║
║  SECÇÃO 2 — SUGESTÃO DE RECEITAS                                     ║
║    Algoritmo que compara os ingredientes da despensa com            ║
║    as receitas disponíveis e calcula a % de compatibilidade.        ║
║                                                                      ║
║  Este ficheiro NÃO sabe nada de botões ou janelas (isso é telas.py) ║
║  e NÃO sabe nada de SQL puro (isso é BD.py).              ║
║  Serve de intermediário entre os dois.                              ║
╚══════════════════════════════════════════════════════════════════════╝
"""

# ── Importações ─────────────────────────────────────────────────────────────
#
# unicodedata → biblioteca para normalizar texto.
#   Usada para remover acentos: "café" → "cafe", "açúcar" → "acucar".
#   Isto permite comparar "bacalhau" com "Bacalhau" ou "bacalhãu" sem problemas.
#
# List, Optional → anotações de tipo:
#   List[X]     = lista de elementos do tipo X
#   Optional[X] = pode ser X ou None (ausência de valor)
#
# banco_dados → o nosso ficheiro BD.py.
#   Importamos os modelos e as funções de conexão.

import unicodedata
from typing import List, Optional
from BD import (
    ItemDespensa, IngredienteReceita, Receita, SugestaoReceita,
    obter_conexao, fechar_conexao,
)


# ══════════════════════════════════════════════════════════════════════════════
# SECÇÃO 1 — GESTÃO DA DESPENSA
#
# Estas funções realizam operações CRUD na tabela 'despensa':
#   C → Create (Criar)      (adicionar_ingrediente)
#   R → Read (Ler/Pesquisar)(obter_todos_ingredientes, pesquisar_ingredientes)
#   U → Update (Atualizar)  (atualizar_ingrediente)
#   D → Delete (Apagar)     (remover_ingrediente)
#   * CRUD é um termo técnico para as 4 operações básicas usadas para gerir informações numa base de dados.
#
# Todas as funções seguem o mesmo padrão:
#   1. Abre a conexão com a BD (obter_conexao)
#   2. Executa o SQL necessário
#      * SQL (Structured Query Language) é a linguagem padrão que usamos para dar ordens a bases de dados (como selecionar ou inserir).
#   3. Fecha a conexão (fechar_conexao) — acontece sempre no bloco "finally"
#
# O bloco try/finally garante que a conexão é fechada mesmo se houver erros.
# ══════════════════════════════════════════════════════════════════════════════


def obter_todos_ingredientes() -> List[ItemDespensa]:
    """
    Devolve uma lista com TODOS os ingredientes da despensa, ordenados por nome.

    "COLLATE NOCASE" no ORDER BY garante que a ordenação ignora maiúsculas:
    "Azeite" e "azeite" são tratados como iguais na ordenação.

    Devolve: lista de ItemDespensa (pode ser lista vazia se a despensa estiver vazia)
    """
    conexao = obter_conexao()
    try:
        cursor = conexao.cursor()

        # SELECT → lê dados da tabela. O * poderia ser usado para "todos os campos",
        # mas preferimos listar explicitamente para clareza e segurança.
        cursor.execute(
            "SELECT id, nome, quantidade, unidade, criado_em, atualizado_em "
            "FROM despensa ORDER BY nome COLLATE NOCASE"
        )

        linhas = cursor.fetchall()  # fetchall() obtém TODAS as linhas do resultado

        # Convertemos cada linha (tuple) num objeto ItemDespensa.
        # r[0] = primeiro campo (id), r[1] = segundo (nome), etc.
        return [
            ItemDespensa(
                id=r[0], nome=r[1],
                quantidade=float(r[2]),  # float() garante que é número decimal
                unidade=r[3], criado_em=r[4], atualizado_em=r[5]
            )
            for r in linhas  # "for r in linhas" → percorre cada linha do resultado
        ]
    finally:
        fechar_conexao(conexao)


def pesquisar_ingredientes(consulta: str) -> List[ItemDespensa]:
    """
    Pesquisa ingredientes cujo nome contenha o texto indicado.

    O operador LIKE com % permite pesquisa parcial:
      LIKE '%ov%' → encontra "ovos", "chouriço com ovo", etc.

    COLLATE NOCASE → ignora maiúsculas/minúsculas na pesquisa.
    f"%{consulta}%" → coloca o % antes e depois do texto procurado.

    Parâmetros:
        consulta → texto a pesquisar (pode ser parcial, ex: "ov" para "ovos")
    """
    conexao = obter_conexao()
    try:
        cursor = conexao.cursor()
        cursor.execute(
            "SELECT id, nome, quantidade, unidade, criado_em, atualizado_em "
            "FROM despensa "
            "WHERE nome LIKE ? COLLATE NOCASE "  # ? será substituído pelo valor abaixo
            "ORDER BY nome COLLATE NOCASE",
            (f"%{consulta}%",),  # O , no final é necessário para criar um tuple
        )
        linhas = cursor.fetchall()
        return [
            ItemDespensa(id=r[0], nome=r[1], quantidade=float(r[2]),
                         unidade=r[3], criado_em=r[4], atualizado_em=r[5])
            for r in linhas
        ]
    finally:
        fechar_conexao(conexao)


def adicionar_ingrediente(nome: str, quantidade: float, unidade: str) -> ItemDespensa:
    """
    Insere um novo ingrediente na despensa e devolve o objeto criado.

    O SQLite atribui automaticamente um ID à nova linha.
    Obtemos esse ID com cursor.lastrowid para criar o objeto ItemDespensa.

    Parâmetros:
        nome      → nome do ingrediente (o .strip() remove espaços no início/fim)
        quantidade → quantidade disponível (ex: 500.0)
        unidade   → unidade de medida (ex: "g", "kg")

    Devolve: o ItemDespensa recém-criado, com o ID atribuído pelo SQLite
    """
    conexao = obter_conexao()
    try:
        cursor = conexao.cursor()

        # INSERT INTO insere uma nova linha na tabela 'despensa'
        cursor.execute(
            "INSERT INTO despensa (nome, quantidade, unidade) VALUES (?, ?, ?)",
            (nome.strip(), quantidade, unidade),
        )

        # commit() é obrigatório para guardar a inserção no ficheiro.
        # * commit: confirma e grava permanentemente as alterações na base de dados (como carregar em "Guardar" num documento).
        conexao.commit()

        # cursor.lastrowid → o ID que o SQLite atribuiu à linha que acabámos de inserir
        # Nota: na versão PostgreSQL, usávamos "RETURNING id" no SQL.
        #       No SQLite, usamos cursor.lastrowid — é equivalente mas diferente na sintaxe.
        id_novo = cursor.lastrowid

        return ItemDespensa(id=id_novo, nome=nome.strip(), quantidade=quantidade, unidade=unidade)
    finally:
        fechar_conexao(conexao)


def atualizar_ingrediente(id_item: int, nome: str, quantidade: float, unidade: str) -> Optional[ItemDespensa]:
    """
    Actualiza os dados de um ingrediente existente na despensa.

    UPDATE modifica uma linha existente. O WHERE id=? garante que só
    modificamos O ingrediente com aquele ID específico.

    cursor.rowcount → número de linhas afectadas pelo UPDATE.
    Se for 0, significa que não existe nenhum ingrediente com aquele ID.

    Parâmetros:
        id_item   → ID do ingrediente a modificar
        nome, quantidade, unidade → novos valores

    Devolve:
        ItemDespensa actualizado, ou None se o ID não existir
    """
    conexao = obter_conexao()
    try:
        cursor = conexao.cursor()
        cursor.execute(
            "UPDATE despensa "
            "SET nome=?, quantidade=?, unidade=?, atualizado_em=CURRENT_TIMESTAMP "
            "WHERE id=?",
            (nome.strip(), quantidade, unidade, id_item),
        )
        # commit() confirma e grava definitivamente a edição deste ingrediente.
        conexao.commit()

        if cursor.rowcount == 0:
            # Nenhuma linha foi modificada → o ID não existe
            return None

        return ItemDespensa(id=id_item, nome=nome.strip(), quantidade=quantidade, unidade=unidade)
    finally:
        fechar_conexao(conexao)


def remover_ingrediente(id_item: int) -> bool:
    """
    Remove um ingrediente da despensa.

    DELETE FROM remove a linha com o ID especificado.

    Devolve:
        True  → ingrediente removido com sucesso
        False → ID não encontrado (nenhuma linha foi apagada)
    """
    conexao = obter_conexao()
    try:
        cursor = conexao.cursor()
        cursor.execute("DELETE FROM despensa WHERE id=?", (id_item,))
        # commit() confirma e grava definitivamente a eliminação deste ingrediente.
        conexao.commit()
        return cursor.rowcount > 0  # True se pelo menos 1 linha foi apagada
    finally:
        fechar_conexao(conexao)


def ingrediente_existe(nome: str, excluir_id: Optional[int] = None) -> bool:
    """
    Verifica se já existe um ingrediente com este nome na despensa.

    Usado para evitar duplicados antes de adicionar ou editar.

    O parâmetro excluir_id serve para edição:
    Quando editamos "Ovos", queremos verificar duplicados mas excluir
    o próprio "Ovos" da verificação (senão nunca conseguiríamos guardar
    com o mesmo nome).

    Parâmetros:
        nome       → nome a verificar
        excluir_id → ID a ignorar na verificação (para edição)

    Devolve:
        True  → já existe (não podemos adicionar)
        False → não existe (podemos adicionar)
    """
    conexao = obter_conexao()
    try:
        cursor = conexao.cursor()
        if excluir_id:
            # Verificação para edição: ignora o próprio ingrediente
            cursor.execute(
                "SELECT 1 FROM despensa WHERE nome=? COLLATE NOCASE AND id != ?",
                (nome, excluir_id),
            )
        else:
            # Verificação simples para adição nova
            cursor.execute(
                "SELECT 1 FROM despensa WHERE nome=? COLLATE NOCASE",
                (nome,),
            )
        # fetchone() devolve a primeira linha ou None se não houver resultados
        return cursor.fetchone() is not None
    finally:
        fechar_conexao(conexao)


# ══════════════════════════════════════════════════════════════════════════════
# SECÇÃO 2 — SUGESTÃO DE RECEITAS
#
# Esta secção contém o algoritmo central da aplicação:
# comparar o que o utilizador TEM com o que as receitas PRECISAM.
#
# O algoritmo tem 3 etapas:
#   1. Normalizar os nomes (remover acentos, converter para minúsculas)
#   2. Verificar se cada ingrediente da receita está na despensa
#   3. Calcular a percentagem de compatibilidade
# ══════════════════════════════════════════════════════════════════════════════


def _normalizar(texto: str) -> str:
    """
    Converte texto para minúsculas e remove acentos.

    Exemplos:
        "Bacalhau" → "bacalhau"
        "açúcar"   → "acucar"
        "Couve-galega" → "couve-galega"

    Como funciona:
      1. unicodedata.normalize("NFKD", ...) → separa cada letra dos seus acentos
         Ex: "é" é separado em "e" + acento
      2. unicodedata.combining(c) → devolve True para os acentos isolados
      3. O join filtra tudo o que for acento, mantendo só as letras base

    O prefixo _ indica que é função interna — não deve ser usada fora deste ficheiro.
    """
    texto_decomposto = unicodedata.normalize("NFKD", texto.lower().strip())
    return "".join(
        caracter for caracter in texto_decomposto
        if not unicodedata.combining(caracter)  # Mantém só caracteres normais (sem acentos)
    )


def _ingrediente_corresponde(nome_despensa: str, nome_receita: str) -> bool:
    """
    Verifica se um ingrediente da despensa "cobre" um ingrediente de uma receita.

    Este algoritmo é tolerante a variações de nome para ser mais útil ao utilizador:
    "frango" deve corresponder a "peito de frango" ou "frango inteiro".

    Estratégias usadas (por ordem de verificação):
      1. Igualdade exacta → "sal" == "sal"
      2. Palavras em comum (sem stopwords) → "couve galega" e "couve-galega têm "couve"
      3. Uma está contida na outra → "ovo" está em "ovos mexidos"

    Parâmetros:
        nome_despensa → nome do ingrediente que o utilizador TEM
        nome_receita  → nome do ingrediente que a receita PRECISA

    Devolve:
        True  → o ingrediente da despensa cobre o ingrediente da receita
        False → não correspondem
    """
    # Normaliza os dois nomes para comparação justa (sem acentos, minúsculas)
    d = _normalizar(nome_despensa)
    r = _normalizar(nome_receita)

    # Estratégia 1: igualdade exacta (o caso mais simples)
    if d == r:
        return True

    # "Palavras de paragem" — palavras pouco informativas que não devem
    # ser usadas sozinhas para determinar correspondência
    palavras_sem_significado = {"de", "do", "da", "em", "com", "a", "o", "e", "um", "uma"}

    # Divide cada nome em palavras e remove as palavras sem significado
    palavras_despensa = set(d.split()) - palavras_sem_significado
    palavras_receita = set(r.split()) - palavras_sem_significado

    if not palavras_despensa or not palavras_receita:
        # Se não sobrar nenhuma palavra, tenta correspondência por substring
        return d in r or r in d

    # Estratégia 2: palavras em comum
    palavras_comuns = palavras_despensa & palavras_receita  # & = interseção de conjuntos

    if palavras_comuns:
        # Só conta como correspondência se as palavras comuns tiverem 4+ letras
        # (evita correspondências falsas com palavras curtas como "ao", "de")
        palavras_significativas = [p for p in palavras_comuns if len(p) >= 4]
        if palavras_significativas:
            return True
        # Se todas as palavras da despensa estiverem na receita, é correspondência
        if all(p in palavras_receita for p in palavras_despensa):
            return True

    # Estratégia 3: uma está contida na outra
    # Ex: "ovo" está em "ovos", "tomate" está em "molho de tomate"
    return d in r or r in d


def _carregar_todas_receitas() -> List[Receita]:
    """
    Carrega todas as receitas da base de dados, incluindo os seus ingredientes.

    Esta função executa 2 queries (consultas):
      1. Busca todas as receitas da tabela 'receitas'
      2. Busca todos os ingredientes da tabela 'ingredientes_receita'

    Depois associa os ingredientes às receitas correspondentes pelo id_receita.

    Usamos um dicionário {id: Receita} para encontrar rapidamente
    a receita certa ao associar cada ingrediente.

    É mais eficiente que fazer uma query por receita (seria N queries para N receitas).

    Devolve: lista de Receita com os ingredientes já incluídos
    """
    conexao = obter_conexao()
    try:
        cursor = conexao.cursor()

        # ── Query 1: Buscar todas as receitas ────────────────────────────
        cursor.execute(
            "SELECT id, titulo, descricao, categoria, dificuldade, "
            "tempo_preparo, tempo_cozedura, porcoes, instrucoes "
            "FROM receitas ORDER BY titulo COLLATE NOCASE"
        )
        linhas_receitas = cursor.fetchall()

        # Criamos um dicionário: {id_receita: objeto_Receita}
        # Isto permite encontrar uma receita pelo ID em tempo O(1)
        receitas: dict[int, Receita] = {}
        for r in linhas_receitas:
            receitas[r[0]] = Receita(
                id=r[0], titulo=r[1],
                descricao=r[2] or "",      # or "" → usa string vazia se for None
                categoria=r[3] or "",
                dificuldade=r[4] or "Médio",
                tempo_preparo=r[5] or 0,
                tempo_cozedura=r[6] or 0,
                porcoes=r[7] or 4,
                instrucoes=r[8] or "",
            )

        # ── Query 2: Buscar todos os ingredientes de todas as receitas ───
        # É mais eficiente uma única query do que uma por receita
        cursor.execute(
            "SELECT id, id_receita, nome_ingrediente, quantidade, unidade, opcional "
            "FROM ingredientes_receita ORDER BY id_receita, id"
        )
        linhas_ingredientes = cursor.fetchall()

        # Associa cada ingrediente à sua receita
        for linha in linhas_ingredientes:
            ingrediente = IngredienteReceita(
                id=linha[0],
                id_receita=linha[1],
                nome_ingrediente=linha[2],
                quantidade=float(linha[3]) if linha[3] is not None else None,
                unidade=linha[4],
                # SQLite guarda booleans como 0 ou 1 (INTEGER).
                # bool() converte: bool(0) = False, bool(1) = True
                opcional=bool(linha[5]),
            )
            # Se a receita existir no dicionário, adiciona o ingrediente à sua lista
            if ingrediente.id_receita in receitas:
                receitas[ingrediente.id_receita].ingredientes.append(ingrediente)

        # Converte o dicionário numa lista e devolve
        return list(receitas.values())

    finally:
        fechar_conexao(conexao)


def obter_sugestoes(
    despensa: List[ItemDespensa],
    apenas_completas: bool = False,
    categoria: Optional[str] = None,
    dificuldade: Optional[str] = None,
    tempo_maximo: Optional[int] = None,
    pesquisa: Optional[str] = None,
) -> List[SugestaoReceita]:
    """
    Algoritmo principal de sugestão de receitas.

    Compara cada receita com os ingredientes disponíveis na despensa
    e calcula a percentagem de compatibilidade.

    Como funciona:
      Para cada receita:
        - Aplica filtros adicionais (nome/pesquisa, categoria, dificuldade, tempo máximo)
        - Conta quantos ingredientes OBRIGATÓRIOS estão disponíveis
        - Calcula percentagem: (disponíveis / total obrigatórios) × 100
        - Cria um SugestaoReceita com esta informação

      Ordena os resultados: 100% primeiro, depois por ordem decrescente

    Parâmetros:
        despensa        → lista de ItemDespensa (o que o utilizador tem)
        apenas_completas → se True, só mostra receitas com 100% de compatibilidade
        categoria       → filtro por categoria (ex: "Sopa", "Sobremesa") ou None/Todas
        dificuldade     → filtro por dificuldade (ex: "Fácil", "Médio", "Difícil") ou None
        tempo_maximo    → tempo total máximo em minutos (ex: 30) ou None
        pesquisa        → texto de pesquisa inserido pelo utilizador (ex: "bolo") ou None

    Devolve: lista de SugestaoReceita ordenada por compatibilidade (maior primeiro)
    """
    # Carrega todas as receitas com os seus ingredientes da base de dados
    todas_receitas = _carregar_todas_receitas()

    # Lista com os nomes dos ingredientes da despensa (para comparação rápida)
    nomes_despensa = [item.nome for item in despensa]

    sugestoes: List[SugestaoReceita] = []

    for receita in todas_receitas:
        # ── FILTRO 1: Pesquisa por Texto (Título ou Descrição) ─────────────────
        # Se foi escrito algum texto para pesquisar:
        if pesquisa:
            # Normalizamos o termo pesquisado (retira acentos e passa para minúsculas)
            termo = _normalizar(pesquisa)
            # Normalizamos o título e a descrição da receita para comparar de forma justa
            titulo_norm = _normalizar(receita.titulo)
            desc_norm = _normalizar(receita.descricao)

            # Se o termo pesquisado NÃO estiver no título E nem na descrição,
            # saltamos esta receita e passamos à próxima da lista
            if termo not in titulo_norm and termo not in desc_norm:
                continue

        # ── FILTRO 2: Categoria da Receita ─────────────────────────────────────
        # Se o utilizador selecionou uma categoria específica (diferente de "Todas"):
        if categoria and categoria != "Todas" and categoria != "📊  Todas as Receitas":
            # Comparamos a categoria da receita com a selecionada (tudo em minúsculas)
            if receita.categoria.lower() != categoria.lower():
                # Se for diferente, saltamos esta receita
                continue

        # ── FILTRO 3: Dificuldade de Preparação ───────────────────────────────
        # Se o utilizador escolheu um nível de dificuldade específico (diferente de "Todas"):
        if dificuldade and dificuldade != "Todas":
            # Comparamos a dificuldade da receita com a pretendida
            if receita.dificuldade.lower() != dificuldade.lower():
                # Se não corresponder, saltamos esta receita
                continue

        # ── FILTRO 4: Tempo Máximo de Execução ────────────────────────────────
        # Se foi definido um limite de tempo máximo (em minutos):
        if tempo_maximo is not None and tempo_maximo > 0:
            # Comparamos o tempo total da receita (preparo + cozedura) com o limite
            if receita.tempo_total > tempo_maximo:
                # Se demorar mais do que o limite definido, saltamos esta receita
                continue

        # Só consideramos os ingredientes OBRIGATÓRIOS para calcular a %
        # (os opcionais não penalizam a receita se faltarem)
        ingredientes_obrigatorios = receita.ingredientes_obrigatorios

        if not ingredientes_obrigatorios:
            # Receita sem ingredientes obrigatórios — ignoramos
            continue

        # Listas para acumular o que está disponível e o que falta
        disponiveis = []
        em_falta = []

        for ingrediente_receita in ingredientes_obrigatorios:
            # Verifica se algum ingrediente da despensa corresponde a este
            encontrado = any(
                _ingrediente_corresponde(nome_desp, ingrediente_receita.nome_ingrediente)
                for nome_desp in nomes_despensa
            )

            if encontrado:
                disponiveis.append(ingrediente_receita.nome_ingrediente)
            else:
                em_falta.append(ingrediente_receita.nome_ingrediente)

        # Calcula a percentagem: disponíveis / total × 100
        percentagem = (len(disponiveis) / len(ingredientes_obrigatorios)) * 100

        # Se o filtro "apenas completas" estiver activo, ignora receitas incompletas
        if apenas_completas and percentagem < 100:
            continue

        sugestoes.append(SugestaoReceita(
            receita=receita,
            percentagem_compatibilidade=round(percentagem, 1),  # Arredonda a 1 decimal
            ingredientes_disponiveis=disponiveis,
            ingredientes_em_falta=em_falta,
        ))

    # Ordena: primeiro por percentagem decrescente (-percentagem),
    # depois por título alfabético (para empates)
    sugestoes.sort(key=lambda s: (-s.percentagem_compatibilidade, s.receita.titulo))

    return sugestoes
