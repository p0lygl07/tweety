#!/usr/bin/env python3
"""
Take the proven Kraken case 3MF and swap ONLY the emblem: kraken -> Tweety canary.

Everything else is left exactly as-is: lid shell, base, wall/USB geometry, plate layout,
object/part ids, per-part extruder assignment, filament config, print profile.

What it does:
  1. Reads lid (object id=3) and kraken (object id=4) out of 3D/Objects/object_2.model
  2. Fills the old kraken-shaped pocket in the lid:   lid  U  kraken
  3. Cuts a new canary-shaped pocket, same depth:     ( ... )  -  canary
  4. Replaces the kraken part mesh with the canary solid
  5. Rewrites object_2.model + renames the parts in model_settings.config
  6. Re-zips every other file byte-for-byte
"""
import re, os, json, shutil, zipfile
import numpy as np
import trimesh
import manifold3d as m

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_3MF = os.path.join(HERE, "k.3mf")
EX = os.path.join(HERE, "ex")
CONTOURS = "/tmp/claude-0/-home-claude/e6f233c3-7467-5a24-a46e-9863cc6136b5/scratchpad/emblem/canary_contours.json"
OUT_3MF = os.path.join(HERE, "tweety-case.3mf")

# The emblem face is the BOTTOM of the lid (z=-3.9 local) — it prints face-down on the
# plate. You therefore view the finished emblem from -Z, which mirrors X. Mirror the art
# so the printed bird reads the same way round as the source insignia.
MIRROR_X = True

OBJ2 = os.path.join(EX, "3D", "Objects", "object_2.model")

# ---------------------------------------------------------------- parse
src = open(OBJ2).read()

def parse_obj(xml, oid):
    mm = re.search(r'<object id="%s"[^>]*>(.*?)</object>' % oid, xml, re.S)
    body = mm.group(1)
    v = np.array([[float(a), float(b), float(c)] for a, b, c in
                  re.findall(r'<vertex x="([-0-9.eE]+)" y="([-0-9.eE]+)" z="([-0-9.eE]+)"', body)])
    f = np.array([[int(a), int(b), int(c)] for a, b, c in
                  re.findall(r'<triangle v1="(\d+)" v2="(\d+)" v3="(\d+)"', body)])
    return trimesh.Trimesh(vertices=v, faces=f, process=False)

lid = parse_obj(src, 3)
kraken = parse_obj(src, 4)
print("lid    :", np.round(lid.extents, 3), "watertight", lid.is_watertight)
print("kraken :", np.round(kraken.extents, 3), "watertight", kraken.is_watertight)

# part-frame -> lid-frame offset, taken from the component transforms in 3dmodel.model
#   lid    component translate = (196,        175,        3.9)
#   kraken component translate = (196.005173, 175.500458, 0.3)
DELTA = np.array([196.005173 - 196.0, 175.500458 - 175.0, 0.3 - 3.9])
print("part->lid delta:", DELTA)

kb = kraken.bounds
KW, KH, KT = (kb[1] - kb[0])
print(f"kraken bbox  W={KW:.3f} H={KH:.3f} T={KT:.3f}")

# ---------------------------------------------------------------- canary solid
d = json.load(open(CONTOURS))
asp = d["aspect"]                       # width / height of the canary art
area = KW * KH                          # match the kraken's visual mass
H = (area / asp) ** 0.5
W = asp * H
print(f"canary bbox  W={W:.3f} H={H:.3f} T={KT:.3f}   (equal bbox area to the kraken)")

def loop(pts):
    out = []
    for x, y in pts:
        X = x * W - W / 2.0
        if MIRROR_X:
            X = -X
        out.append([X, y * H - H / 2.0])
    return out

cs = m.CrossSection([loop(d["outer"])] + [loop(h) for h in d["holes"]], m.FillRule.EvenOdd)
can_man = cs.extrude(KT).translate([0.0, 0.0, -KT / 2.0])   # centred on z, like the kraken
cm = can_man.to_mesh()
canary = trimesh.Trimesh(vertices=np.asarray(cm.vert_properties)[:, :3].copy(),
                         faces=np.asarray(cm.tri_verts).copy(), process=False)
print("canary :", np.round(canary.extents, 3), "watertight", canary.is_watertight,
      "| holes(eye):", len(d["holes"]))

# ---------------------------------------------------------------- lid surgery
kraken_in_lid = kraken.copy(); kraken_in_lid.apply_translation(DELTA)
canary_in_lid = canary.copy(); canary_in_lid.apply_translation(DELTA)

lid_filled = trimesh.boolean.union([lid, kraken_in_lid], engine="manifold")
print("lid filled :", np.round(lid_filled.extents, 3),
      f"vol {lid_filled.volume:.2f} (was {lid.volume:.2f}, +{lid_filled.volume-lid.volume:.2f})")

lid_new = trimesh.boolean.difference([lid_filled, canary_in_lid], engine="manifold")
print("lid new    :", np.round(lid_new.extents, 3),
      f"vol {lid_new.volume:.2f} watertight={lid_new.is_watertight}")

assert lid_new.is_watertight, "new lid is not watertight"
assert canary.is_watertight, "canary is not watertight"
assert np.allclose(lid_new.extents, lid.extents, atol=1e-3), "lid outer size changed!"

# ---------------------------------------------------------------- rewrite object_2.model
def mesh_xml(mesh):
    vs = "\n".join('     <vertex x="%.8g" y="%.8g" z="%.8g"/>' % tuple(p) for p in mesh.vertices)
    ts = "\n".join('     <triangle v1="%d" v2="%d" v3="%d"/>' % tuple(t) for t in mesh.faces)
    return "   <mesh>\n    <vertices>\n%s\n    </vertices>\n    <triangles>\n%s\n    </triangles>\n   </mesh>\n" % (vs, ts)

def replace_obj(xml, oid, mesh):
    pat = re.compile(r'(<object id="%s"[^>]*>)(.*?)(</object>)' % oid, re.S)
    return pat.sub(lambda mo: mo.group(1) + "\n" + mesh_xml(mesh) + "  " + mo.group(3), xml, count=1)

out = replace_obj(src, 3, lid_new)
out = replace_obj(out, 4, canary)
open(OBJ2, "w").write(out)
print("rewrote object_2.model")

# ---------------------------------------------------------------- rename parts
msc = os.path.join(EX, "Metadata", "model_settings.config")
s = open(msc).read()
s = s.replace('value="lid_with_kraken"', 'value="lid_with_canary"')
s = s.replace('value="kraken"', 'value="canary"')
open(msc, "w").write(s)
print("renamed parts in model_settings.config")

# ---------------------------------------------------------------- rezip
if os.path.exists(OUT_3MF):
    os.remove(OUT_3MF)
names = []
with zipfile.ZipFile(SRC_3MF) as z:
    names = z.namelist()                      # preserve original entry order
with zipfile.ZipFile(OUT_3MF, "w", zipfile.ZIP_DEFLATED) as z:
    for n in names:
        p = os.path.join(EX, n)
        z.write(p, n)
print("wrote", OUT_3MF, os.path.getsize(OUT_3MF), "bytes")

# exports for inspection
lid_new.export(os.path.join(HERE, "tweety_lid.stl"))
canary.export(os.path.join(HERE, "tweety_canary.stl"))
