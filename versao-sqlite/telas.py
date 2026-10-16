"""
╔══════════════════════════════════════════════════════════════════════╗
║                         telas.py                                     ║
║                                                                      ║
║  Este ficheiro contém TODA a interface gráfica da aplicação.         ║
║  Usa a biblioteca CustomTkinter (é uma versão melhorada do Tkinter). ║
║                                                                      ║
║  GLOSSÁRIO DE TERMOS TÉCNICOS USADOS NESTE FICHEIRO:                 ║
║    - __init__: O "construtor" de uma classe. É a função inicial que  ║
║                prepara o ecrã ou painel quando este é criado.        ║
║    - trace_add: Uma escuta/monitorizador que avisa o programa        ║
║                 imediatamente quando o utilizador escreve algo numa  ║
║                 caixa de texto (como na barra de pesquisa).          ║
║    - pack: Organizador de ecrã que empilha elementos uns por cima    ║
║            dos outros ou lado a lado de forma automática.            ║
║    - grid: Organizador de ecrã que alinha elementos numa tabela      ║
║            invisível com linhas (rows) e colunas (columns).          ║
║    - lambda: Uma forma rápida e curta de criar funções temporárias   ║
║              na mesma linha, muito usada em cliques de botões.       ║
║                                                                      ║
║  Contém 5 classes (componentes visuais):                             ║
║                                                                      ║
║  1. JanelaPrincipal   → a janela mãe com sidebar de navegação        ║
║  2. AbaDespensa       → lista de ingredientes + botão adicionar      ║
║  3. DialogoIngrediente → formulário para adicionar/editar            ║
║  4. AbaReceitas       → cards de sugestão com % de compatibilidade   ║
║  5. JanelaDetalheReceita → modal com ingredientes + modo de preparo  ║
╚══════════════════════════════════════════════════════════════════════╝
"""

# ── Importações ─────────────────────────────────────────────────────────────
#
# customtkinter → a biblioteca da interface gráfica
# tkinter.messagebox → para mostrar caixas de diálogo (erros, confirmações)
# typing → para anotações de tipo (List, Callable, Optional)
#
# banco_dados → os modelos de dados (ItemDespensa, SugestaoReceita)
# servicos    → as funções de negócio (adicionar, remover, obter sugestões, etc.)

import customtkinter as ctk
from tkinter import messagebox
from typing import List, Callable, Optional

from BD import ItemDespensa, SugestaoReceita
from servicos import (
    obter_todos_ingredientes, pesquisar_ingredientes,
    adicionar_ingrediente, atualizar_ingrediente,
    remover_ingrediente, ingrediente_existe, obter_sugestoes,
)

# ── Configuração global do tema ──────────────────────────────────────────────
# set_appearance_mode("dark") → tema escuro em toda a aplicação
# set_default_color_theme("blue") → cor base dos componentes interativos
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ── Paleta de cores ──────────────────────────────────────────────────────────
# Definimos todas as cores aqui para poder reutilizá-las em toda a UI.
# Os valores são códigos hexadecimais: #RRGGBB (vermelho, verde, azul)
# Exemplo: #0f172a = R:15, G:23, B:42 → azul muito escuro (navy)

COR_FUNDO         = "#0f172a"   # Fundo principal: navy escuro
COR_BARRA_LATERAL = "#0a0f1e"   # Sidebar: ainda mais escuro que o fundo
COR_SUPERFICIE    = "#1e293b"   # Superfície de cards e cabeçalhos
COR_SUPERFICIE2   = "#273549"   # Superfície ligeiramente mais clara (alternância)
COR_DESTAQUE      = "#6366f1"   # Indigo/roxo — cor principal de botões e ícones
COR_SUCESSO       = "#10b981"   # Verde esmeralda — para confirmações e 100%
COR_PERIGO        = "#f43f5e"   # Vermelho rosado — para apagar e erros
COR_TEXTO         = "#f1f5f9"   # Texto principal: branco suave
COR_TEXTO_MUDO    = "#94a3b8"   # Texto secundário: cinza azulado
COR_BORDA         = "#334155"   # Cor das bordas e divisores

# ── Lista de unidades disponíveis no formulário ───────────────────────────────
# Esta lista aparece no dropdown ao adicionar/editar ingredientes.
UNIDADES = [
    "g", "kg", "ml", "l",
    "unidades", "colheres de sopa", "colheres de chá",
    "xícaras", "dentes", "fatias", "ramo", "folhas",
    "pitada", "pacote",
]


# ─────────────────────────────────────────────────────────────────────────────────────────────
# CLASSE 1 — JANELA PRINCIPAL
#
# É a janela "mãe" que contém tudo.
# Tem uma barra lateral (sidebar) com os botões de navegação,
# e uma área de conteúdo que muda consoante o separador selecionado.
# ─────────────────────────────────────────────────────────────────────────────────────────────

