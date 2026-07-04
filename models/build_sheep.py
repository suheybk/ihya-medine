"""Sheep — faceted wool ball (displaced icosphere, flat-shaded), v2 toolkit (linear color)."""
import numpy as np
import trimesh
from trimesh.visual.material import PBRMaterial
from trimesh.visual import TextureVisuals

rng = np.random.default_rng(42)

def lin(c): return [(x/255.0)**2.2 for x in c[:3]]+[1.0]
def M(c): return TextureVisuals(material=PBRMaterial(baseColorFactor=lin(c),
                                roughnessFactor=0.9, metallicFactor=0.0))
def rbox(ex,ey,ez,c,e=0.35,subdiv=2,T=None):
    m=trimesh.creation.icosphere(subdivisions=subdiv,radius=1.0)
    v=m.vertices; m.vertices=np.sign(v)*(np.abs(v)**e)
    m.vertices*=[ex/2,ey/2,ez/2]
    if T is not None: m.apply_transform(T)
    m.apply_translation(c); return m
def ell(rx,ry,rz,c,subdiv=3):
    m=trimesh.creation.icosphere(subdivisions=subdiv,radius=1.0)
    m.apply_scale([rx,ry,rz]); m.apply_translation(c); return m

P=[]
def add(n,m,c): P.append((n,m,c))

WOOL=(243,233,210,255); FACE=(172,90,64,255)
HOOF=(126,60,46,255);  EYE=(72,44,36,255)
MAT=(219,193,152,255)

# ---- base mat ----
add('Mat', rbox(0.95,0.06,0.72,[0,0.03,0.02],e=0.22), MAT)

# ---- faceted wool ball: displaced icosphere, flat-shaded ----
wool=trimesh.creation.icosphere(subdivisions=3, radius=1.0)
v=wool.vertices.copy()
bumps=rng.normal(size=(16,3)); bumps/=np.linalg.norm(bumps,axis=1)[:,None]
field=np.zeros(len(v))
for b in bumps:
    field += np.clip(v@b,0,1)**7
field=(field-field.mean())/ (field.std()+1e-9)
wool.vertices = v * (1.0 + 0.10*field)[:,None]
wool.apply_scale([0.42,0.43,0.40])
wool.apply_translation([0,0.63,-0.02])
wool.unmerge_vertices()
add('Wool', wool, WOOL)

# ---- face plate (smooth sienna) ----
add('Face', ell(0.155,0.205,0.095,[0,0.66,0.355]), FACE)
for s,nm in [(1,'L'),(-1,'R')]:
    e_=ell(0.085,0.055,0.035,[0,0,0])
    e_.apply_transform(trimesh.transformations.euler_matrix(0.25,0,s*-0.55))
    e_.apply_translation([s*0.20,0.74,0.30])
    add(f'Ear_{nm}',e_,FACE)
    add(f'Eye_{nm}', ell(0.021,0.024,0.016,[s*0.068,0.735,0.425],2), EYE)

# ---- legs + cloven hooves ----
for sx,sz,nm in [(1,1,'FL'),(-1,1,'FR'),(1,-1,'BL'),(-1,-1,'BR')]:
    add(f'Leg_{nm}', rbox(0.10,0.26,0.10,[sx*0.14,0.24,sz*0.13],e=0.35), FACE)
    for hs in (1,-1):  # split hoof
        add(f'Hoof_{nm}_{hs}', rbox(0.046,0.10,0.10,
            [sx*0.14+hs*0.027,0.085,sz*0.13+0.005],e=0.35), HOOF)

sc=trimesh.Scene(); t=0
for n,m,c in P:
    m.visual=M(c); sc.add_geometry(m,node_name=n,geom_name=n); t+=len(m.faces)
sc.export('/home/claude/sheep.glb')
print(f'sheep.glb — {len(P)} parts, {t} tris')
