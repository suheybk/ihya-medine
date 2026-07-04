"""Well v2 — fixed toolkit: superellipsoid rounded boxes (clay look) + sRGB->linear colors."""
import numpy as np
import trimesh
from trimesh.visual.material import PBRMaterial
from trimesh.visual import TextureVisuals

rng = np.random.default_rng(5)

def lin(c):
    """sRGB 0-255 -> linear baseColorFactor (glTF expects linear!)"""
    return [ (x/255.0)**2.2 for x in c[:3] ] + [1.0]

def M(c): return TextureVisuals(material=PBRMaterial(baseColorFactor=lin(c),
                                roughnessFactor=0.9, metallicFactor=0.0))

def rbox(ex, ey, ez, c, e=0.35, subdiv=2, T=None):
    """Rounded 'clay pillow' box via superellipsoid mapping of an icosphere."""
    m = trimesh.creation.icosphere(subdivisions=subdiv, radius=1.0)
    v = m.vertices
    m.vertices = np.sign(v) * (np.abs(v) ** e)
    m.vertices *= [ex/2, ey/2, ez/2]
    if T is not None: m.apply_transform(T)
    m.apply_translation(c)
    return m

def ell(rx,ry,rz,c,subdiv=3):
    m=trimesh.creation.icosphere(subdivisions=subdiv,radius=1.0)
    m.apply_scale([rx,ry,rz]); m.apply_translation(c); return m

def cap(p0,p1,r,sec=16):
    p0,p1=np.array(p0,float),np.array(p1,float)
    v=p1-p0; h=np.linalg.norm(v)
    m=trimesh.creation.capsule(height=h,radius=r,count=[sec,sec])
    m.apply_transform(trimesh.geometry.align_vectors([0,0,1],v/h))
    m.apply_translation((p0+p1)/2); return m

def cyl(r,h,c,sec=22,axis='y'):
    m=trimesh.creation.cylinder(radius=r,height=h,sections=sec)
    if axis=='y': m.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2,[1,0,0]))
    elif axis=='x': m.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2,[0,1,0]))
    m.apply_translation(c); return m

def wobble_loft(spine, radii, wscale=1.0, ring_n=14, wob=0.10, seed=0):
    """Organic timber: tube with radius noise (hand-carved look)."""
    r=np.random.default_rng(seed)
    spine=np.asarray(spine,float); n=len(spine)
    ang=np.linspace(0,2*np.pi,ring_n,endpoint=False)
    up=np.array([0.,1.,0.]); verts=[];faces=[]
    noise = 1.0 + wob*r.standard_normal(n); noise[0]=noise[-1]=1.0
    for i in range(n):
        t=spine[min(i+1,n-1)]-spine[max(i-1,0)]; t/=np.linalg.norm(t)
        ref=up if abs(t@up)<0.95 else np.array([1.,0.,0.])
        u=np.cross(t,ref); u/=np.linalg.norm(u); v=np.cross(t,u)
        for a in ang:
            verts.append(spine[i]+radii[i]*noise[i]*(np.cos(a)*u*wscale+np.sin(a)*v))
    for i in range(n-1):
        for j in range(ring_n):
            a=i*ring_n+j; b=i*ring_n+(j+1)%ring_n
            c2=(i+1)*ring_n+(j+1)%ring_n; d=(i+1)*ring_n+j
            faces+=[[a,b,c2],[a,c2,d]]
    verts+= [spine[0],spine[-1]]
    b0,t0=len(verts)-2,len(verts)-1
    for j in range(ring_n):
        faces.append([b0,(j+1)%ring_n,j])
        faces.append([t0,(n-1)*ring_n+j,(n-1)*ring_n+(j+1)%ring_n])
    m=trimesh.Trimesh(np.array(verts),np.array(faces)); m.fix_normals(); return m

def rotX(a): return trimesh.transformations.rotation_matrix(a,[1,0,0])
def rotY(a): return trimesh.transformations.rotation_matrix(a,[0,1,0])

P=[]
def add(n,m,c): P.append((n,m,c))

# ---- palette straight from the reference ----
TERRA =(196, 98, 58,255)   # dark bricks / posts
PEACH =(232,160,105,255)   # mid bricks
LIGHT =(240,196,142,255)   # light bricks
POST  =(186, 88, 52,255)
GOLDB =(212,168, 92,255)
BUCKET=(238,220,190,255)
OLIVE =(150,148, 92,255)
SANDC =(238,200,140,255)

# ---- brick rings: fat rounded clay bricks, tight fit ----
cols=[LIGHT,PEACH,TERRA]
for ring,(ry,n,r0,ph) in enumerate([(0.115,8,0.40,0.0),(0.315,8,0.40,0.39),(0.515,8,0.40,0.0)]):
    for k in range(n):
        a=k*2*np.pi/n + ph
        jit = 1.0 + 0.06*rng.standard_normal()
        b=rbox(0.40*jit,0.215,0.20,[0,0,0], T=rotY(-a))
        b.apply_translation([r0*np.sin(a),ry,r0*np.cos(a)])
        add(f'Brick_{ring}_{k}', b, cols[(k+2*ring)%3])
