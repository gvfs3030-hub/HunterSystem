from __future__ import annotations
import json, os, random, sys, textwrap, zipfile, shutil, webbrowser
import calendar as pycalendar
from datetime import date, timedelta, datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from game_data import (
    create_save, default_profile, PYTHON_PHASES, CAIXA_SUBJECTS,
    PYTHON_MISSION_SUFFIXES, CAIXA_MISSION_SUFFIXES, PYTHON_QUIZ,
    CAIXA_QUIZ, SHOP_ITEMS, STORY, BOSS_NAMES,
)
from campaign_data import build_campaign_missions, chapter_boss_thresholds
from schedule_system import ensure_calendar, day_summary, estimated_minutes, priority_label, reviews_for_date
from adaptive_planner import (subject_metrics, block_readiness, estimate_readiness, exam_pace, next_spacing_date, build_adaptive_question_set, build_caixa_weighted_mock, OBJECTIVE_QUESTIONS, mission_subject)

APP_NAME = "HUNTER SYSTEM — CRÔNICAS DA FORJA"
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
        self.title("Hunter System — Crônicas da Forja")
        self.geometry("1280x820")
        self.minsize(1000, 650)
        self.configure(bg=BG)
        self._apply_window_icon()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self._setup_style()
        self.save_file = save_path()
        self.data = self._load_save()
        self.active_key = self.data.get("active_profile", "python")
        if self.active_key not in self.data["profiles"]:
            self.active_key = "python"
        self.page = "Santuário"
        self.calendar_selected = date.today()
        self.calendar_month = date.today().replace(day=1)
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
        self.after(900, self._announce_due_reviews)

    @property
    def profile(self):
        return self.data["profiles"][self.active_key]

    def _asset_path(self, name):
        """Resolve resources both in source mode and inside PyInstaller's one-file bundle."""
        root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
        return root / "assets" / name

    def _apply_window_icon(self):
        try:
            icon = self._asset_path("hunter_crest.ico")
            if icon.exists():
                self.iconbitmap(str(icon))
        except Exception:
            # Canvas emblem remains available when an OS/theme does not accept .ico.
            pass

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
                        # Migration from the earlier mission-list prototype to the linear campaign.
                        # Keep character/equipment/economy/history, but make the new curriculum its own fresh path.
                        saved = raw["profiles"][key]
                        seed = base["profiles"][key]
                        if safe_int(saved.get("campaign_schema", 0)) < 3:
                            # Preserve character/economy/history and any progress whose stable lesson IDs still exist.
                            # Older prototype missions with different IDs cannot safely map to the new linear curriculum.
                            old_completed = set(saved.get("completed_missions", []))
                            old_reviews = saved.get("review_queue", []) if isinstance(saved.get("review_queue", []), list) else []
                            old_bosses = set(saved.get("bosses_defeated", []))
                            for field in ("level", "xp", "gold", "attributes", "attribute_points", "inventory", "equipped", "potions", "last_study_date", "streak", "history", "event_claims", "notes", "custom_quiz_text", "settings", "lesson_notes", "quiz_stats", "story_seen", "story_chapters_seen", "boss_exam_results"):
                                if field not in saved:
                                    saved[field] = seed.get(field)
                            saved["mission_data"] = seed["mission_data"]
                            saved["boss_data"] = seed["boss_data"]
                            valid_ids = {m["id"] for m in seed["mission_data"]}
                            valid_boss_ids = {b["id"] for b in seed["boss_data"]}
                            saved["completed_missions"] = [mid for mid in old_completed if mid in valid_ids]
                            saved["bosses_defeated"] = [bid for bid in old_bosses if bid in valid_boss_ids]
                            saved["review_queue"] = [r for r in old_reviews if isinstance(r, dict) and r.get("lesson_id") in valid_ids]
                            saved["campaign_schema"] = 3
                            saved.setdefault("history", []).append({"date": date.today().isoformat(), "type": "sistema", "title": "Campanha Crônicas da Forja atualizada", "xp": 0, "gold": 0})
                        for k, v in seed.items():
                            saved.setdefault(k, v)
                        if not isinstance(saved.get("mission_data"), list) or not saved["mission_data"]:
                            saved["mission_data"] = seed["mission_data"]
                        saved["campaign_schema"] = 3
                raw.setdefault("active_profile", "python")
                raw["version"] = 3
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
        elif self.page in ("Campanha", "Missões"): self.page_campaign()
        elif self.page == "Calendário": self.page_calendar()
        elif self.page == "Estratégia": self.page_strategy()
        elif self.page == "Revisões": self.page_reviews()
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
        try:
            # Brand artwork: eclipsed portal, open grimoire and golden relic.
            self.sidebar_logo_image = tk.PhotoImage(file=str(self._asset_path("hunter_crest_small.png")))
            tk.Label(logo, image=self.sidebar_logo_image, bg=SIDEBAR, bd=0).pack(side="left", padx=(0, 10))
        except Exception:
            emblem = tk.Canvas(logo, width=48, height=48, bg=SIDEBAR, highlightthickness=0)
            emblem.pack(side="left", padx=(0, 10))
            emblem.create_oval(2, 2, 46, 46, outline="#6e4b96", width=1)
            emblem.create_oval(6, 6, 42, 42, outline=GOLD, width=1)
            emblem.create_polygon(24, 7, 36, 14, 34, 29, 24, 39, 14, 29, 12, 14, fill=PURPLE_DARK, outline=GOLD, width=1)
            emblem.create_polygon(24, 10, 29, 23, 24, 29, 19, 23, fill="#f4f0ff", outline=GOLD, width=1)
            emblem.create_line(24, 25, 24, 34, fill=GOLD, width=2)
            emblem.create_line(18, 29, 30, 29, fill=GOLD, width=2)
            emblem.create_line(14, 34, 23, 37, fill="#f4f0ff", width=1)
            emblem.create_line(25, 37, 34, 34, fill="#f4f0ff", width=1)
        brand = tk.Frame(logo, bg=SIDEBAR)
        brand.pack(side="left", fill="y")
        tk.Label(brand, text="HUNTER", bg=SIDEBAR, fg=TEXT, font=(FONT, 15, "bold")).pack(anchor="w")
        tk.Label(brand, text="CRÔNICAS  /  DA FORJA", bg=SIDEBAR, fg=PURPLE, font=(FONT, 7, "bold")).pack(anchor="w")
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
        nav = [("Santuário", "⌂"), ("Campanha", "✦"), ("Calendário", "▦"), ("Estratégia", "◈"), ("Revisões", "↻"), ("Chefes", "⚔"), ("Arsenal", "◇"), ("Eventos", "◷"), ("Códice", "▤"), ("Configuração", "⚙")]
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
        tk.Label(bottom, text=f"{len(self.profile['completed_missions'])}/{len(self.profile['mission_data'])} tópicos dominados", bg="#191824", fg=MUTED, font=(FONT, 8)).pack(anchor="w", padx=11, pady=(0, 10))

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
        # Backwards-compatible entry point. A topic can no longer be checked off without its test.
        mission = next((m for m in self.profile["mission_data"] if m["id"] == mission_id), None)
        if mission:
            self.start_lesson(mission)

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
        setting_kicker = {"python":"A CIDADE SEM AURORA  /  CAPÍTULO I", "caixa":"O ARQUIVO DOS ECOS  /  CAPÍTULO I", "custom":"O MAPA EM BRANCO  /  CAPÍTULO I"}.get(self.active_key, "CRÔNICAS DA FORJA")
        tk.Label(left, text=setting_kicker, bg="#20172f", fg=GOLD, font=(FONT, 8, "bold")).pack(anchor="w")
        tk.Label(left, text=p["settings"]["hero"], bg="#20172f", fg=TEXT, font=(FONT, 22, "bold")).pack(anchor="w", pady=(5, 3))
        tk.Label(left, text=p["settings"]["intro"], bg="#20172f", fg="#d5cde8", font=(FONT, 10), wraplength=510, justify="left").pack(anchor="w", pady=(0, 9 if self.active_key == "caixa" else 15))
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
        self._button(actions, "RETOMAR A JORNADA  →", lambda:self.navigate("Campanha"), "primary").pack(side="left", padx=(0, 8))
        self._button(actions, "OUVIR A HISTÓRIA", lambda:self.show_story("intro", replay=True), "secondary").pack(side="left")
        self._button(actions, "ABRIR CALENDÁRIO  ▦", lambda:self.navigate("Calendário"), "gold").pack(side="left", padx=(8, 0))
        art = tk.Frame(hero, bg="#20172f", highlightbackground="#65458b", highlightthickness=1)
        art.grid(row=0, column=1, padx=20, pady=14, sticky="e")
        try:
            # A compact panorama gives the sanctuary a real game-world instead of a placeholder emblem.
            self.dashboard_scene_image = tk.PhotoImage(file=str(self._asset_path("citadel_panorama.png"))).subsample(3, 3)
            tk.Label(art, image=self.dashboard_scene_image, bg="#20172f", bd=0).pack()
        except Exception:
            tk.Label(art, text="◈  CIDADE SEM AURORA  ◈", bg="#20172f", fg=GOLD,
                     font=(FONT, 10, "bold"), width=28, height=7).pack()
        tk.Label(art, text="A FORJA ESTÁ ACESA  ·  UM DIA DE CADA VEZ", bg="#20172f", fg=GOLD,
                 font=(FONT, 7, "bold")).pack(fill="x", pady=(5, 7))

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

        self._section(leftcol, "A próxima página", "UMA MISSÃO LIBERADA POR VEZ")
        mission = self.next_lesson()
        waiting_boss = self.pending_guardian()
        blocked_by_boss = bool(mission and waiting_boss and mission.get("global_index", 0) > waiting_boss.get("threshold", 0))
        if blocked_by_boss:
            msg = self._card(leftcol, f"O guardião aguarda: {waiting_boss['name']}", "CHECKPOINT DA CAMPANHA")
            msg.pack(fill="x")
            tk.Label(msg, text="Você concluiu o trecho exigido. A próxima região só será aberta depois da prova cumulativa e do combate. Reforce o equipamento, se precisar.", bg=PANEL, fg=MUTED, wraplength=600, justify="left").pack(anchor="w", padx=16, pady=(0, 15))
            self._button(msg, "IR À CÂMARA DOS GUARDIÕES  ⚔", lambda:self.navigate("Chefes"), "danger").pack(anchor="w", padx=16, pady=(0, 14))
        elif not mission:
            msg = self._card(leftcol, "Todos os tópicos concluídos", "UM MARCO IMPORTANTE")
            msg.pack(fill="x")
            tk.Label(msg, text="A trilha de estudo foi concluída. Faça as recapitulações pendentes e prove seu domínio na Câmara dos Guardiões.", bg=PANEL, fg=MUTED, wraplength=600, justify="left").pack(anchor="w", padx=16, pady=(0, 15))
            self._button(msg, "ENTRAR NA CÂMARA DOS GUARDIÕES  →", lambda:self.navigate("Chefes"), "gold").pack(anchor="w", padx=16, pady=(0, 14))
        else:
            self._mission_card(leftcol, mission, compact=True)
            tk.Label(leftcol, text="O mapa só revela o próximo passo. Termine a aula, passe no teste e volte amanhã para a recapitulação.", bg=BG, fg=MUTED, font=(FONT, 8), wraplength=640, justify="left").pack(anchor="w", pady=(0, 10))

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
            tk.Label(row, text="Estude, pratique e passe no teste para receber a recompensa.", bg=PANEL, fg="#6f6a85", font=(FONT, 8)).pack(side="left", fill="x", expand=True)
        else:
            tk.Label(row, text="Teste de domínio obrigatório · revisão amanhã", bg=PANEL, fg=MUTED, font=(FONT, 8)).pack(side="left", fill="x", expand=True)
        is_done = mission["id"] in self.profile["completed_missions"]
        self._button(row, "REVER TÓPICO  ↺" if is_done else "INICIAR TÓPICO  →", lambda m=mission:self.start_lesson(m), "secondary" if is_done else "mint").pack(side="right")

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

    # -------------------------- LINEAR CAMPAIGN ---------------------------
    def next_lesson(self):
        completed = set(self.profile.get("completed_missions", []))
        return next((m for m in self.profile["mission_data"] if m["id"] not in completed), None)

    def lesson_by_id(self, lesson_id):
        return next((m for m in self.profile["mission_data"] if m["id"] == lesson_id), None)

    def pending_guardian(self):
        p = self.profile
        count = self.mission_count()
        defeated = set(p.get("bosses_defeated", []))
        for boss in p.get("boss_data", []):
            if boss.get("id") not in defeated and count >= safe_int(boss.get("threshold", 10**9)):
                return boss
        return None

    def due_reviews(self):
        today = date.today().isoformat()
        return [r for r in self.profile.get("review_queue", []) if not r.get("done") and r.get("due_date", "9999") <= today]

    def _announce_due_reviews(self):
        due = len(self.due_reviews())
        if due:
            self.status_var.set(f"Você tem {due} recapitulação(ões) para hoje. Revisar amanhã ajuda a fixar o que estudou.")
            if self.page == "Santuário":
                self.render()

    def _pt_date(self, value):
        weekdays = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado", "domingo"]
        months = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
        return f"{weekdays[value.weekday()]}, {value.day:02d} de {months[value.month-1]} de {value.year}"

    def _calendar_is_boss_blocked(self):
        current = self.next_lesson()
        boss = self.pending_guardian()
        return bool(current and boss and current.get("global_index", 0) > boss.get("threshold", 0)), boss

    # ---------------------- ADAPTIVE STUDY STRATEGY ----------------------
    def page_strategy(self):
        """Evidence-based planner: diagnose gaps, allocate time and track exam readiness."""
        root = self.build_scroll_page()
        p = self.profile
        cfg = ensure_calendar(p, self.active_key)
        today = date.today()
        metrics = subject_metrics(p, self.active_key, today)
        readiness = estimate_readiness(metrics, self.active_key)
        pace = exam_pace(p, self.active_key, today)
        known_text = "Calibração pendente" if readiness["weighted_accuracy"] is None else f"{readiness['weighted_accuracy'] * 100:.1f}% nos assuntos avaliados"

        hero = tk.Frame(root, bg="#21172f", highlightbackground="#67468f", highlightthickness=1)
        hero.pack(fill="x", pady=(0, 12))
        left = tk.Frame(hero, bg="#21172f")
        left.pack(side="left", fill="both", expand=True, padx=18, pady=18)
        tk.Label(left, text="LABORATÓRIO DE DESEMPENHO  /  TREINADOR ADAPTATIVO", bg="#21172f", fg=GOLD, font=(FONT, 8, "bold")).pack(anchor="w")
        tk.Label(left, text="Transforme erros em plano de ação", bg="#21172f", fg=TEXT, font=(FONT, 19, "bold")).pack(anchor="w", pady=(5, 5))
        description = ("O plano combina peso na prova, resultados de diagnóstico, últimos testes, tempo sem revisar e revisões vencidas. "
                       "A sequência da campanha permanece linear; o algoritmo ajusta reforços e tempo, não finge que conteúdos foram aprendidos.")
        tk.Label(left, text=description, bg="#21172f", fg="#d8cfe7", font=(FONT, 9), wraplength=790, justify="left").pack(anchor="w")
        try:
            asset = "iria_portrait.png" if self.active_key == "caixa" else "hunter_portrait.png"
            self.strategy_portrait = tk.PhotoImage(file=str(self._asset_path(asset))).subsample(4, 4)
            tk.Label(hero, image=self.strategy_portrait, bg="#21172f", bd=0).pack(side="right", padx=14, pady=10)
        except Exception:
            pass

        stats = tk.Frame(root, bg=BG)
        stats.pack(fill="x", pady=(0, 12))
        [stats.grid_columnconfigure(i, weight=1, uniform="stats") for i in range(3)]
        cards = [
            ("ESTIMATIVA ATUAL", known_text, PURPLE),
            ("ASSUNTOS CALIBRADOS", f"{readiness['known_subjects']}/{readiness['total_subjects']}", GOLD),
            ("REVISÕES VENCIDAS", str(len(self.due_reviews())), RED if self.due_reviews() else MINT),
        ]
        for idx, (title, value, color) in enumerate(cards):
            card = tk.Frame(stats, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
            card.grid(row=0, column=idx, sticky="ew", padx=(0 if idx == 0 else 5, 0 if idx == 2 else 5))
            tk.Label(card, text=title, bg=PANEL, fg=MUTED, font=(FONT, 8, "bold")).pack(anchor="w", padx=12, pady=(10, 3))
            tk.Label(card, text=value, bg=PANEL, fg=color, font=(FONT, 13, "bold"), wraplength=260, justify="left").pack(anchor="w", padx=12, pady=(0, 11))

        # Caixa is not just a weighted-average race: both objective blocks have their own
        # eliminatory threshold. Present weighted estimates and clearly expose sample coverage.
        if self.active_key == "caixa":
            block_card = self._card(root, "Barreira contra eliminação", "PROJEÇÃO PONDERADA · EDITAL ANEXADO")
            block_card.pack(fill="x", pady=(0, 12))
            block_body = tk.Frame(block_card, bg=PANEL)
            block_body.pack(fill="x", padx=14, pady=(0, 13))
            for block_info in block_readiness(metrics, self.active_key, float(cfg.get("target_score", .85))):
                color = RED if block_info["accuracy"] is not None and block_info["accuracy"] < .50 else GOLD if block_info["accuracy"] is None or block_info["accuracy"] < .65 else MINT
                row = tk.Frame(block_body, bg=PANEL_2, highlightbackground=color, highlightthickness=1)
                row.pack(fill="x", pady=(0, 6))
                tk.Label(row, text=block_info["block"].upper(), bg=PANEL_2, fg=TEXT, font=(FONT, 9, "bold")).pack(anchor="w", padx=11, pady=(8, 2))
                if block_info["accuracy"] is None:
                    detail = f"Sem evidência ainda · calibre {block_info['total_subjects']} disciplinas para estimar este bloco."
                else:
                    coverage = f"{block_info['known_subjects']}/{block_info['total_subjects']} disciplinas calibradas"
                    percent = block_info["accuracy"] * 100
                    points = f" · projeção {block_info['estimated_points']:.1f}/{block_info['max_points']} pontos" if block_info["complete_coverage"] else " · estimativa parcial, não nota prevista"
                    detail = f"{percent:.1f}% ponderados nos assuntos medidos · {coverage}{points} · {block_info['status']}"
                tk.Label(row, text=detail, bg=PANEL_2, fg=color, font=(FONT, 8, "bold"), wraplength=900, justify="left").pack(anchor="w", padx=11, pady=(0, 8))
            tk.Label(block_body, text="O edital anexado prevê eliminação abaixo de 50% do total e abaixo de 50% em Conhecimentos Básicos ou Específicos. A meta interna busca margem acima desse corte; a estimativa só se torna representativa quando você calibra todas as disciplinas e faz simulados. Não é previsão de resultado oficial.", bg=PANEL, fg=MUTED, font=(FONT, 8), wraplength=920, justify="left").pack(anchor="w", pady=(0, 3))

        settings = self._card(root, "Parâmetros do treinador", "AJUSTE AO TEMPO REAL DISPONÍVEL")
        settings.pack(fill="x", pady=(0, 12))
        body = tk.Frame(settings, bg=PANEL)
        body.pack(fill="x", padx=15, pady=(0, 14))
        exam_row = tk.Frame(body, bg=PANEL)
        exam_row.pack(fill="x", pady=(0, 7))
        tk.Label(exam_row, text="Data-alvo da prova (AAAA-MM-DD; deixe vazio se ainda não há data)", bg=PANEL, fg=MUTED, font=(FONT, 8, "bold")).pack(side="left", padx=(0, 8))
        exam_var = tk.StringVar(value=str(cfg.get("exam_date", "")))
        tk.Entry(exam_row, textvariable=exam_var, bg=PANEL_2, fg=TEXT, insertbackground=TEXT, relief="flat", width=15, font=(FONT, 9)).pack(side="left", ipady=5)
        fields = tk.Frame(body, bg=PANEL)
        fields.pack(fill="x", pady=(3, 8))
        tk.Label(fields, text="Tempo diário (min)", bg=PANEL, fg=MUTED, font=(FONT, 8, "bold")).pack(side="left", padx=(0, 7))
        minutes_var = tk.StringVar(value=str(cfg.get("daily_minutes", {"python": 60, "caixa": 120, "custom": 45}.get(self.active_key, 60))))
        tk.Spinbox(fields, from_=20, to=480, increment=10, textvariable=minutes_var, width=5, bg=PANEL_2, fg=TEXT, buttonbackground=PANEL_2, insertbackground=TEXT, relief="flat").pack(side="left", padx=(0, 16), ipady=4)
        tk.Label(fields, text="Mínimo diário de tópicos", bg=PANEL, fg=MUTED, font=(FONT, 8, "bold")).pack(side="left", padx=(0, 7))
        minimum_var = tk.StringVar(value=str(cfg.get("daily_minimum", 2 if self.active_key == "caixa" else 1)))
        tk.Spinbox(fields, from_=1, to=5, textvariable=minimum_var, width=4, bg=PANEL_2, fg=TEXT, buttonbackground=PANEL_2, insertbackground=TEXT, relief="flat").pack(side="left", padx=(0, 16), ipady=4)
        tk.Label(fields, text="Meta de acerto (%)", bg=PANEL, fg=MUTED, font=(FONT, 8, "bold")).pack(side="left", padx=(0, 7))
        target_var = tk.StringVar(value=str(round(float(cfg.get("target_score", .85)) * 100)))
        tk.Spinbox(fields, from_=50, to=100, increment=5, textvariable=target_var, width=4, bg=PANEL_2, fg=TEXT, buttonbackground=PANEL_2, insertbackground=TEXT, relief="flat").pack(side="left", padx=(0, 12), ipady=4)

        def apply_trainer_settings():
            try:
                exam_text = exam_var.get().strip()
                if exam_text:
                    exam = date.fromisoformat(exam_text)
                    if exam < today:
                        if not messagebox.askyesno("Data passada", "A data informada já passou. Salvar mesmo assim para registrar o prazo antigo?", parent=self):
                            return
                minutes = int(minutes_var.get())
                minimum = int(minimum_var.get())
                target_score = int(target_var.get())
                if not 20 <= minutes <= 480:
                    raise ValueError("O tempo diário deve ficar entre 20 e 480 minutos.")
                if not 1 <= minimum <= 5:
                    raise ValueError("O mínimo deve ficar entre 1 e 5 tópicos.")
                if not 50 <= target_score <= 100:
                    raise ValueError("A meta de acerto precisa ficar entre 50% e 100%.")
                cfg["exam_date"] = exam_text
                cfg["daily_minutes"] = minutes
                cfg["daily_minimum"] = minimum
                cfg["target_score"] = target_score / 100
                cfg["version"] = 2
                self.save()
                self.status_var.set("Parâmetros salvos. A projeção e a prioridade dos reforços foram recalculadas.")
                self.render()
            except Exception as exc:
                messagebox.showerror("Configuração inválida", f"Confira data, minutos, mínimo e meta de acerto.\n\n{exc}", parent=self)
        self._button(fields, "SALVAR PLANO", apply_trainer_settings, "primary").pack(side="right")
        tk.Label(body, text="O calendário não transforma horas irreais em promessa. Se a data-alvo exigir mais trabalho do que cabe no seu tempo, a tela sinaliza o risco para você ajustar a meta ou a data.", bg=PANEL, fg=MUTED, font=(FONT, 8), wraplength=920, justify="left").pack(anchor="w", pady=(2, 0))

        # Concrete plan for this session: due reviews first, the linear campaign next, then a
        # targeted booster based on observed weakness and exam weighting.
        blocked_today, boss_today = self._calendar_is_boss_blocked()
        today_plan = day_summary(p, self.active_key, today, today, blocked_today)
        scheduled_minutes = today_plan["estimated_minutes"]
        overdue_reviews = self.due_reviews()
        review_minutes = len(overdue_reviews) * 8
        daily_budget = int(cfg.get("daily_minutes", 60))
        plan_card = self._card(root, "Plano recomendado para hoje", "MÍNIMO VIÁVEL + MAIOR RETORNO ESPERADO")
        plan_card.pack(fill="x", pady=(12, 12))
        plan_body = tk.Frame(plan_card, bg=PANEL)
        plan_body.pack(fill="x", padx=15, pady=(0, 14))
        if overdue_reviews:
            tk.Label(plan_body, text=f"1. MEMÓRIA PRIMEIRO  ·  {len(overdue_reviews)} revisão(ões) pendente(s), cerca de {review_minutes} min. Faça-as sem consulta; falhas viram sinal para reforçar o assunto.", bg=PANEL_2, fg=GOLD, font=(FONT, 9, "bold"), wraplength=900, justify="left", padx=11, pady=9).pack(fill="x", pady=(0, 7))
        else:
            tk.Label(plan_body, text="1. MEMÓRIA EM DIA  ·  não há revisões vencidas; novas revisões serão marcadas em D+1, D+7 e D+30.", bg=PANEL_2, fg=MINT, font=(FONT, 9, "bold"), wraplength=900, justify="left", padx=11, pady=9).pack(fill="x", pady=(0, 7))
        next_item = self.next_lesson()
        if blocked_today and boss_today:
            campaign_line = f"2. PORTAL SELADO  ·  antes de uma nova lição, a tarefa principal é preparar e vencer {boss_today['name']}."
        elif next_item:
            campaign_line = f"2. CAMPANHA LINEAR  ·  {next_item['title']} ({estimated_minutes(next_item, self.active_key)} min estimados). A sequência não é pulada; bônus não marcam tópicos automaticamente."
        else:
            campaign_line = "2. CAMPANHA CONCLUÍDA  ·  use os simulados e as revisões para consolidar antes do último guardião."
        tk.Label(plan_body, text=campaign_line, bg="#211b2f", fg=TEXT, font=(FONT, 9, "bold"), wraplength=900, justify="left", padx=11, pady=9).pack(fill="x", pady=(0, 7))
        estimated_core = scheduled_minutes + review_minutes
        minutes_for_focus = max(0, daily_budget - estimated_core)
        if metrics:
            focus = metrics[0]
            focus_minutes = min(safe_int(focus.get("recommended_minutes", 0)), minutes_for_focus)
            if focus_minutes > 0:
                focus_line = f"3. REFORÇO ESTRATÉGICO  ·  {focus['subject']} — {focus['status'].lower()}. Reserve {focus_minutes} min dentro do tempo restante de {daily_budget} min/dia. {focus['recommendation']}"
            else:
                focus_line = f"3. REFORÇO ESTRATÉGICO  ·  {focus['subject']} é a maior prioridade, mas o mínimo e as revisões já ocupam o orçamento de {daily_budget} min. Não empilhe carga: faça primeiro o essencial e retome o reforço na próxima sessão."
            tk.Label(plan_body, text=focus_line, bg="#1d2928", fg=MINT if focus_minutes else GOLD, font=(FONT, 9), wraplength=900, justify="left", padx=11, pady=9).pack(fill="x", pady=(0, 7))
            focus_actions = tk.Frame(plan_body, bg=PANEL)
            focus_actions.pack(fill="x", pady=(1, 0))
            if focus.get("is_essay") and self.active_key == "caixa":
                self._button(focus_actions, "COMEÇAR TREINO DE REDAÇÃO", self.start_essay_practice, "gold").pack(side="left")
            else:
                self._button(focus_actions, f"TESTAR / REFORÇAR: {focus['subject']}", lambda subject=focus["subject"]:self.start_subject_diagnostic(subject), "mint").pack(side="left")
            tk.Label(focus_actions, text="O reforço é independente da próxima lição. A ordem da campanha não é quebrada e nenhuma etapa é marcada como concluída por estimativa.", bg=PANEL, fg=MUTED, font=(FONT, 8), wraplength=520, justify="left").pack(side="left", padx=10)
        if estimated_core > daily_budget:
            over = estimated_core - daily_budget
            tk.Label(plan_body, text=f"ALERTA DE CARGA  ·  mínimo + revisões estimam {estimated_core} min, {over} min acima do seu orçamento. Faça a revisão e o tópico principal em blocos realistas, ou ajuste o plano; não tente compensar sacrificando o sono.", bg="#3b202a", fg="#ffc1cb", font=(FONT, 8, "bold"), wraplength=900, justify="left", padx=11, pady=9).pack(fill="x", pady=(7, 0))

        if self.active_key == "caixa":
            essay_logs = [x for x in p.get("essay_practice_log", []) if isinstance(x, dict) and x.get("date")]
            last_essay_day = None
            if essay_logs:
                try: last_essay_day = date.fromisoformat(str(essay_logs[-1].get("date")))
                except ValueError: pass
            essay_due = last_essay_day is None or (today - last_essay_day).days >= 7
            sim_logs = p.get("simulados", []) if isinstance(p.get("simulados", []), list) else []
            last_sim_day = None
            if sim_logs:
                try: last_sim_day = date.fromisoformat(str(sim_logs[-1].get("date")))
                except ValueError: pass
            sim_due = last_sim_day is None or (today - last_sim_day).days >= 7
            routine = self._card(root, "Ritual semanal de prova", "REDAÇÃO + RECUPERAÇÃO CUMULATIVA")
            routine.pack(fill="x", pady=(0, 12))
            routine_body = tk.Frame(routine, bg=PANEL)
            routine_body.pack(fill="x", padx=15, pady=(0, 13))
            essay_text = "Treino de redação recomendado nesta semana" if essay_due else f"Redação registrada em {last_essay_day.strftime('%d/%m/%Y')}"
            sim_text = "Simulado adaptativo recomendado nesta semana" if sim_due else f"Último simulado registrado em {last_sim_day.strftime('%d/%m/%Y')}"
            tk.Label(routine_body, text=f"✍  {essay_text}  ·  {('pendente' if essay_due else 'registrado')}", bg=PANEL_2, fg=GOLD if essay_due else MINT, font=(FONT, 9, "bold"), padx=10, pady=8, anchor="w").pack(fill="x", pady=(0, 5))
            tk.Label(routine_body, text=f"⚔  {sim_text}  ·  {('pendente' if sim_due else 'registrado')}", bg=PANEL_2, fg=GOLD if sim_due else MINT, font=(FONT, 9, "bold"), padx=10, pady=8, anchor="w").pack(fill="x", pady=(0, 8))
            routine_actions = tk.Frame(routine_body, bg=PANEL); routine_actions.pack(fill="x")
            self._button(routine_actions, "ESCREVER REDAÇÃO", self.start_essay_practice, "gold").pack(side="left", padx=(0, 8))
            self._button(routine_actions, "SIMULADO 60 QUESTÕES", self.start_caixa_weighted_mock, "primary").pack(side="left")

        self._section(root, "Diagnóstico do desempenho", "RESULTADOS REAIS, NÃO PALPITES")
        tk.Label(root, text="Faça um diagnóstico curto por assunto. O resultado muda a fila de prioridades. Testes de lições e simulados também alimentam o cálculo; assuntos sem evidência ficam marcados como não calibrados.", bg=BG, fg=MUTED, font=(FONT, 9), wraplength=950, justify="left").pack(anchor="w", pady=(0, 8))
        if self.active_key == "caixa":
            tk.Label(root, text="Estratégia da Caixa: o peso objetivo do edital define a importância inicial (15 questões em Conhecimentos Bancários, 10 em Atendimento e 5 nos demais eixos); erros e resultados baixos aumentam a prioridade. Básicos e específicos são acompanhados separadamente por causa dos cortes mínimos do edital 2024 anexado. Redação é eliminatória e recebe treino recorrente.", bg="#211b2f", fg="#e5dcef", font=(FONT, 9), wraplength=920, justify="left", padx=13, pady=11).pack(fill="x", pady=(0, 10))
        metric_host = tk.Frame(root, bg=BG)
        metric_host.pack(fill="x")
        for metric in metrics:
            card = tk.Frame(metric_host, bg=PANEL, highlightbackground=(RED if metric.get("status") == "Ponto crítico" else BORDER), highlightthickness=1)
            card.pack(fill="x", pady=(0, 7))
            main_line = tk.Frame(card, bg=PANEL)
            main_line.pack(fill="x", padx=13, pady=(10, 3))
            left_info = tk.Frame(main_line, bg=PANEL)
            left_info.pack(side="left", fill="x", expand=True)
            tk.Label(left_info, text=f"#{metric['rank']:02d}  ·  {metric['subject']}", bg=PANEL, fg=TEXT, font=(FONT, 10, "bold"), wraplength=650, justify="left").pack(anchor="w")
            if metric.get("known"):
                if metric.get("is_essay"):
                    accuracy_text = f"{metric['accuracy'] * 100:.0f}% dos critérios autoavaliados"
                else:
                    accuracy_text = f"{metric['accuracy'] * 100:.0f}% de acerto observado"
                accuracy_color = MINT if metric["accuracy"] >= float(cfg.get("target_score", .85)) else GOLD if metric["accuracy"] >= .70 else RED
            else:
                accuracy_text = "Sem diagnóstico ainda"
                accuracy_color = MUTED
            tk.Label(left_info, text=f"{metric['status']}  ·  {accuracy_text}  ·  {metric['recommended_minutes']} min recomendados", bg=PANEL, fg=accuracy_color, font=(FONT, 8, "bold")).pack(anchor="w", pady=(3, 0))
            if self.active_key == "caixa" and metric.get("weight"):
                weight_text = f"Peso do edital: {metric['weight']} questão(ões)"
            elif metric.get("is_essay"):
                weight_text = "Treino recorrente · etapa eliminatória"
            else:
                weight_text = f"{metric['lesson_count']} etapas nesta região"
            tk.Label(main_line, text=weight_text, bg=PANEL, fg=GOLD, font=(FONT, 8, "bold"), anchor="e", justify="right", wraplength=185).pack(side="right", padx=(10, 0))
            if metric.get("known"):
                self._progress(card, metric["accuracy"], 1.0, MINT if metric["accuracy"] >= .80 else GOLD if metric["accuracy"] >= .60 else RED, height=5)
            tk.Label(card, text=metric["recommendation"], bg=PANEL, fg=MUTED, font=(FONT, 8), wraplength=850, justify="left").pack(anchor="w", padx=13, pady=(5, 3))
            controls = tk.Frame(card, bg=PANEL)
            controls.pack(fill="x", padx=13, pady=(0, 9))
            if metric.get("known"):
                last = "" if metric.get("days_stale") is None else f" · evidência há {metric['days_stale']} dia(s)"
                tk.Label(controls, text=f"Índice de prioridade: {metric['priority_score']:.2f}{last}", bg=PANEL, fg="#8d87a6", font=(FONT, 7)).pack(side="left")
            else:
                tk.Label(controls, text="O algoritmo evita inventar uma nota: calibre este assunto.", bg=PANEL, fg="#8d87a6", font=(FONT, 7)).pack(side="left")
            if not metric.get("is_essay"):
                self._button(controls, "FAZER DIAGNÓSTICO · 5 QUESTÕES", lambda subject=metric["subject"]:self.start_subject_diagnostic(subject), "secondary").pack(side="right")
            elif self.active_key == "caixa":
                self._button(controls, "TREINO DE REDAÇÃO", self.start_essay_practice, "gold").pack(side="right")

        self._section(root, "Provas de recuperação", "MEDIR, AJUSTAR, REPETIR")
        actions = tk.Frame(root, bg=BG)
        actions.pack(fill="x", pady=(0, 10))
        sim_title = "SIMULADO ADAPTATIVO · 20 QUESTÕES" if self.active_key == "caixa" else "TESTE CUMULATIVO · 20 QUESTÕES"
        self._button(actions, sim_title, self.start_adaptive_simulation, "gold").pack(side="left", padx=(0, 8))
        if self.active_key == "caixa":
            self._button(actions, "SIMULADO 60 QUESTÕES · PESO DO EDITAL", self.start_caixa_weighted_mock, "primary").pack(side="left", padx=(0, 8))
        self._button(actions, "ABRIR CÂMARA DA MEMÓRIA", lambda:self.navigate("Revisões"), "secondary").pack(side="left", padx=(0, 8))
        sims = p.get("simulados", []) if isinstance(p.get("simulados", []), list) else []
        if sims:
            last = sims[-1]
            acc = safe_int(last.get("score", 0)) / max(1, safe_int(last.get("total", 1)))
            sim_card = self._card(root, "Último simulado adaptativo", f"{last.get('date', '')}")
            sim_card.pack(fill="x", pady=(0, 12))
            tk.Label(sim_card, text=f"{last.get('score', 0)}/{last.get('total', 0)} corretas · {acc*100:.0f}% · {'atingiu' if acc >= float(cfg.get('target_score', .85)) else 'ainda não atingiu'} a meta pessoal de {float(cfg.get('target_score', .85))*100:.0f}%", bg=PANEL, fg=MINT if acc >= float(cfg.get('target_score', .85)) else GOLD, font=(FONT, 10, "bold")).pack(anchor="w", padx=15, pady=(0, 7))
            by_block = last.get("by_block", {})
            if by_block:
                block_summary = "  ·  ".join(f"{name}: {v.get('score',0)}/{v.get('total',0)}" for name, v in by_block.items())
                tk.Label(sim_card, text=block_summary, bg=PANEL, fg=GOLD, font=(FONT, 8, "bold"), wraplength=900, justify="left").pack(anchor="w", padx=15, pady=(0, 5))
            by_subject = last.get("by_subject", {})
            if by_subject:
                summary = "  ·  ".join(f"{name}: {v.get('score',0)}/{v.get('total',0)}" for name, v in sorted(by_subject.items()))
                tk.Label(sim_card, text=summary, bg=PANEL, fg=MUTED, font=(FONT, 8), wraplength=900, justify="left").pack(anchor="w", padx=15, pady=(0, 13))
        else:
            tk.Label(root, text="Ainda não há simulados registrados. Faça o primeiro para que a estratégia compare seu desempenho por assunto ao longo do tempo.", bg=BG, fg=MUTED, font=(FONT, 9), wraplength=920, justify="left").pack(anchor="w", pady=(0, 10))

        if pace:
            self._section(root, "Ritmo até a data-alvo", "PROJEÇÃO, NÃO GARANTIA")
            pace_card = self._card(root, pace["status"], f"{pace['days_left']} dia(s) restantes")
            pace_card.pack(fill="x", pady=(0, 12))
            pace_text = (f"Faltam {pace['pending_lessons']} etapas da trilha. Para terminar antes da data escolhida, o ritmo matemático é de cerca de "
                         f"{pace['required_daily_lessons']} tópico(s)/dia e {pace['time_required_per_day']} min/dia estimados; seu plano atual é "
                         f"{pace['daily_minimum']} tópico(s) e {pace['daily_minutes']} min/dia. Isso estima a trilha restante, não prevê sua nota nem substitui revisão e simulados.")
            tk.Label(pace_card, text=pace_text, bg=PANEL, fg=TEXT, font=(FONT, 9), wraplength=900, justify="left").pack(anchor="w", padx=15, pady=(0, 13))

    def start_subject_diagnostic(self, subject):
        p = self.profile
        pool = []
        seen = set()
        for mission in p.get("mission_data", []):
            if mission_subject(mission) != subject:
                continue
            for question in mission.get("quiz", []):
                key = str(question.get("q", "")).strip()
                if not key or key in seen:
                    continue
                seen.add(key)
                item = dict(question)
                item["_planner_subject"] = subject
                pool.append(item)
        if not pool:
            messagebox.showinfo("Diagnóstico indisponível", "Ainda não há questões cadastradas para este assunto.")
            return
        questions = random.sample(pool, min(5, len(pool)))
        def store(score, total, _records):
            p.setdefault("diagnostic_results", {})[subject] = {"score": score, "total": total, "date": date.today().isoformat(), "source": "diagnóstico"}
            self.save()
        def done(_score):
            self.status_var.set(f"Diagnóstico salvo para {subject}. A prioridade de estudo foi recalculada.")
            self.render()
        self.run_quiz_dialog(
            f"Diagnóstico adaptativo · {subject}",
            "Responda sem consultar. Este teste mede o ponto de partida e não libera nem bloqueia etapas da história.",
            questions, 0, done, retry_label="REFAZER DIAGNÓSTICO", on_attempt=store, result_mode="diagnostic")

    def _record_lesson_attempt(self, lesson, score, total, records):
        p = self.profile
        log = p.setdefault("quiz_attempt_log", [])
        log.append({"date": date.today().isoformat(), "lesson_id": lesson["id"], "subject": mission_subject(lesson),
                    "chapter_title": lesson.get("chapter_title", lesson.get("topic", "Geral")), "score": int(score), "total": int(total)})
        if len(log) > 3000:
            del log[:-3000]
        stats = p.setdefault("quiz_stats", {}).setdefault(lesson["id"], {"attempts": 0, "best": 0})
        stats["last_score"] = int(score)
        stats["total"] = int(total)
        stats["last_attempt_date"] = date.today().isoformat()
        stats["best_attempt_score"] = max(safe_int(stats.get("best_attempt_score", 0)), int(score))
        self.save(quiet=True)

    def start_adaptive_simulation(self):
        questions = build_adaptive_question_set(self.profile, self.active_key, count=20, rng=random)
        if not questions:
            messagebox.showinfo("Simulado indisponível", "Ainda não há questões suficientes nesta jornada.")
            return
        mode_name = "Simulado adaptativo" if self.active_key == "caixa" else "Teste cumulativo adaptativo"
        def record(score, total, records):
            p = self.profile
            by_subject = {}
            for result in records:
                subject = result.get("subject", "Geral")
                part = by_subject.setdefault(subject, {"score": 0, "total": 0})
                part["total"] += 1
                if result.get("correct"):
                    part["score"] += 1
            simulation = {"date": date.today().isoformat(), "score": int(score), "total": int(total),
                          "accuracy": round(score / max(1, total), 4), "by_subject": by_subject,
                          "mode": mode_name, "question_count": total}
            p.setdefault("simulados", []).append(simulation)
            p["simulados"] = p["simulados"][-100:]
            p.setdefault("history", []).append({"date": date.today().isoformat(), "type": "simulado", "title": mode_name, "xp": 0, "gold": 0, "score": score, "total": total})
            self.save(quiet=True)
        def finished(score):
            self.status_var.set(f"{mode_name} registrado: {score}/20. O plano agora considera os resultados por assunto.")
            self.render()
        subtitle = "20 questões autorais do aplicativo, distribuídas por peso e reforçadas em áreas fracas. Não é uma prova oficial; o resultado recalibra suas prioridades."
        self.run_quiz_dialog(mode_name, subtitle, questions, 0, finished,
                             retry_label="REFAZER SIMULADO", on_attempt=record, result_mode="simulado")

    def start_caixa_weighted_mock(self):
        if self.active_key != "caixa":
            messagebox.showinfo("Simulado da Caixa", "O simulado com a distribuição do edital está disponível no slot da Caixa.")
            return
        questions = build_caixa_weighted_mock(self.profile, rng=random)
        if len(questions) != 60:
            messagebox.showwarning(
                "Banco de questões insuficiente",
                f"O simulado conseguiu montar {len(questions)} questões, não 60. Confira se você manteve o banco original do projeto.",
                parent=self,
            )
            return
        by_expected = {}
        for question in questions:
            subject = question.get("_planner_subject", "Geral")
            by_expected[subject] = by_expected.get(subject, 0) + 1
        if by_expected != OBJECTIVE_QUESTIONS:
            messagebox.showwarning(
                "Distribuição incompleta",
                "O banco deste perfil não permite compor exatamente a distribuição do edital. Restaure o conteúdo original da campanha da Caixa antes de fazer esse simulado.",
                parent=self,
            )
            return
        breakdown = " · ".join(f"{subject}: {count}" for subject, count in by_expected.items())
        mode_name = "Simulado de treino · distribuição TBN 2024"

        def record(score, total, records):
            p = self.profile
            by_subject = {}
            by_block = {
                "Conhecimentos Básicos": {"score": 0, "total": 0},
                "Conhecimentos Específicos": {"score": 0, "total": 0},
            }
            for result in records:
                subject = result.get("subject", "Geral")
                part = by_subject.setdefault(subject, {"score": 0, "total": 0})
                part["total"] += 1
                if result.get("correct"):
                    part["score"] += 1
                block = result.get("block")
                if block in by_block:
                    by_block[block]["total"] += 1
                    if result.get("correct"):
                        by_block[block]["score"] += 1
            simulation = {
                "date": date.today().isoformat(), "score": int(score), "total": int(total),
                "accuracy": round(score / max(1, total), 4), "by_subject": by_subject,
                "by_block": by_block, "mode": mode_name, "question_count": total,
                "expected_distribution": by_expected, "official_questions": False,
            }
            p.setdefault("simulados", []).append(simulation)
            p["simulados"] = p["simulados"][-100:]
            p.setdefault("history", []).append({"date": date.today().isoformat(), "type": "simulado", "title": mode_name, "score": int(score), "total": int(total), "xp": 0, "gold": 0})
            self.save()

        def finish(score):
            self.status_var.set(f"Simulado de 60 questões concluído: {score}/60. O resultado por matéria e bloco já alimenta a estratégia.")
            self.render()

        self.run_quiz_dialog(
            "Simulado de treino · Técnico Bancário Novo",
            "60 questões com distribuição baseada no edital TBN comum de 2024 enviado. As questões são do banco de estudo do aplicativo, não são itens oficiais da Cesgranrio.\n\n" + breakdown,
            questions, 0, finish, retry_label="REFAZER SIMULADO", on_attempt=record, result_mode="simulado",
        )

    def start_essay_practice(self):
        if self.active_key != "caixa":
            messagebox.showinfo("Treino da redação", "Esta atividade está configurada para a jornada da Caixa.")
            return
        prompts = [
            "Como conciliar a ampliação dos serviços bancários digitais com a inclusão de pessoas com diferentes níveis de letramento digital?",
            "A confiança nas instituições financeiras depende apenas da tecnologia? Discuta o papel da transparência e do atendimento. ",
            "Quais desafios surgem ao proteger dados pessoais sem comprometer a qualidade dos serviços digitais?",
            "Como o atendimento humanizado pode contribuir para a cidadania financeira?",
            "Discuta a importância da educação financeira para decisões de consumo e planejamento de longo prazo.",
            "Como inovação e responsabilidade devem caminhar juntas em serviços oferecidos por instituições financeiras?",
        ]
        prompt = prompts[(len(self.profile.get("essay_practice_log", [])) + date.today().toordinal()) % len(prompts)]
        win = tk.Toplevel(self)
        win.title("Oficina da Redação · Caixa")
        win.geometry("900x720")
        win.minsize(760, 620)
        win.configure(bg=BG)
        win.transient(self); win.grab_set()
        shell = tk.Frame(win, bg=BG); shell.pack(fill="both", expand=True, padx=22, pady=18)
        tk.Label(shell, text="OFICINA DA REDAÇÃO  /  TREINO AUTORAL", bg=BG, fg=GOLD, font=(FONT, 8, "bold")).pack(anchor="w")
        tk.Label(shell, text="Escreva antes de consultar", bg=BG, fg=TEXT, font=(FONT, 18, "bold")).pack(anchor="w", pady=(5, 9))
        tk.Label(shell, text=prompt, bg=PANEL, fg=TEXT, font=(FONT, 10, "bold"), wraplength=820, justify="left", padx=14, pady=13).pack(fill="x", pady=(0, 10))
        essay = tk.Text(shell, bg=PANEL_2, fg=TEXT, insertbackground=TEXT, relief="flat", wrap="word", font=(FONT, 10), padx=12, pady=10)
        essay.pack(fill="both", expand=True, pady=(0, 7))
        tk.Label(shell, text="A autoavaliação não é uma correção automática. Use a rubrica para identificar pontos a melhorar; se possível, peça revisão humana do texto.", bg=BG, fg=MUTED, font=(FONT, 8), wraplength=820, justify="left").pack(anchor="w", pady=(0, 7))
        rubric = tk.Frame(shell, bg=BG); rubric.pack(fill="x", pady=(0, 8))
        rubric_vars = []
        for label in ["Tese clara", "Argumentos desenvolvidos", "Coesão entre parágrafos", "Norma formal e precisão", "Conclusão ligada à tese"]:
            var = tk.BooleanVar(master=win, value=False); rubric_vars.append(var)
            tk.Checkbutton(rubric, text=label, variable=var, bg=BG, fg=TEXT, selectcolor=PANEL_2, activebackground=BG, activeforeground=TEXT, font=(FONT, 8)).pack(side="left", padx=(0, 8))
        def save_essay():
            text_body = essay.get("1.0", "end").strip()
            if len(text_body) < 80:
                if not messagebox.askyesno("Texto curto", "O texto tem menos de 80 caracteres. Salvar mesmo assim como rascunho?", parent=win):
                    return
            score = sum(1 for v in rubric_vars if v.get())
            item = {"date": date.today().isoformat(), "prompt": prompt, "text": text_body,
                    "rubric_score": score, "rubric": [bool(v.get()) for v in rubric_vars],
                    "word_count": len(text_body.split()), "status": "autoavaliado" if all(v.get() for v in rubric_vars) else "precisa de revisão"}
            p = self.profile
            p.setdefault("essay_practice_log", []).append(item)
            p["essay_practice_log"] = p["essay_practice_log"][-100:]
            p.setdefault("history", []).append({"date": date.today().isoformat(), "type": "redação", "title": "Oficina da Redação", "xp": 0, "gold": 0, "score": score, "total": 5})
            self.save(); win.destroy(); self.render()
            self.status_var.set(f"Redação salva com {item['word_count']} palavras. Autoavaliação: {score}/5; não é uma nota oficial.")
            messagebox.showinfo("Redação registrada", f"Texto salvo localmente. Autoavaliação: {score}/5 critérios.\nPalavras: {item['word_count']}\n\nA autoavaliação não substitui correção por uma pessoa qualificada.")
        footer = tk.Frame(shell, bg=BG); footer.pack(fill="x", pady=(6, 0))
        self._button(footer, "CANCELAR", win.destroy, "secondary").pack(side="left")
        self._button(footer, "SALVAR TEXTO E AUTOAVALIAÇÃO", save_essay, "gold").pack(side="right")

    def page_calendar(self):
        """Interactive month calendar with rolling/adaptive daily study plan."""
        root = self.build_scroll_page()
        p = self.profile
        cfg = ensure_calendar(p, self.active_key)
        today = date.today()
        selected = getattr(self, "calendar_selected", today)
        month = getattr(self, "calendar_month", today.replace(day=1))
        try:
            if selected.month != month.month or selected.year != month.year:
                selected = month
                self.calendar_selected = selected
        except Exception:
            selected = today
            self.calendar_selected = today
        blocked, boss = self._calendar_is_boss_blocked()
        daily_min = int(cfg.get("daily_minimum", 1))
        summary = day_summary(p, self.active_key, selected, today, blocked)
        current_metrics = subject_metrics(p, self.active_key, today)

        hero = self._card(root, "Calendário de jornada", "PLANO ADAPTATIVO · O CAMINHO SE AJUSTA AO SEU RITMO")
        hero.pack(fill="x", pady=(0, 12))
        hbody = tk.Frame(hero, bg=PANEL)
        hbody.pack(fill="x", padx=15, pady=(0, 15))
        avatar_box = tk.Frame(hbody, bg=PANEL_2, highlightbackground="#624289", highlightthickness=1)
        avatar_box.pack(side="left", padx=(0, 14), pady=2)
        try:
            asset = "iria_portrait.png" if self.active_key == "caixa" else "hunter_portrait.png"
            self.calendar_character_image = tk.PhotoImage(file=str(self._asset_path(asset))).subsample(3, 3)
            tk.Label(avatar_box, image=self.calendar_character_image, bg=PANEL_2, bd=0).pack()
        except Exception:
            tk.Label(avatar_box, text="✦", bg=PANEL_2, fg=GOLD, font=(FONT, 32), width=4, height=3).pack()
        words = tk.Frame(hbody, bg=PANEL)
        words.pack(side="left", fill="both", expand=True)
        tk.Label(words, text={"python": "A rota de quem constrói", "caixa": "A estratégia do candidato", "custom": "Sua jornada, suas regras"}.get(self.active_key, "Sua jornada"),
                 bg=PANEL, fg=GOLD, font=(FONT, 15, "bold")).pack(anchor="w", pady=(5, 5))
        if self.active_key == "caixa":
            explanation = ("A trilha continua linear, mas o tempo recomendado acompanha a prioridade do edital de 2024: "
                           "Conhecimentos Bancários (15 questões), Atendimento Bancário (10), e os demais eixos objetivos (5 cada). "
                           "Redação recebe sessão própria por ser eliminatória. O calendário sugere mais tempo aos tópicos prioritários.")
        elif self.active_key == "python":
            explanation = ("Cronograma cronológico de Python: um tópico por dia como mínimo inicial. "
                           "Ao terminar a meta, os próximos tópicos aparecem como bônus de hoje e a previsão futura se antecipa.")
        else:
            explanation = ("Cronograma cronológico da sua trilha pessoal. Escolha um mínimo diário viável; "
                           "se estudar além da meta, as próximas etapas serão puxadas para mais cedo.")
        tk.Label(words, text=explanation, bg=PANEL, fg=MUTED, font=(FONT, 9), wraplength=800, justify="left").pack(anchor="w", pady=(0, 10))

        # The calendar includes a separate evidence-based reinforcement session. It is never
        # inserted in place of the next linear lesson and never unlocks future chapters.
        focus = current_metrics[0] if current_metrics else None
        focus_card = self._card(root, "Foco estratégico extra", "O ALGORITMO ESCOLHE ONDE REFORÇAR")
        focus_card.pack(fill="x", pady=(0, 12))
        fb = tk.Frame(focus_card, bg=PANEL); fb.pack(fill="x", padx=15, pady=(0, 13))
        due_now_count = len(self.due_reviews())
        today_focus_plan = day_summary(p, self.active_key, today, today, blocked)
        daily_budget_focus = int(cfg.get("daily_minutes", 60))
        focus_minutes_left = max(0, daily_budget_focus - today_focus_plan["estimated_minutes"] - due_now_count * 8)
        tk.Label(fb, text=f"Ordem da sessão: revisões vencidas ({due_now_count}) → próximo tópico liberado → reforço prioritário, apenas no tempo restante.", bg=PANEL, fg=TEXT, font=(FONT, 9, "bold"), wraplength=900, justify="left").pack(anchor="w", pady=(0, 7))
        if focus:
            focus_minutes = min(safe_int(focus.get("recommended_minutes", 0)), focus_minutes_left)
            if focus_minutes:
                focus_text = f"Maior prioridade agora: {focus['subject']} · {focus['status']} · reserve {focus_minutes} min dentro do orçamento de {daily_budget_focus} min/dia. {focus['recommendation']}"
                focus_color = MINT
            else:
                focus_text = f"Maior prioridade: {focus['subject']} · {focus['status']}. O mínimo e as revisões já ocupam o orçamento de {daily_budget_focus} min; conclua o essencial e retome o reforço na próxima sessão. {focus['recommendation']}"
                focus_color = GOLD
            tk.Label(fb, text=focus_text, bg="#1d2928", fg=focus_color, font=(FONT, 9), wraplength=900, justify="left", padx=11, pady=9).pack(fill="x", pady=(0, 8))
            actions_focus = tk.Frame(fb, bg=PANEL); actions_focus.pack(fill="x")
            if focus.get("is_essay") and self.active_key == "caixa":
                self._button(actions_focus, "TREINO DE REDAÇÃO EXTRA", self.start_essay_practice, "gold").pack(side="left")
            else:
                self._button(actions_focus, "DIAGNÓSTICO / REFORÇO", lambda subject=focus["subject"]:self.start_subject_diagnostic(subject), "mint").pack(side="left")
            self._button(actions_focus, "ABRIR TREINADOR COMPLETO", lambda:self.navigate("Estratégia"), "secondary").pack(side="left", padx=(8, 0))
        else:
            tk.Label(fb, text="Conclua uma primeira etapa para iniciar a calibração por desempenho.", bg=PANEL, fg=MUTED, font=(FONT, 9)).pack(anchor="w")
            self._button(fb, "ABRIR ESTRATÉGIA", lambda:self.navigate("Estratégia"), "primary").pack(anchor="w", pady=(7, 0))

        controls = self._card(root, "Ritmo da campanha", "DEFINA O MÍNIMO — O EXCEDENTE É BÔNUS")
        controls.pack(fill="x", pady=(0, 12))
        cbody = tk.Frame(controls, bg=PANEL)
        cbody.pack(fill="x", padx=15, pady=(0, 14))
        tk.Label(cbody, text="Início do cronograma (AAAA-MM-DD)", bg=PANEL, fg=MUTED, font=(FONT, 8, "bold")).grid(row=0, column=0, sticky="w", padx=(0, 8), pady=4)
        start_var = tk.StringVar(value=str(cfg.get("start_date", today.isoformat())))
        start_entry = tk.Entry(cbody, textvariable=start_var, bg=PANEL_2, fg=TEXT, insertbackground=TEXT, relief="flat", width=15, font=(FONT, 9))
        start_entry.grid(row=0, column=1, sticky="w", padx=(0, 20), pady=4, ipady=5)
        tk.Label(cbody, text="Mínimo de tópicos por dia", bg=PANEL, fg=MUTED, font=(FONT, 8, "bold")).grid(row=0, column=2, sticky="w", padx=(0, 8), pady=4)
        min_var = tk.StringVar(value=str(daily_min))
        minimum_spin = tk.Spinbox(cbody, from_=1, to=5, textvariable=min_var, width=4, bg=PANEL_2, fg=TEXT,
                                  buttonbackground=PANEL_2, insertbackground=TEXT, relief="flat", font=(FONT, 9))
        minimum_spin.grid(row=0, column=3, sticky="w", padx=(0, 12), pady=4, ipady=4)

        def apply_calendar_settings():
            try:
                start_date = date.fromisoformat(start_var.get().strip())
                new_minimum = int(min_var.get())
                if not 1 <= new_minimum <= 5:
                    raise ValueError("O mínimo diário precisa ficar entre 1 e 5 tópicos.")
                cfg["start_date"] = start_date.isoformat()
                cfg["daily_minimum"] = new_minimum
                cfg["version"] = 2
                self.calendar_month = self.calendar_selected.replace(day=1)
                self.save()
                self.status_var.set("Calendário atualizado. A previsão foi recalculada a partir do primeiro tópico aberto.")
                self.render()
            except Exception as exc:
                messagebox.showerror("Configuração inválida", f"Confira a data e o mínimo diário.\n\n{exc}")
        self._button(cbody, "APLICAR E RECALCULAR", apply_calendar_settings, "primary").grid(row=0, column=4, sticky="w", pady=4)
        for col, weight in enumerate([0, 0, 0, 0, 1]):
            cbody.grid_columnconfigure(col, weight=weight)

        calendar_card = self._card(root, "Mapa mensal", "CLIQUE EM UM DIA PARA VER AS MISSÕES")
        calendar_card.pack(fill="x", pady=(0, 12))
        calbody = tk.Frame(calendar_card, bg=PANEL)
        calbody.pack(fill="x", padx=12, pady=(0, 12))
        months_pt = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
        month_head = tk.Frame(calbody, bg=PANEL)
        month_head.pack(fill="x", pady=(0, 8))
        def prev_month():
            self.calendar_month = (self.calendar_month - timedelta(days=1)).replace(day=1)
            self.calendar_selected = self.calendar_month
            self.render()
        def next_month():
            first = self.calendar_month.replace(day=1)
            if first.month == 12:
                self.calendar_month = date(first.year + 1, 1, 1)
            else:
                self.calendar_month = date(first.year, first.month + 1, 1)
            self.calendar_selected = self.calendar_month
            self.render()
        self._button(month_head, "◀ MÊS ANTERIOR", prev_month, "secondary").pack(side="left")
        tk.Label(month_head, text=f"{months_pt[month.month-1].upper()} / {month.year}", bg=PANEL, fg=TEXT, font=(FONT, 13, "bold")).pack(side="left", expand=True)
        self._button(month_head, "PRÓXIMO MÊS ▶", next_month, "secondary").pack(side="right")

        weekday_labels = ["SEG", "TER", "QUA", "QUI", "SEX", "SÁB", "DOM"]
        day_grid = tk.Frame(calbody, bg=PANEL)
        day_grid.pack(fill="x")
        for col, weekday in enumerate(weekday_labels):
            day_grid.grid_columnconfigure(col, weight=1, uniform="calendar")
            tk.Label(day_grid, text=weekday, bg=PANEL, fg=MUTED, font=(FONT, 8, "bold")).grid(row=0, column=col, sticky="ew", padx=2, pady=(0, 4))
        month_weeks = pycalendar.monthcalendar(month.year, month.month)
        # Ensure a stable 6-row calendar so the lower detail panel does not jump vertically.
        month_weeks += [[0] * 7 for _ in range(max(0, 6 - len(month_weeks)))]
        month_weeks = month_weeks[:6]
        for week_index, week in enumerate(month_weeks, start=1):
            for col, day_number in enumerate(week):
                if not day_number:
                    tk.Label(day_grid, text="", bg=PANEL, height=3).grid(row=week_index, column=col, sticky="nsew", padx=2, pady=2)
                    continue
                target = date(month.year, month.month, day_number)
                day_data = day_summary(p, self.active_key, target, today, blocked)
                is_today = target == today
                is_selected = target == selected
                if target < today:
                    done_n = len(day_data["lessons"])
                    suffix = f"✓ {done_n} concluído(s)" if done_n else "sem registro"
                    fg = MINT if done_n else MUTED
                elif blocked:
                    suffix = "⚔ guardião"
                    fg = RED
                else:
                    lesson_n = len(day_data["lessons"])
                    review_n = len(day_data["reviews"])
                    suffix = f"{lesson_n} tópico(s)"
                    if review_n:
                        suffix += f" · ↻{review_n}"
                    fg = GOLD if is_today else MUTED
                if is_selected:
                    bg = "#47316d"
                elif is_today:
                    bg = "#2c2442"
                elif target < today:
                    bg = "#171f25" if len(day_data["lessons"]) else PANEL_2
                else:
                    bg = PANEL_2
                button = tk.Button(day_grid, text=f"{day_number:02d}\n{suffix}", command=lambda d=target:self._select_calendar_day(d),
                                   bg=bg, fg=TEXT if is_selected or is_today else fg, activebackground=PURPLE_DARK,
                                   activeforeground=TEXT, relief="flat", bd=0, height=3, anchor="nw", justify="left",
                                   padx=7, pady=5, font=(FONT, 8, "bold" if is_today or is_selected else "normal"),
                                   wraplength=100, cursor="hand2")
                button.grid(row=week_index, column=col, sticky="nsew", padx=2, pady=2)

        detail = self._card(root, "Plano do dia selecionado", "META MÍNIMA + REVISÕES + MISSÕES ADAPTATIVAS")
        detail.pack(fill="x", pady=(0, 12))
        db = tk.Frame(detail, bg=PANEL)
        db.pack(fill="x", padx=15, pady=(0, 15))
        tk.Label(db, text=self._pt_date(selected).upper(), bg=PANEL, fg=GOLD, font=(FONT, 10, "bold")).pack(anchor="w", pady=(0, 7))
        if selected < today:
            if summary["lessons"]:
                tk.Label(db, text=f"{len(summary['lessons'])} tópico(s) concluído(s) nesta data.", bg=PANEL, fg=MINT, font=(FONT, 9, "bold")).pack(anchor="w", pady=(0, 8))
                for mission in summary["lessons"]:
                    row = tk.Frame(db, bg="#1e2b2a", highlightbackground="#315a50", highlightthickness=1)
                    row.pack(fill="x", pady=3)
                    tk.Label(row, text="✓", bg="#1e2b2a", fg=MINT, font=(FONT, 12, "bold"), width=4).pack(side="left", pady=7)
                    tk.Label(row, text=mission.get("title", "Tópico concluído"), bg="#1e2b2a", fg=TEXT, font=(FONT, 9, "bold"),
                             wraplength=690, justify="left", anchor="w").pack(side="left", fill="x", expand=True, pady=7)
                    self._button(row, "REVER", lambda m=mission:self.start_lesson(m, replay=True), "secondary").pack(side="right", padx=8, pady=6)
            else:
                tk.Label(db, text="Nenhuma conclusão foi registrada para este dia. Os dias anteriores à ativação do calendário podem não ter histórico individual.",
                         bg=PANEL, fg=MUTED, font=(FONT, 9), wraplength=900, justify="left").pack(anchor="w", pady=(0, 8))
        elif blocked:
            tk.Label(db, text=f"PORTAL SELADO — derrote {boss['name']} para liberar a próxima região.", bg=PANEL, fg=RED,
                     font=(FONT, 10, "bold"), wraplength=900, justify="left").pack(anchor="w", pady=(0, 8))
            self._button(db, "IR À CÂMARA DOS GUARDIÕES  ⚔", lambda:self.navigate("Chefes"), "danger").pack(anchor="w", pady=(0, 8))
        elif not summary["lessons"]:
            tk.Label(db, text="A campanha foi concluída ou ainda não começou. Ajuste a data de início ou aproveite para revisar o códice.",
                     bg=PANEL, fg=MINT, font=(FONT, 9), wraplength=900, justify="left").pack(anchor="w", pady=(0, 8))
        else:
            minimum_text = f"MÍNIMO DO DIA: {summary['minimum']} tópico(s)  ·  TEMPO ESTIMADO: {summary['estimated_minutes']} min"
            tk.Label(db, text=minimum_text, bg=PANEL, fg=TEXT, font=(FONT, 9, "bold")).pack(anchor="w", pady=(0, 7))
            if summary["bonus_mode"]:
                tk.Label(db, text="✦ META CUMPRIDA — os próximos tópicos foram puxados para hoje como bônus adaptativo.",
                         bg="#29203b", fg=GOLD, font=(FONT, 9, "bold"), wraplength=900, justify="left", padx=10, pady=8).pack(fill="x", pady=(0, 8))
            if selected > today:
                tk.Label(db, text="PREVISÃO: conclua o mínimo dos dias anteriores para manter esta projeção. Se um dia ficar pendente, o calendário se reorganiza a partir do primeiro tópico não concluído.",
                         bg=PANEL, fg=MUTED, font=(FONT, 8), wraplength=900, justify="left").pack(anchor="w", pady=(0, 8))
            for index, mission in enumerate(summary["lessons"]):
                row = tk.Frame(db, bg="#211d31", highlightbackground=BORDER, highlightthickness=1)
                row.pack(fill="x", pady=3)
                tk.Label(row, text=f"{mission.get('global_index', 0):03d}", bg="#211d31", fg=PURPLE, font=(FONT, 9, "bold"), width=5).pack(side="left", padx=(8, 2), pady=8)
                textf = tk.Frame(row, bg="#211d31")
                textf.pack(side="left", fill="x", expand=True, padx=5, pady=7)
                tk.Label(textf, text=mission.get("title", "Tópico"), bg="#211d31", fg=TEXT, font=(FONT, 9, "bold"), wraplength=660, justify="left").pack(anchor="w")
                meta = f"{priority_label(mission, self.active_key, current_metrics)}  ·  {estimated_minutes(mission, self.active_key)} min"
                tk.Label(textf, text=meta, bg="#211d31", fg=GOLD if self.active_key == "caixa" else MUTED, font=(FONT, 8)).pack(anchor="w", pady=(2, 0))
                current = self.next_lesson()
                if selected == today and current and mission["id"] == current["id"]:
                    self._button(row, "INICIAR", lambda m=mission:self.start_lesson(m), "mint").pack(side="right", padx=9, pady=7)
                elif selected < today and mission["id"] in set(p.get("completed_missions", [])):
                    self._button(row, "REVER", lambda m=mission:self.start_lesson(m, replay=True), "secondary").pack(side="right", padx=9, pady=7)
                else:
                    self._button(row, "PREVISTO" if selected > today else "NA FILA", lambda:None, "secondary", state="disabled").pack(side="right", padx=9, pady=7)
        if summary["reviews"]:
            revcard = self._card(root, "Recapitulações agendadas", f"{len(summary['reviews'])} PARA {selected.strftime('%d/%m/%Y')}")
            revcard.pack(fill="x", pady=(0, 12))
            revbody = tk.Frame(revcard, bg=PANEL)
            revbody.pack(fill="x", padx=15, pady=(0, 12))
            for review in summary["reviews"]:
                tk.Label(revbody, text=f"↻  {review.get('title', 'Revisão de tópico')}", bg=PANEL, fg=TEXT, font=(FONT, 9, "bold"), anchor="w", wraplength=850, justify="left").pack(fill="x", pady=3)
            self._button(revbody, "ABRIR CÂMARA DA MEMÓRIA", lambda:self.navigate("Revisões"), "gold").pack(anchor="w", pady=(5, 0))

        if self.active_key == "caixa":
            priority = self._card(root, "Peso do edital enviado", "REFERÊNCIA DE PLANEJAMENTO · TBN COMUM 2024")
            priority.pack(fill="x", pady=(0, 12))
            pb = tk.Frame(priority, bg=PANEL); pb.pack(fill="x", padx=15, pady=(0, 13))
            for name, points, note in [
                ("Conhecimentos Bancários", "15 questões", "Maior peso objetivo"),
                ("Atendimento Bancário", "10 questões", "Segunda maior parcela"),
                ("Demais eixos objetivos", "5 questões cada", "Repartir a preparação"),
                ("Redação", "Eliminatória", "Reservar treino de escrita"),
            ]:
                line = tk.Frame(pb, bg=PANEL_2); line.pack(fill="x", pady=2)
                tk.Label(line, text=name, bg=PANEL_2, fg=TEXT, font=(FONT, 8, "bold"), width=31, anchor="w").pack(side="left", padx=8, pady=7)
                tk.Label(line, text=points, bg=PANEL_2, fg=GOLD, font=(FONT, 8, "bold"), width=18, anchor="w").pack(side="left", padx=8)
                tk.Label(line, text=note, bg=PANEL_2, fg=MUTED, font=(FONT, 8), anchor="w").pack(side="left", padx=8)

    def _select_calendar_day(self, value):
        self.calendar_selected = value
        self.calendar_month = value.replace(day=1)
        self.render()

    def page_campaign(self):
        root = self.build_scroll_page()
        p = self.profile
        completed = set(p.get("completed_missions", []))
        missions = p["mission_data"]
        current = self.next_lesson()
        done = len(completed)
        pct = int(done * 100 / len(missions)) if missions else 100

        intro = self._card(root, "Crônicas da Forja", "CAMPANHA PRINCIPAL · PROGRESSÃO LINEAR")
        intro.pack(fill="x", pady=(0, 14))
        body = tk.Frame(intro, bg=PANEL)
        body.pack(fill="x", padx=16, pady=(0, 16))
        tk.Label(body, text=p["settings"].get("intro", "A campanha está pronta."), bg=PANEL, fg=MUTED,
                 font=(FONT, 9), wraplength=900, justify="left").pack(anchor="w", pady=(0, 10))
        tk.Label(body, text=f"TÓPICOS DOMINADOS  {done}/{len(missions)}  ·  {pct}%", bg=PANEL, fg=TEXT,
                 font=(FONT, 10, "bold")).pack(anchor="w", pady=(0, 6))
        self._progress(body, done, len(missions), MINT, 9).pack(fill="x")
        due_count = len(self.due_reviews())
        tk.Label(body, text=f"Revisões para hoje: {due_count}  ·  Cada etapa inclui história, resumo, atividade e prova de domínio.",
                 bg=PANEL, fg=GOLD if due_count else MUTED, font=(FONT, 8, "bold" if due_count else "normal")).pack(anchor="w", pady=(8, 0))

        current_card = self._card(root, "Próxima página da história", "SÓ UM PASSO DE CADA VEZ")
        current_card.pack(fill="x", pady=(0, 15))
        cb = tk.Frame(current_card, bg=PANEL)
        cb.pack(fill="x", padx=16, pady=(0, 16))
        pending_boss = self.pending_guardian()
        guardian_blocks_next = bool(current and pending_boss and current.get("global_index", 0) > pending_boss.get("threshold", 0))
        if current and guardian_blocks_next:
            tk.Label(cb, text="PORTAL SELADO  ·  A HISTÓRIA EXIGE UMA PROVA", bg=PANEL, fg=RED, font=(FONT, 8, "bold")).pack(anchor="w", pady=(0, 5))
            tk.Label(cb, text=pending_boss["name"], bg=PANEL, fg=GOLD, font=(FONT, 17, "bold"), wraplength=880, justify="left").pack(anchor="w", pady=(0, 4))
            tk.Label(cb, text="Você chegou a um checkpoint. Estudar mais capítulos agora não abrirá o mapa: demonstre o que aprendeu, derrote o guardião e então a próxima região será liberada.", bg=PANEL, fg=MUTED, font=(FONT, 9), wraplength=880, justify="left").pack(anchor="w")
            row = tk.Frame(cb, bg=PANEL); row.pack(fill="x", pady=(12, 0))
            self._button(row, "IR À CÂMARA DOS GUARDIÕES  ⚔", lambda:self.navigate("Chefes"), "danger").pack(side="left")
            self._button(row, "FAZER REVISÕES  ↻", lambda:self.navigate("Revisões"), "gold" if due_count else "secondary").pack(side="left", padx=(8, 0))
        elif current:
            tk.Label(cb, text=f"CAPÍTULO {current['chapter_index']:02d} / {current['chapter_total']:02d}  ·  TÓPICO {current['global_index']:03d}",
                     bg=PANEL, fg=PURPLE, font=(FONT, 8, "bold")).pack(anchor="w", pady=(0, 4))
            tk.Label(cb, text=current["chapter_title"], bg=PANEL, fg=GOLD, font=(FONT, 10, "bold")).pack(anchor="w")
            tk.Label(cb, text=current["title"], bg=PANEL, fg=TEXT, font=(FONT, 16, "bold"), wraplength=880, justify="left").pack(anchor="w", pady=(4, 5))
            tk.Label(cb, text=current["description"], bg=PANEL, fg=MUTED, font=(FONT, 9), wraplength=880, justify="left").pack(anchor="w")
            row = tk.Frame(cb, bg=PANEL); row.pack(fill="x", pady=(12, 0))
            self._button(row, "ENTRAR NA PRÓXIMA CENA  →", lambda m=current:self.start_lesson(m), "primary").pack(side="left")
            self._button(row, "VER REVISÕES  ↻", lambda:self.navigate("Revisões"), "gold" if due_count else "secondary").pack(side="left", padx=(8, 0))
        else:
            tk.Label(cb, text="Todos os tópicos foram dominados. A história aguarda o último guardião.", bg=PANEL, fg=MINT,
                     font=(FONT, 12, "bold"), wraplength=880, justify="left").pack(anchor="w", pady=(0, 10))
            self._button(cb, "IR À CÂMARA DOS GUARDIÕES  ⚔", lambda:self.navigate("Chefes"), "gold").pack(anchor="w")

        self._section(root, "Mapa capítulo por capítulo", "TÓPICOS CONCLUÍDOS · PRÓXIMO TÓPICO · ETAPAS SELADAS")
        by_chapter = {}
        for m in missions:
            by_chapter.setdefault(m["chapter_index"], []).append(m)
        next_id = current["id"] if current else None
        for chapter_idx, chapter_missions in by_chapter.items():
            chapter_done = sum(m["id"] in completed for m in chapter_missions)
            chapter_total = len(chapter_missions)
            open_chapter = chapter_missions[0]["chapter_title"]
            card = tk.Frame(root, bg=PANEL, highlightbackground=PURPLE if any(m["id"] == next_id for m in chapter_missions) else BORDER, highlightthickness=1)
            card.pack(fill="x", pady=(0, 9))
            head = tk.Frame(card, bg=PANEL); head.pack(fill="x", padx=14, pady=(11, 7))
            tk.Label(head, text=f"{chapter_idx:02d}  ·  {open_chapter}", bg=PANEL, fg=TEXT, font=(FONT, 10, "bold"), wraplength=620, justify="left").pack(side="left", fill="x", expand=True)
            tk.Label(head, text=f"{chapter_done}/{chapter_total}", bg=PANEL, fg=MINT if chapter_done == chapter_total else MUTED, font=(FONT, 8, "bold")).pack(side="right")
            content = tk.Frame(card, bg=PANEL); content.pack(fill="x", padx=14, pady=(0, 11))
            self._progress(content, chapter_done, chapter_total, MINT if chapter_done == chapter_total else PURPLE, 5).pack(fill="x", pady=(0, 7))
            for m in chapter_missions:
                is_done = m["id"] in completed
                is_next = m["id"] == next_id
                row = tk.Frame(content, bg="#201f30" if is_next else ("#15151e" if is_done else PANEL_2),
                               highlightbackground=PURPLE if is_next else BORDER, highlightthickness=1 if is_next else 0)
                row.pack(fill="x", pady=2)
                mark = "✓" if is_done else ("▶" if is_next else "🔒")
                tk.Label(row, text=mark, bg=row.cget("bg"), fg=MINT if is_done else (GOLD if is_next else "#777188"),
                         width=3, font=(FONT, 9, "bold")).pack(side="left", padx=(3, 0), pady=7)
                textf = tk.Frame(row, bg=row.cget("bg")); textf.pack(side="left", fill="x", expand=True, padx=4, pady=5)
                tk.Label(textf, text=f"{m['global_index']:03d}. {m['title']}", bg=row.cget("bg"), fg=TEXT if (is_next or is_done) else "#8b869d",
                         font=(FONT, 8, "bold"), anchor="w", wraplength=700, justify="left").pack(fill="x", anchor="w")
                review = next((r for r in p.get("review_queue", []) if r.get("lesson_id") == m["id"] and not r.get("done")), None)
                small_status = "Dominado" if is_done else ("Desbloqueado agora" if is_next else "Conclua os tópicos anteriores")
                if is_done and review:
                    small_status += " · revisão amanhã" if review.get("due_date", "") > date.today().isoformat() else " · revisão pendente"
                tk.Label(textf, text=small_status, bg=row.cget("bg"), fg=MUTED, font=(FONT, 7), anchor="w").pack(fill="x", anchor="w", pady=(1, 0))
                if is_done:
                    self._button(row, "REVER", lambda lesson=m:self.start_lesson(lesson, replay=True), "secondary").pack(side="right", padx=7, pady=4)
                elif is_next:
                    self._button(row, "INICIAR", lambda lesson=m:self.start_lesson(lesson), "mint").pack(side="right", padx=7, pady=4)
                else:
                    self._button(row, "SELADO", lambda:None, "secondary", state="disabled").pack(side="right", padx=7, pady=4)

    def start_lesson(self, lesson, replay=False):
        p = self.profile
        completed = set(p.get("completed_missions", []))
        next_item = self.next_lesson()
        if lesson["id"] not in completed and next_item and lesson["id"] != next_item["id"]:
            messagebox.showinfo("Página selada", "A história é linear. Conclua o tópico atual e seu teste para abrir esta página.")
            return
        already_done = lesson["id"] in completed
        waiting_boss = self.pending_guardian()
        if not replay and not already_done and waiting_boss and lesson.get("global_index", 0) > waiting_boss.get("threshold", 0):
            messagebox.showinfo("Guardião entre você e a próxima região", f"A próxima página ficará selada até você demonstrar domínio e derrotar {waiting_boss['name']}.")
            self.navigate("Chefes")
            return
        if not replay and not already_done:
            overdue = self.due_reviews()
            if overdue and messagebox.askyesno(
                "A Câmara da Memória chama",
                f"Você tem {len(overdue)} recapitulação(ões) de dias anteriores. Quer reforçar a memória antes de abrir uma nova página?\n\n"
                "Se escolher Não, a campanha continua normalmente; a revisão ficará disponível no menu Revisões.",
                icon="question"):
                self.navigate("Revisões")
                return
        win = tk.Toplevel(self)
        win.title(f"Crônicas da Forja — {lesson['title']}")
        win.geometry("850x650")
        win.minsize(720, 560)
        win.configure(bg=BG)
        win.transient(self); win.grab_set()
        shell = tk.Frame(win, bg=BG); shell.pack(fill="both", expand=True, padx=24, pady=20)

        def clear_shell():
            for child in shell.winfo_children(): child.destroy()

        def draw_story():
            clear_shell()
            tk.Label(shell, text=f"CRÔNICAS DA FORJA  /  CAPÍTULO {lesson['chapter_index']:02d}", bg=BG, fg=GOLD, font=(FONT, 8, "bold")).pack(anchor="w")
            tk.Label(shell, text=lesson["chapter_title"], bg=BG, fg=TEXT, font=(FONT, 20, "bold"), wraplength=780, justify="left").pack(anchor="w", pady=(7, 3))
            tk.Label(shell, text=f"TÓPICO {lesson['global_index']:03d}  ·  {lesson['lesson_index']}/{lesson['lessons_in_chapter']}", bg=BG, fg=PURPLE, font=(FONT, 8, "bold")).pack(anchor="w", pady=(0, 16))
            dialogue = lesson.get("story_intro", "Íria aponta para a próxima página.")
            story_box = tk.Frame(shell, bg="#20172f", highlightbackground="#6b4c91", highlightthickness=1)
            story_box.pack(fill="x", pady=(0, 18))
            try:
                self.lesson_iria_image = tk.PhotoImage(file=str(self._asset_path("iria_portrait.png"))).subsample(3, 3)
                tk.Label(story_box, image=self.lesson_iria_image, bg="#20172f", bd=0).pack(side="left", padx=(10, 14), pady=10)
            except Exception:
                tk.Label(story_box, text="ÍRIA", bg="#20172f", fg=PURPLE, font=(FONT, 13, "bold"), width=8, height=5).pack(side="left", padx=10, pady=10)
            dialogue_panel = tk.Frame(story_box, bg="#20172f")
            dialogue_panel.pack(side="left", fill="both", expand=True, padx=(0, 14), pady=10)
            tk.Label(dialogue_panel, text="ÍRIA  /  NARRADORA", bg="#20172f", fg=GOLD, font=(FONT, 8, "bold")).pack(anchor="w", pady=(3, 5))
            tk.Label(dialogue_panel, text=dialogue, bg="#20172f", fg="#e5dcef", font=(FONT, 10), wraplength=600, justify="left").pack(anchor="w", pady=(0, 5))
            tk.Label(shell, text="SEU OBJETIVO", bg=BG, fg=MINT, font=(FONT, 8, "bold")).pack(anchor="w")
            tk.Label(shell, text=lesson.get("success_criteria", "Explique o conceito e aplique-o em uma atividade."), bg=BG, fg=TEXT,
                     font=(FONT, 10), wraplength=780, justify="left").pack(anchor="w", pady=(5, 15))
            tk.Label(shell, text="Não é necessário decorar a narrativa. O importante é aprender o conteúdo e provar isso no teste.", bg=BG, fg=MUTED,
                     font=(FONT, 9), wraplength=780, justify="left").pack(anchor="w")
            footer = tk.Frame(shell, bg=BG); footer.pack(fill="x", side="bottom", pady=(16, 0))
            self._button(footer, "VOLTAR À CAMPANHA", win.destroy, "secondary").pack(side="left")
            self._button(footer, "AVANÇAR PARA A AULA  →", draw_study, "primary").pack(side="right")

        def draw_study():
            clear_shell()
            tk.Label(shell, text=f"AULA GUIADA  /  {lesson['global_index']:03d}", bg=BG, fg=PURPLE, font=(FONT, 8, "bold")).pack(anchor="w")
            tk.Label(shell, text=lesson["title"], bg=BG, fg=TEXT, font=(FONT, 18, "bold"), wraplength=780, justify="left").pack(anchor="w", pady=(6, 12))
            summary = tk.Frame(shell, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
            summary.pack(fill="x", pady=(0, 10))
            tk.Label(summary, text="ROTEIRO DA MISSÃO", bg=PANEL, fg=GOLD, font=(FONT, 8, "bold")).pack(anchor="w", padx=15, pady=(12, 4))
            tk.Label(summary, text=lesson.get("lesson_text", lesson.get("description", "")), bg=PANEL, fg=TEXT,
                     font=(FONT, 9), wraplength=740, justify="left").pack(anchor="w", padx=15, pady=(0, 12))
            tk.Label(shell, text="ATIVIDADE PRÁTICA — FAÇA ANTES DA PROVA", bg=BG, fg=MINT, font=(FONT, 8, "bold")).pack(anchor="w")
            tk.Label(shell, text=lesson.get("practice", "Estude o tópico na sua fonte principal e resolva um exemplo."), bg=BG, fg=MUTED,
                     font=(FONT, 9), wraplength=780, justify="left").pack(anchor="w", pady=(4, 8))
            tk.Label(shell, text="ANOTAÇÕES DESTA LIÇÃO (SALVAS LOCALMENTE)", bg=BG, fg=PURPLE, font=(FONT, 8, "bold")).pack(anchor="w")
            notes = tk.Text(shell, height=4, bg=PANEL_2, fg=TEXT, insertbackground=TEXT, relief="flat", wrap="word", font=(FONT, 9), padx=10, pady=8)
            notes.pack(fill="both", expand=True, pady=(5, 5))
            notes.insert("1.0", p.get("lesson_notes", {}).get(lesson["id"], ""))
            tk.Label(shell, text="Feche o material, explique o conceito sem consulta e só então confirme que concluiu a atividade.", bg=BG, fg=MUTED, font=(FONT, 8), wraplength=780, justify="left").pack(anchor="w", pady=(0, 4))
            practiced = tk.BooleanVar(master=win, value=False)
            check = tk.Checkbutton(shell, text="CONCLUÍ A ATIVIDADE E CONSIGO EXPLICAR O TÓPICO COM MINHAS PALAVRAS",
                                   variable=practiced, bg=BG, fg=GOLD, selectcolor=PANEL_2, activebackground=BG,
                                   activeforeground=GOLD, font=(FONT, 8, "bold"), anchor="w", justify="left")
            check.pack(fill="x", pady=(3, 0))
            footer = tk.Frame(shell, bg=BG); footer.pack(fill="x", side="bottom", pady=(9, 0))
            self._button(footer, "VOLTAR À HISTÓRIA", draw_story, "secondary").pack(side="left")
            if self.active_key == "python":
                self._button(footer, "ABRIR CURSO NA UDEMY ↗", lambda:webbrowser.open("https://www.udemy.com/course/python-3-do-zero-ao-avancado/"), "secondary").pack(side="left", padx=(7, 0))
            def begin_test():
                if not practiced.get():
                    messagebox.showinfo("Atividade pendente", "Marque a confirmação somente depois de realizar a atividade prática.", parent=win)
                    return
                p.setdefault("lesson_notes", {})[lesson["id"]] = notes.get("1.0", "end").strip()
                self.save()
                win.destroy()
                self.run_quiz_dialog(
                    f"Prova de domínio · {lesson['title']}",
                    "Responda sem consultar. São necessárias 3 respostas corretas em 4 para dominar o tópico.",
                    lesson.get("quiz", []), 3,
                    lambda score:self.finish_lesson(lesson, score),
                    retry_label="REFAZER A PROVA",
                    on_return=lambda:self.start_lesson(lesson, replay=True),
                    on_attempt=lambda score, total, records:self._record_lesson_attempt(lesson, score, total, records),
                )
            test_button = self._button(footer, "PROVAR DOMÍNIO · 4 QUESTÕES →", begin_test, "primary", state="disabled")
            test_button.pack(side="right")
            def update_test_button(*_):
                test_button.configure(state="normal" if practiced.get() else "disabled")
            practiced.trace_add("write", update_test_button)

        if replay or already_done:
            draw_study()
        else:
            draw_story()

    def run_quiz_dialog(self, title, subtitle, questions, required_correct, on_success, retry_label="TENTAR NOVAMENTE", on_return=None, on_attempt=None, result_mode="mastery"):
        if not questions:
            messagebox.showwarning("Teste indisponível", "Ainda não há questões suficientes para esta prova.")
            return
        questions = list(questions)
        random.shuffle(questions)
        win = tk.Toplevel(self)
        win.title(title)
        win.geometry("760x570")
        win.minsize(680, 500)
        win.configure(bg=BG)
        win.transient(self); win.grab_set()
        state = {"index": 0, "score": 0, "answered": False, "answer_records": [], "attempt_logged": False}
        host = tk.Frame(win, bg=BG); host.pack(fill="both", expand=True, padx=24, pady=20)

        def clear():
            for child in host.winfo_children(): child.destroy()

        def draw_question():
            clear(); state["answered"] = False
            q = questions[state["index"]]
            tk.Label(host, text="PROVA DE DOMÍNIO", bg=BG, fg=PURPLE, font=(FONT, 8, "bold")).pack(anchor="w")
            tk.Label(host, text=title, bg=BG, fg=TEXT, font=(FONT, 16, "bold"), wraplength=700, justify="left").pack(anchor="w", pady=(5, 3))
            tk.Label(host, text=f"QUESTÃO {state['index']+1}/{len(questions)}  ·  ACERTOS ATÉ AGORA: {state['score']}", bg=BG, fg=GOLD, font=(FONT, 8, "bold")).pack(anchor="w", pady=(0, 12))
            tk.Label(host, text=q.get("q", "Explique o conceito estudado."), bg=PANEL, fg=TEXT, font=(FONT, 11, "bold"),
                     wraplength=680, justify="left", padx=15, pady=15).pack(fill="x", pady=(0, 12))
            choice = tk.IntVar(value=-1)
            for i, option in enumerate(q.get("options", [])):
                rb = tk.Radiobutton(host, text=f"{chr(65+i)}.  {option}", variable=choice, value=i, bg=BG, fg=TEXT, selectcolor=PANEL_2,
                                    activebackground=BG, activeforeground=TEXT, font=(FONT, 9), wraplength=660, justify="left", anchor="w")
                rb.pack(fill="x", anchor="w", pady=4)
            feedback = tk.Label(host, text="", bg=BG, fg=MUTED, font=(FONT, 9), wraplength=680, justify="left")
            feedback.pack(fill="x", pady=(12, 2))
            footer = tk.Frame(host, bg=BG); footer.pack(fill="x", side="bottom", pady=(14, 0))
            self._button(footer, "SAIR", win.destroy, "secondary").pack(side="left")
            action = self._button(footer, "CONFIRMAR RESPOSTA", lambda:None, "primary")
            action.pack(side="right")

            def submit():
                if not state["answered"]:
                    selected = choice.get()
                    if selected < 0:
                        messagebox.showinfo("Escolha uma alternativa", "Selecione uma alternativa antes de confirmar.", parent=win)
                        return
                    state["answered"] = True
                    correct = selected == q.get("a", 0)
                    if correct: state["score"] += 1
                    state["answer_records"].append({"question": q.get("q", ""), "subject": q.get("_planner_subject", q.get("subject", "Geral")), "block": q.get("_exam_block", q.get("block", "")), "correct": bool(correct)})
                    feedback.configure(text=("CORRETO. " if correct else f"RESPOSTA: {chr(65+q.get('a',0))}. ") + q.get("why", "Revise o conceito."), fg=MINT if correct else RED)
                    action.configure(text="PRÓXIMA QUESTÃO  →", command=advance, bg=PURPLE)
                else:
                    advance()

            def advance():
                if state["index"] + 1 < len(questions):
                    state["index"] += 1; draw_question()
                else:
                    draw_result()
            action.configure(command=submit)

        def draw_result():
            clear()
            total = len(questions); score = state["score"]
            if not state.get("attempt_logged"):
                state["attempt_logged"] = True
                if on_attempt:
                    try:
                        on_attempt(score, total, list(state["answer_records"]))
                    except Exception as exc:
                        messagebox.showwarning("Registro de resultado", f"O resultado foi calculado, mas o registro adaptativo falhou.\n\n{exc}", parent=win)
            passed = score >= required_correct
            if result_mode == "diagnostic":
                heading = "Diagnóstico registrado"
                kicker = "CALIBRAÇÃO DE CONHECIMENTO"
                msg = "Este resultado foi salvo como evidência de desempenho. Ele ajusta a prioridade do assunto, mas não altera a ordem da campanha nem libera conteúdo."
                primary_label = "ATUALIZAR ESTRATÉGIA  →"
            elif result_mode == "simulado":
                heading = "Simulado concluído"
                kicker = "RESULTADO DE TREINO · NÃO É PROVA OFICIAL"
                msg = "O desempenho por assunto foi salvo. As áreas com mais erros recebem prioridade maior no próximo plano. Refaça depois de estudar os pontos fracos e compare a evolução."
                primary_label = "VER ESTRATÉGIA  →"
            else:
                heading = "Prova concluída" if passed else "Ainda há névoa nesta página"
                kicker = "SELO DE DOMÍNIO"
                msg = "Você demonstrou domínio suficiente para avançar. A próxima página da história está pronta." if passed else "Releia as explicações das questões e tente novamente. Seu progresso não será penalizado, mas a próxima página permanece selada."
                primary_label = "CONTINUAR A HISTÓRIA  →"
            tk.Label(host, text=kicker, bg=BG, fg=GOLD, font=(FONT, 8, "bold")).pack(anchor="w")
            tk.Label(host, text=heading, bg=BG, fg=(MINT if passed else RED), font=(FONT, 21, "bold")).pack(anchor="w", pady=(7, 5))
            result_line = f"Resultado: {score}/{total}  ·  {score / max(1, total) * 100:.0f}% de acerto"
            if result_mode == "mastery":
                result_line += f"  ·  mínimo exigido: {required_correct}/{total}"
            tk.Label(host, text=result_line, bg=BG, fg=TEXT, font=(FONT, 12, "bold")).pack(anchor="w", pady=(0, 12))
            tk.Label(host, text=msg, bg=PANEL, fg=MUTED, font=(FONT, 10), wraplength=680, justify="left", padx=15, pady=15).pack(fill="x")
            footer = tk.Frame(host, bg=BG); footer.pack(fill="x", side="bottom", pady=(20, 0))
            if passed or result_mode in ("diagnostic", "simulado"):
                def accept():
                    win.destroy()
                    on_success(score)
                self._button(footer, primary_label, accept, "mint").pack(side="right")
            else:
                def retry():
                    state["index"] = 0; state["score"] = 0; state["answer_records"] = []; state["attempt_logged"] = False; random.shuffle(questions); draw_question()
                self._button(footer, retry_label, retry, "primary").pack(side="right")
                if on_return:
                    self._button(footer, "VOLTAR AO ESTUDO", lambda:(win.destroy(), on_return()), "secondary").pack(side="left")
                else:
                    self._button(footer, "FECHAR", win.destroy, "secondary").pack(side="left")
        draw_question()

    def finish_lesson(self, lesson, score):
        p = self.profile
        lid = lesson["id"]
        stats = p.setdefault("quiz_stats", {}).setdefault(lid, {"attempts": 0, "best": 0})
        stats["attempts"] = safe_int(stats.get("attempts", 0)) + 1
        stats["best"] = max(safe_int(stats.get("best", 0)), score)
        stats["last_score"] = score
        already_done = lid in p.get("completed_missions", [])
        if not already_done:
            p.setdefault("completed_missions", []).append(lid)
            p.setdefault("calendar_completed_on", {})[lid] = date.today().isoformat()
            xp = safe_int(lesson.get("xp", 30)); gold = safe_int(lesson.get("coins", 10))
            p["gold"] += gold
            levels = self.gain_xp(xp)
            self.update_streak()
            p.setdefault("history", []).append({"date": date.today().isoformat(), "type": "lição", "title": lesson["title"], "xp": xp, "gold": gold, "score": score})
            if not any(r.get("lesson_id") == lid and safe_int(r.get("stage", 1)) == 1 for r in p.setdefault("review_queue", [])):
                p["review_queue"].append({"id": f"review_{lid}_s1", "lesson_id": lid, "title": lesson["title"], "topic": lesson["topic"],
                                           "stage": 1, "interval_days": 1, "due_date": (date.today() + timedelta(days=1)).isoformat(), "done": False, "reward_claimed": False})
            if lesson.get("is_chapter_start"):
                seen = p.setdefault("story_chapters_seen", [])
                if lesson["chapter_index"] not in seen: seen.append(lesson["chapter_index"])
            self.status_var.set(f"Tópico dominado: {lesson['title']} · revisão marcada para amanhã.")
        else:
            xp = gold = 0; levels = 0
            self.status_var.set(f"Tópico revisitado: {lesson['title']}. Nenhuma recompensa foi duplicada.")
        self.save(); self.render()
        w = tk.Toplevel(self); w.title("Fragmento conquistado"); w.geometry("620x400"); w.configure(bg=BG); w.transient(self); w.grab_set()
        tk.Label(w, text="FRAGMENTO DA CRÔNICA", bg=BG, fg=GOLD, font=(FONT, 8, "bold")).pack(anchor="w", padx=24, pady=(22, 8))
        tk.Label(w, text="A página responde à sua coragem", bg=BG, fg=MINT if not already_done else TEXT, font=(FONT, 19, "bold"), wraplength=560, justify="left").pack(anchor="w", padx=24)
        reward = "Tópico já conquistado. Seu registro e suas anotações continuam salvos." if already_done else f"+{xp} XP  ·  +{gold} ouro  ·  {score}/4 respostas corretas\nUma recapitulação foi agendada para {(date.today()+timedelta(days=1)).strftime('%d/%m/%Y')}."
        if levels: reward += f"\n\nVocê subiu {levels} nível(is) e recebeu {levels*2} pontos de atributo."
        tk.Label(w, text=reward, bg=PANEL, fg=TEXT, font=(FONT, 10), wraplength=540, justify="left", padx=14, pady=14).pack(fill="x", padx=24, pady=(14, 10))
        line = lesson.get("story_outro", "Íria sorri e aponta para o mapa.")
        if lesson.get("is_chapter_end"):
            line += "\n\nCAPÍTULO CONCLUÍDO. O mapa registra que esta parte da jornada foi atravessada. Um guardião pode exigir uma prova maior antes da próxima grande passagem."
        tk.Label(w, text=line, bg=BG, fg=MUTED, font=(FONT, 9), wraplength=560, justify="left").pack(anchor="w", padx=24, pady=(0, 10))
        pending = self.pending_guardian()
        if pending:
            self._button(w, "AVANÇAR PARA A PROVA DO GUARDIÃO  ⚔", lambda:(w.destroy(), self.navigate("Chefes")), "danger").pack(anchor="e", padx=24, pady=(3, 20))
        else:
            self._button(w, "RETOMAR A CAMPANHA  →", w.destroy, "primary").pack(anchor="e", padx=24, pady=(3, 20))

    # -------------------------- NEXT-DAY REVIEWS --------------------------
    def page_reviews(self):
        root = self.build_scroll_page()
        p = self.profile
        today = date.today().isoformat()
        due = self.due_reviews()
        future = sorted([r for r in p.get("review_queue", []) if not r.get("done") and r.get("due_date", "") > today], key=lambda x:x.get("due_date", ""))
        done_count = sum(1 for r in p.get("review_queue", []) if r.get("done"))
        card = self._card(root, "A Câmara da Memória", "REPETIÇÃO ESPAÇADA · D+1 / D+7 / D+30")
        card.pack(fill="x", pady=(0, 14))
        body = tk.Frame(card, bg=PANEL); body.pack(fill="x", padx=16, pady=(0, 16))
        tk.Label(body, text=f"{len(due)} revisão(ões) vencida(s) hoje  ·  {len(future)} agendada(s)  ·  {done_count} já revisada(s)", bg=PANEL,
                 fg=GOLD if due else TEXT, font=(FONT, 11, "bold")).pack(anchor="w", pady=(0, 6))
        tk.Label(body, text="Cada tópico retorna no dia seguinte; ao passar, a revisão seguinte é espaçada para 7 dias e depois 30 dias. Se não lembrar, revise e tente novamente: isso é informação para ajustar o estudo, não uma punição.", bg=PANEL, fg=MUTED,
                 font=(FONT, 9), wraplength=900, justify="left").pack(anchor="w")

        self._section(root, "Revisões que já venceram", "PRIORIDADE DE HOJE")
        if not due:
            empty = self._card(root, "Nenhuma revisão pendente", "A CÂMARA ESTÁ EM PAZ")
            empty.pack(fill="x", pady=(0, 14))
            tk.Label(empty, text="Continue a campanha. As revisões dos tópicos concluídos aparecerão automaticamente no dia seguinte.", bg=PANEL, fg=MUTED,
                     font=(FONT, 9), wraplength=880, justify="left").pack(anchor="w", padx=16, pady=(0, 14))
        for review in due:
            self._review_card(root, review, due_now=True)
        self._section(root, "Revisões futuras", "SERÃO LIBERADAS NA DATA INDICADA")
        for review in future[:30]:
            self._review_card(root, review, due_now=False)

    def _review_card(self, parent, review, due_now):
        card = tk.Frame(parent, bg=PANEL, highlightbackground=GOLD if due_now else BORDER, highlightthickness=1)
        card.pack(fill="x", pady=(0, 8))
        body = tk.Frame(card, bg=PANEL); body.pack(fill="x", padx=14, pady=11)
        tk.Label(body, text=review.get("topic", "Recapitulação"), bg="#29213a", fg=PURPLE, font=(FONT, 7, "bold"), padx=7, pady=3).pack(anchor="w")
        tk.Label(body, text=review.get("title", "Revisão de tópico"), bg=PANEL, fg=TEXT, font=(FONT, 10, "bold"), wraplength=650, justify="left").pack(anchor="w", pady=(5, 3))
        stage = safe_int(review.get("stage", 1), 1)
        interval = safe_int(review.get("interval_days", {1: 1, 2: 7, 3: 30}.get(stage, 1)), 1)
        tk.Label(body, text=f"Etapa D+{interval} · Data: {review.get('due_date','')} · 3 questões · precisa acertar 2/3", bg=PANEL, fg=MUTED, font=(FONT, 8)).pack(anchor="w")
        if due_now:
            self._button(body, "INICIAR RECAPITULAÇÃO  ↻", lambda r=review:self.start_review(r), "gold").pack(anchor="e", pady=(7, 0))
        else:
            self._button(body, "AGUARDANDO DATA", lambda:None, "secondary", state="disabled").pack(anchor="e", pady=(7, 0))

    def start_review(self, review):
        if review.get("done"):
            messagebox.showinfo("Revisão concluída", "Esta recapitulação já foi concluída.")
            return
        if review.get("due_date", "9999") > date.today().isoformat():
            messagebox.showinfo("Ainda não é o dia", f"Esta recapitulação estará disponível em {review['due_date']}.")
            return
        lesson = self.lesson_by_id(review.get("lesson_id", ""))
        if not lesson:
            messagebox.showwarning("Tópico não encontrado", "O tópico desta revisão não existe mais na trilha atual.")
            return
        questions = list(lesson.get("quiz", []))
        random.shuffle(questions)
        questions = questions[:3]
        self.run_quiz_dialog(
            f"Recapitulação · {lesson['title']}", "Recupere de memória o que estudou ontem. São necessárias 2 respostas corretas em 3.",
            questions, 2, lambda score:self.finish_review(review, lesson, score), retry_label="TENTAR A REVISÃO NOVAMENTE",
            on_attempt=lambda score, total, records:self._record_lesson_attempt(lesson, score, total, records),
        )

    def finish_review(self, review, lesson, score):
        p = self.profile
        review["done"] = True
        review["reviewed_at"] = date.today().isoformat()
        review["score"] = score
        xp = 12 if not review.get("reward_claimed") else 0
        gold = 5 if not review.get("reward_claimed") else 0
        review["reward_claimed"] = True
        p["gold"] += gold
        levels = self.gain_xp(xp)
        self.update_streak()
        p.setdefault("history", []).append({"date":date.today().isoformat(), "type":"revisão", "title":lesson["title"], "xp":xp, "gold":gold, "score":score})
        stage = safe_int(review.get("stage", 1), 1)
        next_stage = stage + 1
        if next_stage <= 3 and not any(r.get("lesson_id") == lesson["id"] and safe_int(r.get("stage", 1)) == next_stage for r in p.setdefault("review_queue", [])):
            interval = {2: 7, 3: 30}[next_stage]
            p["review_queue"].append({"id": f"review_{lesson['id']}_s{next_stage}", "lesson_id": lesson["id"],
                                       "title": lesson["title"], "topic": lesson["topic"], "stage": next_stage,
                                       "interval_days": interval, "due_date": (date.today() + timedelta(days=interval)).isoformat(),
                                       "done": False, "reward_claimed": False})
        self.save(); self.render()
        msg = f"Recapitulação concluída: {score}/3.\n+{xp} XP · +{gold} ouro."
        if levels: msg += f"\nVocê subiu {levels} nível(is)!"
        next_review = next((r for r in p.get("review_queue", []) if r.get("lesson_id") == lesson["id"] and not r.get("done") and safe_int(r.get("stage", 1)) == next_stage), None)
        if next_review:
            msg += f"\nPróxima revisão: {next_review['due_date']} (D+{next_review.get('interval_days', 7)})."
        self.status_var.set(f"Memória reforçada: {lesson['title']}.")
        messagebox.showinfo("Memória reforçada", msg)

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
            previous_defeated = i == 0 or p["boss_data"][i-1]["id"] in p.get("bosses_defeated", [])
            unlocked = count >= boss["threshold"] and previous_defeated
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
                self._button(main, "PROVAR DOMÍNIO  →", lambda b=boss:self.start_boss_exam(b), "danger").pack(side="right", padx=(8,0))
            else:
                self._button(main, "BLOQUEADO", lambda:None, "secondary", state="disabled").pack(side="right", padx=(8,0))

    def start_boss_exam(self, boss):
        """Require a cumulative knowledge check before opening the turn-based boss fight."""
        p = self.profile
        completed = set(p.get("completed_missions", []))
        pool, seen = [], set()
        for lesson in p.get("mission_data", []):
            if lesson.get("id") not in completed:
                continue
            for question in lesson.get("quiz", []):
                key = question.get("q", "")
                if key and key not in seen:
                    seen.add(key)
                    pool.append(dict(question))
            if lesson.get("global_index", 0) >= boss.get("threshold", 0):
                break
        if not pool:
            messagebox.showinfo("Prova ainda não disponível", "Conclua os tópicos exigidos antes de fazer a prova do guardião.")
            return
        random.shuffle(pool)
        questions = pool[:min(5, len(pool))]
        needed = max(1, (len(questions) * 4 + 4) // 5)
        def passed(score):
            p.setdefault("boss_exam_results", {})[boss["id"]] = {
                "date": date.today().isoformat(), "score": score, "total": len(questions), "passed": True
            }
            self.save()
            messagebox.showinfo("Selo aceito", f"Você acertou {score}/{len(questions)}. O guardião aceitou sua prova. Prepare-se para o combate.")
            self.fight_boss(boss)
        self.run_quiz_dialog(
            f"Prova do guardião · {boss['name']}",
            f"Revisão cumulativa de tudo que você concluiu. É necessário acertar {needed} de {len(questions)} para abrir a batalha.",
            questions, needed, passed, retry_label="REFAZER A PROVA",
        )

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
        tk.Label(cb,text="Se alterar os temas, o aplicativo cria cinco páginas guiadas para cada tema: definir objetivo, estudar, praticar com apoio, aplicar sem consulta e explicar/consolidar. Cada página tem história, teste de domínio e recapitulação no dia seguinte.",bg=PANEL,fg=MUTED,font=(FONT,8),wraplength=900,justify="left").pack(anchor="w",pady=(6,12))
        tk.Label(cb,text="Missões personalizadas (opcional)",bg=PANEL,fg=MUTED,font=(FONT,8,"bold")).pack(anchor="w",pady=(0,4))
        missions_text=tk.Text(cb,height=6,bg=PANEL_2,fg=TEXT,insertbackground=TEXT,relief="flat",wrap="word",font=("Consolas",9),padx=8,pady=7)
        missions_text.pack(fill="x")
        missions_text.insert("1.0",s.get("missions_text",""))
        tk.Label(cb,text="Uma etapa por linha: TEMA | TÍTULO | DESCRIÇÃO | XP | OURO. Cada linha vira uma página com prova de domínio e revisão no dia seguinte. Se deixar vazio, cada tema gera cinco páginas guiadas.",bg=PANEL,fg=MUTED,font=(FONT,8),wraplength=900,justify="left").pack(anchor="w",pady=(5,0))

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
                lines=[line for line in custom_lines.splitlines() if line.strip() and not line.strip().startswith("#")]
                for i,line in enumerate(lines,1):
                    parts=[x.strip() for x in line.split("|")]
                    if len(parts)<5:
                        messagebox.showwarning("Formato de missão",f"Linha {i} precisa ter: TEMA | TÍTULO | DESCRIÇÃO | XP | OURO.");return
                    topic,title,description=parts[0],parts[1],parts[2]
                    template=build_campaign_missions("custom",[topic])[0]
                    item=dict(template)
                    item["id"]=f"user_{i}"
                    item["chapter_title"]=topic; item["chapter_index"]=i; item["chapter_total"]=len(lines)
                    item["lesson_index"]=1; item["lessons_in_chapter"]=1; item["global_index"]=i
                    item["chapter_last_lesson_id"]=item["id"]; item["is_chapter_start"]=True; item["is_chapter_end"]=True
                    item["boss_checkpoint"]=i in chapter_boss_thresholds([{"global_index":j+1,"is_chapter_end":True} for j in range(len(lines))],5)
                    item["topic"]=topic; item["title"]=title; item["description"]=description
                    item["lesson_text"]=f"IDEIA-CHAVE\n{description}\n\nPOR QUE ISSO IMPORTA\nConecte a ideia ao material principal e explique-a com suas palavras."
                    item["practice"]=description; item["success_criteria"]=f"Você consegue explicar '{title}' e demonstrar a competência sem apenas copiar."
                    item["story_intro"]=f"Íria abre o capítulo {i}: '{title}'. A passagem só se abrirá depois que você demonstrar o que aprendeu."
                    item["story_outro"]=f"O selo de '{title}' se acende. Mais um fragmento da sua jornada foi conquistado."
                    item["xp"]=max(0,safe_int(parts[3],30)); item["coins"]=max(0,safe_int(parts[4],10))
                    # If a custom question has the same subject/topic, use it for this lesson's mastery test.
                    matching=[]
                    for qi,qline in enumerate(qtext.get("1.0","end").splitlines(),1):
                        if not qline.strip() or qline.strip().startswith("#"): continue
                        qparts=[x.strip() for x in qline.split("|")]
                        if len(qparts)>=8 and qparts[0].casefold()==topic.casefold() and qparts[6].upper() in "ABCD":
                            matching.append({"id":f"customq{qi}","subject":qparts[0],"q":qparts[1],"options":qparts[2:6],"a":"ABCD".index(qparts[6].upper()),"why":qparts[7]})
                    if matching:item["quiz"]=matching[:4]
                    new_missions.append(item)
                if not new_missions:
                    messagebox.showwarning("Missões vazias","Não encontrei missões válidas.");return
                p["mission_data"]=new_missions
                valid={m["id"] for m in new_missions}
                p["completed_missions"]=[mid for mid in p["completed_missions"] if mid in valid]
                p["review_queue"]=[r for r in p.get("review_queue",[]) if r.get("lesson_id") in valid]
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
        row1=tk.Frame(root,bg=BG);row1.pack(fill="x",pady=(0,8))
        row2=tk.Frame(root,bg=BG);row2.pack(fill="x",pady=(0,15))
        self._button(row1,"SALVAR PERSONALIZAÇÃO  ✓",apply_settings,"primary").pack(side="left",padx=(0,8))
        self._button(row1,"BACKUP COMPLETO ZIP  ↓",self.export_full_backup,"gold").pack(side="left",padx=(0,8))
        self._button(row1,"IMPORTAR ZIP / JSON  ↑",self.import_save,"secondary").pack(side="left",padx=(0,8))
        self._button(row2,"EXPORTAR SAVE JSON",self.export_save,"secondary").pack(side="left",padx=(0,8))
        self._button(row2,"REINICIAR / APAGAR PROGRESSO DESTE SLOT",self.reset_active_profile,"danger").pack(side="left",padx=(0,8))

    def make_generic_missions(self,topics):
        return build_campaign_missions("custom", topics)

    def _write_safety_backup(self, tag="safety"):
        """Write a complete local save copy before a destructive operation."""
        folder = self.save_file.parent / "backups"
        folder.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = folder / f"hunter_system_{tag}_{stamp}.json"
        path.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def export_full_backup(self):
        """Export all three slots and the manifest in one portable ZIP."""
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = filedialog.asksaveasfilename(
            title="Salvar backup completo", defaultextension=".zip",
            filetypes=[("Backup completo Hunter System", "*.zip")],
            initialfile=f"HunterSystem_Backup_Completo_{stamp}.zip")
        if not path:
            return
        try:
            save_json = json.dumps(self.data, ensure_ascii=False, indent=2).encode("utf-8")
            manifest = {
                "application": APP_NAME, "format_version": 1,
                "created_at": datetime.now().isoformat(timespec="seconds"),
                "active_profile": self.active_key,
                "profiles": {
                    key: {"title": profile.get("settings", {}).get("title", key),
                          "completed_topics": len(profile.get("completed_missions", [])),
                          "total_topics": len(profile.get("mission_data", []))}
                    for key, profile in self.data.get("profiles", {}).items()
                },
                "contents": ["save.json", "manifest.json"],
            }
            with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                archive.writestr("save.json", save_json)
                archive.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
            messagebox.showinfo("Backup completo criado", f"Os três slots, anotações, inventário, revisões e histórico foram incluídos.\n\nArquivo:\n{path}")
        except Exception as exc:
            messagebox.showerror("Erro ao criar backup", f"Não foi possível criar o ZIP.\n\n{exc}")

    def export_save(self):
        path=filedialog.asksaveasfilename(title="Exportar save JSON",defaultextension=".json",filetypes=[("Arquivo JSON","*.json")],initialfile="hunter_system_save.json")
        if not path:return
        try:
            with open(path,"w",encoding="utf-8") as f:json.dump(self.data,f,ensure_ascii=False,indent=2)
            messagebox.showinfo("Exportado",f"Save JSON salvo em:\n{path}")
        except Exception as exc:messagebox.showerror("Erro ao exportar",str(exc))

    def reset_active_profile(self):
        """Reset only the active slot; always make a whole-save safety copy first."""
        p = self.profile
        title = p.get("settings", {}).get("title", self.active_key)
        confirm = messagebox.askyesno(
            "Apagar progresso deste slot?",
            f"Isso vai reiniciar somente o slot atual:\n\n{title}\n\n"
            "O personagem, XP, ouro, itens, capítulos concluídos, revisões, anotações e personalizações deste slot serão apagados.\n"
            "Os outros dois slots não serão alterados. Um backup de segurança será criado automaticamente.\n\nDeseja continuar?",
            icon="warning")
        if not confirm:
            return
        try:
            backup = self._write_safety_backup(f"antes_reiniciar_{self.active_key}")
            self.data["profiles"][self.active_key] = default_profile(self.active_key)
            self.save()
            self.current_question = None
            self.current_answered = False
            self.page = "Santuário"
            self.render()
            self.status_var.set(f"Slot reiniciado. Backup de segurança em {backup}")
            messagebox.showinfo("Slot reiniciado", f"A jornada foi reiniciada. Os demais slots continuam intactos.\n\nBackup automático:\n{backup}")
        except Exception as exc:
            messagebox.showerror("Erro ao reiniciar slot", f"O progresso não foi reiniciado com segurança.\n\n{exc}")

    def _upgrade_imported_profile(self, key, candidate, seed):
        """Merge a profile from a backup with this version's schema without trusting missing fields."""
        if not isinstance(candidate, dict):
            raise ValueError(f"O slot '{key}' não contém um perfil válido.")
        normalized = dict(seed)
        schema = safe_int(candidate.get("campaign_schema", 0))
        if schema < 3:
            old_done = set(candidate.get("completed_missions", []))
            old_bosses = set(candidate.get("bosses_defeated", []))
            for field in ("level", "xp", "gold", "attributes", "attribute_points", "inventory", "equipped", "potions", "last_study_date", "streak", "history", "event_claims", "notes", "custom_quiz_text", "settings", "lesson_notes", "quiz_stats", "story_seen", "story_chapters_seen", "boss_exam_results"):
                if field in candidate:
                    normalized[field] = candidate[field]
            valid_ids = {m["id"] for m in seed["mission_data"]}
            valid_boss_ids = {b["id"] for b in seed["boss_data"]}
            normalized["completed_missions"] = [mid for mid in old_done if mid in valid_ids]
            normalized["bosses_defeated"] = [bid for bid in old_bosses if bid in valid_boss_ids]
            normalized["review_queue"] = [r for r in candidate.get("review_queue", []) if isinstance(r, dict) and r.get("lesson_id") in valid_ids]
            normalized["mission_data"] = seed["mission_data"]
            normalized["boss_data"] = seed["boss_data"]
        else:
            normalized.update(candidate)
        for field, default_value in seed.items():
            normalized.setdefault(field, default_value)
        if not isinstance(normalized.get("mission_data"), list) or not normalized["mission_data"]:
            normalized["mission_data"] = seed["mission_data"]
        known_ids = {m.get("id") for m in normalized["mission_data"]}
        normalized["completed_missions"] = [mid for mid in normalized.get("completed_missions", []) if mid in known_ids]
        normalized["review_queue"] = [r for r in normalized.get("review_queue", []) if isinstance(r, dict) and r.get("lesson_id") in known_ids]
        normalized["campaign_schema"] = 3
        return normalized

    def import_save(self):
        path=filedialog.askopenfilename(title="Importar backup completo ou save",filetypes=[("Backup completo ZIP", "*.zip"), ("Save JSON", "*.json"), ("Todos os arquivos", "*.*")])
        if not path:return
        if not messagebox.askyesno("Substituir progresso?","O arquivo substituirá os três slots do aplicativo. Antes da importação, será criado um backup local de segurança. Continuar?", icon="warning"):return
        try:
            if str(path).lower().endswith(".zip"):
                with zipfile.ZipFile(path, "r") as archive:
                    if "save.json" not in archive.namelist():
                        raise ValueError("Este ZIP não contém save.json e não parece ser um backup Hunter System válido.")
                    incoming = json.loads(archive.read("save.json").decode("utf-8"))
            else:
                with open(path,"r",encoding="utf-8") as f:incoming=json.load(f)
            if not isinstance(incoming,dict) or not isinstance(incoming.get("profiles"),dict):
                raise ValueError("Formato de save inválido: a seção profiles não foi encontrada.")
            safety = self._write_safety_backup("antes_importar")
            fresh=create_save()
            for key in ("python","caixa","custom"):
                if key in incoming["profiles"]:
                    fresh["profiles"][key] = self._upgrade_imported_profile(key, incoming["profiles"][key], fresh["profiles"][key])
            active = incoming.get("active_profile", "python")
            fresh["active_profile"] = active if active in fresh["profiles"] else "python"
            self.data=fresh
            self.active_key=fresh["active_profile"]
            self.current_question = None
            self.current_answered = False
            self.save();self.render()
            messagebox.showinfo("Backup importado",f"Progresso restaurado com sucesso.\n\nBackup de segurança do save anterior:\n{safety}")
        except Exception as exc:messagebox.showerror("Erro ao importar",f"Arquivo inválido ou incompatível. O aplicativo manteve o save atual se a validação falhou.\n\n{exc}")

    # ------------------------------- STORY ---------------------------------
    def show_story(self, scene, replay=False):
        p=self.profile
        lines=STORY.get(scene)
        if scene == "intro" and self.active_key == "caixa":
            lines = [("ÍRIA, arquivista", "O Arquivo dos Ecos guarda leis, números, escolhas e promessas feitas a pessoas que precisam de respostas claras. A névoa não apaga as páginas: ela mistura conceitos até parecerem iguais."), ("ÍRIA, arquivista", "Você seguirá uma rota de leitura, cálculo, ética, sistema financeiro e atendimento. O mapa segue o edital de 2024 que você forneceu; confirme sempre o conteúdo de uma seleção futura em fontes oficiais."), ("VOCÊ", "Não quero só reconhecer as palavras. Quero justificar as respostas."), ("ÍRIA, arquivista", "Então cada página terminará com uma prova. Amanhã, a memória será chamada novamente. E, ao fim de cada região, um guardião reunirá os assuntos que você já atravessou.")]
        elif scene == "intro" and self.active_key == "custom":
            lines = [("ÍRIA", "Este mapa ainda não tem nome nem destino. É você quem escolhe o que merece ser aprendido."), ("VOCÊ", "E se a rota mudar?"), ("ÍRIA", "Então reescrevemos a próxima página. Mas seguimos em ordem: entender, praticar, demonstrar e revisitar. A campanha pertence a você, não o contrário.")]
        if scene.startswith("boss_"):
            idx = safe_int(scene.split("_")[-1], 1)
            if self.active_key == "python":
                boss_lines = {
                    1: [("ÍRIA", "A primeira barreira caiu. O guardião tentou confundir sintaxe com compreensão, mas você demonstrou que consegue ler o código e explicar por que ele funciona."), ("ECO", "A próxima porta exigirá que funções e objetos cooperem. Uma solução isolada não basta."), ("VOCÊ", "Então vou construir ferramentas, não apenas decorar comandos.")],
                    2: [("ÍRIA", "A Arquiteta dos Módulos recuou. Você aprendeu a dar responsabilidade a cada parte do sistema."), ("ECO", "Os dados ainda podem se perder. Erros escondidos também podem passar despercebidos."), ("VOCÊ", "Vou proteger os registros e provar meu código com testes.")],
                    3: [("ÍRIA", "O Devorador de Dados perdeu o controle. Persistência e testes transformam uma demonstração frágil em algo verificável."), ("ECO", "Uma aplicação não vive só no laboratório."), ("VOCÊ", "Ainda preciso aprender a entregar, integrar e manter o que construí.")],
                    4: [("ÍRIA", "A Sombra de Produção foi vencida. Você já não encara uma aplicação como um arquivo solto, mas como um sistema que precisa ser explicado e mantido."), ("ECO", "O último guardião não aceitará um amontoado de aulas assistidas."), ("VOCÊ", "Vou reunir tudo em um projeto que funcione.")],
                }
                lines = boss_lines.get(idx, lines)
            elif self.active_key == "caixa":
                boss_lines = {
                    1: [("ÍRIA", "Você atravessou a primeira prova: leu enunciados com cuidado e evitou alternativas que apenas pareciam corretas."), ("ECO", "Os números não aceitarão aproximações feitas sem identificar taxa, prazo e regime."), ("VOCÊ", "Vou explicitar as premissas antes de calcular.")],
                    2: [("ÍRIA", "A Balança do Capital se equilibrou porque você separou conceitos, fórmulas e hipóteses."), ("ECO", "A próxima passagem não se resolve com cálculo; ela exige responsabilidade."), ("VOCÊ", "Conhecimento sem ética não abre o cofre.")],
                    3: [("ÍRIA", "O Guardião do Sigilo recuou. Você entendeu que privacidade, integridade e controle fazem parte do trabalho bancário."), ("ECO", "Agora o sistema inteiro será posto à prova: instituições, produtos, canais e atendimento."), ("VOCÊ", "Vou ligar cada conceito à situação em que ele se aplica.")],
                    4: [("ÍRIA", "A Serpente dos Mercados perdeu a última escama. Os conceitos agora formam uma rota, não uma lista solta."), ("ECO", "A prova final reúne memória, análise, atendimento e escrita."), ("VOCÊ", "Vou recuperar o que sei, identificar o que falta e enfrentar a última página.")],
                }
                lines = boss_lines.get(idx, lines)
        elif scene == "ending" and self.active_key == "python":
            lines = [("REI DO CÓDIGO INACABADO", "Você voltou a cada etapa, testou suas hipóteses e transformou pequenas práticas num projeto demonstrável."), ("ÍRIA", "O curso não termina quando o último vídeo acaba. Termina esta campanha quando você consegue usar o que aprendeu sem depender da demonstração."), ("NARRADOR", "A Forja se apaga porque a chama agora pertence a você. A próxima missão será escolhida por quem aprendeu a construir.")]
        elif scene == "ending" and self.active_key == "caixa":
            lines = [("EXAMINADOR DA ÚLTIMA PROVA", "Você não venceu por reconhecer palavras. Venceu ao recuperar conceitos, justificar respostas e organizar argumentos."), ("ÍRIA", "O edital anexado foi o mapa desta campanha, não uma promessa sobre concursos futuros. Continue acompanhando regras e conteúdos oficiais quando uma nova seleção for publicada."), ("NARRADOR", "O cofre abre. A jornada de estudo continua, mas agora você sabe medir o próprio avanço.")]
        if not lines:
            lines=[("ÍRIA","A próxima página ainda não foi escrita. Continue sua jornada e volte depois.")]
        w=tk.Toplevel(self);w.title("Crônicas da Cidade Sem Aurora")
        w.geometry("850x515");w.minsize(760,470);w.configure(bg="#100e18");w.transient(self);w.grab_set()
        canvas=tk.Canvas(w,height=5,bg=PURPLE,highlightthickness=0);canvas.pack(fill="x")
        story_banner = {"python":"CRÔNICAS  /  CIDADE SEM AURORA", "caixa":"ARQUIVO DOS ECOS  /  ROTA BANCÁRIA", "custom":"JORNADA LIVRE  /  MAPA EM BRANCO"}.get(self.active_key, "CRÔNICAS DA FORJA")
        story_title = {"intro":"A CHAMA QUE RESTOU" if self.active_key == "python" else ("O ARQUIVO DOS ECOS" if self.active_key == "caixa" else "O MAPA EM BRANCO"),"boss_1":"A PRIMEIRA PORTA","boss_2":"A MEMÓRIA DA NÉVOA","boss_3":"O MAPA INVISÍVEL","boss_4":"A ÚLTIMA PONTE","ending":"O FIM DA ÚLTIMA PÁGINA"}.get(scene,"UM FRAGMENTO DA CRÔNICA")
        tk.Label(w,text=story_banner,bg="#100e18",fg=GOLD,font=(FONT,8,"bold")).pack(anchor="w",padx=24,pady=(17,5))
        tk.Label(w,text=story_title,bg="#100e18",fg=TEXT,font=(FONT,18,"bold")).pack(anchor="w",padx=24,pady=(0,10))
        middle=tk.Frame(w,bg="#100e18");middle.pack(fill="both",expand=True,padx=24,pady=(0,12))
        portrait_panel=tk.Frame(middle,bg="#1b1528",highlightbackground="#624289",highlightthickness=1,width=205)
        portrait_panel.pack(side="left",fill="y",padx=(0,15));portrait_panel.pack_propagate(False)
        try:
            self.story_iria_image=tk.PhotoImage(file=str(self._asset_path("iria_portrait.png"))).subsample(2,2)
            self.story_hunter_image=tk.PhotoImage(file=str(self._asset_path("hunter_portrait.png"))).subsample(2,2)
            portrait=tk.Label(portrait_panel,image=self.story_iria_image,bg="#1b1528",bd=0)
            portrait.pack(padx=5,pady=(8,4))
        except Exception:
            portrait=tk.Label(portrait_panel,text="ÍRIA",bg="#1b1528",fg=PURPLE,font=(FONT,18,"bold"),width=14,height=8)
            portrait.pack(padx=5,pady=8)
        tk.Label(portrait_panel,text="CRÔNICAS DA FORJA",bg="#1b1528",fg=GOLD,font=(FONT,8,"bold")).pack(pady=(0,7))
        dialogue_panel=tk.Frame(middle,bg="#171421",highlightbackground="#393048",highlightthickness=1)
        dialogue_panel.pack(side="left",fill="both",expand=True)
        speaker=tk.Label(dialogue_panel,text="",bg="#171421",fg=PURPLE,font=(FONT,9,"bold"));speaker.pack(anchor="w",padx=18,pady=(19,7))
        body=tk.Label(dialogue_panel,text="",bg="#171421",fg="#e3dced",font=(FONT,11),wraplength=525,justify="left",anchor="nw")
        body.pack(fill="both",expand=True,padx=18,pady=(0,16))
        footer=tk.Frame(dialogue_panel,bg="#171421");footer.pack(fill="x",padx=18,pady=(0,17))
        counter=tk.Label(footer,text="",bg="#171421",fg=MUTED,font=(FONT,8));counter.pack(side="left")
        btn=self._button(footer,"CONTINUAR  →",lambda:None,"primary");btn.pack(side="right")
        i={"n":0}
        def next_line():
            if i["n"]>=len(lines):
                if scene not in p.get("story_seen",[]):p.setdefault("story_seen",[]).append(scene)
                self.save();w.destroy();self.render();return
            who,dialogue=lines[i["n"]]
            speaker.configure(text=who.upper())
            body.configure(text=dialogue)
            # Portrait changes with the speaker so dialogue feels like a scene, not a bare popup.
            if "VOCÊ" in who.upper() or "ECO" in who.upper() or "REI" in who.upper() or "EXAMINADOR" in who.upper():
                try: portrait.configure(image=self.story_hunter_image)
                except Exception: pass
            else:
                try: portrait.configure(image=self.story_iria_image)
                except Exception: pass
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
