"""
Janela modal de detalhe de uma receita.
Exibe informações completas: ingredientes disponíveis/em falta e modo de preparo.
"""
import customtkinter as ctk
from app.models.recipe import RecipeSuggestion, Recipe


# Paleta de cores
C_BG        = "#0f172a"
C_SURFACE   = "#1e293b"
C_SURFACE2  = "#273549"
C_ACCENT    = "#6366f1"
C_SUCCESS   = "#10b981"
C_DANGER    = "#f43f5e"
C_WARNING   = "#f59e0b"
C_TEXT      = "#f1f5f9"
C_TEXT_MUTED = "#94a3b8"
C_BORDER    = "#334155"


class RecipeDetailWindow(ctk.CTkToplevel):
    """Janela de detalhe completo de uma receita."""

    def __init__(self, parent, suggestion: RecipeSuggestion):
        super().__init__(parent)
        self.suggestion = suggestion
        self.recipe = suggestion.recipe

        self._setup_window()
        self._build_ui()

    def _setup_window(self):
        self.title(f"🍽️ {self.recipe.title}")
        self.geometry("800x700")
        self.minsize(700, 600)
        self.configure(fg_color=C_BG)
        self.grab_set()   # Modal
        self.focus_set()
        # Centralizar na tela
        self.after(10, self._center_window)

    def _center_window(self):
        self.update_idletasks()
        w, h = 800, 700
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _build_ui(self):
        # ── Header ──────────────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color=C_SURFACE, corner_radius=0)
        header.pack(fill="x", padx=0, pady=0)

        # Linha topo: emoji + título + fechar
        top_row = ctk.CTkFrame(header, fg_color="transparent")
        top_row.pack(fill="x", padx=24, pady=(20, 8))

        emoji_label = ctk.CTkLabel(
            top_row,
            text=self.recipe.category_emoji,
            font=ctk.CTkFont(size=36),
            text_color=C_TEXT,
        )
        emoji_label.pack(side="left", padx=(0, 12))

        title_frame = ctk.CTkFrame(top_row, fg_color="transparent")
        title_frame.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(
            title_frame,
            text=self.recipe.title,
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=C_TEXT,
            anchor="w",
        ).pack(fill="x")

        ctk.CTkLabel(
            title_frame,
            text=self.recipe.description,
            font=ctk.CTkFont(size=13),
            text_color=C_TEXT_MUTED,
            anchor="w",
            wraplength=550,
        ).pack(fill="x")

        close_btn = ctk.CTkButton(
            top_row,
            text="✕",
            width=36,
            height=36,
            corner_radius=18,
            fg_color=C_SURFACE2,
            hover_color=C_DANGER,
            text_color=C_TEXT,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.destroy,
        )
        close_btn.pack(side="right", padx=(12, 0))

        # Linha de metadados
        meta_row = ctk.CTkFrame(header, fg_color="transparent")
        meta_row.pack(fill="x", padx=24, pady=(0, 16))

        meta_items = [
            ("⏱️", f"Prep: {self.recipe.prep_time} min", None),
            ("🔥", f"Cozedura: {self.recipe.cook_time} min", None),
            ("⏰", f"Total: {self.recipe.total_time_display}", None),
            ("👥", f"{self.recipe.servings} porções", None),
            (self.recipe.difficulty_emoji, self.recipe.difficulty, None),
            ("📁", self.recipe.category, None),
        ]

        for icon, label, _ in meta_items:
            chip = ctk.CTkFrame(meta_row, fg_color=C_SURFACE2, corner_radius=20)
            chip.pack(side="left", padx=(0, 8))
            ctk.CTkLabel(
                chip,
                text=f"{icon} {label}",
                font=ctk.CTkFont(size=12),
                text_color=C_TEXT_MUTED,
                padx=12,
                pady=6,
            ).pack()

        # Barra de compatibilidade
        compat_frame = ctk.CTkFrame(header, fg_color="transparent")
        compat_frame.pack(fill="x", padx=24, pady=(0, 16))

        pct = self.suggestion.compatibility_pct
        pct_color = self.suggestion.recipe.category_emoji  # reutilizar cor
        bar_color = self.suggestion.compatibility_color

        ctk.CTkLabel(
            compat_frame,
            text=f"Compatibilidade com a despensa: {pct:.0f}%",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=bar_color,
            anchor="w",
        ).pack(fill="x", pady=(0, 4))

        bar = ctk.CTkProgressBar(
            compat_frame,
            height=10,
            corner_radius=5,
            progress_color=bar_color,
            fg_color=C_SURFACE2,
        )
        bar.pack(fill="x")
        bar.set(pct / 100)

        # ── Corpo (scrollável) ───────────────────────────────────────────
        body = ctk.CTkScrollableFrame(self, fg_color=C_BG, scrollbar_button_color=C_SURFACE2)
        body.pack(fill="both", expand=True, padx=0, pady=0)

        # Secção: Ingredientes
        self._section_title(body, "🥕 Ingredientes")
        ing_frame = ctk.CTkFrame(body, fg_color=C_SURFACE, corner_radius=12)
        ing_frame.pack(fill="x", padx=20, pady=(0, 16))

        all_required = self.recipe.required_ingredients
        available_set = set(self.suggestion.available_ingredients)
        optional_ings = [i for i in self.recipe.ingredients if i.optional]

        if all_required:
            ctk.CTkLabel(
                ing_frame,
                text="Ingredientes obrigatórios",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=C_TEXT_MUTED,
                anchor="w",
            ).pack(fill="x", padx=16, pady=(12, 4))

            for ing in all_required:
                is_available = ing.ingredient_name in available_set
                icon = "✅" if is_available else "❌"
                color = C_SUCCESS if is_available else C_DANGER
                row = ctk.CTkFrame(ing_frame, fg_color="transparent")
                row.pack(fill="x", padx=16, pady=2)
                ctk.CTkLabel(row, text=icon, font=ctk.CTkFont(size=14),
                             text_color=color, width=28).pack(side="left")
                ctk.CTkLabel(
                    row,
                    text=ing.display,
                    font=ctk.CTkFont(size=13),
                    text_color=C_TEXT if is_available else C_TEXT_MUTED,
                    anchor="w",
                ).pack(side="left", fill="x", expand=True)

        if optional_ings:
            ctk.CTkLabel(
                ing_frame,
                text="Opcionais / Garnish",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=C_TEXT_MUTED,
                anchor="w",
            ).pack(fill="x", padx=16, pady=(12, 4))

            for ing in optional_ings:
                row = ctk.CTkFrame(ing_frame, fg_color="transparent")
                row.pack(fill="x", padx=16, pady=2)
                ctk.CTkLabel(row, text="⭕", font=ctk.CTkFont(size=14),
                             text_color=C_TEXT_MUTED, width=28).pack(side="left")
                ctk.CTkLabel(
                    row,
                    text=ing.display,
                    font=ctk.CTkFont(size=13),
                    text_color=C_TEXT_MUTED,
                    anchor="w",
                ).pack(side="left", fill="x", expand=True)

        # Padding bottom inside card
        ctk.CTkFrame(ing_frame, fg_color="transparent", height=8).pack()

        # Secção: Modo de Preparo
        self._section_title(body, "📋 Modo de Preparo")
        inst_frame = ctk.CTkFrame(body, fg_color=C_SURFACE, corner_radius=12)
        inst_frame.pack(fill="x", padx=20, pady=(0, 16))

        steps = self.recipe.instructions.strip().split("\n")
        for i, step in enumerate(steps):
            step = step.strip()
            if not step:
                continue
            # Remove numeração se já existir (ex: "1. ")
            if step[:2].rstrip(". ").isdigit():
                text = step[step.index(".") + 1:].strip() if "." in step else step
                step_num = step.split(".")[0].strip()
            else:
                text = step
                step_num = str(i + 1)

            step_row = ctk.CTkFrame(inst_frame, fg_color=C_SURFACE2, corner_radius=8)
            step_row.pack(fill="x", padx=16, pady=4)

            # Número do passo
            num_label = ctk.CTkFrame(step_row, fg_color=C_ACCENT, corner_radius=14,
                                     width=28, height=28)
            num_label.pack(side="left", padx=(12, 10), pady=10)
            num_label.pack_propagate(False)
            ctk.CTkLabel(
                num_label,
                text=step_num,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="white",
            ).place(relx=0.5, rely=0.5, anchor="center")

            ctk.CTkLabel(
                step_row,
                text=text,
                font=ctk.CTkFont(size=13),
                text_color=C_TEXT,
                anchor="w",
                justify="left",
                wraplength=620,
            ).pack(side="left", fill="x", expand=True, padx=(0, 12), pady=10)

        # Padding final
        ctk.CTkFrame(body, fg_color="transparent", height=20).pack()

    def _section_title(self, parent, title: str):
        ctk.CTkLabel(
            parent,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=C_TEXT,
            anchor="w",
        ).pack(fill="x", padx=20, pady=(16, 8))
