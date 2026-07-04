"""Traveler NPC — patched coat, draped sash, shoulder pouch. v2 toolkit (rounded + linear color)."""
import numpy as np
import trimesh
from trimesh.visual.material import PBRMaterial
from trimesh.visual import TextureVisuals

def lin(c): return [(x/255.0)**2.2 for x in c[:3]]+[1.0]
def M(c): return TextureVisuals(material=PBRMaterial(baseColorFactor=lin(c),
                                roughnessFactor=0.9, metallicFactor=0.0))
def rbox(ex,ey,ez,c,e=0.35,subdiv=2,T=None,flat=False):
    m=trimesh.creation.icosphere(subdivisions=subdiv,radius=1.0)
    v=m.vertices; m.vertices=np.sign(v)*(np.abs(v)**e)
    m.vertices*=[ex/2,ey/2,ez/2]
    if T is not None: m.apply_transform(T)
    m.apply_translation(c)
    if flat: m.unmerge_vertices()
    return m
def ell(rx,ry,rz,c,subdiv=3,flat=False):
    m=trimesh.creation.icosphere(subdivisions=subdiv,radius=1.0)
    m.apply_scale([rx,ry,rz]); m.apply_translation(c)
    if flat: m.unmerge_vertices()
    return m
def cap(p0,p1,r,sec=14):
    p0,p1=np.array(p0,float),np.array(p1,float)
    v=p1-p0; h=np.linalg.norm(v)
    m=trimesh.creation.capsule(height=h,radius=r,count=[sec,sec])
    m.apply_transform(trimesh.geometry.align_vectors([0,0,1],v/h))
    m.apply_translation((p0+p1)/2); return m
def cyl(r,h,c,sec=18):
    m=trimesh.creation.cylinder(radius=r,height=h,sections=sec)
    m.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2,[1,0,0]))
    m.apply_translation(c); return m
def torus_xz(rx,rz,minor,c,sec=28):
    m=trimesh.creation.torus(major_radius=1.0,minor_radius=minor,
                             major_sections=sec,minor_sections=10)
    m.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2,[1,0,0]))
    m.apply_scale([rx,1.0,rz]); m.apply_translation(c); return m
def rotX(a): return trimesh.transformations.rotation_matrix(a,[1,0,0])
def rotY(a): return trimesh.transformations.rotation_matrix(a,[0,1,0])
def rotZ(a): return trimesh.transformations.rotation_matrix(a,[0,0,1])

P=[]
def add(n,m,c): P.append((n,m,c))

SKIN=(233,172,120,255); COAT=(206,124,92,255); ROBE=(216,170,118,255)
SASH1=(224,162,112,255); SASH2=(204,136,94,255)
SCARF=(242,235,215,255); BAND=(196,164,132,255)
STRAP=(166,118,82,255); POUCH=(142,138,88,255)
PCREAM=(242,232,202,255); PTERRA=(198,108,70,255)
EYE=(88,58,44,255); BROW=(172,116,72,255)

# base plinth
add('Base', rbox(0.90,0.10,0.58,[0,0.05,0.02],e=0.30), PTERRA)

# body: salmon coat + tan robe front
add('Body_Coat', ell(0.175,0.35,0.15,[0,0.60,0.0]), COAT)
add('Robe_Front', ell(0.085,0.32,0.145,[0,0.58,0.035]), ROBE)
add('Robe_Hem', ell(0.16,0.10,0.14,[0,0.30,0.02]), ROBE)

# draped sash: faceted folds from left shoulder to right hip
sash=[(-0.055,0.82,0.145,0.16,SASH1),(-0.02,0.74,0.15,0.20,SASH2),
      (0.015,0.65,0.155,0.24,SASH1),(0.05,0.55,0.155,0.27,SASH2),
      (0.075,0.44,0.15,0.28,SASH1),(0.06,0.33,0.145,0.26,SASH2)]
for i,(sx,sy,sz,w,col) in enumerate(sash):
    f=rbox(w,0.105,0.075,[0,0,0],e=0.42,T=rotZ(-0.52),flat=True)
    f.apply_translation([sx,sy,sz])
    add(f'Sash_{i}',f,col)