class JanelaPrincipal:
    """
    Janela principal da aplicação.

    Usa o padrão de "sidebar + conteúdo":
      - À esquerda: barra lateral com logo e botões de navegação
      - À direita: área de conteúdo que mostra AbaDespensa ou AbaReceitas
    """

    def __init__(self):
        """
        Construtor da classe. É executado automaticamente toda vez que
        um novo objeto JanelaPrincipal é criado (ex: JanelaPrincipal()).

        O parâmetro 'self' é a referência à própria instância que está
        sendo criada. Ele permite acessar e definir atributos e métodos
        deste objeto (é como o 'eu' da classe).
        """
        # ctk.CTk() → cria a janela principal (equivalente ao Tk() do Tkinter base)
        self.janela = ctk.CTk()

        # Controla qual separador está ativo: "despensa" ou "receitas"
        self._separador_ativo = "despensa"

        self._configurar_janela()
        self._construir_layout()

    def _configurar_janela(self):
        """
        Define as propriedades básicas da janela (título, tamanho, cor).
        O prefixo _ indica que é um método interno (não deve ser chamado fora da classe).
        """
        self.janela.title("Despensa Inteligente")
        self.janela.geometry("1100x720")    # largura x altura em píxeis
        self.janela.minsize(900, 600)        # tamanho mínimo (não pode encolher mais)
        self.janela.configure(fg_color=COR_FUNDO)
        self._centrar_janela()

    def _centrar_janela(self):
        """
        Coloca a janela no centro do ecrã.
        Calcula a posição x, y com base no tamanho do ecrã e da janela.
        """
        self.janela.update_idletasks()  # Força o Tkinter a calcular os tamanhos actuais
        largura, altura = 1100, 720
        largura_ecra = self.janela.winfo_screenwidth()
        altura_ecra = self.janela.winfo_screenheight()
        # Geometria no formato "LARGURAxALTURA+X+Y"
        self.janela.geometry(
            f"{largura}x{altura}+{(largura_ecra - largura) // 2}+{(altura_ecra - altura) // 2}"
        )

    def _construir_layout(self):
        """
        Constrói a estrutura principal: sidebar à esquerda + conteúdo à direita.

        O layout é feito com pack() — um gestor de geometria do Tkinter
        que coloca widgets lado a lado ou em cima uns dos outros.

        side="left" → coloca à esquerda
        fill="y"    → estica verticalmente para preencher a altura toda
        fill="both" expand=True → preenche todo o espaço disponível
        """
        # Frame exterior que contém tudo
        frame_principal = ctk.CTkFrame(self.janela, fg_color=COR_FUNDO, corner_radius=0)
        frame_principal.pack(fill="both", expand=True)

        # ── Barra lateral (sidebar) ───────────────────────────────────────
        # width=240 → largura fixa de 240 píxeis
        # pack_propagate(False) → impede que o conteúdo altere a largura definida
        self._barra_lateral = ctk.CTkFrame(
            frame_principal, fg_color=COR_BARRA_LATERAL, corner_radius=0, width=240
        )
        self._barra_lateral.pack(side="left", fill="y")
        self._barra_lateral.pack_propagate(False)
        self._construir_barra_lateral()

        # Linha divisória entre sidebar e conteúdo (1 pixel de largura)
        ctk.CTkFrame(
            frame_principal, fg_color=COR_BORDA, width=1, corner_radius=0
        ).pack(side="left", fill="y")

        # ── Área de conteúdo ─────────────────────────────────────────────
        self._area_conteudo = ctk.CTkFrame(frame_principal, fg_color=COR_FUNDO, corner_radius=0)
        self._area_conteudo.pack(side="left", fill="both", expand=True)

        # Cria os dois separadores (abas)
        # Passamos funções como argumentos:
        #   on_change=self._ao_mudar_despensa → chama este método quando a despensa muda
        #   obter_itens_despensa=self._obter_itens → fornece os ingredientes à aba de receitas
        self._aba_despensa = AbaDespensa(
            self._area_conteudo,
            ao_mudar=self._ao_mudar_despensa
        )
        self._aba_receitas = AbaReceitas(
            self._area_conteudo,
            obter_itens_despensa=self._obter_itens_despensa
        )

        # Mostra o separador inicial
        self._mostrar_separador("despensa")

    def _construir_barra_lateral(self):
        """Constrói o conteúdo da barra lateral: logo, navegação e info."""

        # ── Logo / Cabeçalho ─────────────────────────────────────────────
        frame_logo = ctk.CTkFrame(self._barra_lateral, fg_color="transparent", height=120)
        frame_logo.pack(fill="x")
        frame_logo.pack_propagate(False)

        ctk.CTkLabel(
            frame_logo, text="🍽️",
            font=ctk.CTkFont(size=44), text_color=COR_DESTAQUE
        ).pack(pady=(24, 0))
        ctk.CTkLabel(
            frame_logo, text="Despensa",
            font=ctk.CTkFont(size=16, weight="bold"), text_color=COR_TEXTO
        ).pack()
        ctk.CTkLabel(
            frame_logo, text="Inteligente",
            font=ctk.CTkFont(size=16, weight="bold"), text_color=COR_DESTAQUE
        ).pack()

        # Linha separadora
        ctk.CTkFrame(self._barra_lateral, fg_color=COR_BORDA, height=1).pack(
            fill="x", padx=20, pady=16
        )

        # ── Título da secção de navegação ────────────────────────────────
        ctk.CTkLabel(
            self._barra_lateral, text="NAVEGAÇÃO",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=COR_TEXTO_MUDO, anchor="w"
        ).pack(fill="x", padx=20, pady=(0, 8))

        # ── Botões de navegação ──────────────────────────────────────────
        # Guardamos referência aos botões para poder mudar a cor quando selecionados
        self._btn_despensa = self._criar_botao_nav("Minha Despensa", "despensa")
        self._btn_receitas = self._criar_botao_nav("Receitas", "receitas")

        # Espaço flexível que empurra a info para baixo
        ctk.CTkFrame(self._barra_lateral, fg_color="transparent").pack(fill="both", expand=True)

        # ── Informação no rodapé ─────────────────────────────────────────
        ctk.CTkFrame(self._barra_lateral, fg_color=COR_BORDA, height=1).pack(
            fill="x", padx=20, pady=8
        )
        frame_info = ctk.CTkFrame(self._barra_lateral, fg_color="transparent", height=70)
        frame_info.pack(fill="x", pady=8)
        frame_info.pack_propagate(False)

        ctk.CTkLabel(
            frame_info, text="🟢  Pronto",
            font=ctk.CTkFont(size=11), text_color=COR_SUCESSO
        ).pack(pady=(2, 8))

    def _criar_botao_nav(self, texto: str, nome_separador: str) -> ctk.CTkButton:
        """
        Cria e retorna um botão de navegação na sidebar.

        command=lambda t=nome_separador: self._mostrar_separador(t)
          → lambda cria uma função anónima que chama _mostrar_separador
          → o t=nome_separador "captura" o valor actual da variável
            (sem isto, todos os botões usariam o último valor do loop)
        """
        botao = ctk.CTkButton(
            self._barra_lateral, text=texto,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="transparent", hover_color=COR_SUPERFICIE,
            text_color=COR_TEXTO_MUDO, anchor="w",
            corner_radius=10, height=44,
            command=lambda t=nome_separador: self._mostrar_separador(t),
        )
        botao.pack(fill="x", padx=12, pady=2)
        return botao

    def _mostrar_separador(self, nome: str):
        """
        Muda o conteúdo visível para o separador indicado.

        pack_forget() → esconde um widget sem o destruir
        pack()        → mostra o widget novamente

        Também actualiza as cores dos botões de navegação.
        """
        self._separador_ativo = nome

        # Esconde ambas as abas
        self._aba_despensa.pack_forget()
        self._aba_receitas.pack_forget()

        # Repõe a cor "inativo" em ambos os botões
        for botao in [self._btn_despensa, self._btn_receitas]:
            botao.configure(fg_color="transparent", text_color=COR_TEXTO_MUDO)

        if nome == "despensa":
            # Mostra a aba da despensa e destaca o seu botão
            self._aba_despensa.pack(fill="both", expand=True)
            self._btn_despensa.configure(fg_color=COR_SUPERFICIE, text_color=COR_DESTAQUE)
        else:
            # Mostra a aba de receitas e destaca o seu botão
            self._aba_receitas.pack(fill="both", expand=True)
            self._btn_receitas.configure(fg_color=COR_SUPERFICIE, text_color=COR_DESTAQUE)
            # after(100, ...) → espera 100ms antes de actualizar as sugestões
            # Garante que a aba está visível antes de começar a carregar dados
            self.janela.after(100, self._aba_receitas.atualizar)

    def _ao_mudar_despensa(self):
        """
        Chamada quando a despensa muda (ingrediente adicionado/editado/removido).
        Actualmente vazia, mas pode ser usada para actualizar outras partes da UI.
        """
        pass

    def _obter_itens_despensa(self) -> List[ItemDespensa]:
        """
        Devolve a lista atual de ingredientes da despensa.
        É passada como argumento à AbaReceitas para que ela possa
        obter os ingredientes sem aceder directamente ao serviço.
        """
        return self._aba_despensa.obter_itens()

    def iniciar(self):
        """
        Inicia o loop de eventos do Tkinter.
        mainloop() mantém a janela aberta e responde a cliques, teclas, etc.
        Só termina quando o utilizador fecha a janela.
        """
        self.janela.mainloop()


# ══════════════════════════════════════════════════════════════════════════════
# CLASSE 2 — ABA DA DESPENSA
#
# Mostra a lista de ingredientes com opções de pesquisa, adição,
# edição e remoção. Herda de ctk.CTkFrame (é um painel dentro da janela).
# ══════════════════════════════════════════════════════════════════════════════

