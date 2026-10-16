"""
Aba de sugestão de receitas.
Exibe cards com compatibilidade percentual e botão para ver detalhes.
"""
import customtkinter as ctk
from typing import List, Callable, Optional

from app.models.recipe import RecipeSuggestion
from app.models.ingredient import PantryItem
from app.services import recipe_service
from app.ui.recipe_detail import RecipeDetailWindow

# Paleta de cores
C_BG         = "#0f172a"
C_SURFACE    = "#1e293b"
C_SURFACE2   = "#273549"
C_ACCENT     = "#6366f1"
C_SUCCESS    = "#10b981"
C_DANGER     = "#f43f5e"
C_WARNING    = "#f59e0b"
C_TEXT       = "#f1f5f9"
C_TEXT_MUTED = "#94a3b8"
C_BORDER     = "#334155"


class RecipesTab(ctk.CTkFrame):
    """Aba de sugestão de receitas com filtro e cards visuais."""

    def __init__(self, parent, get_pantry_items: Callable[[], List[PantryItem]]):
        super().__init__(parent, fg_color=C_BG, corner_radius=0)
        self.get_pantry_items = get_pantry_items
        self._suggestions: List[RecipeSuggestion] = []
        self._only_complete = ctk.BooleanVar(value=False)
        self._build_ui()

    # ── Construção da UI ────────────────────────────────────────────────

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color=C_SURFACE, corner_radius=0, height=80)
        header.pack(fill="x")
        header.pack_propagate(False)

        h_inner = ctk.CTkFrame(header, fg_color="transparent")
        h_inner.pack(fill="both", expand=True, padx=24, pady=16)

        ctk.CTkLabel(
            h_inner,
            text="🍳  Sugestão de Receitas",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=C_TEXT,
            anchor="w",
        ).pack(side="left")

        # Botão Atualizar
        self._refresh_btn = ctk.CTkButton(
            h_inner,
            text="🔄  Atualizar",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=C_ACCENT,
            hover_color="#4f46e5",
            corner_radius=10,
            height=38,
            command=self.refresh,
        )
        self._refresh_btn.pack(side="right")

        # Barra de filtros
        filter_bar = ctk.CTkFrame(self, fg_color=C_SURFACE, corner_radius=0, height=60)
        filter_bar.pack(fill="x")
        filter_bar.pack_propagate(False)

        f_inner = ctk.CTkFrame(filter_bar, fg_color="transparent")
        f_inner.pack(fill="both", expand=True, padx=24, pady=10)

        ctk.CTkLabel(
            f_inner,
            text="Filtro:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=C_TEXT_MUTED,
        ).pack(side="left", padx=(0, 12))

        self._seg_btn = ctk.CTkSegmentedButton(
            f_inner,
            values=["📊  Todas as Receitas", "✅  Apenas Completas"],
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=C_SURFACE2,
            selected_color=C_ACCENT,
            selected_hover_color="#4f46e5",
            unselected_color=C_SURFACE2,
            unselected_hover_color=C_BORDER,
            text_color=C_TEXT,
            text_color_disabled=C_TEXT_MUTED,
            corner_radius=8,
            command=self._on_filter_change,
        )
        self._seg_btn.pack(side="left")
        self._seg_btn.set("📊  Todas as Receitas")

        # Contador de resultados
        self._result_label = ctk.CTkLabel(
            f_inner,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=C_TEXT_MUTED,
        )
        self._result_label.pack(side="right")

        # Área principal (scrollable)
        self._scroll = ctk.CTkScrollableFrame(
            self,
            fg_color=C_BG,
            scrollbar_button_color=C_SURFACE2,
            scrollbar_button_hover_color=C_ACCENT,
        )
        self._scroll.pack(fill="both", expand=True)

        # Render estado inicial
        self._render_empty_state("Clica em «Atualizar» para ver as sugestões\ncom base na tua despensa.")

    # ── Dados ────────────────────────────────────────────────────────────

    def refresh(self):
        """Recarrega sugestões com base na despensa atual."""
        self._refresh_btn.configure(state="disabled", text="⏳  A carregar...")
        self.after(50, self._do_refresh)

    def _do_refresh(self):
        try:
            pantry = self.get_pantry_items()
            only_complete = self._seg_btn.get() == "✅  Apenas Completas"
            self._suggestions = recipe_service.get_suggestions(pantry, only_complete=only_complete)
            self._render_suggestions()
        except Exception as e:
            self._render_empty_state(f"Erro ao carregar receitas:\n{e}")
        finally:
            self._refresh_btn.configure(state="normal", text="🔄  Atualizar")

    def _on_filter_change(self, _):
        self.refresh()

    # ── Renderização ─────────────────────────────────────────────────────

    def _clear_scroll(self):
        for w in self._scroll.winfo_children():
            w.destroy()

    def _render_empty_state(self, message: str):
        self._clear_scroll()
        self._result_label.configure(text="")
        ctk.CTkLabel(
            self._scroll,
            text=f"🍽️\n\n{message}",
            font=ctk.CTkFont(size=15),
            text_color=C_TEXT_MUTED,
            justify="center",
        ).pack(expand=True, pady=80)

    def _render_suggestions(self):
        self._clear_scroll()

        count = len(self._suggestions)
        self._result_label.configure(
            text=f"{count} receita{'s' if count != 1 else ''} encontrada{'s' if count != 1 else ''}"
        )

        if count == 0:
            pantry = self.get_pantry_items()
            if not pantry:
                self._render_empty_state(
                    "A tua despensa está vazia.\nAdiciona ingredientes para ver sugestões!"
                )
            else:
                self._render_empty_state(
                    "Nenhuma receita compatível com a tua despensa.\nTenta adicionar mais ingredientes!"
                )
            return

        # Padding top
        ctk.CTkFrame(self._scroll, fg_color="transparent", height=8).pack()

        for suggestion in self._suggestions:
            self._render_recipe_card(suggestion)

        # Padding bottom
        ctk.CTkFrame(self._scroll, fg_color="transparent", height=16).pack()

    def _render_recipe_card(self, s: RecipeSuggestion):
        """Renderiza um card de receita com barra de progresso e informações."""
        card = ctk.CTkFrame(
            self._scroll,
            fg_color=C_SURFACE,
            corner_radius=14,
        )
        card.pack(fill="x", padx=20, pady=6)

        # ── Linha superior ──────────────────────────────────────────────
        top_row = ctk.CTkFrame(card, fg_color="transparent")
        top_row.pack(fill="x", padx=16, pady=(14, 4))

        # Emoji da categoria
        ctk.CTkLabel(
            top_row,
            text=s.recipe.category_emoji,
            font=ctk.CTkFont(size=26),
            text_color=C_TEXT,
            width=40,
        ).pack(side="left", padx=(0, 10))

        # Título e categoria
        info = ctk.CTkFrame(top_row, fg_color="transparent")
        info.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(
            info,
            text=s.recipe.title,
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=C_TEXT,
            anchor="w",
        ).pack(fill="x")

        meta_row = ctk.CTkFrame(info, fg_color="transparent")
        meta_row.pack(fill="x")

        for chip_text, chip_color in [
            (s.recipe.category, C_TEXT_MUTED),
            (f"{s.recipe.difficulty_emoji} {s.recipe.difficulty}", None),
            (f"⏰ {s.recipe.total_time_display}", None),
            (f"👥 {s.recipe.servings} porções", None),
        ]:
            ctk.CTkLabel(
                meta_row,
                text=chip_text,
                font=ctk.CTkFont(size=11),
                text_color=chip_color or C_TEXT_MUTED,
            ).pack(side="left", padx=(0, 12))

        # Botão Ver Receita
        ctk.CTkButton(
            top_row,
            text="Ver Receita →",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=C_ACCENT,
            hover_color="#4f46e5",
            text_color="white",
            corner_radius=8,
            width=110,
            height=34,
            command=lambda sg=s: self._open_detail(sg),
        ).pack(side="right", padx=(12, 0))

        # ── Barra de compatibilidade ─────────────────────────────────────
        pct = s.compatibility_pct
        bar_color = s.compatibility_color

        compat_frame = ctk.CTkFrame(card, fg_color="transparent")
        compat_frame.pack(fill="x", padx=16, pady=(4, 4))

        # Texto de compatibilidade
        label_row = ctk.CTkFrame(compat_frame, fg_color="transparent")
        label_row.pack(fill="x")

        ctk.CTkLabel(
            label_row,
            text=f"{'✅ Completa!' if s.is_complete else f'🧩 {pct:.0f}% compatível'}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=bar_color,
            anchor="w",
        ).pack(side="left")

        avail_count = len(s.available_ingredients)
        total_count = len(s.recipe.required_ingredients)
        ctk.CTkLabel(
            label_row,
            text=f"{avail_count}/{total_count} ingredientes disponíveis",
            font=ctk.CTkFont(size=11),
            text_color=C_TEXT_MUTED,
            anchor="e",
        ).pack(side="right")

        # Barra de progresso
        bar = ctk.CTkProgressBar(
            compat_frame,
            height=8,
            corner_radius=4,
            progress_color=bar_color,
            fg_color=C_SURFACE2,
        )
        bar.pack(fill="x", pady=(4, 0))
        bar.set(min(pct / 100, 1.0))

        # ── Ingredientes em falta ────────────────────────────────────────
        if s.missing_ingredients:
            missing_frame = ctk.CTkFrame(card, fg_color=C_SURFACE2, corner_radius=8)
            missing_frame.pack(fill="x", padx=16, pady=(6, 12))

            missing_inner = ctk.CTkFrame(missing_frame, fg_color="transparent")
            missing_inner.pack(fill="x", padx=12, pady=8)

            ctk.CTkLabel(
                missing_inner,
                text="❌ Faltam: ",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=C_DANGER,
            ).pack(side="left")

            missing_text = ",  ".join(s.missing_ingredients[:5])
            if len(s.missing_ingredients) > 5:
                missing_text += f" ... +{len(s.missing_ingredients) - 5} mais"

            ctk.CTkLabel(
                missing_inner,
                text=missing_text,
                font=ctk.CTkFont(size=11),
                text_color=C_TEXT_MUTED,
                wraplength=550,
                anchor="w",
            ).pack(side="left", fill="x", expand=True)
        else:
            ctk.CTkFrame(card, fg_color="transparent", height=8).pack()

    def _open_detail(self, suggestion: RecipeSuggestion):
        RecipeDetailWindow(self, suggestion)
