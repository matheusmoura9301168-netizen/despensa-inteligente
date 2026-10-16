"""
Aba de gestão da despensa.
Permite adicionar, editar, remover e pesquisar ingredientes.
"""
import customtkinter as ctk
from tkinter import messagebox
from typing import Callable, List, Optional

from app.models.ingredient import PantryItem
from app.services import pantry_service

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

UNITS = [
    "g", "kg", "ml", "l",
    "unidades", "colheres de sopa", "colheres de chá",
    "xícaras", "dentes", "fatias", "ramo", "folhas",
    "pitada", "pacote",
]


class PantryTab(ctk.CTkFrame):
    """Aba principal da despensa."""

    def __init__(self, parent, on_change: Optional[Callable] = None):
        super().__init__(parent, fg_color=C_BG, corner_radius=0)
        self.on_change = on_change
        self._items: List[PantryItem] = []
        self._search_var = ctk.StringVar()
        self._search_var.trace_add("write", self._on_search_change)
        self._build_ui()
        self.refresh()

    # ── Construção da UI ────────────────────────────────────────────────

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color=C_SURFACE, corner_radius=0, height=80)
        header.pack(fill="x")
        header.pack_propagate(False)

        header_inner = ctk.CTkFrame(header, fg_color="transparent")
        header_inner.pack(fill="both", expand=True, padx=24, pady=16)

        ctk.CTkLabel(
            header_inner,
            text="🥕  Minha Despensa",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=C_TEXT,
            anchor="w",
        ).pack(side="left")

        # Botão Adicionar
        self._add_btn = ctk.CTkButton(
            header_inner,
            text="＋  Adicionar Ingrediente",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=C_ACCENT,
            hover_color="#4f46e5",
            corner_radius=10,
            height=38,
            command=self._open_add_dialog,
        )
        self._add_btn.pack(side="right")

        # Barra de pesquisa
        search_frame = ctk.CTkFrame(self, fg_color=C_SURFACE, corner_radius=0, height=56)
        search_frame.pack(fill="x")
        search_frame.pack_propagate(False)

        search_inner = ctk.CTkFrame(search_frame, fg_color="transparent")
        search_inner.pack(fill="both", expand=True, padx=24, pady=10)

        ctk.CTkLabel(
            search_inner,
            text="🔍",
            font=ctk.CTkFont(size=16),
            text_color=C_TEXT_MUTED,
        ).pack(side="left", padx=(0, 8))

        self._search_entry = ctk.CTkEntry(
            search_inner,
            textvariable=self._search_var,
            placeholder_text="Pesquisar ingrediente...",
            font=ctk.CTkFont(size=13),
            fg_color=C_SURFACE2,
            border_color=C_BORDER,
            text_color=C_TEXT,
            placeholder_text_color=C_TEXT_MUTED,
            corner_radius=8,
            height=36,
        )
        self._search_entry.pack(side="left", fill="x", expand=True)

        # Contador
        self._count_label = ctk.CTkLabel(
            search_inner,
            text="0 ingredientes",
            font=ctk.CTkFont(size=12),
            text_color=C_TEXT_MUTED,
        )
        self._count_label.pack(side="right", padx=(12, 0))

        # Lista (scrollable)
        self._list_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=C_BG,
            scrollbar_button_color=C_SURFACE2,
            scrollbar_button_hover_color=C_ACCENT,
        )
        self._list_frame.pack(fill="both", expand=True, padx=0, pady=0)

        # Estado vazio
        self._empty_label = ctk.CTkLabel(
            self._list_frame,
            text="🧺\n\nA tua despensa está vazia.\nClica em «Adicionar Ingrediente» para começar!",
            font=ctk.CTkFont(size=15),
            text_color=C_TEXT_MUTED,
            justify="center",
        )

    # ── Dados ────────────────────────────────────────────────────────────

    def refresh(self):
        """Recarrega a lista de ingredientes da BD."""
        query = self._search_var.get().strip()
        if query:
            self._items = pantry_service.search_items(query)
        else:
            self._items = pantry_service.get_all_items()
        self._render_list()
        if self.on_change:
            self.on_change()

    def _on_search_change(self, *_):
        self.refresh()

    # ── Renderização ─────────────────────────────────────────────────────

    def _render_list(self):
        """Re-renderiza a lista de ingredientes."""
        for widget in self._list_frame.winfo_children():
            widget.destroy()

        self._count_label.configure(
            text=f"{len(self._items)} ingrediente{'s' if len(self._items) != 1 else ''}"
        )

        if not self._items:
            self._empty_label = ctk.CTkLabel(
                self._list_frame,
                text="🧺\n\nA tua despensa está vazia.\nClica em «Adicionar Ingrediente» para começar!",
                font=ctk.CTkFont(size=15),
                text_color=C_TEXT_MUTED,
                justify="center",
            )
            self._empty_label.pack(expand=True, pady=80)
            return

        for i, item in enumerate(self._items):
            self._render_item_row(item, i)

    def _render_item_row(self, item: PantryItem, index: int):
        """Renderiza uma linha de ingrediente."""
        bg = C_SURFACE if index % 2 == 0 else C_SURFACE2

        row = ctk.CTkFrame(self._list_frame, fg_color=bg, corner_radius=10, height=56)
        row.pack(fill="x", padx=20, pady=(4, 0))
        row.pack_propagate(False)

        inner = ctk.CTkFrame(row, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=16)

        # Ícone
        ctk.CTkLabel(
            inner,
            text="🧂",
            font=ctk.CTkFont(size=18),
            text_color=C_ACCENT,
            width=32,
        ).pack(side="left", pady=12)

        # Nome
        ctk.CTkLabel(
            inner,
            text=item.name,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=C_TEXT,
            anchor="w",
        ).pack(side="left", fill="x", expand=True, padx=(8, 0), pady=12)

        # Quantidade + unidade
        qty_text = item.display_quantity
        ctk.CTkLabel(
            inner,
            text=qty_text,
            font=ctk.CTkFont(size=13),
            text_color=C_TEXT_MUTED,
            width=120,
            anchor="e",
        ).pack(side="left", pady=12)

        # Botão Editar
        edit_btn = ctk.CTkButton(
            inner,
            text="✏️",
            width=36,
            height=32,
            corner_radius=8,
            fg_color=C_SURFACE2 if index % 2 == 0 else C_SURFACE,
            hover_color=C_ACCENT,
            text_color=C_TEXT,
            font=ctk.CTkFont(size=14),
            command=lambda it=item: self._open_edit_dialog(it),
        )
        edit_btn.pack(side="left", padx=(8, 4), pady=12)

        # Botão Remover
        del_btn = ctk.CTkButton(
            inner,
            text="🗑️",
            width=36,
            height=32,
            corner_radius=8,
            fg_color=C_SURFACE2 if index % 2 == 0 else C_SURFACE,
            hover_color=C_DANGER,
            text_color=C_TEXT,
            font=ctk.CTkFont(size=14),
            command=lambda it=item: self._confirm_delete(it),
        )
        del_btn.pack(side="left", pady=12)

    # ── Diálogos ─────────────────────────────────────────────────────────

    def _open_add_dialog(self):
        IngredientDialog(self, title="Adicionar Ingrediente", on_save=self._save_new)

    def _open_edit_dialog(self, item: PantryItem):
        IngredientDialog(
            self,
            title="Editar Ingrediente",
            item=item,
            on_save=lambda name, qty, unit: self._save_edit(item.id, name, qty, unit),
        )

    def _save_new(self, name: str, quantity: float, unit: str):
        if pantry_service.item_exists(name):
            messagebox.showwarning("Duplicado", f"'{name}' já existe na despensa.")
            return
        pantry_service.add_item(name, quantity, unit)
        self.refresh()

    def _save_edit(self, item_id: int, name: str, quantity: float, unit: str):
        if pantry_service.item_exists(name, exclude_id=item_id):
            messagebox.showwarning("Duplicado", f"'{name}' já existe na despensa.")
            return
        pantry_service.update_item(item_id, name, quantity, unit)
        self.refresh()

    def _confirm_delete(self, item: PantryItem):
        if messagebox.askyesno(
            "Remover Ingrediente",
            f"Tens a certeza que queres remover «{item.name}»?",
        ):
            pantry_service.delete_item(item.id)
            self.refresh()

    def get_items(self) -> List[PantryItem]:
        return pantry_service.get_all_items()


