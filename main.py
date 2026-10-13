from __future__ import annotations
import json, os, random, sys, textwrap
from datetime import date, timedelta
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from game_data import (
    create_save, default_profile, PYTHON_PHASES, CAIXA_SUBJECTS,
    PYTHON_MISSION_SUFFIXES, CAIXA_MISSION_SUFFIXES, PYTHON_QUIZ,
    CAIXA_QUIZ, SHOP_ITEMS, STORY, BOSS_NAMES,
)

APP_NAME = "HUNTER SYSTEM"
BG = "#0b0b12"
SIDEBAR = "#11111b"
PANEL = "#171724"
PANEL_2 = "#202033"
BORDER = "#303048"
TEXT = "#f4f0ff"
MUTED = "#a09bb8"
PURPLE = "#9c6bff"
PURPLE_DARK = "#6c43c5"
GOLD = "#f1be67"
MINT = "#7ee0c1"
RED = "#ff6c83"
BLUE = "#75b9ff"
FONT = "Segoe UI"


def save_path() -> Path:
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", str(Path.home()))) / "HunterSystem"
    else:
        base = Path.home() / ".hunter_system"
    base.mkdir(parents=True, exist_ok=True)
    return base / "save.json"


def safe_int(value, default=0):
    try:
        return int(str(value).strip())
    except Exception:
        return default


def xp_needed(level: int) -> int:
    return 100 + max(0, level - 1) * 40


def clamp(value, low, high):
    return max(low, min(high, value))