class AbaDespensa(ctk.CTkFrame):
    """
    Aba que mostra e gere os ingredientes da despensa.

    Herdar de ctk.CTkFrame significa que esta classe É um painel visual.
    Pode ser colocada dentro de outra janela como qualquer outro widget.
    """

    def __init__(self, parent, ao_mudar: Optional[Callable] = None):
        """
        Inicializa a aba.

        parent    → o widget pai onde esta aba será colocada
        ao_mudar  → função a chamar quando a despensa é alterada
                    (Callable = "algo que pode ser chamado como função")
        """
        # super().__init__() → inicializa o CTkFrame base
        super().__init__(parent, fg_color=COR_FUNDO, corner_radius=0)

        self.ao_mudar = ao_mudar              # Função de callback (pode ser None)
        self._itens: List[ItemDespensa] = []  # Lista dos ingredientes actuais

        # StringVar → variável especial do Tkinter que notifica automaticamente
        # quando o seu valor muda. Usada para a barra de pesquisa.
        self._texto_pesquisa = ctk.StringVar()
        # trace_add("write", ...) → chama _ao_mudar_pesquisa sempre que o texto muda
        self._texto_pesquisa.trace_add("write", self._ao_mudar_pesquisa)

        self._construir_interface()
        self.atualizar()  # Carrega os ingredientes ao iniciar

    def _construir_interface(self):
        """Constrói todos os elementos visuais da aba."""

        # ── Cabeçalho ────────────────────────────────────────────────────
        cabecalho = ctk.CTkFrame(self, fg_color=COR_SUPERFICIE, corner_radius=0, height=80)
        cabecalho.pack(fill="x")
        cabecalho.pack_propagate(False)

        interior_cab = ctk.CTkFrame(cabecalho, fg_color="transparent")
        interior_cab.pack(fill="both", expand=True, padx=24, pady=16)

        ctk.CTkLabel(
            interior_cab, text="Minha Despensa",
            font=ctk.CTkFont(size=20, weight="bold"), text_color=COR_TEXTO, anchor="w"
        ).pack(side="left")

        # Botão "Adicionar Ingrediente" — ao clicar, abre o diálogo de adição
        ctk.CTkButton(
            interior_cab, text="＋  Adicionar Ingrediente",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COR_DESTAQUE, hover_color="#4f46e5",
            corner_radius=10, height=38,
            command=self._abrir_dialogo_adicionar
        ).pack(side="right")

        # ── Barra de pesquisa ────────────────────────────────────────────
        barra_pesquisa = ctk.CTkFrame(self, fg_color=COR_SUPERFICIE, corner_radius=0, height=56)
        barra_pesquisa.pack(fill="x")
        barra_pesquisa.pack_propagate(False)

        interior_pes = ctk.CTkFrame(barra_pesquisa, fg_color="transparent")
        interior_pes.pack(fill="both", expand=True, padx=24, pady=10)

        ctk.CTkLabel(interior_pes, text="🔍", font=ctk.CTkFont(size=16),
                     text_color=COR_TEXTO_MUDO).pack(side="left", padx=(0, 8))

        # textvariable=self._texto_pesquisa → liga o campo à StringVar
        # Qualquer texto escrito actualiza automaticamente a variável
        ctk.CTkEntry(
            interior_pes, textvariable=self._texto_pesquisa,
            placeholder_text="Pesquisar ingrediente...",
            font=ctk.CTkFont(size=13), fg_color=COR_SUPERFICIE2,
            border_color=COR_BORDA, text_color=COR_TEXTO,
            placeholder_text_color=COR_TEXTO_MUDO,
            corner_radius=8, height=36
        ).pack(side="left", fill="x", expand=True)

        # Contador de ingredientes (actualizado em _renderizar_lista)
        self._label_contador = ctk.CTkLabel(
            interior_pes, text="0 ingredientes",
            font=ctk.CTkFont(size=12), text_color=COR_TEXTO_MUDO
        )
        self._label_contador.pack(side="right", padx=(12, 0))

        # ── Lista com scroll ──────────────────────────────────────────────
        # CTkScrollableFrame → painel com barra de scroll automática
        self._frame_lista = ctk.CTkScrollableFrame(
            self, fg_color=COR_FUNDO,
            scrollbar_button_color=COR_SUPERFICIE2,
            scrollbar_button_hover_color=COR_DESTAQUE,
        )
        self._frame_lista.pack(fill="both", expand=True)

    def atualizar(self):
        """
        Recarrega a lista de ingredientes da base de dados e actualiza o ecrã.
        Chamada ao iniciar, após adicionar/editar/remover, e ao pesquisar.
        """
        consulta = self._texto_pesquisa.get().strip()

        # Se houver texto de pesquisa, usa pesquisar_ingredientes
        # Caso contrário, obtém todos os ingredientes
        if consulta:
            self._itens = pesquisar_ingredientes(consulta)
        else:
            self._itens = obter_todos_ingredientes()

        self._renderizar_lista()

        # Notifica que a despensa mudou (se houver callback definido)
        if self.ao_mudar:
            self.ao_mudar()

    def _ao_mudar_pesquisa(self, *_):
        """
        Chamada automaticamente sempre que o texto da pesquisa muda.
        O *_ aceita qualquer número de argumentos extras (que o Tkinter passa
        mas que não precisamos de usar).
        """
        self.atualizar()

    def _renderizar_lista(self):
        """
        Limpa e redesenha a lista de ingredientes no ecrã.

        winfo_children() → obtém todos os widgets filhos de um frame
        destroy() → remove um widget do ecrã
        """
        # Apaga todos os itens actuais da lista
        for widget in self._frame_lista.winfo_children():
            widget.destroy()

        # Actualiza o contador
        total = len(self._itens)
        sufixo = "s" if total != 1 else ""
        self._label_contador.configure(text=f"{total} ingrediente{sufixo}")

        if not self._itens:
            # Mostra mensagem quando a lista está vazia
            ctk.CTkLabel(
                self._frame_lista,
                text="🧺\n\nA tua despensa está vazia.\nClica em «Adicionar Ingrediente» para começar!",
                font=ctk.CTkFont(size=15), text_color=COR_TEXTO_MUDO, justify="center",
            ).pack(expand=True, pady=80)
            return

        # Desenha cada ingrediente na lista
        for indice, item in enumerate(self._itens):
            self._desenhar_linha_ingrediente(item, indice)

    def _desenhar_linha_ingrediente(self, item: ItemDespensa, indice: int):
        """
        Desenha uma linha na lista para um ingrediente.

        Alterna as cores de fundo (linhas pares/ímpares) para facilitar a leitura.
        indice % 2 → resto da divisão por 2: par=0, ímpar=1
        """
        cor_fundo = COR_SUPERFICIE if indice % 2 == 0 else COR_SUPERFICIE2
        cor_fundo_alt = COR_SUPERFICIE2 if indice % 2 == 0 else COR_SUPERFICIE

        linha = ctk.CTkFrame(self._frame_lista, fg_color=cor_fundo, corner_radius=10, height=56)
        linha.pack(fill="x", padx=20, pady=(4, 0))
        linha.pack_propagate(False)

        interior = ctk.CTkFrame(linha, fg_color="transparent")
        interior.pack(fill="both", expand=True, padx=16)

        # Ícone
        ctk.CTkLabel(interior, text="🧂", font=ctk.CTkFont(size=18),
                     text_color=COR_DESTAQUE, width=32).pack(side="left", pady=12)

        # Nome do ingrediente
        ctk.CTkLabel(
            interior, text=item.nome,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COR_TEXTO, anchor="w"
        ).pack(side="left", fill="x", expand=True, padx=(8, 0), pady=12)

        # Quantidade formatada (ex: "500 g")
        ctk.CTkLabel(
            interior, text=item.quantidade_formatada,
            font=ctk.CTkFont(size=13), text_color=COR_TEXTO_MUDO, width=120, anchor="e"
        ).pack(side="left", pady=12)

        # Botão editar — command usa lambda para "capturar" o item correto
        ctk.CTkButton(
            interior, text="✏️", width=36, height=32, corner_radius=8,
            fg_color=cor_fundo_alt, hover_color=COR_DESTAQUE, text_color=COR_TEXTO,
            font=ctk.CTkFont(size=14),
            command=lambda i=item: self._abrir_dialogo_editar(i)
        ).pack(side="left", padx=(8, 4), pady=12)

        # Botão remover
        ctk.CTkButton(
            interior, text="🗑️", width=36, height=32, corner_radius=8,
            fg_color=cor_fundo_alt, hover_color=COR_PERIGO, text_color=COR_TEXTO,
            font=ctk.CTkFont(size=14),
            command=lambda i=item: self._confirmar_remocao(i)
        ).pack(side="left", pady=12)

    def _abrir_dialogo_adicionar(self):
        """Abre o formulário para adicionar um novo ingrediente."""
        DialogoIngrediente(self, titulo="Adicionar Ingrediente", ao_guardar=self._guardar_novo)

    def _abrir_dialogo_editar(self, item: ItemDespensa):
        """Abre o formulário pré-preenchido para editar um ingrediente."""
        DialogoIngrediente(
            self, titulo="Editar Ingrediente", item=item,
            ao_guardar=lambda n, q, u: self._guardar_edicao(item.id, n, q, u)
        )

    def _guardar_novo(self, nome: str, quantidade: float, unidade: str):
        """
        Guarda um novo ingrediente após validação de duplicados.
        Chamada pelo DialogoIngrediente quando o utilizador clica "Guardar".
        """
        if ingrediente_existe(nome):
            messagebox.showwarning("Duplicado", f"'{nome}' já existe na despensa.")
            return
        adicionar_ingrediente(nome, quantidade, unidade)
        self.atualizar()

    def _guardar_edicao(self, id_item: int, nome: str, quantidade: float, unidade: str):
        """Guarda as alterações a um ingrediente existente."""
        if ingrediente_existe(nome, excluir_id=id_item):
            messagebox.showwarning("Duplicado", f"'{nome}' já existe na despensa.")
            return
        atualizar_ingrediente(id_item, nome, quantidade, unidade)
        self.atualizar()

    def _confirmar_remocao(self, item: ItemDespensa):
        """
        Mostra caixa de confirmação antes de remover um ingrediente.
        messagebox.askyesno → devolve True se o utilizador clicar "Sim"
        """
        confirmado = messagebox.askyesno(
            "Remover Ingrediente",
            f"Tens a certeza que queres remover «{item.nome}»?"
        )
        if confirmado:
            remover_ingrediente(item.id)
            self.atualizar()

    def obter_itens(self) -> List[ItemDespensa]:
        """
        Devolve a lista actualizada de ingredientes da despensa.
        Chamada pela JanelaPrincipal para fornecer dados à AbaReceitas.
        """
        return obter_todos_ingredientes()


