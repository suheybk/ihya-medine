"""Boy with takke cap, blue tunic, beige pants — v2 toolkit (rounded + linear color)."""
import numpy as np
import trimesh
from trimesh.visual.material import PBRMaterial
from trimesh.visual import TextureVisuals

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
def cap(p0,p1,r,sec=14):
    p0,p1=np.array(p0,float),np.array(p1,float)
    v=p1-p0; h=np.linalg.norm(v)
    m=trimesh.creation.capsule(height=h,radius=r,count=[sec,sec])
    m.apply_transform(trimesh.geometry.align_vectors([0,0,1],v/h))
    m.apply_translation((p0+p1)/2); return m
def rotX(a): return trimesh.transformations.rotation_matrix(a,[1,0,0])
def rotZ(a): return trimesh.transformations.rotation_matrix(a,[0,0,1])

P=[]
def add(n,m,c): P.append((n,m,c))

SKIN=(244,206,176,255); BLUE=(170,184,226,255); PANT=(209,197,171,255)
SHOE=(172,112,66,255);  SOLE=(138,86,52,255)
HAIR=(96,62,46,255);    CAP=(106,80,62,255)
EYE=(66,46,38,255);     BROW=(84,56,42,255)

# ---- legs / pants / shoes ----
for s,nm in [(1,'L'),(-1,'R')]:
    add(f'Pant_{nm}', rbox(0.115,0.26,0.115,[s*0.062,0.235,0.0],e=0.32), PANT)
    add(f'Shoe_{nm}', ell(0.062,0.048,0.105,[s*0.065,0.055,0.035],2), SHOE)
    add(f'Sole_{nm}', ell(0.065,0.022,0.108,[s*0.065,0.025,0.035],2), SOLE)

# ---- tunic ----
add('Tunic', ell(0.145,0.235,0.12,[0,0.475,0.0]), BLUE)
add('Tunic_Hem', ell(0.14,0.09,0.115,[0,0.31,0.0]), BLUE)
# arms down, slightly forward
for s,nm in [(1,'L'),(-1,'R')]:
    add(f'Sleeve_{nm}', cap([s*0.13,0.62,0.01],[s*0.185,0.36,0.05],0.048), BLUE)
    add(f'Hand_{nm}', ell(0.038,0.048,0.038,[s*0.19,0.315,0.06],2), SKIN)

# ---- head ----
add('Head', ell(0.135,0.14,0.13,[0,0.79,0.01]), SKIN)
for s,nm in [(1,'L'),(-1,'R')]:
    add(f'Ear_{nm}', ell(0.022,0.03,0.022,[s*0.132,0.775,0.0],2), SKIN)
    add(f'Eye_{nm}', ell(0.018,0.026,0.012,[s*0.052,0.795,0.125],2), EYE)
    # brows: gentle arcs
    add(f'Brow_{nm}', cap([s*0.075,0.845,0.112],[s*0.028,0.852,0.12],0.008,8), BROW)
add('Nose', ell(0.012,0.016,0.014,[0,0.765,0.142],2), (232,178,146,255))
add('Smile', cap([-0.016,0.735,0.132],[0.016,0.735,0.132],0.006,8), (198,138,108,255))
add('Smile_C', ell(0.007,0.007,0.005,[0.021,0.74,0.130],1), (198,138,108,255))

# ---- hair: back/side mass + swoosh bangs ----
add('Hair_Back', ell(0.142,0.13,0.135,[0,0.815,-0.02]), HAIR)
bangs=[(-0.07,0.865,0.10,0.28),(-0.01,0.875,0.115,-0.15),(0.055,0.868,0.105,0.3),(0.10,0.85,0.08,-0.25)]
for i,(bx,by,bz,a) in enumerate(bangs):
    b=ell(0.05,0.028,0.035,[0,0,0],2)
    b.apply_transform(rotZ(a)); b.apply_translation([bx,by,bz])
    add(f'Bang_{i}', b, HAIR)
add('Hair_SideR', ell(0.03,0.06,0.05,[-0.125,0.79,0.03],2), HAIR)
add('Hair_SideL', ell(0.03,0.06,0.05,[0.125,0.79,0.03],2), HAIR)

# ---- takke cap: flat-topped, slightly tilted back ----
cp=rbox(0.275,0.135,0.27,[0,0,0],e=0.28,T=rotX(-0.08))
cp.apply_translation([0,0.935,-0.015])
add('Cap', cp, CAP)
add('Cap_Rim', ell(0.142,0.05,0.138,[0,0.885,-0.012]), CAP)

sc=trimesh.Scene(); t=0
for n,m,c in P:
    m.visual=M(c); sc.add_geometry(m,node_name=n,geom_name=n); t+=len(m.faces)
sc.export('/home/claude/boy_takke.glb')
print(f'boy_takke.glb — {len(P)} parts, {t} tris')