# top rim: slightly smaller, lighter, inset
for k in range(8):
    a=k*2*np.pi/8+0.39
    b=rbox(0.36,0.17,0.18,[0,0,0], T=rotY(-a))
    b.apply_translation([0.375*np.sin(a),0.685,0.375*np.cos(a)])
    add(f'Rim_{k}', b, LIGHT if k%2 else PEACH)

# ---- organic timber posts (wobbly, chunky) ----
for s,nm,seed in [(1,'R',3),(-1,'L',7)]:
    sp=[[s*0.44,0.45,0],[s*0.45,0.85,0],[s*0.43,1.25,0],[s*0.44,1.62,0]]
    add(f'Post_{nm}', wobble_loft(sp,[0.095,0.10,0.09,0.095],wscale=1.25,wob=0.09,seed=seed), POST)
# crossbeam: wobbly horizontal timber, past the posts, slightly clumsy ends
sp=[[-0.72,1.68,0],[-0.35,1.70,0],[0.0,1.69,0],[0.38,1.70,0],[0.72,1.68,0]]
add('Crossbeam', wobble_loft(sp,[0.10,0.115,0.11,0.115,0.10],wscale=1.0,wob=0.07,seed=11), POST)
add('Beam_EndL', ell(0.10,0.11,0.11,[-0.72,1.68,0],2), POST)
add('Beam_EndR', ell(0.10,0.11,0.11,[0.72,1.68,0],2), POST)
# diagonal support rope/rod
add('Brace', cap([-0.43,1.02,0.0],[-0.03,1.56,0.0],0.016,10), POST)

# ---- pulley ----
add('Bracket', rbox(0.06,0.16,0.12,[0,1.545,0]), GOLDB)
add('Bracket_Pin', ell(0.035,0.035,0.025,[0,1.60,0.062],2), GOLDB)
add('Wheel', cyl(0.105,0.055,[0,1.44,0],22,axis='x'), TERRA)
add('Wheel_Groove', cyl(0.112,0.02,[0,1.44,0],22,axis='x'), TERRA)
# rope over wheel down to hook
add('Rope', cap([0.0,1.44,0.09],[0.06,1.13,0.02],0.018,10), TERRA)
add('Rope_Curl', cap([0.0,1.53,0.06],[0.0,1.44,0.10],0.016,8), TERRA)
h=trimesh.creation.torus(major_radius=0.055,minor_radius=0.014,major_sections=22,minor_sections=8)
h.apply_translation([0.06,1.075,0.02]); add('Hook', h, BUCKET)

# ---- bucket: tapered, wavy rim, handle, towel ----
bk=wobble_loft([[0.06,0.80,0.02],[0.06,0.88,0.02],[0.06,0.97,0.02]],
               [0.105,0.115,0.13], wob=0.0, seed=1)
add('Bucket', bk, BUCKET)
add('Bucket_In', cyl(0.10,0.02,[0.06,0.965,0.02],20), (210,185,150,255))
for k in range(3):  # wavy rim bumps
    a=k*2.1+0.4
    add(f'Rim_B_{k}', ell(0.045,0.03,0.045,[0.06+0.115*np.cos(a),0.985,0.02+0.115*np.sin(a)],2), BUCKET)
hd=trimesh.creation.torus(major_radius=0.115,minor_radius=0.016,major_sections=26,minor_sections=8)
hd.apply_transform(rotY(np.pi/2)); hd.apply_transform(rotX(np.pi/2))
hd.apply_translation([0.06,0.99,0.02]); add('Bucket_Handle', hd, BUCKET)
add('Towel', rbox(0.10,0.16,0.03,[-0.055,0.90,0.02], T=rotX(0.12)), OLIVE)

# ---- grass + sand ----
add('Sand1', ell(0.30,0.09,0.20,[0.52,0.04,0.32],2), SANDC)
add('Sand2', ell(0.20,0.06,0.14,[-0.48,0.03,0.38],2), SANDC)
for i,(gx,gz,s) in enumerate([(-0.52,0.28,1),(0.55,0.22,-1),(0.30,0.50,1),(-0.35,-0.45,-1)]):
    for j in range(3):
        g=ell(0.030,0.13,0.055,[0,0,0],2)
        g.apply_transform(trimesh.transformations.rotation_matrix(0.45*(j-1),[0,0,1]))
        g.apply_translation([gx+0.05*(j-1),0.10,gz])
        add(f'Grass_{i}_{j}', g, OLIVE)

sc=trimesh.Scene(); t=0
for n,m,c in P:
    m.visual=M(c); sc.add_geometry(m,node_name=n,geom_name=n); t+=len(m.faces)
sc.export('/home/claude/well.glb')
print(f'well.glb v2 — {len(P)} parts, {t} tris')
