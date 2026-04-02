"""
ui.py — Interface gráfica premium do 2DFIX usando CustomTkinter.
"""

import customtkinter as ctk
from tkinter import filedialog
import os
import sys
import platform
import subprocess
import threading
import time
import webbrowser

from processor import processar_arquivo


def _criar_icone_github(size: int, cor: tuple):
    """Renderiza o GitHub Mark (octocat simplificado) via Pillow."""
    from PIL import Image, ImageDraw
    scale = 4
    s = size * scale
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = (cor[0], cor[1], cor[2], 255)
    # Corpo principal (círculo)
    d.ellipse([int(s*0.04), int(s*0.18), int(s*0.96), int(s*0.96)], fill=c)
    # Orelha esquerda
    d.polygon([
        (int(s*0.04), int(s*0.44)),
        (int(s*0.30), int(s*0.44)),
        (int(s*0.22), int(s*0.02)),
    ], fill=c)
    # Orelha direita
    d.polygon([
        (int(s*0.70), int(s*0.44)),
        (int(s*0.96), int(s*0.44)),
        (int(s*0.78), int(s*0.02)),
    ], fill=c)
    resample = getattr(Image, "LANCZOS", getattr(Image, "ANTIALIAS", Image.BICUBIC))
    return img.resize((size, size), resample)


def _resource_path(relative: str) -> str:
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative)


def _open_file(path: str):
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


def _open_folder(path: str):
    folder = os.path.dirname(path)
    if platform.system() == "Windows":
        os.startfile(folder)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", folder])
    else:
        subprocess.Popen(["xdg-open", folder])


# ── Themes ───────────────────────────────────────────────────────────────────
ACCENT = "#1E90FF"
ACCENT_HOVER = "#1565C0"
SUCCESS = "#2ECC71"
ERROR = "#E74C3C"
GITHUB_URL = "https://github.com/alanaraujo-bit/2dfix"

THEMES = {
    "dark": {
        "bg": "#0E1117",
        "card": "#161B22",
        "text": "#E6EDF3",
        "text_secondary": "#8B949E",
        "input_bg": "#0D1117",
        "input_border": "#30363D",
        "border": "#21262D",
        "disabled_btn": "#21262D",
        "hover_btn": "#1C2128",
    },
    "light": {
        "bg": "#F5F7FA",
        "card": "#FFFFFF",
        "text": "#0A2540",
        "text_secondary": "#57606A",
        "input_bg": "#F6F8FA",
        "input_border": "#D0D7DE",
        "border": "#D8DEE4",
        "disabled_btn": "#D0D7DE",
        "hover_btn": "#E8ECF0",
    },
}

# ── Fonts ────────────────────────────────────────────────────────────────────
FONT_BRAND = ("Segoe UI", 24, "bold")
FONT_SUBTITLE = ("Segoe UI", 11)
FONT_LABEL = ("Segoe UI", 11)
FONT_INPUT = ("Segoe UI", 12)
FONT_BUTTON = ("Segoe UI", 13, "bold")
FONT_SMALL = ("Segoe UI", 11)
FONT_RESULT = ("Segoe UI", 13)

# ── Dimensions ───────────────────────────────────────────────────────────────
WIN_W = 860
WIN_H = 520
CARD_R = 14
BTN_R = 10
INPUT_H = 40

