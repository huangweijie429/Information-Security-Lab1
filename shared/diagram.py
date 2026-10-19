"""Tiny box-and-arrow diagram renderer (Pillow) used by Work 2 and Work 3.

Keeps figures deterministic and reviewable in code instead of hand-drawn images.
"""
from __future__ import annotations

import textwrap
from dataclasses import dataclass, field

from PIL import Image, ImageDraw, ImageFont

PALETTE = {
    "bg": "#ffffff",
    "text": "#1b1b1b",
    "muted": "#5a5a5a",
    "entity": ("#e8f0fe", "#4a6fb5"),
    "process": ("#e6f4ea", "#3c7a4a"),
    "store": ("#fff4e5", "#b5761f"),
    "state": ("#eef1f5", "#4b5563"),
    "loss": ("#fdecea", "#b3261e"),
    "attacker": ("#f3e8fd", "#6b3fa0"),
    "edge": "#3d4450",
}


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    # CJK-capable fonts first, Latin fallbacks after them
    names = (["msyhbd.ttc", "msyh.ttc", "simhei.ttf"] if bold else ["msyh.ttc", "msyh.ttf"])
    names += ["arialbd.ttf", "arial.ttf"] if bold else ["arial.ttf"]
    for name in names:
        for base in ("C:/Windows/Fonts/", ""):
            try:
                return ImageFont.truetype(base + name, size)
            except OSError:
                continue
    return ImageFont.load_default()


@dataclass
class Node:
    key: str
    x: int
    y: int
    w: int
    h: int
    text: str
    kind: str = "process"


@dataclass
class Edge:
    src: str
    dst: str
    label: str = ""
    offset: int = 0
    dashed: bool = False


@dataclass
class Diagram:
    width: int = 1600
    height: int = 1000
    title: str = ""
    nodes: dict[str, Node] = field(default_factory=dict)
    edges: list[Edge] = field(default_factory=list)

    def box(self, key, x, y, w, h, text, kind="process"):
        self.nodes[key] = Node(key, x, y, w, h, text, kind)
        return self

    def arrow(self, src, dst, label="", offset=0, dashed=False):
        self.edges.append(Edge(src, dst, label, offset, dashed))
        return self

    # -- geometry ---------------------------------------------------------
    def _center(self, key: str) -> tuple[int, int]:
        n = self.nodes[key]
        return n.x + n.w // 2, n.y + n.h // 2

    def _border_point(self, key: str, tx: int, ty: int) -> tuple[int, int]:
        """Point on the node border along the line from centre towards (tx, ty)."""
        n = self.nodes[key]
        cx, cy = n.x + n.w / 2, n.y + n.h / 2
        dx, dy = tx - cx, ty - cy
        if dx == 0 and dy == 0:
            return int(cx), int(cy)
        scale = min(
            (n.w / 2) / abs(dx) if dx else float("inf"),
            (n.h / 2) / abs(dy) if dy else float("inf"),
        )
        return int(cx + dx * scale), int(cy + dy * scale)

    # -- render -----------------------------------------------------------
    def save(self, path: str, scale: int = 2) -> str:
        img = Image.new("RGB", (self.width, self.height), PALETTE["bg"])
        d = ImageDraw.Draw(img)
        f_title = _font(30, bold=True)
        f_node = _font(18)
        f_small = _font(15)

        if self.title:
            d.text((self.width // 2, 26), self.title, font=f_title, fill=PALETTE["text"], anchor="ma")

        for e in self.edges:
            (sx, sy), (dx_, dy_) = self._center(e.src), self._center(e.dst)
            p1 = self._border_point(e.src, dx_, dy_)
            p2 = self._border_point(e.dst, sx, sy)
            colour = PALETTE["edge"]
            w = 2
            if e.dashed:
                self._dashed_line(d, p1, p2, colour, w)
            else:
                d.line([p1, p2], fill=colour, width=w)
            self._arrow_head(d, p1, p2, colour)
            if e.label:
                mx, my = (p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2 + e.offset
                tw = d.textlength(e.label, font=f_small)
                d.rectangle([mx - tw / 2 - 4, my - 10, mx + tw / 2 + 4, my + 10], fill="#ffffff")
                d.text((mx, my), e.label, font=f_small, fill=PALETTE["muted"], anchor="mm")

        for n in self.nodes.values():
            fill, outline = PALETTE[n.kind]
            radius = 28 if n.kind == "entity" else 10
            d.rounded_rectangle([n.x, n.y, n.x + n.w, n.y + n.h], radius=radius,
                                fill=fill, outline=outline, width=3)
            lines = []
            for part in n.text.split("\n"):
                lines += textwrap.wrap(part, width=max(12, int(n.w / 10))) or [""]
            total = len(lines) * 22
            ty = n.y + n.h / 2 - total / 2 + 11
            for line in lines:
                d.text((n.x + n.w / 2, ty), line, font=f_node, fill=PALETTE["text"], anchor="mm")
                ty += 22

        if scale != 1:
            img = img.resize((self.width * scale, self.height * scale), Image.LANCZOS)
        img.save(path, dpi=(220, 220))
        return path

    @staticmethod
    def _dashed_line(d, p1, p2, colour, width, dash=12, gap=8):
        import math

        dist = math.dist(p1, p2)
        if dist == 0:
            return
        ux, uy = (p2[0] - p1[0]) / dist, (p2[1] - p1[1]) / dist
        pos = 0.0
        while pos < dist:
            end = min(pos + dash, dist)
            d.line([(p1[0] + ux * pos, p1[1] + uy * pos), (p1[0] + ux * end, p1[1] + uy * end)],
                   fill=colour, width=width)
            pos = end + gap

    @staticmethod
    def _arrow_head(d, p1, p2, colour, size=14):
        import math

        angle = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
        left = (p2[0] - size * math.cos(angle - 0.4), p2[1] - size * math.sin(angle - 0.4))
        right = (p2[0] - size * math.cos(angle + 0.4), p2[1] - size * math.sin(angle + 0.4))
        d.polygon([p2, left, right], fill=colour)