# ══════════════════════════════════════════════════════════════════════════════
# CLASSE 3 — DIÁLOGO DE INGREDIENTE
#
# Formulário pop-up para adicionar ou editar um ingrediente.
# Herda de CTkToplevel (janela secundária/modal).
# "Modal" = bloqueia a interação com a janela principal enquanto está aberta.
# ══════════════════════════════════════════════════════════════════════════════

class DialogoIngrediente(ctk.CTkToplevel):
    """
    Janela pop-up (modal) com formulário para adicionar ou editar ingrediente.

    Aparece por cima da janela principal e bloqueia interação com ela
    enquanto está aberta (graças a self.grab_set()).
    """

    def __init__(self, parent, titulo: str, ao_guardar: Callable,
                 item: Optional[ItemDespensa] = None):
        """
        parent     → janela pai (AbaDespensa)
        titulo     → título da janela ("Adicionar" ou "Editar Ingrediente")
        ao_guardar → função a chamar com (nome, quantidade, unidade) quando guardar
        item       → ItemDespensa a editar (None se for adição nova)
        """
        super().__init__(parent)
        self.ao_guardar = ao_guardar
        self.item = item  # None = modo adição, ItemDespensa = modo edição

        self.title(titulo)
        self.geometry("420x320")
        self.resizable(False, False)  # Impede redimensionamento
        self.configure(fg_color=COR_FUNDO)
        self.grab_set()   # Torna modal (bloqueia a janela pai)
        self.focus_set()  # Coloca o foco nesta janela
        self.after(10, self._centrar)  # Centra após 10ms (tempo para renderizar)
        self._construir_interface()

    def _centrar(self):
        """Centra a janela no ecrã."""
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"420x320+{(sw - 420) // 2}+{(sh - 320) // 2}")

    def _construir_interface(self):
        """Constrói o formulário com campos de texto e botões."""

        # Título do formulário
        ctk.CTkLabel(
            self, text=f"🧂  {self.title()}",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color=COR_TEXTO, anchor="w"
        ).pack(fill="x", padx=24, pady=(20, 16))

        # ── Frame do formulário ───────────────────────────────────────────
        formulario = ctk.CTkFrame(self, fg_color=COR_SUPERFICIE, corner_radius=12)
        formulario.pack(fill="x", padx=20)

        # Campo: Nome do Ingrediente
        ctk.CTkLabel(formulario, text="Nome do Ingrediente",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=COR_TEXTO_MUDO, anchor="w"
                     ).grid(row=0, column=0, columnspan=2, sticky="w", padx=16, pady=(12, 4))

        self._campo_nome = ctk.CTkEntry(
            formulario, placeholder_text="Ex: Ovos, Farinha, Tomate...",
            font=ctk.CTkFont(size=13), fg_color=COR_SUPERFICIE2,
            border_color=COR_BORDA, text_color=COR_TEXTO,
            placeholder_text_color=COR_TEXTO_MUDO, corner_radius=8, height=38
        )
        self._campo_nome.grid(row=1, column=0, columnspan=2, sticky="ew",
                               padx=16, pady=(0, 12))

        # Rótulos para quantidade e unidade
        ctk.CTkLabel(formulario, text="Quantidade",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=COR_TEXTO_MUDO, anchor="w"
                     ).grid(row=2, column=0, sticky="w", padx=16, pady=(0, 4))
        ctk.CTkLabel(formulario, text="Unidade",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=COR_TEXTO_MUDO, anchor="w"
                     ).grid(row=2, column=1, sticky="w", padx=16, pady=(0, 4))

        # Campo: Quantidade
        self._campo_quantidade = ctk.CTkEntry(
            formulario, placeholder_text="Ex: 500",
            font=ctk.CTkFont(size=13), fg_color=COR_SUPERFICIE2,
            border_color=COR_BORDA, text_color=COR_TEXTO,
            placeholder_text_color=COR_TEXTO_MUDO, corner_radius=8, height=38
        )
        self._campo_quantidade.grid(row=3, column=0, sticky="ew",
                                     padx=(16, 4), pady=(0, 12))

        # ComboBox: Unidade (dropdown com lista de opções)
        self._combo_unidade = ctk.CTkComboBox(
            formulario, values=UNIDADES,
            font=ctk.CTkFont(size=13), fg_color=COR_SUPERFICIE2,
            border_color=COR_BORDA, text_color=COR_TEXTO,
            button_color=COR_DESTAQUE, button_hover_color="#4f46e5",
            dropdown_fg_color=COR_SUPERFICIE, dropdown_text_color=COR_TEXTO,
            dropdown_hover_color=COR_SUPERFICIE2, corner_radius=8, height=38
        )
        self._combo_unidade.grid(row=3, column=1, sticky="ew",
                                  padx=(4, 16), pady=(0, 12))

        # Configura as colunas para terem peso igual (expandem igualmente)
        formulario.columnconfigure(0, weight=1)
        formulario.columnconfigure(1, weight=1)

        # ── Pré-preenche se for modo edição ─────────────────────────────
        if self.item:
            # Preenche com os valores actuais do ingrediente
            self._campo_nome.insert(0, self.item.nome)
            # Mostra quantidade sem decimais desnecessários
            qtd = int(self.item.quantidade) if self.item.quantidade == int(self.item.quantidade) else self.item.quantidade
            self._campo_quantidade.insert(0, str(qtd))
            self._combo_unidade.set(self.item.unidade)
        else:
            # Modo adição: valor padrão no dropdown
            self._combo_unidade.set("unidades")

        # ── Botões Cancelar e Guardar ────────────────────────────────────
        fila_botoes = ctk.CTkFrame(self, fg_color="transparent")
        fila_botoes.pack(fill="x", padx=20, pady=16)

        ctk.CTkButton(
            fila_botoes, text="Cancelar",
            font=ctk.CTkFont(size=13),
            fg_color=COR_SUPERFICIE, hover_color=COR_SUPERFICIE2, text_color=COR_TEXTO_MUDO,
            corner_radius=8, height=38, command=self.destroy
        ).pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(
            fila_botoes, text="✔  Guardar",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COR_DESTAQUE, hover_color="#4f46e5", text_color="white",
            corner_radius=8, height=38, command=self._submeter
        ).pack(side="right", fill="x", expand=True, padx=(8, 0))

    def _submeter(self):
        """
        Valida os campos e chama a função ao_guardar se tudo estiver correcto.
        Chamada quando o utilizador clica "✔ Guardar".
        """
        nome = self._campo_nome.get().strip()
        texto_quantidade = self._campo_quantidade.get().strip()
        unidade = self._combo_unidade.get().strip()

        # ── Validações ───────────────────────────────────────────────────
        if not nome:
            messagebox.showerror("Erro", "O nome do ingrediente não pode estar vazio.", parent=self)
            return

        try:
            # .replace(",", ".") → permite vírgula como separador decimal
            quantidade = float(texto_quantidade.replace(",", "."))
            if quantidade <= 0:
                raise ValueError("Quantidade deve ser positiva")
        except ValueError:
            messagebox.showerror("Erro", "Quantidade inválida. Insere um número positivo.", parent=self)
            return

        if not unidade:
            messagebox.showerror("Erro", "Seleciona uma unidade.", parent=self)
            return

        # Chama a função de guardar passada pelo AbaDespensa
        self.ao_guardar(nome, quantidade, unidade)
        # Fecha o diálogo
        self.destroy()