# patches
patches=[( 0.14,0.72,0.145,0.07,0.09,PCREAM,-0.1),   # right chest
         (-0.06,0.50,0.185,0.07,0.06,PCREAM,0.05),   # sash cream
         ( 0.02,0.40,0.20,0.07,0.06,PTERRA,-0.35),   # sash terracotta
         ( 0.12,0.30,0.16,0.07,0.09,PCREAM,0.0)]     # hem
for i,(px,py,pz,w,h,col,a) in enumerate(patches):
    p=rbox(w,h,0.02,[0,0,0],e=0.45,T=rotZ(a))
    p.apply_translation([px,py,pz])
    add(f'Patch_{i}',p,col)
add('Patch_Arm', rbox(0.02,0.08,0.06,[ -0.245,0.72,0.02],e=0.45), PCREAM)

# head + face
add('Head', ell(0.115,0.125,0.11,[0,1.06,0.03]), SKIN)
add('Nose', ell(0.014,0.024,0.02,[0,1.035,0.14],2), SKIN)
for s,nm in [(1,'L'),(-1,'R')]:
    add(f'Eye_{nm}', ell(0.013,0.017,0.010,[s*0.045,1.065,0.128],2), EYE)
    add(f'Brow_{nm}', cap([s*0.062,1.105,0.118],[s*0.024,1.11,0.124],0.007,8), BROW)
sm=cap([-0.020,0.995,0.132],[0.020,0.995,0.132],0.006,8)
add('Smile', sm, (196,124,84,255))
for s in (1,-1):
    add(f'Smile_C_{"L" if s>0 else "R"}', ell(0.008,0.008,0.006,[s*0.024,1.0,0.130],1), (196,124,84,255))

# headscarf: dome + band + long side/back flaps
add('Scarf_Top', ell(0.128,0.088,0.122,[0,1.145,0.02]), SCARF)
add('Scarf_Band', torus_xz(0.121,0.116,0.020,[0,1.115,0.02]), BAND)
for s,nm in [(1,'L'),(-1,'R')]:
    add(f'Scarf_Side_{nm}', rbox(0.055,0.30,0.10,[s*0.118,0.965,-0.005],e=0.35), SCARF)
add('Scarf_Back', rbox(0.19,0.30,0.05,[0,0.965,-0.088],e=0.35), SCARF)

# arms slightly out-down
for s,nm in [(1,'L'),(-1,'R')]:
    add(f'Sleeve_{nm}', cap([s*0.155,0.86,0.02],[s*0.30,0.63,0.05],0.055), COAT)
    add(f'Hand_{nm}', ell(0.045,0.055,0.045,[s*0.325,0.575,0.058],2), SKIN)

# shoulder strap + pouch on right hip
add('Strap', cap([-0.095,0.885,0.135],[0.195,0.545,0.15],0.020), STRAP)
add('Strap_Back', cap([-0.095,0.885,-0.075],[0.19,0.55,-0.06],0.020), STRAP)
pb=ell(0.095,0.115,0.075,[0.245,0.455,0.15],2,flat=True)
add('Pouch', pb, POUCH)
add('Pouch_Flap', rbox(0.145,0.06,0.10,[0.24,0.545,0.15],e=0.4), (196,168,124,255))
add('Pouch_Tie', ell(0.025,0.03,0.025,[0.245,0.56,0.20],1), STRAP)

# feet + sandals
for s,nm in [(1,'L'),(-1,'R')]:
    add(f'Foot_{nm}', ell(0.05,0.04,0.09,[s*0.075,0.145,0.075],2), SKIN)
    add(f'Sandal_{nm}', ell(0.06,0.02,0.105,[s*0.075,0.113,0.08],2), (176,128,84,255))
    add(f'Sandal_Strap_{nm}', cap([s*0.045,0.16,0.075],[s*0.105,0.16,0.075],0.010,8), (176,128,84,255))

sc=trimesh.Scene(); t=0
for n,m,c in P:
    m.visual=M(c); sc.add_geometry(m,node_name=n,geom_name=n); t+=len(m.faces)
sc.export('/home/claude/traveler.glb')
print(f'traveler.glb — {len(P)} parts, {t} tris')
