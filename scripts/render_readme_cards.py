#!/usr/bin/env python3
"""Render animated SVG cards for the profile README from data/contributions.json.
STATIC=1 -> no animation (final frame), for screenshots."""
import json, os, datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "cards"; OUT.mkdir(exist_ok=True)
STATIC = os.environ.get("STATIC") == "1"

# ---- edit these ----
NAME = "Efe Gürkan"
TAGLINE = "Building apps and sites."
INK, PAPER, BLUE, MUTED = "#14120f", "#f6f1e7", "#2f5bff", "#8a8578"
SERIF = "Georgia, 'Times New Roman', serif"
SANS = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
# --------------------

cal = json.loads((ROOT / "data/contributions.json").read_text())["data"]["viewer"]["contributionsCollection"]["contributionCalendar"]
days = [d for w in cal["weeks"] for d in w["contributionDays"]]
total = cal["totalContributions"]
active = sum(1 for d in days if d["contributionCount"] > 0)
busiest = max(days, key=lambda d: d["contributionCount"])
streak = cur = 0
for d in days:
    cur = cur + 1 if d["contributionCount"] else 0
    streak = max(streak, cur)
months = {}
for d in days:
    k = d["date"][:7]; months[k] = months.get(k, 0) + d["contributionCount"]
mkeys = sorted(months)[-12:]

def css(extra=""):
    if STATIC: return "<style>" + extra + "</style>"
    return ("<style>@keyframes rise{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}"
            "@keyframes grow{from{transform:scaleY(0)}to{transform:scaleY(1)}}"
            "@keyframes pop{from{opacity:0;transform:scale(.3)}to{opacity:1;transform:scale(1)}}"
            "@media (prefers-reduced-motion:reduce){*{animation:none!important}}" + extra + "</style>")

def svg(w, h, body, name):
    s = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{css()}<rect width="{w}" height="{h}" rx="14" fill="{PAPER}"/>{body}</svg>'
    (OUT / name).write_text(s)

def anim(delay, kind="rise", dur=.7):
    return "" if STATIC else f'style="animation:{kind} {dur}s cubic-bezier(.2,.8,.2,1) {delay}s both;transform-box:fill-box"'

# hero
svg(900, 220, f'''
<text x="40" y="100" font-family="{SERIF}" font-size="64" fill="{INK}" {anim(.1)}>{NAME}</text>
<text x="40" y="148" font-family="{SANS}" font-size="20" fill="{MUTED}" {anim(.4)}>{TAGLINE}</text>
<rect x="40" y="172" width="90" height="4" fill="{BLUE}" {anim(.7)}/>''', "hero.svg")

# contribution graph (blue)
cell, gap = 11, 3
weeks = cal["weeks"]; mx = max(d["contributionCount"] for d in days) or 1
rects = []
for wi, w in enumerate(weeks):
    for di, d in enumerate(w["contributionDays"]):
        c = d["contributionCount"]
        op = 0.08 if c == 0 else 0.25 + 0.75 * c / mx
        fill = INK if c == 0 else BLUE
        delay = 1.0 + wi * 0.02
        rects.append(f'<rect x="{40+wi*(cell+gap)}" y="{50+di*(cell+gap)}" width="{cell}" height="{cell}" rx="2" fill="{fill}" opacity="{op:.2f}" {anim(delay,"pop",.4)}/>')
gw = 80 + len(weeks) * (cell + gap)
svg(max(gw, 900), 50 + 7 * (cell + gap) + 30, f'<text x="40" y="32" font-family="{SANS}" font-size="14" fill="{MUTED}">{total} contributions in the last year</text>' + "".join(rects), "graph.svg")

# monthly bars
bh = 120; bmax = max(months[k] for k in mkeys) or 1; best = max(mkeys, key=lambda k: months[k])
bars = []
for i, k in enumerate(mkeys):
    v = months[k]; h = max(3, int(bh * v / bmax)); x = 40 + i * 70
    col = BLUE if k == best else INK
    op = 1 if k == best else .75
    lab = dt.date.fromisoformat(k + "-01").strftime("%b")
    bars.append(f'<rect x="{x}" y="{40+bh-h}" width="46" height="{h}" rx="4" fill="{col}" opacity="{op}" style="transform-origin:bottom;{"" if STATIC else f"animation:grow .8s ease {1.6+i*.06}s both;"}transform-box:fill-box"/>'
                f'<text x="{x+23}" y="{40+bh+20}" text-anchor="middle" font-family="{SANS}" font-size="12" fill="{MUTED}">{lab}</text>'
                f'<text x="{x+23}" y="{34+bh-h}" text-anchor="middle" font-family="{SANS}" font-size="12" fill="{col}">{v}</text>')
svg(900, 210, "".join(bars), "months.svg")

# tiles
def tile(name, color, big, small, d):
    svg(290, 150, f'<rect x="0" y="0" width="290" height="8" fill="{color}"/>'
        f'<text x="24" y="50" font-family="{SANS}" font-size="12" letter-spacing="2" fill="{MUTED}">{small.upper()}</text>'
        f'<text x="24" y="108" font-family="{SERIF}" font-size="56" fill="{INK}" {anim(d)}>{big}</text>', name)
tile("total.svg", BLUE, total, "contributions", 2.2)
tile("streak.svg", "#e5484d", f"{streak}d", "longest streak", 2.4)
tile("active.svg", "#f5b800", active, "active days", 2.6)
print("ok", total, active, streak, busiest["date"])