# ══════════════════════════════════════════════════════════════════════════════
# CLASSE 4 — ABA DE RECEITAS
#
# Mostra os cards de sugestão com a percentagem de compatibilidade
# de cada receita com a despensa actual.
# ══════════════════════════════════════════════════════════════════════════════

class AbaReceitas(ctk.CTkFrame):
    """
    Aba que mostra as sugestões de receitas com base nos ingredientes que temos na despensa.

    Como funciona:
      1. Lê os ingredientes que o utilizador tem guardados.
      2. Permite aplicar múltiplos filtros (pesquisa por texto, tipo de prato, dificuldade, tempo).
      3. Apresenta uma lista de receitas ordenadas pelas mais fáceis de fazer com o que temos em casa.
    """

    def __init__(self, parent, obter_itens_despensa: Callable[[], List[ItemDespensa]]):
        """
        Esta função é o construtor da aba de receitas.
        Ela cria o painel básico e configura as variáveis de controlo.
        """
        super().__init__(parent, fg_color=COR_FUNDO, corner_radius=0)

        # Guarda a função que nos permite ler a lista de ingredientes da despensa
        self.obter_itens_despensa = obter_itens_despensa

        # Lista onde guardaremos as receitas sugeridas que passam pelos filtros
        self._sugestoes: List[SugestaoReceita] = []

        # Variável especial para a barra de pesquisa que deteta mudanças de texto
        # Sempre que o utilizador digitar uma letra, a aplicação é notificada
        self._texto_pesquisa_receita = ctk.StringVar()
        # Diz ao Python para chamar a função '_ao_mudar_pesquisa' sempre que o texto for alterado
        self._texto_pesquisa_receita.trace_add("write", self._ao_mudar_pesquisa)

        # Guarda a referência da tarefa de desenho dos cards para podermos cancelar se o filtro mudar a meio
        self._tarefa_renderizacao = None

        # Constrói os botões, caixas de seleção e a lista na tela
        self._construir_interface()

    def _construir_interface(self):
        """Constrói todos os elementos gráficos desta aba (cabeçalho, filtros e lista)."""

        # ── 1. CABEÇALHO DA TELA ───────────────────────────────────────────
        cabecalho = ctk.CTkFrame(self, fg_color=COR_SUPERFICIE, corner_radius=0, height=80)
        cabecalho.pack(fill="x")
        cabecalho.pack_propagate(False)

        interior_cab = ctk.CTkFrame(cabecalho, fg_color="transparent")
        interior_cab.pack(fill="both", expand=True, padx=24, pady=16)

        # Título principal da aba
        ctk.CTkLabel(
            interior_cab, text="🍳  Sugestão de Receitas",
            font=ctk.CTkFont(size=20, weight="bold"), text_color=COR_TEXTO, anchor="w"
        ).pack(side="left")

        # Botão "Atualizar" — recarrega e aplica todos os filtros de imediato
        self._btn_atualizar = ctk.CTkButton(
            interior_cab, text="🔄  Atualizar",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COR_DESTAQUE, hover_color="#4f46e5",
            corner_radius=10, height=38, command=self.atualizar
        )
        self._btn_atualizar.pack(side="right")

        # Rótulo de texto para mostrar o resultado da pesquisa (ex: "5 receitas encontradas")
        # Fica localizado à esquerda do botão de Atualizar
        self._label_resultado = ctk.CTkLabel(
            interior_cab, text="",
            font=ctk.CTkFont(size=12), text_color=COR_TEXTO_MUDO
        )
        self._label_resultado.pack(side="right", padx=(0, 16))

        # ── 2. PAINEL DE FILTROS AVANÇADOS ─────────────────────────────────
        # Criamos um painel cinzento para colocar todos os botões e caixas de seleção
        barra_filtro = ctk.CTkFrame(self, fg_color=COR_SUPERFICIE, corner_radius=0)
        barra_filtro.pack(fill="x")

        # Grid (grelha) interior para alinhar todos os controlos na horizontal
        interior_fil = ctk.CTkFrame(barra_filtro, fg_color="transparent")
        interior_fil.pack(fill="both", expand=True, padx=24, pady=12)

        # ── FILTRO A: Pesquisa por Texto
        ctk.CTkLabel(
            interior_fil, text="🔍  Pesquisar Receita:",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COR_TEXTO_MUDO, anchor="w"
        ).grid(row=0, column=0, sticky="w", padx=(0, 10), pady=(0, 2))

        self._campo_pesquisa_rec = ctk.CTkEntry(
            interior_fil, textvariable=self._texto_pesquisa_receita,
            placeholder_text="Escreva para pesquisar...",
            font=ctk.CTkFont(size=12), fg_color=COR_SUPERFICIE2,
            border_color=COR_BORDA, text_color=COR_TEXTO,
            placeholder_text_color=COR_TEXTO_MUDO,
            corner_radius=8, height=34, width=180
        )
        self._campo_pesquisa_rec.grid(row=1, column=0, sticky="ew", padx=(0, 10))

        # ── FILTRO B: Seleção de Categoria
        ctk.CTkLabel(
            interior_fil, text="📁  Categoria:",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COR_TEXTO_MUDO, anchor="w"
        ).grid(row=0, column=1, sticky="w", padx=(0, 10), pady=(0, 2))

        categorias = [
            "Todas", "Prato Principal", "Sopa",
            "Entrada", "Sobremesa", "Pequeno-Almoço",
            "Lanche", "Acompanhamento"
        ]
        self._combo_categoria = ctk.CTkComboBox(
            interior_fil, values=categorias,
            font=ctk.CTkFont(size=12), fg_color=COR_SUPERFICIE2,
            border_color=COR_BORDA, text_color=COR_TEXTO,
            button_color=COR_DESTAQUE, button_hover_color="#4f46e5",
            dropdown_fg_color=COR_SUPERFICIE, dropdown_text_color=COR_TEXTO,
            dropdown_hover_color=COR_SUPERFICIE2, corner_radius=8, height=34, width=140,
            command=self._ao_mudar_filtro_combo
        )
        self._combo_categoria.grid(row=1, column=1, sticky="ew", padx=(0, 10))
        self._combo_categoria.set("Todas")

        # ── FILTRO C: Seleção de Dificuldade
        ctk.CTkLabel(
            interior_fil, text="⚡  Dificuldade:",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COR_TEXTO_MUDO, anchor="w"
        ).grid(row=0, column=2, sticky="w", padx=(0, 10), pady=(0, 2))

        dificuldades = ["Todas", "Fácil", "Médio", "Difícil"]
        self._combo_dificuldade = ctk.CTkComboBox(
            interior_fil, values=dificuldades,
            font=ctk.CTkFont(size=12), fg_color=COR_SUPERFICIE2,
            border_color=COR_BORDA, text_color=COR_TEXTO,
            button_color=COR_DESTAQUE, button_hover_color="#4f46e5",
            dropdown_fg_color=COR_SUPERFICIE, dropdown_text_color=COR_TEXTO,
            dropdown_hover_color=COR_SUPERFICIE2, corner_radius=8, height=34, width=100,
            command=self._ao_mudar_filtro_combo
        )
        self._combo_dificuldade.grid(row=1, column=2, sticky="ew", padx=(0, 10))
        self._combo_dificuldade.set("Todas")

        # ── FILTRO D: Seleção de Tempo Máximo de Preparo/Cozedura
        ctk.CTkLabel(
            interior_fil, text="⏱️  Tempo Máx:",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COR_TEXTO_MUDO, anchor="w"
        ).grid(row=0, column=3, sticky="w", padx=(0, 10), pady=(0, 2))

        tempos = ["Qualquer tempo", "< 15 min", "< 30 min", "< 60 min", "< 120 min"]
        self._combo_tempo = ctk.CTkComboBox(
            interior_fil, values=tempos,
            font=ctk.CTkFont(size=12), fg_color=COR_SUPERFICIE2,
            border_color=COR_BORDA, text_color=COR_TEXTO,
            button_color=COR_DESTAQUE, button_hover_color="#4f46e5",
            dropdown_fg_color=COR_SUPERFICIE, dropdown_text_color=COR_TEXTO,
            dropdown_hover_color=COR_SUPERFICIE2, corner_radius=8, height=34, width=130,
            command=self._ao_mudar_filtro_combo
        )
        self._combo_tempo.grid(row=1, column=3, sticky="ew", padx=(0, 10))
        self._combo_tempo.set("Qualquer tempo")

        # ── FILTRO E: Ingredientes Completos vs Parciais
        ctk.CTkLabel(
            interior_fil, text="🧩  Ingredientes:",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COR_TEXTO_MUDO, anchor="w"
        ).grid(row=0, column=4, sticky="w", padx=(0, 10), pady=(0, 2))

        self._filtro = ctk.CTkSegmentedButton(
            interior_fil,
            values=["Todas", "Apenas Completas"],
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=COR_SUPERFICIE2, selected_color=COR_DESTAQUE,
            selected_hover_color="#4f46e5", unselected_color=COR_SUPERFICIE2,
            unselected_hover_color=COR_BORDA, text_color=COR_TEXTO,
            corner_radius=8, height=34, command=self._ao_mudar_filtro_segmented
        )
        self._filtro.grid(row=1, column=4, sticky="ew", padx=(0, 10))
        self._filtro.set("Todas")

        # Distribui os pesos das colunas na grelha para que fiquem bem arrumados na horizontal
        interior_fil.columnconfigure(0, weight=2)  # A pesquisa ganha mais espaço
        interior_fil.columnconfigure(1, weight=1)
        interior_fil.columnconfigure(2, weight=1)
        interior_fil.columnconfigure(3, weight=1)
        interior_fil.columnconfigure(4, weight=1)

        # ── 3. ÁREA DE SCROLL (ONDE APARECEM OS CARDS) ─────────────────────
        # Frame com scroll automático para rolar as receitas
        self._area_scroll = ctk.CTkScrollableFrame(
            self, fg_color=COR_FUNDO,
            scrollbar_button_color=COR_SUPERFICIE2,
            scrollbar_button_hover_color=COR_DESTAQUE
        )
        self._area_scroll.pack(fill="both", expand=True)

        # Mostra uma mensagem amigável a sugerir clicar em Atualizar
        self._mostrar_estado_vazio("Clica em «Atualizar» para ver as sugestões\ncom base na tua despensa.")

    def atualizar(self):
        """
        Método principal para iniciar o carregamento das receitas.
        Desativa o botão e programa o cálculo em segundo plano para a interface não congelar.
        """
        # Se estiver a decorrer um desenho de receitas anterior, cancelamo-lo de imediato
        if self._tarefa_renderizacao:
            self.after_cancel(self._tarefa_renderizacao)
            self._tarefa_renderizacao = None

        # Desativa temporariamente o botão e muda o texto para "A carregar..."
        self._btn_atualizar.configure(state="disabled", text="⏳  A carregar...")

        # Dá 50 milissegundos de intervalo ao Windows/Mac/Linux para atualizar a tela
        # e depois executa a lógica de atualização real.
        self.after(50, self._executar_atualizacao)

    def _executar_atualizacao(self):
        """Lê os filtros selecionados pelo utilizador e calcula as sugestões."""
        try:
            # 1. Obtém a lista atual de ingredientes da despensa
            despensa = self.obter_itens_despensa()

            # 2. Descobre se o utilizador quer apenas receitas que pode fazer já (100% de ingredientes)
            apenas_completas = self._filtro.get() == "Apenas Completas"

            # 3. Lê o texto escrito no campo de pesquisa
            pesquisa = self._texto_pesquisa_receita.get().strip()

            # 4. Lê a categoria selecionada
            categoria = self._combo_categoria.get()

            # 5. Lê a dificuldade selecionada
            dificuldade = self._combo_dificuldade.get()

            # 6. Lê a opção de tempo máximo e converte de texto para número de minutos
            tempo_str = self._combo_tempo.get()
            tempo_maximo = None
            if "<" in tempo_str:
                # Remove o "<" e o "min" para ficar apenas o número (ex: "< 30 min" virá 30)
                tempo_maximo = int(tempo_str.replace("<", "").replace("min", "").strip())

            # 7. Chama o motor de sugestões com todas estas informações selecionadas!
            self._sugestoes = obter_sugestoes(
                despensa=despensa,
                apenas_completas=apenas_completas,
                categoria=categoria,
                dificuldade=dificuldade,
                tempo_maximo=tempo_maximo,
                pesquisa=pesquisa
            )

            # 8. Limpa os cards de receitas que estavam desenhados anteriormente
            self._limpar_scroll()

            # 9. Atualiza o rótulo com o número de receitas encontradas
            total = len(self._sugestoes)
            sufixo_r = "s" if total != 1 else ""
            sufixo_e = "s" if total != 1 else ""
            self._label_resultado.configure(
                text=f"{total} receita{sufixo_r} encontrada{sufixo_e}"
            )

            # Se não foi encontrada nenhuma receita que cumpra os filtros:
            if total == 0:
                if not despensa:
                    msg = "A tua despensa está vazia.\nAdiciona ingredientes para ver sugestões!"
                else:
                    msg = "Nenhuma receita encontrada com estes filtros.\nTenta alargar as tuas opções de pesquisa!"
                self._mostrar_estado_vazio(msg)
                return

            # Adiciona um pequeno espaçador invisível no topo da lista
            ctk.CTkFrame(self._area_scroll, fg_color="transparent", height=8).pack()

            # 10. Começa a desenhar os cards de receitas em pequenos lotes (a começar no índice 0)
            self._desenhar_lote_receitas(0)

        except Exception as erro:
            self._mostrar_estado_vazio(f"Erro ao carregar receitas:\n{erro}")
        finally:
            # No final de tudo (correndo bem ou mal), devolve o botão ao estado normal
            self._btn_atualizar.configure(state="normal", text="🔄  Atualizar")

    def _desenhar_lote_receitas(self, indice_inicio: int):
        """
        Desenha as receitas em pequenos blocos (4 de cada vez)
        e aguarda 1ms antes de desenhar o próximo bloco. Isto evita que o programa trave.
        """
        tamanho_lote = 4
        total_sugestoes = len(self._sugestoes)

        # Calcula o limite máximo de receitas para este lote
        limite = min(indice_inicio + tamanho_lote, total_sugestoes)
        for i in range(indice_inicio, limite):
            self._desenhar_card_receita(self._sugestoes[i])

        # Se ainda sobrarem receitas por desenhar:
        if limite < total_sugestoes:
            # Agenda a si própria para desenhar o resto no milissegundo seguinte.
            # Este curto intervalo liberta a interface gráfica para responder a cliques e rolagem.
            self._tarefa_renderizacao = self.after(
                1, lambda: self._desenhar_lote_receitas(limite)
            )
        else:
            # Quando desenhar a última receita, coloca um pequeno espaçador no final
            ctk.CTkFrame(self._area_scroll, fg_color="transparent", height=16).pack()
            self._tarefa_renderizacao = None

    def _ao_mudar_pesquisa(self, *_):
        """Esta função corre automaticamente sempre que o utilizador escreve na barra de pesquisa."""
        self.atualizar()

    def _ao_mudar_filtro_combo(self, _):
        """Esta função corre quando o utilizador muda qualquer uma das caixas de escolha (ComboBox)."""
        self.atualizar()

    def _ao_mudar_filtro_segmented(self, _):
        """Esta função corre quando o utilizador clica no botão 'Apenas Completas'."""
        self.atualizar()

    def _limpar_scroll(self):
        """Apaga todos os widgets/cards desenhados na área de rolagem (limpa a tela)."""
        for widget in self._area_scroll.winfo_children():
            widget.destroy()

    def _mostrar_estado_vazio(self, mensagem: str):
        """Mostra uma mensagem explicativa centrada quando não há receitas."""
        self._limpar_scroll()
        self._label_resultado.configure(text="")
        ctk.CTkLabel(
            self._area_scroll, text=f"🍽️\n\n{mensagem}",
            font=ctk.CTkFont(size=15), text_color=COR_TEXTO_MUDO, justify="center"
        ).pack(expand=True, pady=80)

    def _desenhar_card_receita(self, sugestao: SugestaoReceita):
        """
        Desenha o painel retangular (card) correspondente a uma sugestão de receita.
        Mostra o título, tempo de confeção, barra de ingredientes disponíveis e ingredientes em falta.
        """
        card = ctk.CTkFrame(self._area_scroll, fg_color=COR_SUPERFICIE, corner_radius=14)
        card.pack(fill="x", padx=20, pady=6)

        # ── Fila de topo: Emoji da categoria + Título + Botão Ver Receita ──
        fila_top = ctk.CTkFrame(card, fg_color="transparent")
        fila_top.pack(fill="x", padx=16, pady=(14, 4))

        # Desenha o emoji correspondente à categoria (ex: sopa -> 🥣, principal -> 🍽️)
        ctk.CTkLabel(
            fila_top, text=sugestao.receita.emoji_categoria,
            font=ctk.CTkFont(size=26), text_color=COR_TEXTO, width=40
        ).pack(side="left", padx=(0, 10))

        frame_info = ctk.CTkFrame(fila_top, fg_color="transparent")
        frame_info.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(
            frame_info, text=sugestao.receita.titulo,
            font=ctk.CTkFont(size=15, weight="bold"), text_color=COR_TEXTO, anchor="w"
        ).pack(fill="x")

        # Metadados numa linha horizontal (categoria, dificuldade, tempo, porções)
        fila_meta = ctk.CTkFrame(frame_info, fg_color="transparent")
        fila_meta.pack(fill="x")
        for texto in [
            sugestao.receita.categoria,
            f"{sugestao.receita.emoji_dificuldade} {sugestao.receita.dificuldade}",
            f"⏰ {sugestao.receita.tempo_total_formatado}",
            f"👥 {sugestao.receita.porcoes} porções"
        ]:
            ctk.CTkLabel(fila_meta, text=texto, font=ctk.CTkFont(size=11),
                         text_color=COR_TEXTO_MUDO).pack(side="left", padx=(0, 12))

        # Botão "Ver Receita" — abre JanelaDetalheReceita passando a sugestão
        ctk.CTkButton(
            fila_top, text="Ver Receita →",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=COR_DESTAQUE, hover_color="#4f46e5",
            text_color="white", corner_radius=8, width=110, height=34,
            command=lambda s=sugestao: JanelaDetalheReceita(self, s)
        ).pack(side="right", padx=(12, 0))

        # ── Barra de compatibilidade ──────────────────────────────────────
        percentagem = sugestao.percentagem_compatibilidade
        cor = sugestao.cor_compatibilidade

        frame_compat = ctk.CTkFrame(card, fg_color="transparent")
        frame_compat.pack(fill="x", padx=16, pady=(4, 4))

        fila_rot = ctk.CTkFrame(frame_compat, fg_color="transparent")
        fila_rot.pack(fill="x")

        ctk.CTkLabel(
            fila_rot,
            text="✅ Completa!" if sugestao.e_completa else f"🧩 {percentagem:.0f}% compatível",
            font=ctk.CTkFont(size=12, weight="bold"), text_color=cor, anchor="w"
        ).pack(side="left")

        total_obr = len(sugestao.receita.ingredientes_obrigatorios)
        total_disp = len(sugestao.ingredientes_disponiveis)
        ctk.CTkLabel(
            fila_rot, text=f"{total_disp}/{total_obr} ingredientes disponíveis",
            font=ctk.CTkFont(size=11), text_color=COR_TEXTO_MUDO, anchor="e"
        ).pack(side="right")

        # A barra de progresso vai de 0.0 a 1.0 (não de 0 a 100)
        barra = ctk.CTkProgressBar(frame_compat, height=8, corner_radius=4,
                                    progress_color=cor, fg_color=COR_SUPERFICIE2)
        barra.pack(fill="x", pady=(4, 0))
        barra.set(min(percentagem / 100, 1.0))  # min(..., 1.0) garante que não passa de 100%

        # ── Ingredientes em falta (se houver) ────────────────────────────
        if sugestao.ingredientes_em_falta:
            frame_falta = ctk.CTkFrame(card, fg_color=COR_SUPERFICIE2, corner_radius=8)
            frame_falta.pack(fill="x", padx=16, pady=(6, 12))

            interior_falta = ctk.CTkFrame(frame_falta, fg_color="transparent")
            interior_falta.pack(fill="x", padx=12, pady=8)

            ctk.CTkLabel(interior_falta, text="❌ Faltam: ",
                         font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=COR_PERIGO).pack(side="left")

            # Mostra no máximo 5 ingredientes em falta para não sobrecarregar
            texto_falta = ",  ".join(sugestao.ingredientes_em_falta[:5])
            if len(sugestao.ingredientes_em_falta) > 5:
                texto_falta += f" ... +{len(sugestao.ingredientes_em_falta) - 5} mais"

            ctk.CTkLabel(interior_falta, text=texto_falta,
                         font=ctk.CTkFont(size=11), text_color=COR_TEXTO_MUDO,
                         wraplength=550, anchor="w"
                         ).pack(side="left", fill="x", expand=True)
        else:
            # Espaço de respiro no fundo do card quando não há ingredientes em falta
            ctk.CTkFrame(card, fg_color="transparent", height=8).pack()