class ScrollFrame(tk.Frame):
    def __init__(self, parent, bg=BG, **kwargs):
        super().__init__(parent, bg=bg, **kwargs)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner = tk.Frame(self.canvas, bg=bg)
        self.window = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.inner.bind("<Configure>", self._on_configure)
        self.canvas.bind("<Configure>", self._on_canvas)

    def _on_configure(self, _event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas(self, event):
        self.canvas.itemconfigure(self.window, width=event.width)

    def _wheel(self, event):
        try:
            if self.winfo_exists() and self.winfo_ismapped():
                self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except Exception:
            pass


class HunterSystem(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hunter System — A Forja da Constância")
        self.geometry("1280x820")
        self.minsize(1000, 650)
        self.configure(bg=BG)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self._setup_style()
        self.save_file = save_path()
        self.data = self._load_save()
        self.active_key = self.data.get("active_profile", "python")
        if self.active_key not in self.data["profiles"]:
            self.active_key = "python"
        self.page = "Santuário"
        self.page_frames = {}
        self.timer_seconds = 25 * 60
        self.timer_running = False
        self.timer_job = None
        self.current_question = None
        self.current_answered = False
        self.quiz_order = []
        self.quiz_option_buttons = []
        self.status_var = tk.StringVar(value="A Forja está acesa. Uma missão por vez.")
        self._active_scroll_canvas = None
        self._build_shell()
        self.render()
        profile = self.profile
        if "intro" not in profile.get("story_seen", []):
            self.after(450, lambda: self.show_story("intro"))

    @property
    def profile(self):
        return self.data["profiles"][self.active_key]

    def _setup_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("TScrollbar", background=PANEL_2, troughcolor=BG, bordercolor=BG, arrowcolor=MUTED)
        style.configure("Treeview", background=PANEL, fieldbackground=PANEL, foreground=TEXT, borderwidth=0, rowheight=30)
        style.configure("Treeview.Heading", background=PANEL_2, foreground=TEXT, relief="flat")
        style.map("Treeview", background=[("selected", PURPLE_DARK)], foreground=[("selected", TEXT)])
        style.configure("TCombobox", fieldbackground=PANEL_2, background=PANEL_2, foreground=TEXT, arrowcolor=TEXT)
        style.map("TCombobox", fieldbackground=[("readonly", PANEL_2)], foreground=[("readonly", TEXT)])

    def _load_save(self):
        try:
            if self.save_file.exists():
                with self.save_file.open("r", encoding="utf-8") as f:
                    raw = json.load(f)
                base = create_save()
                for key in ("python", "caixa", "custom"):
                    if key not in raw.get("profiles", {}):
                        raw.setdefault("profiles", {})[key] = base["profiles"][key]
                    else:
                        # Corrige saves de versões futuras/incompletas sem apagar dados conhecidos.
                        seed = base["profiles"][key]
                        for k, v in seed.items():
                            raw["profiles"][key].setdefault(k, v)
                raw.setdefault("active_profile", "python")
                raw["version"] = 1
                return raw
        except Exception as exc:
            try:
                messagebox.showwarning("Save recuperado", f"Não foi possível ler o save anterior. Um novo save será iniciado.\n\nDetalhe: {exc}")
            except Exception:
                pass
        return create_save()

    def save(self, quiet=True):
        try:
            self.data["active_profile"] = self.active_key
            tmp = self.save_file.with_suffix(".tmp")
            with tmp.open("w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            tmp.replace(self.save_file)
            if not quiet:
                self.status_var.set(f"Progresso salvo localmente · {self.save_file}")
        except Exception as exc:
            messagebox.showerror("Erro ao salvar", f"O progresso não pôde ser salvo.\n\n{exc}")

    def _build_shell(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.sidebar = tk.Frame(self, bg=SIDEBAR, width=244, highlightbackground=BORDER, highlightthickness=1)
        self.sidebar.grid(row=0, column=0, sticky="nsw")
        self.sidebar.grid_propagate(False)
        self.right = tk.Frame(self, bg=BG)
        self.right.grid(row=0, column=1, sticky="nsew")
        self.right.grid_columnconfigure(0, weight=1)
        self.right.grid_rowconfigure(1, weight=1)
        self.header = tk.Frame(self.right, bg=BG, height=72)
        self.header.grid(row=0, column=0, sticky="ew", padx=26, pady=(20, 12))
        self.header.grid_columnconfigure(0, weight=1)
        self.content_host = tk.Frame(self.right, bg=BG)
        self.content_host.grid(row=1, column=0, sticky="nsew", padx=26, pady=(0, 8))
        self.content_host.grid_columnconfigure(0, weight=1)
        self.content_host.grid_rowconfigure(0, weight=1)
        self.bind_all("<MouseWheel>", self._scroll_active_page)
        status = tk.Frame(self.right, bg=BG, height=30)
        status.grid(row=2, column=0, sticky="ew", padx=26, pady=(0, 12))
        tk.Label(status, textvariable=self.status_var, bg=BG, fg=MUTED, font=(FONT, 9), anchor="w").pack(side="left", fill="x", expand=True)
        tk.Label(status, text="SALVAMENTO LOCAL  •  SEM CONTA  •  SEM INTERNET", bg=BG, fg="#68647c", font=(FONT, 8, "bold")).pack(side="right")

    def _label(self, parent, text, size=10, color=TEXT, bold=False, **kwargs):
        return tk.Label(parent, text=text, bg=kwargs.pop("bg", parent.cget("bg") if "bg" in parent.keys() else BG), fg=color,
                        font=(FONT, size, "bold" if bold else "normal"), **kwargs)

    def _button(self, parent, text, command, kind="primary", width=None, state="normal"):
        opts = {
            "primary": (PURPLE, "#ffffff", PURPLE_DARK),
            "secondary": (PANEL_2, TEXT, BORDER),
            "gold": (GOLD, "#19111b", "#d39e45"),
            "danger": ("#572033", "#ffdce3", "#8e3654"),
            "quiet": (parent.cget("bg"), MUTED, parent.cget("bg")),
            "mint": ("#1d5049", MINT, "#277264"),
        }
        bg, fg, active = opts.get(kind, opts["primary"])
        b = tk.Button(parent, text=text, command=command, bg=bg, fg=fg, activebackground=active,
                      activeforeground=TEXT, relief="flat", bd=0, padx=13, pady=8,
                      font=(FONT, 9, "bold"), cursor="hand2", state=state, disabledforeground="#5e5970")
        if width:
            b.configure(width=width)
        return b

    def _card(self, parent, title=None, subtitle=None, padx=16, pady=14):
        frame = tk.Frame(parent, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        if title:
            head = tk.Frame(frame, bg=PANEL)
            head.pack(fill="x", padx=padx, pady=(pady, 6))
            tk.Label(head, text=title.upper(), bg=PANEL, fg=TEXT, font=(FONT, 10, "bold"), anchor="w").pack(side="left", fill="x", expand=True)
            if subtitle:
                tk.Label(head, text=subtitle, bg=PANEL, fg=MUTED, font=(FONT, 8)).pack(side="right")
        return frame

    def _section(self, parent, title, subtitle=None):
        f = tk.Frame(parent, bg=BG)
        f.pack(fill="x", pady=(16, 9))
        tk.Label(f, text=title, bg=BG, fg=TEXT, font=(FONT, 15, "bold"), anchor="w").pack(side="left")
        if subtitle:
            tk.Label(f, text=subtitle, bg=BG, fg=MUTED, font=(FONT, 9), anchor="e").pack(side="right")
        return f

    def _progress(self, parent, value, maximum, color=PURPLE, height=8):
        outside = tk.Frame(parent, bg="#29283c", height=height)
        outside.pack(fill="x")
        outside.pack_propagate(False)
        width = max(0.0, min(1.0, (value / maximum) if maximum else 0))
        inside = tk.Frame(outside, bg=color, height=height)
        inside.place(relx=0, rely=0, relwidth=width, relheight=1)
        return outside

    def render(self):
        self._render_sidebar()
        self._render_header()
        for w in self.content_host.winfo_children():
            w.destroy()
        self.content_host.grid_rowconfigure(0, weight=1)
        self.content_host.grid_columnconfigure(0, weight=1)
        if self.page == "Santuário": self.page_dashboard()
        elif self.page == "Missões": self.page_missions()
        elif self.page == "Chefes": self.page_bosses()
        elif self.page == "Arsenal": self.page_armory()
        elif self.page == "Eventos": self.page_events()
        elif self.page == "Códice": self.page_codex()
        elif self.page == "Configuração": self.page_settings()

    def _render_sidebar(self):
        for w in self.sidebar.winfo_children():
            w.destroy()
        logo = tk.Frame(self.sidebar, bg=SIDEBAR)
        logo.pack(fill="x", padx=18, pady=(22, 22))
        emblem = tk.Canvas(logo, width=42, height=42, bg=SIDEBAR, highlightthickness=0)
        emblem.pack(side="left", padx=(0, 10))
        emblem.create_polygon(21, 1, 39, 13, 35, 32, 21, 41, 7, 32, 3, 13, fill=PURPLE_DARK, outline=GOLD, width=1)
        emblem.create_line(21, 8, 21, 34, fill=GOLD, width=2)
        emblem.create_line(12, 20, 30, 20, fill=GOLD, width=2)
        brand = tk.Frame(logo, bg=SIDEBAR)
        brand.pack(side="left", fill="y")
        tk.Label(brand, text="HUNTER", bg=SIDEBAR, fg=TEXT, font=(FONT, 15, "bold")).pack(anchor="w")
        tk.Label(brand, text="SYSTEM  /  FORJA DA CONSTÂNCIA", bg=SIDEBAR, fg=PURPLE, font=(FONT, 7, "bold")).pack(anchor="w")
        tk.Label(self.sidebar, text="SLOTS DE JORNADA", bg=SIDEBAR, fg=MUTED, font=(FONT, 8, "bold"), anchor="w").pack(fill="x", padx=18, pady=(0, 8))
        slot_data = [
            ("python", "01", "FORJA DO CÓDIGO", "Python · curso Udemy", PURPLE),
            ("caixa", "02", "ROTA DA CAIXA", "Técnico Bancário Novo", GOLD),
            ("custom", "03", "JORNADA LIVRE", "Personalizável", MINT),
        ]
        for key, num, title, sub, color in slot_data:
            selected = key == self.active_key
            card_bg = "#24213a" if selected else SIDEBAR
            button = tk.Frame(self.sidebar, bg=card_bg, highlightbackground=color if selected else BORDER, highlightthickness=1, cursor="hand2")
            button.pack(fill="x", padx=13, pady=4)
            button.bind("<Button-1>", lambda e, k=key: self.switch_profile(k))
            icon = tk.Frame(button, bg=color, width=31, height=34)
            icon.pack(side="left", padx=10, pady=9)
            icon.pack_propagate(False)
            tk.Label(icon, text=num, bg=color, fg="#15121d", font=(FONT, 9, "bold")).pack(expand=True)
            textf = tk.Frame(button, bg=card_bg)
            textf.pack(side="left", fill="x", expand=True, pady=7)
            slot_title = self.data["profiles"][key]["settings"].get("title", title)
            tk.Label(textf, text=slot_title,
                     bg=card_bg, fg=TEXT, font=(FONT, 8, "bold"), anchor="w", wraplength=145).pack(fill="x", anchor="w")
            tk.Label(textf, text=sub, bg=card_bg, fg=MUTED, font=(FONT, 8), anchor="w").pack(fill="x", anchor="w")
            for widget in (textf, *textf.winfo_children(), icon, *icon.winfo_children()):
                widget.bind("<Button-1>", lambda e, k=key: self.switch_profile(k))
        tk.Frame(self.sidebar, bg=BORDER, height=1).pack(fill="x", padx=18, pady=(18, 13))
        tk.Label(self.sidebar, text="REFÚGIO", bg=SIDEBAR, fg=MUTED, font=(FONT, 8, "bold"), anchor="w").pack(fill="x", padx=18, pady=(0, 8))
        nav = [("Santuário", "⌂"), ("Missões", "✦"), ("Chefes", "⚔"), ("Arsenal", "◇"), ("Eventos", "◷"), ("Códice", "▤"), ("Configuração", "⚙")]
        for label, glyph in nav:
            selected = self.page == label
            b = tk.Frame(self.sidebar, bg="#27223d" if selected else SIDEBAR, cursor="hand2")
            b.pack(fill="x", padx=13, pady=2)
            b.bind("<Button-1>", lambda e, p=label: self.navigate(p))
            tk.Label(b, text=glyph, bg=b.cget("bg"), fg=PURPLE if selected else MUTED, font=(FONT, 13), width=3).pack(side="left", pady=5)
            tk.Label(b, text=label, bg=b.cget("bg"), fg=TEXT if selected else MUTED, font=(FONT, 9, "bold" if selected else "normal")).pack(side="left", pady=7)
            for child in b.winfo_children(): child.bind("<Button-1>", lambda e, p=label: self.navigate(p))
        spacer = tk.Frame(self.sidebar, bg=SIDEBAR)
        spacer.pack(fill="both", expand=True)
        bottom = tk.Frame(self.sidebar, bg="#191824", highlightbackground=BORDER, highlightthickness=1)
        bottom.pack(fill="x", padx=13, pady=14)
        tk.Label(bottom, text=f"NÍVEL {self.profile['level']}  ·  {self.profile['settings']['archetype'].upper()}", bg="#191824", fg=GOLD, font=(FONT, 8, "bold")).pack(anchor="w", padx=11, pady=(10, 2))
        tk.Label(bottom, text=f"{len(self.profile['completed_missions'])}/{len(self.profile['mission_data'])} missões concluídas", bg="#191824", fg=MUTED, font=(FONT, 8)).pack(anchor="w", padx=11, pady=(0, 10))

    def _render_header(self):
        for w in self.header.winfo_children(): w.destroy()
        left = tk.Frame(self.header, bg=BG)
        left.grid(row=0, column=0, sticky="w")
        tk.Label(left, text=self.page.upper(), bg=BG, fg=PURPLE, font=(FONT, 8, "bold")).pack(anchor="w")
        tk.Label(left, text=self.profile["settings"]["title"], bg=BG, fg=TEXT, font=(FONT, 19, "bold")).pack(anchor="w", pady=(2, 0))
        right = tk.Frame(self.header, bg=BG)
        right.grid(row=0, column=1, sticky="e")
        tk.Label(right, text=f"✦ {self.profile['gold']} OURO", bg=BG, fg=GOLD, font=(FONT, 10, "bold")).pack(side="left", padx=(0, 16))
        tk.Label(right, text=f"LVL {self.profile['level']}", bg=PANEL_2, fg=TEXT, font=(FONT, 9, "bold"), padx=10, pady=7).pack(side="left")

    def switch_profile(self, key):
        if key not in self.data["profiles"] or key == self.active_key:
            return
        self.save()
        self.active_key = key
        self.data["active_profile"] = key
        self.current_question = None
        self.render()
        self.status_var.set(f"Slot ativo: {self.profile['settings']['title']}.")

    def navigate(self, page):
        self.page = page
        self.render()

    def mission_count(self):
        return len(self.profile["completed_missions"])

    def total_missions(self):
        return len(self.profile["mission_data"])

    def max_hp(self, profile=None):
        p = profile or self.profile
        attrs = p["attributes"]
        bonus = sum(self.item_stats(item_id).get("hp", 0) for item_id in p["equipped"].values() if item_id)
        return 100 + (p["level"] - 1) * 7 + attrs["endurance"] * 8 + bonus

    def item_stats(self, item_id):
        for item in SHOP_ITEMS:
            if item["id"] == item_id:
                return item
        return {"attack":0,"defense":0,"hp":0,"focus":0,"slot":"unknown"}

    def attack_stat(self, profile=None):
        p = profile or self.profile
        base = 10 + p["attributes"]["strength"] * 3
        return base + sum(self.item_stats(item_id).get("attack", 0) for item_id in p["equipped"].values() if item_id)

    def defense_stat(self, profile=None):
        p = profile or self.profile
        return sum(self.item_stats(item_id).get("defense", 0) for item_id in p["equipped"].values() if item_id) + p["attributes"]["endurance"]

    def focus_stat(self, profile=None):
        p = profile or self.profile
        return p["attributes"]["focus"] + sum(self.item_stats(item_id).get("focus", 0) for item_id in p["equipped"].values() if item_id)

    def gain_xp(self, amount):
        p = self.profile
        p["xp"] += amount
        levels = 0
        while p["xp"] >= xp_needed(p["level"]):
            p["xp"] -= xp_needed(p["level"])
            p["level"] += 1
            p["attribute_points"] += 2
            levels += 1
        return levels

    def update_streak(self):
        p = self.profile
        today = date.today()
        last = p.get("last_study_date", "")
        today_s = today.isoformat()
        if last == today_s:
            return
        if last:
            try:
                delta = (today - date.fromisoformat(last)).days
            except Exception:
                delta = 2
            p["streak"] = p.get("streak", 0) + 1 if delta == 1 else 1
        else:
            p["streak"] = 1
        p["last_study_date"] = today_s

    def complete_mission(self, mission_id):
        p = self.profile
        mission = next((m for m in p["mission_data"] if m["id"] == mission_id), None)
        if not mission or mission_id in p["completed_missions"]:
            return
        p["completed_missions"].append(mission_id)
        p["gold"] += mission.get("coins", 10)
        levels = self.gain_xp(mission.get("xp", 30))
        self.update_streak()
        p["history"].append({"date":date.today().isoformat(),"type":"missão","title":mission["title"],"xp":mission.get("xp",30),"gold":mission.get("coins",10)})
        self.save()
        self.render()
        msg = f"Missão concluída: {mission['title']}\n+{mission.get('xp',30)} XP  ·  +{mission.get('coins',10)} ouro"
        if levels:
            msg += f"\n\nSUBIU {levels} NÍVEL(IS)! Você recebeu {levels*2} pontos de atributo."
        self.status_var.set("Missão registrada. A jornada continua.")
        messagebox.showinfo("Recompensa recebida", msg)

    def spend_attribute(self, attr):
        p = self.profile
        if p["attribute_points"] <= 0:
            messagebox.showinfo("Sem pontos", "Suba de nível para ganhar pontos de atributo.")
            return
        p["attributes"][attr] += 1
        p["attribute_points"] -= 1
        self.save()
        self.render()

    def add_reward(self, xp, gold, label, add_streak=True):
        p = self.profile
        p["gold"] += gold
        levels = self.gain_xp(xp)
        if add_streak: self.update_streak()
        p["history"].append({"date":date.today().isoformat(),"type":"recompensa","title":label,"xp":xp,"gold":gold})
        self.save()
        self.render()
        self.status_var.set(f"{label}: +{xp} XP e +{gold} ouro.")
        if levels:
            messagebox.showinfo("Nível aumentado", f"Você alcançou o nível {p['level']} e recebeu {levels*2} pontos de atributo.")

    def _scroll_active_page(self, event):
        canvas = self._active_scroll_canvas
        if canvas is not None:
            try:
                if canvas.winfo_exists():
                    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except Exception:
                pass

    def build_scroll_page(self):
        sf = ScrollFrame(self.content_host, bg=BG)
        sf.grid(row=0, column=0, sticky="nsew")
        sf.inner.configure(padx=2, pady=1)
        self._active_scroll_canvas = sf.canvas
        return sf.inner

    # ------------------------------ DASHBOARD ------------------------------
    def page_dashboard(self):
        root = self.build_scroll_page()
        p = self.profile
        xp_goal = xp_needed(p["level"])
        completed = self.mission_count()
        total = self.total_missions()
        pct = int(completed * 100 / total) if total else 0

        hero = tk.Frame(root, bg="#20172f", highlightbackground="#5a3b83", highlightthickness=1)
        hero.pack(fill="x", pady=(0, 14))
        hero.grid_columnconfigure(0, weight=1)
        hero.grid_columnconfigure(1, weight=0)
        left = tk.Frame(hero, bg="#20172f")
        left.grid(row=0, column=0, sticky="nsew", padx=22, pady=20)
        tk.Label(left, text="A CIDADE SEM AURORA  /  CAPÍTULO I", bg="#20172f", fg=GOLD, font=(FONT, 8, "bold")).pack(anchor="w")
        tk.Label(left, text=p["settings"]["hero"], bg="#20172f", fg=TEXT, font=(FONT, 22, "bold")).pack(anchor="w", pady=(5, 3))
        tk.Label(left, text=p["settings"]["intro"], bg="#20172f", fg="#d5cde8", font=(FONT, 10), wraplength=700, justify="left").pack(anchor="w", pady=(0, 9 if self.active_key == "caixa" else 15))
        if self.active_key == "caixa":
            tk.Label(left, text="ESTRUTURA DO EDITAL ENVIADO  ·  25 BÁSICAS  /  35 ESPECÍFICAS  /  REDAÇÃO ELIMINATÓRIA", bg="#20172f", fg=GOLD, font=(FONT, 7, "bold"), wraplength=720, justify="left").pack(anchor="w", pady=(0, 9))
        line = tk.Frame(left, bg="#20172f")
        line.pack(fill="x")
        tk.Label(line, text=f"PROGRESSO DA JORNADA  {completed}/{total}  ·  {pct}%", bg="#20172f", fg=MUTED, font=(FONT, 8, "bold")).pack(anchor="w", pady=(0, 6))
        bar = tk.Frame(line, bg="#413453", height=7)
        bar.pack(fill="x")
        tk.Frame(bar, bg=PURPLE, height=7).place(relx=0, rely=0, relwidth=pct/100, relheight=1)
        actions = tk.Frame(left, bg="#20172f")
        actions.pack(anchor="w", pady=(14, 0))
        self._button(actions, "RETOMAR A JORNADA  →", lambda:self.navigate("Missões"), "primary").pack(side="left", padx=(0, 8))
        self._button(actions, "OUVIR A HISTÓRIA", lambda:self.show_story("intro", replay=True), "secondary").pack(side="left")
        sigil = tk.Canvas(hero, width=172, height=170, bg="#20172f", highlightthickness=0)
        sigil.grid(row=0, column=1, padx=22, pady=12)
        sigil.create_oval(24, 18, 148, 142, outline="#593e80", width=2)
        sigil.create_oval(36, 30, 136, 130, outline=GOLD, width=1)
        sigil.create_polygon(86, 30, 113, 68, 101, 115, 86, 130, 71, 115, 59, 68, fill=PURPLE_DARK, outline=GOLD, width=2)
        sigil.create_line(86, 42, 86, 119, fill=GOLD, width=3)
        sigil.create_line(69, 78, 103, 78, fill=GOLD, width=3)
        sigil.create_text(86, 153, text="CONSTÂNCIA", fill=GOLD, font=(FONT, 8, "bold"))

        grid = tk.Frame(root, bg=BG)
        grid.pack(fill="x")
        grid.grid_columnconfigure(0, weight=3, uniform="main")
        grid.grid_columnconfigure(1, weight=2, uniform="main")
        leftcol = tk.Frame(grid, bg=BG)
        leftcol.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        rightcol = tk.Frame(grid, bg=BG)
        rightcol.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        stats = self._card(leftcol, "Status do Caçador", "SEU ESTADO ATUAL")
        stats.pack(fill="x", pady=(0, 14))
        statsbody = tk.Frame(stats, bg=PANEL)
        statsbody.pack(fill="x", padx=16, pady=(0, 16))
        top = tk.Frame(statsbody, bg=PANEL)
        top.pack(fill="x")
        av = tk.Canvas(top, width=65, height=65, bg=PANEL, highlightthickness=0)
        av.pack(side="left", padx=(0, 12))
        av.create_oval(4, 4, 61, 61, fill="#302648", outline=PURPLE, width=2)
        av.create_text(32, 31, text=str(p["level"]), fill=GOLD, font=(FONT, 20, "bold"))
        idbox = tk.Frame(top, bg=PANEL)
        idbox.pack(side="left", fill="x", expand=True)
        tk.Label(idbox, text=f"NÍVEL {p['level']}  ·  {p['settings']['archetype']}", bg=PANEL, fg=GOLD, font=(FONT, 9, "bold")).pack(anchor="w")
        tk.Label(idbox, text=p["settings"]["hero"], bg=PANEL, fg=TEXT, font=(FONT, 13, "bold"), wraplength=280).pack(anchor="w", pady=(3, 5))
        tk.Label(idbox, text=f"{p['xp']} / {xp_goal} XP para o próximo nível", bg=PANEL, fg=MUTED, font=(FONT, 8)).pack(anchor="w")
        self._progress(statsbody, p["xp"], xp_goal, PURPLE, 7).pack(fill="x", pady=(7, 12))
        for attr, label, color in [("strength","FORÇA",RED),("focus","FOCO",BLUE),("endurance","VIGOR",MINT)]:
            row = tk.Frame(statsbody, bg=PANEL)
            row.pack(fill="x", pady=3)
            tk.Label(row, text=label, bg=PANEL, fg=MUTED, font=(FONT, 8, "bold"), width=10, anchor="w").pack(side="left")
            tk.Label(row, text=str(p["attributes"][attr]), bg=PANEL, fg=TEXT, font=(FONT, 9, "bold"), width=3).pack(side="left")
            self._progress(row, p["attributes"][attr], max(10, p["attributes"][attr]+4), color, 5).pack(side="left", fill="x", expand=True, padx=8)
            if p["attribute_points"] > 0:
                self._button(row, "+", lambda a=attr:self.spend_attribute(a), "secondary", width=2).pack(side="right")
        footer = tk.Frame(statsbody, bg=PANEL)
        footer.pack(fill="x", pady=(10, 0))
        tk.Label(footer, text=f"⚔ {self.attack_stat()} ATQ", bg=PANEL, fg=RED, font=(FONT, 9, "bold")).pack(side="left", padx=(0, 14))
        tk.Label(footer, text=f"⬡ {self.defense_stat()} DEF", bg=PANEL, fg=BLUE, font=(FONT, 9, "bold")).pack(side="left", padx=(0, 14))
        tk.Label(footer, text=f"♥ {self.max_hp()} HP", bg=PANEL, fg=MINT, font=(FONT, 9, "bold")).pack(side="left")
        if p["attribute_points"]:
            tk.Label(statsbody, text=f"Você tem {p['attribute_points']} ponto(s) de atributo para distribuir.", bg=PANEL, fg=GOLD, font=(FONT, 8)).pack(anchor="w", pady=(8, 0))

        self._section(leftcol, "Missões em destaque", "PRÓXIMOS PASSOS")
        missions = [m for m in p["mission_data"] if m["id"] not in p["completed_missions"]][:4]
        if not missions:
            msg = self._card(leftcol, "Todas as missões concluídas", "UM MARCO IMPORTANTE")
            msg.pack(fill="x")
            tk.Label(msg, text="Sua trilha foi concluída. É hora de revisar, enfrentar o guardião final e celebrar o que construiu.", bg=PANEL, fg=MUTED, wraplength=600, justify="left").pack(anchor="w", padx=16, pady=(0, 15))
        for mission in missions:
            self._mission_card(leftcol, mission, compact=True)

        streak = self._card(rightcol, "Ritmo da jornada", "CONSTÂNCIA > INTENSIDADE")
        streak.pack(fill="x", pady=(0, 14))
        sb = tk.Frame(streak, bg=PANEL)
        sb.pack(fill="x", padx=16, pady=(0, 16))
        tk.Label(sb, text="◷", bg=PANEL, fg=GOLD, font=(FONT, 24, "bold")).pack(side="left", padx=(0, 10))
        st = tk.Frame(sb, bg=PANEL)
        st.pack(side="left", fill="x", expand=True)
        tk.Label(st, text=f"{p.get('streak',0)} dia(s) de sequência", bg=PANEL, fg=TEXT, font=(FONT, 12, "bold")).pack(anchor="w")
        tk.Label(st, text="Registre ao menos uma missão ou desafio no dia.", bg=PANEL, fg=MUTED, font=(FONT, 8), wraplength=255, justify="left").pack(anchor="w", pady=(3, 0))
        self._button(st, "VER EVENTOS  →", lambda:self.navigate("Eventos"), "secondary").pack(anchor="w", pady=(8, 0))

        boss_card = self._card(rightcol, "Próximo guardião", "A PRÓXIMA PROVA")
        boss_card.pack(fill="x", pady=(0, 14))
        next_boss = next((b for b in p["boss_data"] if b["id"] not in p["bosses_defeated"]), None)
        bb = tk.Frame(boss_card, bg=PANEL)
        bb.pack(fill="x", padx=16, pady=(0, 16))
        if next_boss:
            tk.Label(bb, text="☠", bg=PANEL, fg=RED, font=(FONT, 26, "bold")).pack(side="left", padx=(0, 12))
            bt = tk.Frame(bb, bg=PANEL); bt.pack(side="left", fill="x", expand=True)
            tk.Label(bt, text=next_boss["name"], bg=PANEL, fg=TEXT, font=(FONT, 11, "bold"), wraplength=220).pack(anchor="w")
            tk.Label(bt, text=f"Exige {next_boss['threshold']} missões concluídas · Recompensa {next_boss['reward_xp']} XP", bg=PANEL, fg=MUTED, font=(FONT, 8), wraplength=240, justify="left").pack(anchor="w", pady=(4, 0))
            self._button(bb, "VER", lambda:self.navigate("Chefes"), "danger").pack(side="right", padx=(5,0))
        else:
            tk.Label(bb, text="Todos os guardiões derrotados. A história foi encerrada.", bg=PANEL, fg=MINT, font=(FONT, 10), wraplength=320).pack(anchor="w")

        quick = self._card(rightcol, "Acesso rápido", "SEM PERDER O RITMO")
        quick.pack(fill="x", pady=(0, 14))
        qb = tk.Frame(quick, bg=PANEL); qb.pack(fill="x", padx=16, pady=(0, 15))
        for title, desc, page in [("Treinar 25 min", "Uma sessão focada", "Eventos"),("Testar memória", "Questões rápidas", "Códice"),("Melhorar equipamento", "Troque ouro por atributos", "Arsenal")]:
            linef = tk.Frame(qb, bg=PANEL); linef.pack(fill="x", pady=4)
            tk.Label(linef, text=title, bg=PANEL, fg=TEXT, font=(FONT, 9, "bold")).pack(side="left", anchor="w")
            tk.Label(linef, text=desc, bg=PANEL, fg=MUTED, font=(FONT, 8)).pack(side="left", padx=8)
            self._button(linef, "ABRIR", lambda pg=page:self.navigate(pg), "secondary").pack(side="right")

        self._section(root, "Crônicas recentes", "SEU HISTÓRICO LOCAL")
        hist = self._card(root)
        hist.pack(fill="x", pady=(0, 14))
        recent = list(reversed(p.get("history", [])[-5:]))
        if not recent:
            tk.Label(hist, text="Nenhuma ação registrada ainda. Conclua sua primeira missão para escrever a primeira linha da crônica.", bg=PANEL, fg=MUTED, font=(FONT, 9), wraplength=800, justify="left").pack(anchor="w", padx=16, pady=15)
        for item in recent:
            row = tk.Frame(hist, bg=PANEL); row.pack(fill="x", padx=16, pady=6)
            tk.Label(row, text=item.get("date","—"), bg=PANEL, fg=MUTED, font=(FONT, 8), width=11, anchor="w").pack(side="left")
            tk.Label(row, text=item.get("title","Ação"), bg=PANEL, fg=TEXT, font=(FONT, 9), anchor="w", wraplength=600).pack(side="left", fill="x", expand=True)
            tk.Label(row, text=f"+{item.get('xp',0)} XP", bg=PANEL, fg=PURPLE, font=(FONT, 8, "bold")).pack(side="left", padx=8)
            tk.Label(row, text=f"+{item.get('gold',0)} G", bg=PANEL, fg=GOLD, font=(FONT, 8, "bold")).pack(side="right")

    def _mission_card(self, parent, mission, compact=False):
        card = tk.Frame(parent, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill="x", pady=(0, 9))
        top = tk.Frame(card, bg=PANEL); top.pack(fill="x", padx=15, pady=(12, 5))
        tk.Label(top, text=mission["topic"].upper(), bg="#2c2440", fg=PURPLE, font=(FONT, 7, "bold"), padx=7, pady=3).pack(side="left")
        if self.active_key == "caixa" and mission.get("weight", 0):
            block = "BÁSICOS" if mission.get("block") == "Conhecimentos Básicos" else "ESPECÍFICOS"
            tk.Label(top, text=f"{block} · {mission['weight']} QUESTÕES", bg="#24243a", fg=BLUE, font=(FONT, 7, "bold"), padx=6, pady=3).pack(side="left", padx=(7,0))
        tk.Label(top, text=f"+{mission['xp']} XP  ·  +{mission['coins']} G", bg=PANEL, fg=GOLD, font=(FONT, 8, "bold")).pack(side="right")
        tk.Label(card, text=mission["title"], bg=PANEL, fg=TEXT, font=(FONT, 11, "bold"), anchor="w", wraplength=760).pack(fill="x", padx=15, pady=(2, 3))
        tk.Label(card, text=mission["description"], bg=PANEL, fg=MUTED, font=(FONT, 9), anchor="w", justify="left", wraplength=620).pack(fill="x", padx=15, pady=(0, 10))
        row = tk.Frame(card, bg=PANEL); row.pack(fill="x", padx=15, pady=(0, 12))
        if compact:
            tk.Label(row, text="Uma etapa de cada vez. Registre apenas quando terminar.", bg=PANEL, fg="#6f6a85", font=(FONT, 8)).pack(side="left", fill="x", expand=True)
        else:
            tk.Label(row, text="Recompensa ao concluir", bg=PANEL, fg=MUTED, font=(FONT, 8)).pack(side="left", fill="x", expand=True)
        self._button(row, "CONCLUIR MISSÃO  ✓", lambda mid=mission["id"]:self.complete_mission(mid), "mint").pack(side="right")

    # ------------------------------ MISSIONS -------------------------------
    def page_missions(self):
        root = self.build_scroll_page()
        p = self.profile
        done = len(p["completed_missions"]); total = len(p["mission_data"])
        card = self._card(root, "Mapa da campanha", "CADA ETAPA GERA EXPERIÊNCIA")
        card.pack(fill="x", pady=(0, 15))
        body = tk.Frame(card, bg=PANEL); body.pack(fill="x", padx=16, pady=(0, 16))
        tk.Label(body, text=f"{done} de {total} missões concluídas", bg=PANEL, fg=TEXT, font=(FONT, 12, "bold")).pack(anchor="w", pady=(0, 7))
        self._progress(body, done, total, MINT, 9).pack(fill="x")
        tk.Label(body, text="Marque uma missão somente depois de estudar/praticar. A recompensa representa esforço real — não precisa correr.", bg=PANEL, fg=MUTED, font=(FONT, 9), wraplength=900, justify="left").pack(anchor="w", pady=(8, 0))
        controls = tk.Frame(root, bg=BG); controls.pack(fill="x", pady=(0, 12))
        tk.Label(controls, text="FILTRAR POR TEMA", bg=BG, fg=MUTED, font=(FONT, 8, "bold")).pack(side="left", padx=(0, 7))
        topics = ["Todos os temas"] + list(dict.fromkeys(m["topic"] for m in p["mission_data"]))
        topic_var = tk.StringVar(value="Todos os temas")
        cb = ttk.Combobox(controls, values=topics, textvariable=topic_var, state="readonly", width=32)
        cb.pack(side="left", padx=(0, 14))
        status_var = tk.StringVar(value="Pendentes")
        status = ttk.Combobox(controls, values=["Pendentes","Concluídas","Todas"], textvariable=status_var, state="readonly", width=15)
        status.pack(side="left")
        list_frame = tk.Frame(root, bg=BG); list_frame.pack(fill="x")
        def refresh(*_):
            for w in list_frame.winfo_children(): w.destroy()
            chosen = topic_var.get(); mode = status_var.get()
            shown = 0
            for mission in p["mission_data"]:
                is_done = mission["id"] in p["completed_missions"]
                if chosen != "Todos os temas" and mission["topic"] != chosen: continue
                if mode == "Pendentes" and is_done: continue
                if mode == "Concluídas" and not is_done: continue
                shown += 1
                if is_done:
                    f = tk.Frame(list_frame, bg="#13131c", highlightbackground="#27273b", highlightthickness=1)
                    f.pack(fill="x", pady=(0, 7))
                    tk.Label(f, text="✓", bg="#13131c", fg=MINT, font=(FONT, 15, "bold"), width=4).pack(side="left", padx=(5,0), pady=10)
                    mid = tk.Frame(f, bg="#13131c"); mid.pack(side="left", fill="x", expand=True, pady=10)
                    tk.Label(mid, text=mission["title"], bg="#13131c", fg="#aaa5bd", font=(FONT, 10, "bold"), anchor="w").pack(fill="x")
                    tk.Label(mid, text=f"{mission['topic']}  ·  concluída", bg="#13131c", fg="#6f6b83", font=(FONT, 8), anchor="w").pack(fill="x", pady=(2,0))
                    tk.Label(f, text=f"+{mission['xp']} XP", bg="#13131c", fg="#6f6b83", font=(FONT, 8, "bold")).pack(side="right", padx=18)
                else:
                    self._mission_card(list_frame, mission, compact=False)
            if not shown:
                tk.Label(list_frame, text="Nenhuma missão neste filtro. Experimente outra opção.", bg=BG, fg=MUTED, font=(FONT, 10)).pack(anchor="w", pady=20)
        cb.bind("<<ComboboxSelected>>", refresh); status.bind("<<ComboboxSelected>>", refresh)
        refresh()

    # -------------------------------- BOSSES -------------------------------
    def page_bosses(self):
        root = self.build_scroll_page()
        p = self.profile
        count = self.mission_count()
        header = self._card(root, "Câmara dos guardiões", "COMBATE POR TURNOS")
        header.pack(fill="x", pady=(0, 15))
        hb = tk.Frame(header, bg=PANEL); hb.pack(fill="x", padx=16, pady=(0, 15))
        tk.Label(hb, text="A força abre portas. A preparação vence batalhas.", bg=PANEL, fg=TEXT, font=(FONT, 12, "bold")).pack(anchor="w")
        tk.Label(hb, text=f"Seu poder atual: {self.attack_stat()} ATQ  ·  {self.defense_stat()} DEF  ·  {self.max_hp()} HP    |    Missões: {count}/{self.total_missions()}", bg=PANEL, fg=MUTED, font=(FONT, 9)).pack(anchor="w", pady=(4, 0))
        for i, boss in enumerate(p["boss_data"]):
            defeated = boss["id"] in p["bosses_defeated"]
            unlocked = count >= boss["threshold"]
            card = tk.Frame(root, bg=PANEL if unlocked else "#12121b", highlightbackground=GOLD if defeated else (PURPLE if unlocked else BORDER), highlightthickness=1)
            card.pack(fill="x", pady=(0, 11))
            main = tk.Frame(card, bg=card.cget("bg")); main.pack(fill="x", padx=17, pady=15)
            sig = tk.Canvas(main, width=66, height=66, bg=card.cget("bg"), highlightthickness=0); sig.pack(side="left", padx=(0,15))
            sig.create_oval(5,5,61,61, fill="#3e1e35" if unlocked else "#242431", outline=GOLD if defeated else (RED if unlocked else BORDER), width=2)
            sig.create_text(33,33,text="✦" if defeated else ("☠" if unlocked else "?"), fill=GOLD if defeated else (RED if unlocked else MUTED), font=(FONT,21,"bold"))
            textf = tk.Frame(main, bg=card.cget("bg")); textf.pack(side="left", fill="x", expand=True)
            tk.Label(textf, text=f"GUARDIÃO {i+1:02d}  /  {('DERROTADO' if defeated else ('DISPONÍVEL' if unlocked else 'SELADO'))}", bg=card.cget("bg"), fg=MINT if defeated else (GOLD if unlocked else MUTED), font=(FONT, 8, "bold")).pack(anchor="w")
            tk.Label(textf, text=boss["name"], bg=card.cget("bg"), fg=TEXT if unlocked else "#827d91", font=(FONT, 14, "bold")).pack(anchor="w", pady=(3,2))
            tk.Label(textf, text=boss.get("subtitle",""), bg=card.cget("bg"), fg=MUTED, font=(FONT,9), wraplength=570, justify="left").pack(anchor="w")
            tk.Label(textf, text=f"Vida do chefe: {boss['hp']}  ·  Ataque: {boss['attack']}  ·  Recompensa: {boss['reward_xp']} XP / {boss['reward_gold']} ouro  ·  Libera com {boss['threshold']} missões", bg=card.cget("bg"), fg="#817b98", font=(FONT,8), wraplength=670, justify="left").pack(anchor="w", pady=(7,0))
            if defeated:
                self._button(main, "VITÓRIA  ✓", lambda:None, "mint", state="disabled").pack(side="right", padx=(8,0))
            elif unlocked:
                self._button(main, "ENTRAR NO DUELO  →", lambda b=boss:self.fight_boss(b), "danger").pack(side="right", padx=(8,0))
            else:
                self._button(main, "BLOQUEADO", lambda:None, "secondary", state="disabled").pack(side="right", padx=(8,0))

    def fight_boss(self, boss):
        p = self.profile
        w = tk.Toplevel(self)
        w.title(f"Duelo — {boss['name']}")
        w.geometry("620x600")
        w.resizable(False, False)
        w.configure(bg=BG)
        w.transient(self); w.grab_set()
        state = {"player_hp":self.max_hp(),"boss_hp":boss["hp"],"guard":False,"over":False}
        tk.Label(w, text="CÂMARA DE COMBATE", bg=BG, fg=PURPLE, font=(FONT,9,"bold")).pack(anchor="w", padx=24, pady=(20,4))
        tk.Label(w, text=boss["name"], bg=BG, fg=TEXT, font=(FONT,20,"bold"), wraplength=560).pack(anchor="w", padx=24)
        tk.Label(w, text=boss.get("subtitle",""), bg=BG, fg=MUTED, font=(FONT,9), wraplength=550, justify="left").pack(anchor="w", padx=24, pady=(3,18))
        statsf = tk.Frame(w, bg=PANEL, highlightbackground=BORDER, highlightthickness=1); statsf.pack(fill="x", padx=24, pady=(0,14))
        phpl = tk.Label(statsf, text="", bg=PANEL, fg=MINT, font=(FONT,9,"bold")); phpl.pack(anchor="w", padx=14, pady=(12,4))
        pbar = tk.Frame(statsf, bg="#2a2a3d", height=10); pbar.pack(fill="x", padx=14); pbar.pack_propagate(False)
        phpf = tk.Frame(pbar, bg=MINT); phpf.place(relx=0,rely=0,relheight=1,relwidth=1)
        bhpl = tk.Label(statsf, text="", bg=PANEL, fg=RED, font=(FONT,9,"bold")); bhpl.pack(anchor="w", padx=14, pady=(12,4))
        bbar = tk.Frame(statsf, bg="#2a2a3d", height=10); bbar.pack(fill="x", padx=14); bbar.pack_propagate(False)
        bhpf = tk.Frame(bbar, bg=RED); bhpf.place(relx=0,rely=0,relheight=1,relwidth=1)
        log = tk.Text(w, height=8, bg="#101019", fg="#d4cde7", insertbackground=TEXT, relief="flat", wrap="word", font=(FONT,9), padx=12,pady=10)
        log.pack(fill="both", expand=True, padx=24, pady=(0,12)); log.configure(state="disabled")
        actionf = tk.Frame(w,bg=BG); actionf.pack(fill="x", padx=24,pady=(0,22))
        close_btn = self._button(actionf,"FECHAR",w.destroy,"secondary",state="disabled")
        close_btn.pack(side="right")

        def write_log(message):
            log.configure(state="normal"); log.insert("end", message+"\n"); log.see("end"); log.configure(state="disabled")
        def update_bars():
            phpl.configure(text=f"VOCÊ  ·  {max(0,state['player_hp'])}/{self.max_hp()} HP")
            bhpl.configure(text=f"{boss['name']}  ·  {max(0,state['boss_hp'])}/{boss['hp']} HP")
            phpf.place_configure(relwidth=max(0,state['player_hp']/self.max_hp()))
            bhpf.place_configure(relwidth=max(0,state['boss_hp']/boss['hp']))
        def finish(victory):
            state["over"] = True
            for child in actionf.winfo_children():
                if child is not close_btn: child.configure(state="disabled")
            close_btn.configure(state="normal", text="ENCERRAR")
            if victory:
                p["bosses_defeated"].append(boss["id"])
                levels = self.gain_xp(boss["reward_xp"])
                p["gold"] += boss["reward_gold"]
                p["history"].append({"date":date.today().isoformat(),"type":"chefe","title":f"Derrotou {boss['name']}","xp":boss["reward_xp"],"gold":boss["reward_gold"]})
                self.update_streak()
                idx = p["boss_data"].index(boss)
                scene = "ending" if idx == len(p["boss_data"])-1 else f"boss_{idx+1}"
                p["story_seen"].append(scene) if scene not in p["story_seen"] else None
                self.save()
                write_log(f"VITÓRIA! +{boss['reward_xp']} XP · +{boss['reward_gold']} ouro.")
                if levels: write_log(f"Você subiu de nível! +{levels*2} pontos de atributo.")
                self.status_var.set(f"Guardião derrotado: {boss['name']}.")
                if scene == "ending":
                    w.after(500, lambda:self._after_final_boss(w))
                elif scene not in p.get("story_seen_shown", []):
                    w.after(500, lambda:self._after_boss_story(w, scene))
            else:
                write_log("Você recuou. Nenhuma recompensa foi perdida. Reforce equipamento ou complete novas missões e tente outra vez.")
        def enemy_turn(guarded=False):
            damage = max(3, boss["attack"] - self.defense_stat())
            if guarded: damage = max(1, damage // 3)
            state["player_hp"] -= damage
            write_log(f"{boss['name']} ataca e causa {damage} de dano.")
            if state["player_hp"] <= 0:
                update_bars(); finish(False); return
            update_bars()
        def attack():
            if state["over"]: return
            damage = max(4, self.attack_stat() + random.randint(-3,7))
            state["boss_hp"] -= damage
            write_log(f"Você ataca com precisão e causa {damage} de dano.")
            if state["boss_hp"] <= 0:
                state["boss_hp"] = 0; update_bars(); finish(True); return
            enemy_turn(False)
        def defend():
            if state["over"]: return
            write_log("Você assume uma postura defensiva e prepara o contra-ataque.")
            enemy_turn(True)
        def potion():
            if state["over"]: return
            if p.get("potions",0) <= 0:
                write_log("Você não tem elixires. Compre um no Arsenal antes do próximo duelo."); return
            p["potions"] -= 1
            heal = min(self.max_hp()-state["player_hp"], 35 + p["attributes"]["endurance"]*3)
            state["player_hp"] += heal
            write_log(f"Você usa um Elixir de Ânimo e recupera {heal} HP.")
            enemy_turn(False)
        self._button(actionf,"ATACAR",attack,"primary").pack(side="left",padx=(0,8))
        self._button(actionf,"DEFENDER",defend,"secondary").pack(side="left",padx=(0,8))
        self._button(actionf,f"ELIXIR ({p.get('potions',0)})",potion,"mint").pack(side="left",padx=(0,8))
        update_bars()
        write_log("O combate começou. Escolha uma ação a cada turno.")

    def _after_boss_story(self, window, scene):
        try: window.destroy()
        except Exception: pass
        self.render()
        self.show_story(scene)

    def _after_final_boss(self, window):
        try: window.destroy()
        except Exception: pass
        self.render()
        self.show_story("ending")

    # ------------------------------- ARMORY ---------------------------------
    def page_armory(self):
        root = self.build_scroll_page()
        p = self.profile
        statcard = self._card(root, "Equipamento e atributos", "CADA PEÇA MUDA O COMBATE")
        statcard.pack(fill="x", pady=(0,14))
        sb = tk.Frame(statcard,bg=PANEL); sb.pack(fill="x",padx=16,pady=(0,15))
        for col, (name,val,color) in enumerate([("ATAQUE",self.attack_stat(),RED),("DEFESA",self.defense_stat(),BLUE),("VIDA MÁXIMA",self.max_hp(),MINT),("FOCO",self.focus_stat(),PURPLE)]):
            box = tk.Frame(sb,bg=PANEL_2); box.grid(row=0,column=col,sticky="ew",padx=4)
            sb.grid_columnconfigure(col,weight=1)
            tk.Label(box,text=name,bg=PANEL_2,fg=MUTED,font=(FONT,7,"bold")).pack(anchor="w",padx=10,pady=(9,2))
            tk.Label(box,text=str(val),bg=PANEL_2,fg=color,font=(FONT,18,"bold")).pack(anchor="w",padx=10,pady=(0,9))
        equips = self._card(root,"Itens equipados","SLOTS ATIVOS")
        equips.pack(fill="x",pady=(0,14))
        eb = tk.Frame(equips,bg=PANEL); eb.pack(fill="x",padx=16,pady=(0,15))
        item_by_id = {i["id"]:i for i in SHOP_ITEMS}
        for slot,label in [("weapon","ARMA"),("armor","ARMADURA"),("charm","TALISMÃ")]:
            iid = p["equipped"].get(slot); item=item_by_id.get(iid) if iid else None
            row = tk.Frame(eb,bg=PANEL_2); row.pack(fill="x",pady=4)
            tk.Label(row,text=label,bg=PANEL_2,fg=GOLD,font=(FONT,8,"bold"),width=12,anchor="w").pack(side="left",padx=11,pady=10)
            tk.Label(row,text=item["name"] if item else "Slot vazio",bg=PANEL_2,fg=TEXT if item else MUTED,font=(FONT,10,"bold")).pack(side="left",fill="x",expand=True)
            if item:
                stats = f"ATQ +{item['attack']}  DEF +{item['defense']}  HP +{item['hp']}  FOCO +{item['focus']}"
                tk.Label(row,text=stats,bg=PANEL_2,fg=MUTED,font=(FONT,8)).pack(side="left",padx=10)
                self._button(row,"DESEQUIPAR",lambda s=slot:self.unequip(s),"secondary").pack(side="right",padx=9)
        self._section(root,"Mercado da Forja","COMPRE COM OURO CONQUISTADO")
        shop = tk.Frame(root,bg=BG); shop.pack(fill="x")
        for item in SHOP_ITEMS:
            if item["id"] == "weapon_training": continue
            row = tk.Frame(shop,bg=PANEL,highlightbackground=BORDER,highlightthickness=1); row.pack(fill="x",pady=(0,8))
            icon = tk.Label(row,text={"weapon":"⚔","armor":"⬡","charm":"✦","consumable":"♥"}.get(item["slot"],"◇"),bg=PANEL,fg=GOLD,font=(FONT,18,"bold"),width=4)
            icon.pack(side="left",padx=(8,0),pady=12)
            t = tk.Frame(row,bg=PANEL);t.pack(side="left",fill="x",expand=True,pady=12)
            tk.Label(t,text=item["name"],bg=PANEL,fg=TEXT,font=(FONT,11,"bold")).pack(anchor="w")
            tk.Label(t,text=item["desc"],bg=PANEL,fg=MUTED,font=(FONT,8),wraplength=550,justify="left").pack(anchor="w",pady=(3,4))
            tk.Label(t,text=f"ATQ +{item['attack']} · DEF +{item['defense']} · HP +{item['hp']} · FOCO +{item['focus']}",bg=PANEL,fg="#8f89a7",font=(FONT,8)).pack(anchor="w")
            right=tk.Frame(row,bg=PANEL);right.pack(side="right",padx=14)
            tk.Label(right,text=f"✦ {item['cost']}",bg=PANEL,fg=GOLD,font=(FONT,10,"bold")).pack(pady=(0,6))
            owned = item["id"] in p["inventory"]
            if item["slot"] == "consumable":
                self._button(right,"COMPRAR",lambda it=item:self.buy_item(it),"gold",state="normal" if p["gold"]>=item["cost"] else "disabled").pack()
            elif owned:
                self._button(right,"EQUIPAR",lambda it=item:self.equip_item(it),"secondary",state="disabled" if p["equipped"].get(item["slot"])==item["id"] else "normal").pack()
            else:
                self._button(right,"COMPRAR",lambda it=item:self.buy_item(it),"gold",state="normal" if p["gold"]>=item["cost"] else "disabled").pack()
        if p["gold"] < 60:
            tk.Label(root,text="Dica: missões, eventos e chefes rendem ouro. Não precisa comprar tudo — escolha peças que complementem seu estilo.",bg=BG,fg=MUTED,font=(FONT,9),wraplength=850,justify="left").pack(anchor="w",pady=10)

    def buy_item(self,item):
        p=self.profile
        if p["gold"]<item["cost"]:
            messagebox.showinfo("Ouro insuficiente","Conclua missões ou eventos para juntar mais ouro.");return
        p["gold"]-=item["cost"]
        if item["slot"]=="consumable":
            p["potions"] = p.get("potions",0)+1
        else:
            p["inventory"].append(item["id"])
            p["equipped"][item["slot"]]=item["id"]
        p["history"].append({"date":date.today().isoformat(),"type":"compra","title":f"Comprou {item['name']}","xp":0,"gold":-item["cost"]})
        self.save();self.render();self.status_var.set(f"Item adquirido: {item['name']}.")

    def equip_item(self,item):
        p=self.profile
        if item["id"] not in p["inventory"]:return
        p["equipped"][item["slot"]]=item["id"]
        self.save();self.render();self.status_var.set(f"Equipado: {item['name']}.")

    def unequip(self,slot):
        self.profile["equipped"][slot]=None
        self.save();self.render()

    # -------------------------------- EVENTS --------------------------------
    def page_events(self):
        root=self.build_scroll_page();p=self.profile
        today=date.today().isoformat()
        intro=self._card(root,"Quadro de contratos", "DESAFIOS DIÁRIOS")
        intro.pack(fill="x",pady=(0,14))
        ib=tk.Frame(intro,bg=PANEL);ib.pack(fill="x",padx=16,pady=(0,15))
        tk.Label(ib,text="Você não precisa de motivação infinita. Precisa de um próximo passo visível.",bg=PANEL,fg=TEXT,font=(FONT,11,"bold")).pack(anchor="w")
        tk.Label(ib,text=f"Data da sessão: {date.today().strftime('%d/%m/%Y')}  ·  Sequência atual: {p.get('streak',0)} dia(s)",bg=PANEL,fg=MUTED,font=(FONT,9)).pack(anchor="w",pady=(4,0))
        # Pomodoro
        timer=self._card(root,"Ritual de foco", "25 MINUTOS · SEM DISTRAÇÕES")
        timer.pack(fill="x",pady=(0,14))
        tb=tk.Frame(timer,bg=PANEL);tb.pack(fill="x",padx=16,pady=(0,16))
        self.timer_label=tk.Label(tb,text=self._fmt_time(self.timer_seconds),bg=PANEL,fg=GOLD,font=(FONT,34,"bold"))
        self.timer_label.pack(side="left",padx=(0,22))
        tt=tk.Frame(tb,bg=PANEL);tt.pack(side="left",fill="x",expand=True)
        tk.Label(tt,text="Uma sessão de estudo com uma meta concreta.",bg=PANEL,fg=TEXT,font=(FONT,10,"bold")).pack(anchor="w")
        tk.Label(tt,text="Ao zerar, o sistema registra a recompensa uma única vez por dia neste slot.",bg=PANEL,fg=MUTED,font=(FONT,8),wraplength=480,justify="left").pack(anchor="w",pady=(3,0))
        btns=tk.Frame(tb,bg=PANEL);btns.pack(side="right")
        self._button(btns,"INICIAR / RETOMAR",self.start_timer,"primary").pack(pady=(0,6),fill="x")
        self._button(btns,"PAUSAR",self.pause_timer,"secondary").pack(pady=(0,6),fill="x")
        self._button(btns,"REINICIAR",self.reset_timer,"secondary").pack(fill="x")
        events=[
            ("revisao","Ritual de revisão","Escolha uma matéria que estudou antes e tente recuperar os pontos principais sem consultar o material.",25,12),
            ("questoes","Três provas do Oráculo","Responda a três questões do Códice e anote o assunto que merece nova revisão.",35,16),
            ("planejamento","Mapa do amanhã","Defina por escrito a próxima tarefa e deixe o material pronto para reduzir a fricção de começar.",20,10),
        ]
        self._section(root,"Contratos diários","RECOMPENSAS UMA VEZ POR DATA")
        for key,title,desc,xp,gold in events:
            claimed=p.get("event_claims",{}).get(key)==today
            c=tk.Frame(root,bg=PANEL,highlightbackground=MINT if claimed else BORDER,highlightthickness=1);c.pack(fill="x",pady=(0,9))
            row=tk.Frame(c,bg=PANEL);row.pack(fill="x",padx=16,pady=14)
            tk.Label(row,text="✓" if claimed else "✦",bg=PANEL,fg=MINT if claimed else GOLD,font=(FONT,18,"bold"),width=3).pack(side="left",padx=(0,9))
            textf=tk.Frame(row,bg=PANEL);textf.pack(side="left",fill="x",expand=True)
            tk.Label(textf,text=title,bg=PANEL,fg=TEXT,font=(FONT,11,"bold")).pack(anchor="w")
            tk.Label(textf,text=desc,bg=PANEL,fg=MUTED,font=(FONT,9),wraplength=650,justify="left").pack(anchor="w",pady=(3,4))
            tk.Label(textf,text=f"RECOMPENSA  +{xp} XP  ·  +{gold} OURO",bg=PANEL,fg=GOLD,font=(FONT,8,"bold")).pack(anchor="w")
            self._button(row,"CONCLUÍDO ✓" if claimed else "REGISTRAR DESAFIO",lambda k=key,t=title,x=xp,g=gold:self.claim_event(k,t,x,g),"mint" if not claimed else "secondary",state="disabled" if claimed else "normal").pack(side="right",padx=(8,0))
        note=self._card(root,"Regra de ouro","GAMIFICAÇÃO COMO APOIO, NÃO COMO CULPA")
        note.pack(fill="x",pady=(8,0))
        tk.Label(note,text="Se perder um dia, volte no seguinte. A sequência serve para tornar o hábito visível, não para transformar uma pausa em fracasso.",bg=PANEL,fg=MUTED,font=(FONT,9),wraplength=900,justify="left").pack(anchor="w",padx=16,pady=(0,15))

    def _fmt_time(self,seconds):
        return f"{max(0,seconds)//60:02d}:{max(0,seconds)%60:02d}"

    def start_timer(self):
        if self.timer_running: return
        if self.timer_seconds<=0: self.timer_seconds=25*60
        self.timer_running=True
        self._tick_timer()
        self.status_var.set("Sessão de foco iniciada. Uma coisa de cada vez.")

    def _tick_timer(self):
        if not self.timer_running:return
        if self.timer_seconds>0:self.timer_seconds-=1
        if hasattr(self,"timer_label") and self.timer_label.winfo_exists():self.timer_label.configure(text=self._fmt_time(self.timer_seconds))
        if self.timer_seconds<=0:
            self.timer_running=False
            key="foco";today=date.today().isoformat()
            if self.profile.get("event_claims",{}).get(key)!=today:
                self.profile.setdefault("event_claims",{})[key]=today
                self.add_reward(55,25,"Sessão de foco concluída")
                messagebox.showinfo("Sessão concluída","Você ficou 25 minutos com a atenção na tarefa. Recompensa registrada.")
            else:
                self.status_var.set("O cronômetro terminou. A recompensa de foco de hoje já foi recebida.")
            if hasattr(self,"timer_label") and self.timer_label.winfo_exists():self.timer_label.configure(text="00:00")
            return
        self.timer_job=self.after(1000,self._tick_timer)

    def pause_timer(self):
        self.timer_running=False
        if self.timer_job:
            try:self.after_cancel(self.timer_job)
            except Exception:pass
            self.timer_job=None
        self.status_var.set("Sessão pausada. Retome quando estiver pronto.")

    def reset_timer(self):
        self.pause_timer();self.timer_seconds=25*60
        if hasattr(self,"timer_label") and self.timer_label.winfo_exists():self.timer_label.configure(text=self._fmt_time(self.timer_seconds))

    def claim_event(self,key,title,xp,gold):
        today=date.today().isoformat()
        if self.profile.get("event_claims",{}).get(key)==today:return
        self.profile.setdefault("event_claims",{})[key]=today
        self.add_reward(xp,gold,title)

    # -------------------------------- CODEX ---------------------------------
    def _custom_quiz_items(self):
        raw=self.profile.get("custom_quiz_text","")
        items=[]
        for n,line in enumerate(raw.splitlines(),1):
            if not line.strip() or line.strip().startswith("#"):continue
            parts=[x.strip() for x in line.split("|")]
            if len(parts)<8:continue
            correct=parts[6].upper()
            if correct not in "ABCD":continue
            items.append({"id":f"customq{n}","subject":parts[0],"q":parts[1],"options":parts[2:6],"a":"ABCD".index(correct),"why":parts[7]})
        return items

    def quiz_items(self):
        if self.active_key=="python": base=PYTHON_QUIZ
        elif self.active_key=="caixa": base=CAIXA_QUIZ
        else: base=[]
        return list(base)+self._custom_quiz_items()

    def page_codex(self):
        root=self.build_scroll_page();p=self.profile
        head=self._card(root,"Códice do conhecimento","RECUPERAÇÃO ATIVA")
        head.pack(fill="x",pady=(0,14))
        hb=tk.Frame(head,bg=PANEL);hb.pack(fill="x",padx=16,pady=(0,15))
        tk.Label(hb,text="Tente responder antes de reler. Errar aqui é barato: é assim que você descobre o que precisa revisar.",bg=PANEL,fg=TEXT,font=(FONT,10,"bold"),wraplength=900,justify="left").pack(anchor="w")
        items=self.quiz_items()
        answered=len(p.get("quiz_answered",[]))
        tk.Label(hb,text=f"Questões disponíveis: {len(items)}  ·  Já respondidas neste slot: {answered}",bg=PANEL,fg=MUTED,font=(FONT,9)).pack(anchor="w",pady=(5,0))
        qcard=self._card(root,"Desafio atual","UMA QUESTÃO POR VEZ")
        qcard.pack(fill="x",pady=(0,14))
        qb=tk.Frame(qcard,bg=PANEL);qb.pack(fill="x",padx=16,pady=(0,16))
        if not items:
            tk.Label(qb,text="Este slot ainda não possui questões. No slot personalizado, adicione-as na Configuração usando o formato indicado.",bg=PANEL,fg=MUTED,font=(FONT,10),wraplength=850,justify="left").pack(anchor="w",pady=12)
        else:
            if not self.current_question or self.current_question not in items:
                unseen=[q for q in items if q["id"] not in p.get("quiz_answered",[])]
                self.current_question=random.choice(unseen or items)
                self.current_answered=False
            q=self.current_question
            tk.Label(qb,text=q.get("subject","GERAL").upper(),bg="#2c2440",fg=PURPLE,font=(FONT,8,"bold"),padx=8,pady=4).pack(anchor="w",pady=(0,10))
            tk.Label(qb,text=q["q"],bg=PANEL,fg=TEXT,font=(FONT,13,"bold"),wraplength=880,justify="left").pack(anchor="w",pady=(0,14))
            self.quiz_option_buttons = []
            for idx,opt in enumerate(q["options"]):
                already=self.current_answered
                def answer(i=idx, question=q): self.answer_quiz(question,i,feedback)
                b=self._button(qb,f"{chr(65+idx)}   {opt}",answer,"secondary",state="disabled" if already else "normal")
                b.configure(anchor="w",justify="left",wraplength=820)
                b.pack(fill="x",pady=4)
                self.quiz_option_buttons.append(b)
            feedback=tk.Frame(qb,bg=PANEL)
            feedback.pack(fill="x",pady=(10,0))
            if self.current_answered:
                previous=p.get("quiz_answered",[])
                tk.Label(feedback,text="Questão já respondida nesta jornada. Você ainda pode revisar a explicação.",bg=PANEL,fg=MUTED,font=(FONT,9)).pack(anchor="w")
                self._button(feedback,"PRÓXIMA QUESTÃO  →",self.next_question,"primary").pack(anchor="e",pady=(10,0))
            else:
                self._button(feedback,"PULAR / VER OUTRA",self.next_question,"quiet").pack(anchor="e",pady=(8,0))
        self._section(root,"Como usar o Códice","APRENDER SEM CULPA")
        guide=self._card(root)
        guide.pack(fill="x")
        tk.Label(guide,text="1. Responda sem consultar o material.  2. Leia a explicação.  3. Volte ao conteúdo se houver dúvida.  4. Para o slot personalizado, crie questões com alternativas e gabarito próprio.",bg=PANEL,fg=MUTED,font=(FONT,9),wraplength=900,justify="left").pack(anchor="w",padx=16,pady=15)

    def answer_quiz(self,question,idx,feedback_frame):
        p=self.profile
        correct=idx==question["a"]
        first=question["id"] not in p.get("quiz_answered",[])
        p.setdefault("quiz_answered",[]).append(question["id"]) if first else None
        for w in feedback_frame.winfo_children():w.destroy()
        color=MINT if correct else RED
        msg="CORRETO!" if correct else f"AINDA NÃO. A resposta é {chr(65+question['a'])}."
        tk.Label(feedback_frame,text=msg,bg=PANEL,fg=color,font=(FONT,11,"bold")).pack(anchor="w")
        tk.Label(feedback_frame,text=question.get("why","Revise o tema e tente novamente."),bg=PANEL,fg=MUTED,font=(FONT,9),wraplength=850,justify="left").pack(anchor="w",pady=(5,0))
        if first and correct:
            p["gold"]+=3; levels=self.gain_xp(8)
            p["history"].append({"date":date.today().isoformat(),"type":"questão","title":f"Acertou: {question['subject']}","xp":8,"gold":3})
            self.update_streak()
            tk.Label(feedback_frame,text="Recompensa: +8 XP · +3 ouro",bg=PANEL,fg=GOLD,font=(FONT,8,"bold")).pack(anchor="w",pady=(5,0))
        elif first:
            p["history"].append({"date":date.today().isoformat(),"type":"questão","title":f"Revisou: {question['subject']}","xp":0,"gold":0})
        self.current_answered=True
        for option_button in getattr(self, "quiz_option_buttons", []):
            try: option_button.configure(state="disabled")
            except Exception: pass
        self.save()
        self._render_sidebar()
        self._render_header()

    def next_question(self):
        self.current_question=None;self.current_answered=False;self.render()

    # ------------------------------ SETTINGS -------------------------------
    def page_settings(self):
        root=self.build_scroll_page();p=self.profile;s=p["settings"]
        note=self._card(root,"Personalizar este slot","ALTERAÇÕES SALVAS APENAS NESTA JORNADA")
        note.pack(fill="x",pady=(0,14))
        nb=tk.Frame(note,bg=PANEL);nb.pack(fill="x",padx=16,pady=(0,14))
        tk.Label(nb,text="O terceiro slot pode virar qualquer jornada. Você pode também personalizar os outros perfis; as alterações permanecem salvas no próprio slot.",bg=PANEL,fg=MUTED,font=(FONT,9),wraplength=900,justify="left").pack(anchor="w")
        form=self._card(root,"Identidade da campanha","NOME, PERSONAGEM E NARRATIVA")
        form.pack(fill="x",pady=(0,14))
        fb=tk.Frame(form,bg=PANEL);fb.pack(fill="x",padx=16,pady=(0,16))
        fields={}
        def add_entry(label,key,value):
            row=tk.Frame(fb,bg=PANEL);row.pack(fill="x",pady=5)
            tk.Label(row,text=label,bg=PANEL,fg=MUTED,font=(FONT,8,"bold"),width=23,anchor="w").pack(side="left")
            ent=tk.Entry(row,bg=PANEL_2,fg=TEXT,insertbackground=TEXT,relief="flat",font=(FONT,10))
            ent.pack(side="left",fill="x",expand=True,ipady=7)
            ent.insert(0,value);fields[key]=ent
        add_entry("Nome da campanha","title",s.get("title",""))
        add_entry("Nome do personagem","hero",s.get("hero",""))
        add_entry("Classe / arquétipo","archetype",s.get("archetype",""))
        tk.Label(fb,text="Sinopse e motivação",bg=PANEL,fg=MUTED,font=(FONT,8,"bold")).pack(anchor="w",pady=(8,4))
        story_text=tk.Text(fb,height=4,bg=PANEL_2,fg=TEXT,insertbackground=TEXT,relief="flat",wrap="word",font=(FONT,9),padx=8,pady=7)
        story_text.pack(fill="x");story_text.insert("1.0",s.get("intro",""))

        content=self._card(root,"Trilha de estudo","UM TEMA POR LINHA")
        content.pack(fill="x",pady=(0,14))
        cb=tk.Frame(content,bg=PANEL);cb.pack(fill="x",padx=16,pady=(0,16))
        tk.Label(cb,text="Temas / módulos",bg=PANEL,fg=MUTED,font=(FONT,8,"bold")).pack(anchor="w",pady=(0,4))
        topics_text=tk.Text(cb,height=8,bg=PANEL_2,fg=TEXT,insertbackground=TEXT,relief="flat",wrap="word",font=(FONT,9),padx=8,pady=7)
        topics_text.pack(fill="x")
        topics_text.insert("1.0","\n".join(s.get("topics",[])))
        tk.Label(cb,text="Se você alterar a lista de temas, novas missões genéricas serão montadas para cada tema (teoria, prática/questões e revisão). Missões já concluídas serão preservadas quando os IDs continuarem iguais.",bg=PANEL,fg=MUTED,font=(FONT,8),wraplength=900,justify="left").pack(anchor="w",pady=(6,12))
        tk.Label(cb,text="Missões personalizadas (opcional)",bg=PANEL,fg=MUTED,font=(FONT,8,"bold")).pack(anchor="w",pady=(0,4))
        missions_text=tk.Text(cb,height=6,bg=PANEL_2,fg=TEXT,insertbackground=TEXT,relief="flat",wrap="word",font=("Consolas",9),padx=8,pady=7)
        missions_text.pack(fill="x")
        missions_text.insert("1.0",s.get("missions_text",""))
        tk.Label(cb,text="Uma missão por linha: TEMA | TÍTULO | DESCRIÇÃO | XP | OURO. Se deixar vazio, a trilha gera três missões por tema.",bg=PANEL,fg=MUTED,font=(FONT,8),wraplength=900,justify="left").pack(anchor="w",pady=(5,0))

        bosses=self._card(root,"Chefes e história","UM GUARDIÃO POR LINHA")
        bosses.pack(fill="x",pady=(0,14))
        bb=tk.Frame(bosses,bg=PANEL);bb.pack(fill="x",padx=16,pady=(0,16))
        boss_text=tk.Text(bb,height=5,bg=PANEL_2,fg=TEXT,insertbackground=TEXT,relief="flat",wrap="word",font=(FONT,9),padx=8,pady=7)
        boss_text.pack(fill="x");boss_text.insert("1.0","\n".join(s.get("boss_names",[x[0] for x in BOSS_NAMES])))
        tk.Label(bb,text="As batalhas liberam conforme você conclui missões. O último chefe exige 100% da trilha.",bg=PANEL,fg=MUTED,font=(FONT,8)).pack(anchor="w",pady=(5,0))

        quiz=self._card(root,"Questões personalizadas","FORMATO COM ALTERNATIVAS A–D")
        quiz.pack(fill="x",pady=(0,14))
        qbox=tk.Frame(quiz,bg=PANEL);qbox.pack(fill="x",padx=16,pady=(0,16))
        qtext=tk.Text(qbox,height=5,bg=PANEL_2,fg=TEXT,insertbackground=TEXT,relief="flat",wrap="word",font=("Consolas",9),padx=8,pady=7)
        qtext.pack(fill="x");qtext.insert("1.0",p.get("custom_quiz_text",""))
        tk.Label(qbox,text="Uma questão por linha: TEMA | PERGUNTA | OPÇÃO A | OPÇÃO B | OPÇÃO C | OPÇÃO D | GABARITO A/B/C/D | EXPLICAÇÃO. Use | como separador e evite esse caractere no texto.",bg=PANEL,fg=MUTED,font=(FONT,8),wraplength=900,justify="left").pack(anchor="w",pady=(5,0))

        actions=tk.Frame(root,bg=BG);actions.pack(fill="x",pady=(0,15))
        def apply_settings():
            old_topics=s.get("topics",[])
            new_topics=[line.strip() for line in topics_text.get("1.0","end").splitlines() if line.strip()]
            if not new_topics:
                messagebox.showwarning("Trilha vazia","Adicione ao menos um tema antes de salvar.");return
            for key,ent in fields.items(): s[key]=ent.get().strip() or s.get(key,"")
            s["intro"]=story_text.get("1.0","end").strip()
            custom_lines=missions_text.get("1.0","end").strip()
            old_missions=p["mission_data"]
            if custom_lines:
                new_missions=[]
                for i,line in enumerate(custom_lines.splitlines(),1):
                    if not line.strip() or line.strip().startswith("#"):continue
                    parts=[x.strip() for x in line.split("|")]
                    if len(parts)<5:
                        messagebox.showwarning("Formato de missão",f"Linha {i} precisa ter: TEMA | TÍTULO | DESCRIÇÃO | XP | OURO.");return
                    new_missions.append({"id":f"user_{i}","topic":parts[0],"title":parts[1],"description":parts[2],"xp":max(0,safe_int(parts[3],30)),"coins":max(0,safe_int(parts[4],10)),"kind":"study"})
                if not new_missions:
                    messagebox.showwarning("Missões vazias","Não encontrei missões válidas.");return
                p["mission_data"]=new_missions
                p["completed_missions"]=[mid for mid in p["completed_missions"] if mid in {m["id"] for m in new_missions}]
            elif new_topics != old_topics:
                p["mission_data"]=self.make_generic_missions(new_topics)
                p["completed_missions"]=[mid for mid in p["completed_missions"] if mid in {m["id"] for m in p["mission_data"]}]
            s["topics"]=new_topics
            s["missions_text"]=custom_lines
            names=[line.strip() for line in boss_text.get("1.0","end").splitlines() if line.strip()]
            if not names:names=["O Guardião da Última Página"]
            old_bosses=p["boss_data"]
            new_bosses=[]
            total=len(p["mission_data"])
            for i,name in enumerate(names):
                prior=old_bosses[i] if i<len(old_bosses) else {}
                is_final=i==len(names)-1
                new_bosses.append({"id":prior.get("id",f"{self.active_key}_boss_{i+1}"),"name":name,"subtitle":prior.get("subtitle","Uma prova criada para esta jornada."),"threshold":total if is_final else max(1,int(total*(i+1)/len(names))),"hp":prior.get("hp",120+i*65),"attack":prior.get("attack",8+i*3),"reward_xp":prior.get("reward_xp",70+i*25),"reward_gold":prior.get("reward_gold",45+i*20)})
            s["boss_names"]=names
            p["boss_data"]=new_bosses
            p["bosses_defeated"]=[bid for bid in p["bosses_defeated"] if bid in {b["id"] for b in new_bosses}]
            p["custom_quiz_text"]=qtext.get("1.0","end").strip()
            self.save();self.render()
            self.status_var.set("Configurações da jornada salvas.")
            messagebox.showinfo("Configuração salva","Sua campanha foi atualizada. O progresso das missões cujos IDs foram mantidos continua salvo.")
        self._button(actions,"SALVAR PERSONALIZAÇÃO  ✓",apply_settings,"primary").pack(side="left",padx=(0,8))
        self._button(actions,"EXPORTAR SAVE JSON",self.export_save,"secondary").pack(side="left",padx=(0,8))
        self._button(actions,"IMPORTAR SAVE JSON",self.import_save,"secondary").pack(side="left")

    def make_generic_missions(self,topics):
        suffixes=PYTHON_MISSION_SUFFIXES if self.active_key=="python" else CAIXA_MISSION_SUFFIXES
        missions=[]
        for i,topic in enumerate(topics):
            for j,(verb,how,xp,coins) in enumerate(suffixes):
                missions.append({"id":f"custom_{i+1}_{j+1}","topic":topic,"title":f"{topic}: {verb}","description":how,"xp":xp,"coins":coins,"kind":"study"})
        return missions

    def export_save(self):
        path=filedialog.asksaveasfilename(title="Exportar save",defaultextension=".json",filetypes=[("Arquivo JSON","*.json")],initialfile="hunter_system_save.json")
        if not path:return
        try:
            with open(path,"w",encoding="utf-8") as f:json.dump(self.data,f,ensure_ascii=False,indent=2)
            messagebox.showinfo("Exportado",f"Backup salvo em:\n{path}")
        except Exception as exc:messagebox.showerror("Erro ao exportar",str(exc))

    def import_save(self):
        path=filedialog.askopenfilename(title="Importar save",filetypes=[("Arquivo JSON","*.json")])
        if not path:return
        if not messagebox.askyesno("Substituir progresso?","A importação substituirá o progresso atual nos slots. Recomenda-se exportar um backup antes. Continuar?"):return
        try:
            with open(path,"r",encoding="utf-8") as f:incoming=json.load(f)
            if not isinstance(incoming,dict) or not isinstance(incoming.get("profiles"),dict):raise ValueError("Formato de save inválido.")
            fresh=create_save()
            for key in ("python","caixa","custom"):
                if key in incoming["profiles"]:fresh["profiles"][key]=incoming["profiles"][key]
            fresh["active_profile"]=incoming.get("active_profile","python")
            self.data=fresh;self.active_key=fresh["active_profile"] if fresh["active_profile"] in fresh["profiles"] else "python"
            self.save();self.render();messagebox.showinfo("Importado","Progresso importado com sucesso.")
        except Exception as exc:messagebox.showerror("Erro ao importar",f"Arquivo inválido ou incompatível.\n\n{exc}")

    # ------------------------------- STORY ---------------------------------
    def show_story(self, scene, replay=False):
        p=self.profile
        lines=STORY.get(scene)
        if not lines:
            lines=[("ÍRIA","A próxima página ainda não foi escrita. Continue sua jornada e volte depois.")]
        w=tk.Toplevel(self);w.title("Crônicas da Cidade Sem Aurora")
        w.geometry("650x430");w.resizable(False,False);w.configure(bg="#100e18");w.transient(self);w.grab_set()
        canvas=tk.Canvas(w,width=650,height=5,bg=PURPLE,highlightthickness=0);canvas.pack(fill="x")
        tk.Label(w,text="CRÔNICAS  /  CIDADE SEM AURORA",bg="#100e18",fg=GOLD,font=(FONT,8,"bold")).pack(anchor="w",padx=28,pady=(24,8))
        tk.Label(w,text={"intro":"A CHAMA QUE RESTOU","boss_1":"A PRIMEIRA PORTA","boss_2":"A MEMÓRIA DA NÉVOA","boss_3":"O MAPA INVISÍVEL","boss_4":"A ÚLTIMA PONTE","ending":"O FIM DA ÚLTIMA PÁGINA"}.get(scene,"UM FRAGMENTO DA CRÔNICA"),bg="#100e18",fg=TEXT,font=(FONT,18,"bold")).pack(anchor="w",padx=28)
        speaker=tk.Label(w,text="",bg="#100e18",fg=PURPLE,font=(FONT,9,"bold"));speaker.pack(anchor="w",padx=28,pady=(20,6))
        body=tk.Label(w,text="",bg="#100e18",fg="#d8d1e8",font=(FONT,11),wraplength=590,justify="left",anchor="nw")
        body.pack(fill="both",expand=True,padx=28,pady=(0,12))
        footer=tk.Frame(w,bg="#100e18");footer.pack(fill="x",padx=28,pady=(0,22))
        counter=tk.Label(footer,text="",bg="#100e18",fg=MUTED,font=(FONT,8));counter.pack(side="left")
        btn=self._button(footer,"CONTINUAR  →",lambda:None,"primary");btn.pack(side="right")
        i={"n":0}
        def next_line():
            if i["n"]>=len(lines):
                if scene not in p.get("story_seen",[]):p.setdefault("story_seen",[]).append(scene)
                self.save();w.destroy();self.render();return
            who,dialogue=lines[i["n"]]
            speaker.configure(text=who.upper())
            body.configure(text=dialogue)
            counter.configure(text=f"FRAGMENTO {i['n']+1:02d} / {len(lines):02d}")
            i["n"]+=1
            btn.configure(text="ENCERRAR  ✓" if i["n"]>=len(lines) else "CONTINUAR  →")
        btn.configure(command=next_line)
        next_line()

    def on_close(self):
        self.pause_timer()
        self.save()
        self.destroy()


def main():
    app=HunterSystem()
    app.mainloop()

if __name__=="__main__":
    main()