class App2DFix(ctk.CTk):

    def __init__(self):
        super().__init__()

        self._theme = "dark"
        self._t = THEMES[self._theme]

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("2DFIX")
        self.geometry(f"{WIN_W}x{WIN_H}")
        self.minsize(720, 460)
        self.resizable(True, True)
        self.configure(fg_color=self._t["bg"])

        try:
            self.iconbitmap(_resource_path("icon.ico"))
        except Exception:
            pass

        self._last_output_path: str | None = None
        self._themed_widgets: list[tuple] = []
        self._sub_rows: list[dict] = []  # dynamic substitution rows
        self._theme_anim_gen: int = 0   # incremented on every toggle to cancel in-flight animations

        self._build_ui()
        self._atualizar_estado_botao()

    # ── Build UI ─────────────────────────────────────────────────────────────
    def _build_ui(self):
        t = self._t

        self._root_frame = ctk.CTkFrame(self, fg_color=t["bg"])
        self._root_frame.pack(fill="both", expand=True)
        self._reg("frame_bg", self._root_frame)

        content = ctk.CTkFrame(self._root_frame, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=48, pady=36)

        # ── Header row ───────────────────────────────────────────────────
        header = ctk.CTkFrame(content, fg_color="transparent")
        header.pack(fill="x", pady=(0, 24))
        header.grid_columnconfigure(0, weight=1)

        title_block = ctk.CTkFrame(header, fg_color="transparent")
        title_block.grid(row=0, column=0, sticky="w")

        self._lbl_brand = ctk.CTkLabel(
            title_block, text="2DFIX", font=FONT_BRAND, text_color=ACCENT,
        )
        self._lbl_brand.pack(side="left")

        self._lbl_subtitle = ctk.CTkLabel(
            title_block, text="  Correção Inteligente de Dados",
            font=FONT_SUBTITLE, text_color=t["text_secondary"],
        )
        self._lbl_subtitle.pack(side="left", padx=(8, 0), pady=(4, 0))
        self._reg("text_secondary", self._lbl_subtitle)

        icon = "☀" if self._theme == "dark" else "☾"
        self._theme_btn = ctk.CTkButton(
            header, text=icon, width=36, height=36,
            font=("Segoe UI", 16), fg_color="transparent",
            hover_color=t["border"], corner_radius=8,
            text_color=t["text_secondary"],
            command=self._toggle_theme,
        )
        self._theme_btn.grid(row=0, column=2, sticky="ne")
        self._reg("theme_btn", self._theme_btn)

        # Ícone GitHub (criado aqui onde o CTk já está inicializado)
        _ic_dark = _criar_icone_github(16, (139, 148, 158))
        _ic_light = _criar_icone_github(16, (87, 96, 106))
        self._github_icon = ctk.CTkImage(
            light_image=_ic_light, dark_image=_ic_dark, size=(16, 16)
        )

        self._github_btn = ctk.CTkButton(
            header, image=self._github_icon, text="", width=36, height=36,
            fg_color="transparent",
            hover_color=t["border"], corner_radius=8,
            command=self._abrir_github,
        )
        self._github_btn.grid(row=0, column=1, sticky="ne", padx=(0, 4))
        self._reg("github_btn", self._github_btn)

        # Separator
        self._sep = ctk.CTkFrame(content, fg_color=t["border"], height=1)
        self._sep.pack(fill="x", pady=(0, 28))
        self._reg("border_line", self._sep)

        # ── Arquivos (dois campos lado a lado) ───────────────────────────
        files_frame = ctk.CTkFrame(content, fg_color="transparent")
        files_frame.pack(fill="x", pady=(0, 16))
        files_frame.grid_columnconfigure(0, weight=1)
        files_frame.grid_columnconfigure(1, weight=1)

        files_left = ctk.CTkFrame(files_frame, fg_color="transparent")
        files_left.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self._make_file_field(files_left, "Arquivo de entrada", "var_entrada",
                              "Selecione o arquivo .txt", self._selecionar_entrada)

        files_right = ctk.CTkFrame(files_frame, fg_color="transparent")
        files_right.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        self._make_file_field(files_right, "Arquivo de saída", "var_saida",
                              "Local para salvar o arquivo corrigido", self._selecionar_saida)

        # ── Label da seção ────────────────────────────────────────────────
        lbl_subs = ctk.CTkLabel(
            content, text="Substituições", font=FONT_LABEL,
            text_color=t["text_secondary"],
        )
        lbl_subs.pack(anchor="w", pady=(0, 6))
        self._reg("text_secondary", lbl_subs)

        # ── Substituições — área com scroll ───────────────────────────────
        self._subs_scroll = ctk.CTkScrollableFrame(
            content,
            fg_color=t["input_bg"],
            scrollbar_button_color=t["border"],
            scrollbar_button_hover_color=t["input_border"],
            corner_radius=8,
            border_width=1,
            border_color=t["input_border"],
        )
        self._subs_scroll.pack(fill="both", expand=True)
        self._subs_container = self._subs_scroll
        self._reg("subs_scroll", self._subs_scroll)

        self._add_sub_row()

        self._btn_add_sub = ctk.CTkButton(
            content, text="＋  Adicionar substituição", height=32,
            font=FONT_SMALL, fg_color="transparent",
            border_color=t["border"], border_width=1,
            hover_color=t["border"], corner_radius=BTN_R,
            text_color=ACCENT, command=self._add_sub_row,
        )
        self._btn_add_sub.pack(fill="x", pady=(6, 0))
        self._reg("add_sub_btn", self._btn_add_sub)

        # ── Bottom area ──────────────────────────────────────────────────
        bottom = ctk.CTkFrame(content, fg_color="transparent")
        bottom.pack(fill="x", pady=(20, 0))

        self.btn_corrigir = ctk.CTkButton(
            bottom, text="Corrigir Arquivo", height=46,
            font=FONT_BUTTON, fg_color=ACCENT, hover_color=ACCENT_HOVER,
            corner_radius=BTN_R, command=self._executar, state="disabled",
        )
        self.btn_corrigir.pack(fill="x")

        # Progress bar (hidden)
        self._progress = ctk.CTkProgressBar(
            bottom, mode="indeterminate", height=3,
            progress_color=ACCENT, fg_color=t["border"],
        )
        self._reg("progress_bg", self._progress)

        # Result area (hidden)
        self._result_frame = ctk.CTkFrame(bottom, fg_color="transparent")

        self._lbl_result = ctk.CTkLabel(
            self._result_frame, text="", font=FONT_RESULT,
            text_color=SUCCESS, justify="center",
        )
        self._lbl_result.pack(fill="x", pady=(0, 10))

        btn_row = ctk.CTkFrame(self._result_frame, fg_color="transparent")
        btn_row.pack(anchor="center")

        self._btn_open_file = ctk.CTkButton(
            btn_row, text="Abrir arquivo", height=36,
            font=FONT_SMALL, fg_color="transparent",
            border_color=ACCENT, border_width=1,
            hover_color=t["border"], corner_radius=BTN_R,
            text_color=ACCENT, command=self._abrir_arquivo,
        )
        self._btn_open_file.pack(side="left", expand=True, fill="x", padx=(0, 6))
        self._reg("outline_btn", self._btn_open_file)

        self._btn_open_folder = ctk.CTkButton(
            btn_row, text="Abrir pasta", height=36,
            font=FONT_SMALL, fg_color="transparent",
            border_color=ACCENT, border_width=1,
            hover_color=t["border"], corner_radius=BTN_R,
            text_color=ACCENT, command=self._abrir_pasta,
        )
        self._btn_open_folder.pack(side="left", expand=True, fill="x", padx=(6, 0))
        self._reg("outline_btn", self._btn_open_folder)

        # Error label (hidden)
        self._lbl_error = ctk.CTkLabel(
            bottom, text="", font=FONT_SMALL,
            text_color=ERROR, wraplength=700, justify="left",
        )

    # ── Widget registration for theme transitions ────────────────────────────
    def _reg(self, role: str, widget):
        self._themed_widgets.append((role, widget))

    # ── Dynamic substitution rows ───────────────────────────────────────────
    def _add_sub_row(self):
        t = self._t
        idx = len(self._sub_rows) + 1

        row_frame = ctk.CTkFrame(self._subs_container, fg_color="transparent")
        row_frame.pack(fill="x", pady=(0, 10))

        # Header with label and remove button
        header = ctk.CTkFrame(row_frame, fg_color="transparent")
        header.pack(fill="x", pady=(0, 4))

        lbl = ctk.CTkLabel(header, text=f"Substituição {idx}", font=FONT_LABEL,
                            text_color=t["text_secondary"])
        lbl.pack(side="left")
        self._reg("text_secondary", lbl)

        # Remove button (hidden on first row)
        btn_rm = ctk.CTkButton(
            header, text="✕", width=26, height=26,
            font=("Segoe UI", 12), fg_color="transparent",
            hover_color=t["border"], corner_radius=6,
            text_color=ERROR, command=None,
        )
        self._reg("rm_btn", btn_rm)

        var_old = ctk.StringVar()
        var_new = ctk.StringVar()
        var_old.trace_add("write", lambda *_: self._atualizar_estado_botao())
        var_new.trace_add("write", lambda *_: self._atualizar_estado_botao())

        e_old = ctk.CTkEntry(
            row_frame, textvariable=var_old, height=INPUT_H, font=FONT_INPUT,
            placeholder_text="Sequência incorreta",
            fg_color=t["input_bg"], border_color=t["input_border"],
            border_width=1, corner_radius=8, text_color=t["text"],
        )
        e_old.pack(fill="x", pady=(0, 4))
        self._reg("entry", e_old)

        e_new = ctk.CTkEntry(
            row_frame, textvariable=var_new, height=INPUT_H, font=FONT_INPUT,
            placeholder_text="Sequência correta",
            fg_color=t["input_bg"], border_color=t["input_border"],
            border_width=1, corner_radius=8, text_color=t["text"],
        )
        e_new.pack(fill="x")
        self._reg("entry", e_new)

        row_data = {
            "frame": row_frame, "var_old": var_old, "var_new": var_new,
            "label": lbl, "btn_rm": btn_rm,
        }
        self._sub_rows.append(row_data)

        btn_rm.configure(command=lambda rd=row_data: self._remove_sub_row(rd))
        self._refresh_sub_labels()
        self._atualizar_estado_botao()

    def _remove_sub_row(self, row_data: dict):
        if len(self._sub_rows) <= 1:
            return
        row_data["frame"].pack_forget()
        row_data["frame"].destroy()
        self._sub_rows.remove(row_data)
        self._refresh_sub_labels()
        self._atualizar_estado_botao()

    def _refresh_sub_labels(self):
        for i, rd in enumerate(self._sub_rows, 1):
            rd["label"].configure(text=f"Substituição {i}")
            if len(self._sub_rows) > 1:
                rd["btn_rm"].pack(side="right")
            else:
                rd["btn_rm"].pack_forget()

    # ── Field builders ───────────────────────────────────────────────────────
    def _make_file_field(self, parent, label_text, var_name, placeholder, command):
        t = self._t

        lbl = ctk.CTkLabel(parent, text=label_text, font=FONT_LABEL,
                            text_color=t["text_secondary"])
        lbl.pack(anchor="w", pady=(0, 4))
        self._reg("text_secondary", lbl)

        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=(0, 16))
        row.grid_columnconfigure(0, weight=1)

        var = ctk.StringVar()
        setattr(self, var_name, var)
        var.trace_add("write", lambda *_: self._atualizar_estado_botao())

        entry = ctk.CTkEntry(
            row, textvariable=var, height=INPUT_H, font=FONT_INPUT,
            placeholder_text=placeholder,
            fg_color=t["input_bg"], border_color=t["input_border"],
            border_width=1, corner_radius=8, text_color=t["text"],
        )
        entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self._reg("entry", entry)

        btn = ctk.CTkButton(
            row, text="…", width=42, height=INPUT_H,
            font=("Segoe UI", 14), fg_color=t["input_bg"],
            hover_color=t["border"], corner_radius=8,
            border_color=t["input_border"], border_width=1,
            text_color=t["text_secondary"], command=command,
        )
        btn.grid(row=0, column=1)
        self._reg("browse_btn", btn)

    def _make_text_field(self, parent, label_text, var_name, placeholder):
        t = self._t

        lbl = ctk.CTkLabel(parent, text=label_text, font=FONT_LABEL,
                            text_color=t["text_secondary"])
        lbl.pack(anchor="w", pady=(0, 4))
        self._reg("text_secondary", lbl)

        var = ctk.StringVar()
        setattr(self, var_name, var)
        var.trace_add("write", lambda *_: self._atualizar_estado_botao())

        entry = ctk.CTkEntry(
            parent, textvariable=var, height=INPUT_H, font=FONT_INPUT,
            placeholder_text=placeholder,
            fg_color=t["input_bg"], border_color=t["input_border"],
            border_width=1, corner_radius=8, text_color=t["text"],
        )
        entry.pack(fill="x", pady=(0, 16))
        self._reg("entry", entry)

    # ── File selection ───────────────────────────────────────────────────────
    def _selecionar_entrada(self):
        caminho = filedialog.askopenfilename(
            title="Selecionar arquivo de entrada",
            filetypes=[("Arquivos de texto", "*.txt"), ("Todos os arquivos", "*.*")],
        )
        if caminho:
            self.var_entrada.set(caminho)
            if not self.var_saida.get():
                base, ext = os.path.splitext(caminho)
                self.var_saida.set(f"{base}_corrigido{ext}")

    def _selecionar_saida(self):
        caminho = filedialog.asksaveasfilename(
            title="Salvar arquivo corrigido como",
            defaultextension=".txt",
            filetypes=[("Arquivos de texto", "*.txt"), ("Todos os arquivos", "*.*")],
        )
        if caminho:
            self.var_saida.set(caminho)

    # ── Button state ─────────────────────────────────────────────────────────
    def _campos_validos(self) -> bool:
        if not self.var_entrada.get().strip() or not self.var_saida.get().strip():
            return False
        for rd in self._sub_rows:
            if not rd["var_old"].get().strip() or not rd["var_new"].get().strip():
                return False
        return True

    def _atualizar_estado_botao(self, *_args):
        if not hasattr(self, "btn_corrigir"):
            return
        t = self._t
        if self._campos_validos():
            self.btn_corrigir.configure(state="normal", fg_color=ACCENT)
        else:
            self.btn_corrigir.configure(state="disabled", fg_color=t["disabled_btn"])

    # ── Execution ────────────────────────────────────────────────────────────
    def _executar(self):
        self._hide_results()

        caminho_entrada = self.var_entrada.get().strip()
        caminho_saida = self.var_saida.get().strip()

        if os.path.abspath(caminho_entrada) == os.path.abspath(caminho_saida):
            self._show_error("O arquivo de saída não pode ser o mesmo que o de entrada.")
            return

        if not os.path.isfile(caminho_entrada):
            self._show_error(f"Arquivo não encontrado: {caminho_entrada}")
            return

        mapeamentos = []
        for rd in self._sub_rows:
            old = rd["var_old"].get().strip()
            new = rd["var_new"].get().strip()
            if old and new:
                mapeamentos.append((old, new))

        if not mapeamentos:
            self._show_error("Informe ao menos uma substituição.")
            return

        # Auto-rename se o arquivo de saída já existir
        caminho_saida = self._gerar_nome_unico(caminho_saida)
        self.var_saida.set(caminho_saida)

        self.btn_corrigir.configure(state="disabled", text="Processando…", fg_color=self._t["disabled_btn"])
        self._progress.pack(fill="x", pady=(10, 0))
        self._progress.start()
        self._start_time = time.perf_counter()

        threading.Thread(
            target=self._processar_thread,
            args=(caminho_entrada, caminho_saida, mapeamentos),
            daemon=True,
        ).start()

    @staticmethod
    def _gerar_nome_unico(caminho: str) -> str:
        """Se o arquivo já existe, adiciona _1, _2, ... até encontrar um nome livre."""
        if not os.path.exists(caminho):
            return caminho
        base, ext = os.path.splitext(caminho)
        i = 1
        while os.path.exists(f"{base}_{i}{ext}"):
            i += 1
        return f"{base}_{i}{ext}"

    def _processar_thread(self, caminho_entrada, caminho_saida, mapeamentos):
        try:
            resultados = processar_arquivo(caminho_entrada, caminho_saida, mapeamentos)
            elapsed = time.perf_counter() - self._start_time
            self.after(0, self._on_success, resultados, caminho_saida, elapsed)
        except PermissionError:
            self.after(0, self._on_error,
                       "Permissão negada. Verifique se o arquivo não está aberto em outro programa.")
        except ValueError as e:
            self.after(0, self._on_error, str(e))
        except Exception as e:
            self.after(0, self._on_error, f"Erro inesperado: {e}")

    def _finish_progress(self):
        self._progress.stop()
        self._progress.pack_forget()
        self.btn_corrigir.configure(text="Corrigir Arquivo")
        self._atualizar_estado_botao()

    def _on_success(self, resultados: list[dict], caminho_saida: str, elapsed: float = 0):
        self._finish_progress()
        total = sum(r['contagem'] for r in resultados)
        self._last_output_path = caminho_saida

        if total == 0:
            self._show_error("Nenhuma sequência foi encontrada no arquivo.")
            return

        nome_saida = os.path.basename(caminho_saida)

        if elapsed < 1:
            tempo = f"{elapsed * 1000:.0f}ms"
        else:
            tempo = f"{elapsed:.1f}s"

        linhas = [f"✔ Concluído em {tempo}  ·  {total} substituição(ões)"]
        for r in resultados:
            if r['contagem'] > 0:
                linhas.append(f"{r['incorreto']}  →  {r['correto']}  ({r['contagem']}x)")
        linhas.append(f"Salvo em: {nome_saida}")
        resumo = "\n".join(linhas)

        self._lbl_result.configure(text=resumo, text_color=SUCCESS)
        self._result_frame.pack(fill="x", pady=(14, 0))

    def _on_error(self, msg: str):
        self._finish_progress()
        self._show_error(msg)

    # ── Result helpers ───────────────────────────────────────────────────────
    def _hide_results(self):
        self._result_frame.pack_forget()
        self._lbl_error.pack_forget()

    def _show_error(self, msg: str):
        self._lbl_error.configure(text=f"✕  {msg}")
        self._lbl_error.pack(fill="x", pady=(14, 0))

    def _abrir_arquivo(self):
        if self._last_output_path and os.path.isfile(self._last_output_path):
            _open_file(self._last_output_path)

    def _abrir_pasta(self):
        if self._last_output_path:
            _open_folder(self._last_output_path)

    def _abrir_github(self):
        webbrowser.open(GITHUB_URL)

    # ── Theme toggle — animated interpolation ────────────────────────────────

    @staticmethod
    def _lerp_hex(c1: str, c2: str, t: float) -> str:
        """Interpolate between two #RRGGBB hex colors."""
        r = round(int(c1[1:3], 16) + (int(c2[1:3], 16) - int(c1[1:3], 16)) * t)
        g = round(int(c1[3:5], 16) + (int(c2[3:5], 16) - int(c1[3:5], 16)) * t)
        b = round(int(c1[5:7], 16) + (int(c2[5:7], 16) - int(c1[5:7], 16)) * t)
        return f"#{r:02X}{g:02X}{b:02X}"

    @staticmethod
    def _ease_in_out(t: float) -> float:
        """Cubic ease-in-out — smooth start and end."""
        return t * t * (3.0 - 2.0 * t)

    def _apply_theme_colors(self, t: dict):
        """Apply a color dict to all registered widgets without rebuilding."""
        self.configure(fg_color=t["bg"])
        for role, w in self._themed_widgets:
            try:
                if role == "frame_bg":
                    w.configure(fg_color=t["bg"])
                elif role == "text_secondary":
                    w.configure(text_color=t["text_secondary"])
                elif role == "theme_btn":
                    w.configure(hover_color=t["border"], text_color=t["text_secondary"])
                elif role == "border_line":
                    w.configure(fg_color=t["border"])
                elif role == "entry":
                    w.configure(fg_color=t["input_bg"], border_color=t["input_border"], text_color=t["text"])
                elif role == "browse_btn":
                    w.configure(fg_color=t["input_bg"], hover_color=t["border"], border_color=t["input_border"], text_color=t["text_secondary"])
                elif role == "outline_btn":
                    w.configure(hover_color=t["border"])
                elif role == "progress_bg":
                    w.configure(fg_color=t["border"])
                elif role == "add_sub_btn":
                    w.configure(border_color=t["border"], hover_color=t["border"])
                elif role == "rm_btn":
                    w.configure(hover_color=t["border"])
                elif role == "github_btn":
                    w.configure(hover_color=t["border"])
                elif role == "subs_scroll":
                    w.configure(
                        fg_color=t["input_bg"],
                        scrollbar_button_color=t["border"],
                        scrollbar_button_hover_color=t["input_border"],
                        border_color=t["input_border"],
                    )
            except Exception:
                pass

    def _animate_theme(self, t_from: dict, t_to: dict, steps: int = 14, duration_ms: int = 220):
        """Drive a non-blocking color interpolation between two theme palettes."""
        step_ms = max(1, duration_ms // steps)
        gen = self._theme_anim_gen  # snapshot — used to abort if another toggle fires

        def step(i: int):
            if gen != self._theme_anim_gen:
                return  # a newer toggle fired; let it own the animation
            progress = self._ease_in_out(i / steps)
            current = {k: self._lerp_hex(t_from[k], t_to[k], progress) for k in t_to}
            self._apply_theme_colors(current)
            if i < steps:
                self.after(step_ms, lambda: step(i + 1))
            else:
                # Sync CTk's internal mode once — colors already match, no visual change.
                ctk.set_appearance_mode(self._theme)
                self._atualizar_estado_botao()

        step(1)

    def _toggle_theme(self):
        t_from = dict(self._t)  # snapshot current palette before switching
        new_theme = "light" if self._theme == "dark" else "dark"
        self._theme = new_theme
        self._t = THEMES[new_theme]

        icon = "☀" if new_theme == "dark" else "☾"
        self._theme_btn.configure(text=icon)

        # Bump generation to cancel any in-flight animation, then start a new one
        self._theme_anim_gen += 1
        self._animate_theme(t_from, THEMES[new_theme])