# ── Diálogo de Adicionar/Editar ──────────────────────────────────────────────

class IngredientDialog(ctk.CTkToplevel):
    """Modal para adicionar ou editar um ingrediente da despensa."""

    def __init__(self, parent, title: str, on_save: Callable,
                 item: Optional[PantryItem] = None):
        super().__init__(parent)
        self.on_save = on_save
        self.item = item

        self.title(title)
        self.geometry("420x320")
        self.resizable(False, False)
        self.configure(fg_color=C_BG)
        self.grab_set()
        self.focus_set()
        self.after(10, self._center)
        self._build_ui()

    def _center(self):
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - 420) // 2
        y = (sh - 320) // 2
        self.geometry(f"420x320+{x}+{y}")

    def _build_ui(self):
        # Título
        ctk.CTkLabel(
            self,
            text="🧂  " + self.title(),
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color=C_TEXT,
            anchor="w",
        ).pack(fill="x", padx=24, pady=(20, 16))

        form = ctk.CTkFrame(self, fg_color=C_SURFACE, corner_radius=12)
        form.pack(fill="x", padx=20)

        # Nome
        self._add_field(form, "Nome do Ingrediente", 0)
        self._name_entry = ctk.CTkEntry(
            form,
            placeholder_text="Ex: Ovos, Farinha, Tomate...",
            font=ctk.CTkFont(size=13),
            fg_color=C_SURFACE2,
            border_color=C_BORDER,
            text_color=C_TEXT,
            placeholder_text_color=C_TEXT_MUTED,
            corner_radius=8,
            height=38,
        )
        self._name_entry.grid(row=1, column=0, columnspan=2, sticky="ew", padx=16, pady=(0, 12))

        # Quantidade
        self._add_field(form, "Quantidade", 2)
        self._qty_entry = ctk.CTkEntry(
            form,
            placeholder_text="Ex: 500",
            font=ctk.CTkFont(size=13),
            fg_color=C_SURFACE2,
            border_color=C_BORDER,
            text_color=C_TEXT,
            placeholder_text_color=C_TEXT_MUTED,
            corner_radius=8,
            height=38,
        )
        self._qty_entry.grid(row=3, column=0, sticky="ew", padx=(16, 4), pady=(0, 12))

        # Unidade
        self._add_field(form, "Unidade", 2, col=1, label_text="Unidade")
        self._unit_combo = ctk.CTkComboBox(
            form,
            values=UNITS,
            font=ctk.CTkFont(size=13),
            fg_color=C_SURFACE2,
            border_color=C_BORDER,
            text_color=C_TEXT,
            button_color=C_ACCENT,
            button_hover_color="#4f46e5",
            dropdown_fg_color=C_SURFACE,
            dropdown_text_color=C_TEXT,
            dropdown_hover_color=C_SURFACE2,
            corner_radius=8,
            height=38,
        )
        self._unit_combo.grid(row=3, column=1, sticky="ew", padx=(4, 16), pady=(0, 12))

        form.columnconfigure(0, weight=1)
        form.columnconfigure(1, weight=1)

        # Preencher se editando
        if self.item:
            self._name_entry.insert(0, self.item.name)
            qty_val = int(self.item.quantity) if self.item.quantity == int(self.item.quantity) else self.item.quantity
            self._qty_entry.insert(0, str(qty_val))
            self._unit_combo.set(self.item.unit)
        else:
            self._unit_combo.set("unidades")

        # Botões
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=16)

        ctk.CTkButton(
            btn_row,
            text="Cancelar",
            font=ctk.CTkFont(size=13),
            fg_color=C_SURFACE,
            hover_color=C_SURFACE2,
            text_color=C_TEXT_MUTED,
            corner_radius=8,
            height=38,
            command=self.destroy,
        ).pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(
            btn_row,
            text="✔  Guardar",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=C_ACCENT,
            hover_color="#4f46e5",
            text_color="white",
            corner_radius=8,
            height=38,
            command=self._submit,
        ).pack(side="right", fill="x", expand=True, padx=(8, 0))

    def _add_field(self, parent, text: str, row: int, col: int = 0, label_text: str = None):
        ctk.CTkLabel(
            parent,
            text=label_text or text,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=C_TEXT_MUTED,
            anchor="w",
        ).grid(row=row, column=col, sticky="w", padx=16,
               pady=(12, 4) if row == 0 else (0, 4))

    def _submit(self):
        name = self._name_entry.get().strip()
        qty_str = self._qty_entry.get().strip()
        unit = self._unit_combo.get().strip()

        if not name:
            messagebox.showerror("Erro", "O nome do ingrediente não pode estar vazio.", parent=self)
            return

        try:
            qty = float(qty_str.replace(",", "."))
            if qty <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Erro", "Quantidade inválida. Insere um número positivo.", parent=self)
            return

        if not unit:
            messagebox.showerror("Erro", "Seleciona uma unidade.", parent=self)
            return

        self.on_save(name, qty, unit)
        self.destroy()