# ══════════════════════════════════════════════════════════════════════════════
# CLASSE 5 — JANELA DE DETALHE DA RECEITA
#
# Pop-up que mostra a receita completa:
#   - Cabeçalho com título, descrição e metadados
#   - Barra de compatibilidade com a despensa
#   - Lista de ingredientes com ✅/❌ por cada um
#   - Modo de preparo passo a passo
# ══════════════════════════════════════════════════════════════════════════════

class JanelaDetalheReceita(ctk.CTkToplevel):
    """
    Janela modal que mostra os detalhes completos de uma receita.
    Abre ao clicar "Ver Receita →" num card de sugestão.
    """

    def __init__(self, parent, sugestao: SugestaoReceita):
        super().__init__(parent)
        self.sugestao = sugestao
        self.receita = sugestao.receita  # Atalho para não escrever self.sugestao.receita sempre

        self._configurar_janela()
        self._construir_interface()

    def _configurar_janela(self):
        """Configura título, tamanho e posição da janela."""
        self.title(f"🍽️ {self.receita.titulo}")
        self.geometry("800x700")
        self.minsize(700, 600)
        self.configure(fg_color=COR_FUNDO)
        self.grab_set()
        self.focus_set()
        self.after(10, self._centrar)

    def _centrar(self):
        """Centra a janela no ecrã."""
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"800x700+{(sw - 800) // 2}+{(sh - 700) // 2}")

    def _construir_interface(self):
        """Constrói o cabeçalho e o corpo com ingredientes e instruções."""

        # ── Cabeçalho fixo (não faz scroll) ──────────────────────────────
        cabecalho = ctk.CTkFrame(self, fg_color=COR_SUPERFICIE, corner_radius=0)
        cabecalho.pack(fill="x")

        # Fila com emoji, título, descrição e botão de fechar
        fila_topo = ctk.CTkFrame(cabecalho, fg_color="transparent")
        fila_topo.pack(fill="x", padx=24, pady=(20, 8))

        ctk.CTkLabel(
            fila_topo, text=self.receita.emoji_categoria,
            font=ctk.CTkFont(size=36), text_color=COR_TEXTO
        ).pack(side="left", padx=(0, 12))

        frame_titulo = ctk.CTkFrame(fila_topo, fg_color="transparent")
        frame_titulo.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(
            frame_titulo, text=self.receita.titulo,
            font=ctk.CTkFont(size=22, weight="bold"), text_color=COR_TEXTO, anchor="w"
        ).pack(fill="x")
        ctk.CTkLabel(
            frame_titulo, text=self.receita.descricao,
            font=ctk.CTkFont(size=13), text_color=COR_TEXTO_MUDO,
            anchor="w", wraplength=550
        ).pack(fill="x")

        # Botão "X" para fechar a janela
        ctk.CTkButton(
            fila_topo, text="✕", width=36, height=36, corner_radius=18,
            fg_color=COR_SUPERFICIE2, hover_color=COR_PERIGO,
            text_color=COR_TEXTO, font=ctk.CTkFont(size=14, weight="bold"),
            command=self.destroy
        ).pack(side="right", padx=(12, 0))

        # ── Chips de metadados ────────────────────────────────────────────
        # Chips = pequenas etiquetas arredondadas com informação
        fila_meta = ctk.CTkFrame(cabecalho, fg_color="transparent")
        fila_meta.pack(fill="x", padx=24, pady=(0, 16))

        for icone, texto in [
            ("⏱️", f"Prep: {self.receita.tempo_preparo} min"),
            ("🔥", f"Cozedura: {self.receita.tempo_cozedura} min"),
            ("⏰", f"Total: {self.receita.tempo_total_formatado}"),
            ("👥", f"{self.receita.porcoes} porções"),
            (self.receita.emoji_dificuldade, self.receita.dificuldade),
            ("📁", self.receita.categoria),
        ]:
            chip = ctk.CTkFrame(fila_meta, fg_color=COR_SUPERFICIE2, corner_radius=20)
            chip.pack(side="left", padx=(0, 8))
            ctk.CTkLabel(chip, text=f"{icone} {texto}",
                         font=ctk.CTkFont(size=12), text_color=COR_TEXTO_MUDO,
                         padx=12, pady=6).pack()

        # ── Barra de compatibilidade ──────────────────────────────────────
        percentagem = self.sugestao.percentagem_compatibilidade
        cor = self.sugestao.cor_compatibilidade

        frame_compat = ctk.CTkFrame(cabecalho, fg_color="transparent")
        frame_compat.pack(fill="x", padx=24, pady=(0, 16))

        ctk.CTkLabel(
            frame_compat, text=f"Compatibilidade com a despensa: {percentagem:.0f}%",
            font=ctk.CTkFont(size=13, weight="bold"), text_color=cor, anchor="w"
        ).pack(fill="x", pady=(0, 4))

        barra = ctk.CTkProgressBar(frame_compat, height=10, corner_radius=5,
                                    progress_color=cor, fg_color=COR_SUPERFICIE2)
        barra.pack(fill="x")
        barra.set(percentagem / 100)

        # ── Corpo com scroll (ingredientes + instruções) ──────────────────
        corpo = ctk.CTkScrollableFrame(self, fg_color=COR_FUNDO,
                                        scrollbar_button_color=COR_SUPERFICIE2)
        corpo.pack(fill="both", expand=True)

        # ── Secção: Ingredientes ──────────────────────────────────────────
        self._titulo_secao(corpo, "🥕 Ingredientes")

        frame_ing = ctk.CTkFrame(corpo, fg_color=COR_SUPERFICIE, corner_radius=12)
        frame_ing.pack(fill="x", padx=20, pady=(0, 16))

        # Conjunto dos ingredientes disponíveis (para verificação rápida)
        disponiveis = set(self.sugestao.ingredientes_disponiveis)
        obrigatorios = self.receita.ingredientes_obrigatorios
        opcionais = [i for i in self.receita.ingredientes if i.opcional]

        # Ingredientes obrigatórios com ✅ ou ❌
        if obrigatorios:
            ctk.CTkLabel(frame_ing, text="Ingredientes obrigatórios",
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=COR_TEXTO_MUDO, anchor="w"
                         ).pack(fill="x", padx=16, pady=(12, 4))

            for ing in obrigatorios:
                disponivel = ing.nome_ingrediente in disponiveis
                fila = ctk.CTkFrame(frame_ing, fg_color="transparent")
                fila.pack(fill="x", padx=16, pady=2)

                ctk.CTkLabel(
                    fila, text="✅" if disponivel else "❌",
                    font=ctk.CTkFont(size=14),
                    text_color=COR_SUCESSO if disponivel else COR_PERIGO, width=28
                ).pack(side="left")

                ctk.CTkLabel(
                    fila, text=ing.exibir,
                    font=ctk.CTkFont(size=13),
                    text_color=COR_TEXTO if disponivel else COR_TEXTO_MUDO, anchor="w"
                ).pack(side="left", fill="x", expand=True)

        # Ingredientes opcionais com ⭕
        if opcionais:
            ctk.CTkLabel(frame_ing, text="Opcionais / Garnish",
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=COR_TEXTO_MUDO, anchor="w"
                         ).pack(fill="x", padx=16, pady=(12, 4))

            for ing in opcionais:
                fila = ctk.CTkFrame(frame_ing, fg_color="transparent")
                fila.pack(fill="x", padx=16, pady=2)
                ctk.CTkLabel(fila, text="⭕", font=ctk.CTkFont(size=14),
                             text_color=COR_TEXTO_MUDO, width=28).pack(side="left")
                ctk.CTkLabel(fila, text=ing.exibir, font=ctk.CTkFont(size=13),
                             text_color=COR_TEXTO_MUDO, anchor="w"
                             ).pack(side="left", fill="x", expand=True)

        ctk.CTkFrame(frame_ing, fg_color="transparent", height=8).pack()

        # ── Secção: Modo de Preparo ───────────────────────────────────────
        self._titulo_secao(corpo, "📋 Modo de Preparo")

        frame_inst = ctk.CTkFrame(corpo, fg_color=COR_SUPERFICIE, corner_radius=12)
        frame_inst.pack(fill="x", padx=20, pady=(0, 16))

        # Divide as instruções por linha e desenha cada passo
        for linha in self.receita.instrucoes.strip().split("\n"):
            linha = linha.strip()
            if not linha:
                continue

            # Tenta extrair o número do passo (ex: "1." ou "2.")
            if linha[0].isdigit() and "." in linha:
                numero = linha.split(".")[0].strip()
                texto_passo = linha[linha.index(".") + 1:].strip()
            else:
                numero = "•"
                texto_passo = linha

            # Card do passo com número colorido
            fila_passo = ctk.CTkFrame(frame_inst, fg_color=COR_SUPERFICIE2, corner_radius=8)
            fila_passo.pack(fill="x", padx=16, pady=4)

            # Círculo colorido com o número do passo
            badge = ctk.CTkFrame(fila_passo, fg_color=COR_DESTAQUE,
                                  corner_radius=14, width=28, height=28)
            badge.pack(side="left", padx=(12, 10), pady=10)
            badge.pack_propagate(False)
            ctk.CTkLabel(badge, text=numero,
                         font=ctk.CTkFont(size=11, weight="bold"),
                         text_color="white").place(relx=0.5, rely=0.5, anchor="center")

            # Texto do passo
            ctk.CTkLabel(
                fila_passo, text=texto_passo,
                font=ctk.CTkFont(size=13), text_color=COR_TEXTO,
                anchor="w", justify="left", wraplength=620
            ).pack(side="left", fill="x", expand=True, padx=(0, 12), pady=10)

        ctk.CTkFrame(corpo, fg_color="transparent", height=20).pack()

    def _titulo_secao(self, parent, titulo: str):
        """
        Desenha um título de secção dentro do corpo da janela.
        Método auxiliar para evitar repetição de código.
        """
        ctk.CTkLabel(
            parent, text=titulo,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COR_TEXTO, anchor="w"
        ).pack(fill="x", padx=20, pady=(16, 8))
