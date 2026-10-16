"""
Janela principal da aplicação Despensa Inteligente.
Usa CustomTkinter com tema escuro, sidebar de navegação e conteúdo por abas.
"""
import customtkinter as ctk

from app.ui.pantry_tab import PantryTab
from app.ui.recipes_tab import RecipesTab

# Configuração global do CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Paleta de cores
C_BG         = "#0f172a"
C_SIDEBAR    = "#0a0f1e"
C_SURFACE    = "#1e293b"
C_SURFACE2   = "#273549"
C_ACCENT     = "#6366f1"
C_ACCENT2    = "#4f46e5"
C_SUCCESS    = "#10b981"
C_TEXT       = "#f1f5f9"
C_TEXT_MUTED = "#94a3b8"
C_BORDER     = "#334155"


class AppWindow:
    """Janela principal da aplicação."""

    def __init__(self):
        self.root = ctk.CTk()
        self._active_tab = "pantry"
        self._setup_window()
        self._build_layout()

    def _setup_window(self):
        self.root.title("🍽️ Despensa Inteligente")
        self.root.geometry("1100x720")
        self.root.minsize(900, 600)
        self.root.configure(fg_color=C_BG)
        self._center_window()

    def _center_window(self):
        self.root.update_idletasks()
        w, h = 1100, 720
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    # ── Layout ───────────────────────────────────────────────────────────

    def _build_layout(self):
        # Container principal
        main = ctk.CTkFrame(self.root, fg_color=C_BG, corner_radius=0)
        main.pack(fill="both", expand=True)

        # Sidebar esquerda
        self._sidebar = ctk.CTkFrame(main, fg_color=C_SIDEBAR, corner_radius=0, width=240)
        self._sidebar.pack(side="left", fill="y")
        self._sidebar.pack_propagate(False)
        self._build_sidebar()

        # Separador
        sep = ctk.CTkFrame(main, fg_color=C_BORDER, width=1, corner_radius=0)
        sep.pack(side="left", fill="y")

        # Área de conteúdo
        self._content_area = ctk.CTkFrame(main, fg_color=C_BG, corner_radius=0)
        self._content_area.pack(side="left", fill="both", expand=True)

        # Inicializar abas
        self._pantry_tab = PantryTab(
            self._content_area,
            on_change=self._on_pantry_change,
        )
        self._recipes_tab = RecipesTab(
            self._content_area,
            get_pantry_items=self._get_pantry_items,
        )

        # Mostrar aba inicial
        self._show_tab("pantry")

    def _build_sidebar(self):
        # Logo / Título
        logo_frame = ctk.CTkFrame(self._sidebar, fg_color="transparent", height=120)
        logo_frame.pack(fill="x")
        logo_frame.pack_propagate(False)

        ctk.CTkLabel(
            logo_frame,
            text="🍽️",
            font=ctk.CTkFont(size=44),
            text_color=C_ACCENT,
        ).pack(pady=(24, 0))

        ctk.CTkLabel(
            logo_frame,
            text="Despensa",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=C_TEXT,
        ).pack()

        ctk.CTkLabel(
            logo_frame,
            text="Inteligente",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=C_ACCENT,
        ).pack()

        # Separador
        ctk.CTkFrame(self._sidebar, fg_color=C_BORDER, height=1).pack(fill="x", padx=20, pady=16)

        # Secção de navegação
        ctk.CTkLabel(
            self._sidebar,
            text="NAVEGAÇÃO",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=C_TEXT_MUTED,
            anchor="w",
        ).pack(fill="x", padx=20, pady=(0, 8))

        # Botões de navegação
        self._nav_pantry = self._nav_button("🥕  Minha Despensa", "pantry")
        self._nav_recipes = self._nav_button("🍳  Receitas", "recipes")

        # Espaçador
        ctk.CTkFrame(self._sidebar, fg_color="transparent").pack(fill="both", expand=True)

        # Separador inferior
        ctk.CTkFrame(self._sidebar, fg_color=C_BORDER, height=1).pack(fill="x", padx=20, pady=8)

        # Info inferior
        info_frame = ctk.CTkFrame(self._sidebar, fg_color="transparent", height=70)
        info_frame.pack(fill="x", pady=8)
        info_frame.pack_propagate(False)

        ctk.CTkLabel(
            info_frame,
            text="🐳  PostgreSQL + Docker",
            font=ctk.CTkFont(size=11),
            text_color=C_TEXT_MUTED,
        ).pack(pady=(8, 2))

        ctk.CTkLabel(
            info_frame,
            text="v1.0.0  •  Python 3.11",
            font=ctk.CTkFont(size=10),
            text_color=C_BORDER,
        ).pack()

        # Status da BD
        self._db_status = ctk.CTkLabel(
            info_frame,
            text="🟢  Conectado",
            font=ctk.CTkFont(size=11),
            text_color=C_SUCCESS,
        )
        self._db_status.pack(pady=(2, 8))

    def _nav_button(self, text: str, tab_name: str) -> ctk.CTkButton:
        btn = ctk.CTkButton(
            self._sidebar,
            text=text,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="transparent",
            hover_color=C_SURFACE,
            text_color=C_TEXT_MUTED,
            anchor="w",
            corner_radius=10,
            height=44,
            command=lambda t=tab_name: self._show_tab(t),
        )
        btn.pack(fill="x", padx=12, pady=2)
        return btn

    # ── Lógica de navegação ──────────────────────────────────────────────

    def _show_tab(self, tab_name: str):
        self._active_tab = tab_name

        # Esconder todas as abas
        self._pantry_tab.pack_forget()
        self._recipes_tab.pack_forget()

        # Resetar estilos dos botões
        for btn in [self._nav_pantry, self._nav_recipes]:
            btn.configure(fg_color="transparent", text_color=C_TEXT_MUTED)

        # Mostrar aba e destacar botão
        if tab_name == "pantry":
            self._pantry_tab.pack(fill="both", expand=True)
            self._nav_pantry.configure(fg_color=C_SURFACE, text_color=C_ACCENT)
        else:
            self._recipes_tab.pack(fill="both", expand=True)
            self._nav_recipes.configure(fg_color=C_SURFACE, text_color=C_ACCENT)
            # Auto-refresh quando muda para a aba de receitas
            self.root.after(100, self._recipes_tab.refresh)

    def _on_pantry_change(self):
        """Callback chamado quando a despensa muda."""
        pass  # Pode ser usado para badge de contagem, etc.

    def _get_pantry_items(self):
        return self._pantry_tab.get_items()

    # ── Execução ─────────────────────────────────────────────────────────

    def run(self):
        """Inicia o loop principal da aplicação."""
        self.root.mainloop()
