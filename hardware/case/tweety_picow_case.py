#!/usr/bin/env python3
# Tweety — Raspberry Pi Pico W two-shell case (P01yg107 Labs house style)
# PETG-CF body + flush two-colour Hyper-PLA canary emblem on the lid.
# Adapted from the Kraken/Pico case: Pico W shares the Pico footprint, so the
# shell carries over; the squid emblem is replaced by the Tweety canary and an
# LED light-window is added so the heartbeat/trip blink shows through the lid.
#
# Outputs (next to this script):
#   tweety_base.stl, tweety_lid.stl, tweety_emblem.stl   (individual parts)
#   tweety-case.3mf                                        (assembled, 3 objects)
#   tweety-case-topview.png                                (sanity render)
#
# 2-colour print: in the slicer, select the EMBLEM object and assign it
# filament 2 (Hyper-PLA red #D7191F). Body = filament 1 (PETG-CF #0C0C0D).
# The canary's eye is a knockout, so the black case shows through it.

import json, os
import numpy as np
import manifold3d as m
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
EMBLEM_JSON = os.path.join(HERE, "emblem", "canary_contours.json")

# ---------------- parameters (mm) -------------------------------------------
BW, BL, PCB = 21.0, 51.0, 1.0     # Pico W board: width, length, PCB thickness
CL          = 0.4                 # clearance around board
WALL        = 2.0                 # side wall thickness
FLOOR_T     = 1.2                 # floor under board
TOPCLR      = 3.6                 # headroom above PCB for components (USB, can)
FIT         = 0.35                # lid-lip clearance into cavity
LID_T       = 1.6                 # lid top-plate thickness
LIP_H       = 3.0                 # lid lip depth (inserts into base)
CORNER      = 2.5                 # outer corner radius
USB_W, USB_H = 9.0, 4.0          # micro-USB cutout (short +Y end)
EMB_W       = 17.0               # canary emblem width on the lid
EMB_DEPTH   = 0.8                # emblem height / pocket depth (flush inlay)
LED_D       = 2.2                # LED light-window diameter
LED_XY      = (0.0, 21.5)        # LED window centre on lid (verify vs board)
SEG         = 48

# derived
IN_W  = BW + 2*CL
IN_L  = BL + 2*CL
OUT_W = IN_W + 2*WALL
OUT_L = IN_L + 2*WALL
CAV_H = PCB + TOPCLR
BASE_H = FLOOR_T + CAV_H
TOP_Z  = LIP_H + LID_T            # lid total height (lip + plate)

# ---------------- helpers ---------------------------------------------------
def rbox(w, l, h, r):
    """Rounded rectangular prism, centred in XY, sitting on z=0."""
    r = max(0.01, min(r, w/2 - 0.01, l/2 - 0.01))
    try:
        cs = m.CrossSection.square([w - 2*r, l - 2*r], center=True)
        cs = cs.offset(r, m.JoinType.Round, 2.0, 0.05)
    except Exception:
        cs = m.CrossSection.square([w, l], center=True)
    return cs.extrude(h)

def cube_c(x, y, z):
    return m.Manifold.cube([x, y, z], center=True)

def canary_cs(width):
    d = json.load(open(EMBLEM_JSON))
    asp = d["aspect"]
    h = width / asp
    def rescale(loop):
        return [[x*width - width/2.0, y*h - h/2.0] for x, y in loop]
    outer = rescale(d["outer"])
    holes = [rescale(lp) for lp in d["holes"]]
    return m.CrossSection([outer] + holes, m.FillRule.EvenOdd)

def to_tri(man, name):
    mesh = man.to_mesh()
    v = np.asarray(mesh.vert_properties)[:, :3].copy()
    f = np.asarray(mesh.tri_verts).copy()
    t = trimesh.Trimesh(vertices=v, faces=f, process=False)
    t.metadata["name"] = name
    return t

# ---------------- base ------------------------------------------------------
outer  = rbox(OUT_W, OUT_L, BASE_H, CORNER)
cavity = rbox(IN_W, IN_L, CAV_H + 0.2, CORNER - WALL).translate([0, 0, FLOOR_T])
base   = outer - cavity
# micro-USB cutout on +Y short end, at board-edge height
usb = cube_c(USB_W, WALL + 3, USB_H).translate([0, OUT_L/2 - WALL/2, FLOOR_T + PCB/2])
base = base - usb

# ---------------- lid -------------------------------------------------------
plate = rbox(OUT_W, OUT_L, LID_T, CORNER).translate([0, 0, LIP_H])
lip   = rbox(IN_W - 2*FIT, IN_L - 2*FIT, LIP_H + 0.01, CORNER - WALL)
lid   = plate + lip

emb_cs = canary_cs(EMB_W)
# pocket cut into the lid top (slightly deeper so emblem seats flush)
pocket = emb_cs.extrude(EMB_DEPTH + 0.25).translate([0, 0, TOP_Z - EMB_DEPTH])
lid = lid - pocket
# LED light-window (through the lid)
led = m.Manifold.cylinder(TOP_Z + 1.0, LED_D/2, LED_D/2, SEG).translate([LED_XY[0], LED_XY[1], -0.5])
lid = lid - led

# ---------------- emblem (separate colour part) -----------------------------
emblem = emb_cs.extrude(EMB_DEPTH).translate([0, 0, TOP_Z - EMB_DEPTH])

# ---------------- export ----------------------------------------------------
tb, tl, te = to_tri(base, "tweety_base"), to_tri(lid, "tweety_lid"), to_tri(emblem, "tweety_emblem")
tb.export(os.path.join(HERE, "tweety_base.stl"))
tl.export(os.path.join(HERE, "tweety_lid.stl"))
te.export(os.path.join(HERE, "tweety_emblem.stl"))

scene = trimesh.Scene()
# base off to the side so the plate view is clean; lid+emblem stay registered
scene.add_geometry(tb, node_name="tweety_base", geom_name="tweety_base",
                   transform=trimesh.transformations.translation_matrix([OUT_W + 6, 0, 0]))
scene.add_geometry(tl, node_name="tweety_lid", geom_name="tweety_lid")
scene.add_geometry(te, node_name="tweety_emblem", geom_name="tweety_emblem")
scene.export(os.path.join(HERE, "tweety-case.3mf"))

print("parts:")
for t in (tb, tl, te):
    bb = t.bounds
    print(f"  {t.metadata['name']:14s} size {np.round(bb[1]-bb[0],2)}  watertight={t.is_watertight}")

# ---------------- top-view sanity render ------------------------------------
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPoly
fig, ax = plt.subplots(figsize=(4, 7))
ax.add_patch(plt.Rectangle((-OUT_W/2, -OUT_L/2), OUT_W, OUT_L, fill=False, ec="#0C0C0D", lw=2))
for poly in emb_cs.to_polygons():
    ax.add_patch(MplPoly(poly, closed=True, fc="#D7191F", ec="none"))
ax.add_patch(plt.Circle(LED_XY, LED_D/2, fc="#2f7d3e", ec="none"))
ax.set_xlim(-OUT_W/2 - 3, OUT_W/2 + 3); ax.set_ylim(-OUT_L/2 - 3, OUT_L/2 + 3)
ax.set_aspect("equal"); ax.axis("off")
ax.set_title("Tweety lid — top view", fontsize=10)
plt.savefig(os.path.join(HERE, "tweety-case-topview.png"), dpi=120, bbox_inches="tight")
print("wrote tweety-case.3mf + STLs + topview png")
