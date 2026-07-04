"""Build 7 stylized game assets from reference JPGs -> game-ready GLBs (Y-up, grounded)."""
import numpy as np
import trimesh
from trimesh.visual.material import PBRMaterial
from trimesh.visual import TextureVisuals

rng = np.random.default_rng(7)

def M(color, rough=0.85):
    return TextureVisuals(material=PBRMaterial(baseColorFactor=color,
                          roughnessFactor=rough, metallicFactor=0.0))

def ell(rx, ry, rz, c, subdiv=3, flat=False):
    m = trimesh.creation.icosphere(subdivisions=subdiv, radius=1.0)
    m.apply_scale([rx, ry, rz]); m.apply_translation(c)
    if flat: m.unmerge_vertices()
    return m

def cap(p0, p1, r, sec=20):
    p0, p1 = np.array(p0, float), np.array(p1, float)
    v = p1 - p0; h = np.linalg.norm(v)
    m = trimesh.creation.capsule(height=h, radius=r, count=[sec, sec])
    m.apply_transform(trimesh.geometry.align_vectors([0, 0, 1], v / h))
    m.apply_translation((p0 + p1) / 2)
    return m

def cyl(r, h, c, sec=26):
    m = trimesh.creation.cylinder(radius=r, height=h, sections=sec)
    m.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [1, 0, 0]))
    m.apply_translation(c); return m

def box(ex, ey, ez, c, T=None):
    m = trimesh.creation.box(extents=[ex, ey, ez])
    if T is not None: m.apply_transform(T)
    m.apply_translation(c); return m

def torus_xz(rx, rz, minor, c, sec=40):
    m = trimesh.creation.torus(major_radius=1.0, minor_radius=minor,
                               major_sections=sec, minor_sections=12)
    m.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [1, 0, 0]))
    m.apply_scale([rx, 1.0, rz]); m.apply_translation(c); return m

def loft(spine, radii, wscale=1.0, vscale=1.0, ring_n=12, flat=False):
    """Tube along spine with elliptical cross-section (wscale horizontal, vscale vertical)."""
    spine = np.asarray(spine, float); n = len(spine)
    ang = np.linspace(0, 2*np.pi, ring_n, endpoint=False)
    up = np.array([0., 1., 0.]); verts, faces = [], []
    for i in range(n):
        t = spine[min(i+1, n-1)] - spine[max(i-1, 0)]; t /= np.linalg.norm(t)
        ref = up if abs(t @ up) < 0.95 else np.array([1., 0., 0.])
        u = np.cross(t, ref); u /= np.linalg.norm(u); v = np.cross(t, u)
        for a in ang:
            verts.append(spine[i] + radii[i]*(np.cos(a)*u*wscale + np.sin(a)*v*vscale))
    for i in range(n-1):
        for j in range(ring_n):
            a = i*ring_n+j; b = i*ring_n+(j+1)%ring_n
            c = (i+1)*ring_n+(j+1)%ring_n; d = (i+1)*ring_n+j
            faces += [[a,b,c],[a,c,d]]
    verts += [spine[0], spine[-1]]
    b0, t0 = len(verts)-2, len(verts)-1
    for j in range(ring_n):
        faces.append([b0, (j+1)%ring_n, j])
        faces.append([t0, (n-1)*ring_n+j, (n-1)*ring_n+(j+1)%ring_n])
    m = trimesh.Trimesh(np.array(verts), np.array(faces)); m.fix_normals()
    if flat: m.unmerge_vertices()
    return m

def export(parts, path):
    sc = trimesh.Scene(); tri = 0
    for name, mesh, col in parts:
        mesh.visual = M(col)
        sc.add_geometry(mesh, node_name=name, geom_name=name)
        tri += len(mesh.faces)
    sc.export(path)
    print(f'{path.split("/")[-1]:26s} {len(parts):3d} parts {tri:6d} tris')

# ================================================================ DATE PALM
def palm_leaf(base, yaw, droop, L, crown_y):
    n = 14; t = np.linspace(0, 1, n)
    d = np.array([np.sin(yaw), 0, np.cos(yaw)])
    spine = base + np.outer(L*t, d)
    spine[:,1] = crown_y + 0.10*t - droop*t**2
    radii = 0.075*np.sin(np.pi*np.clip(t*0.92+0.08,0,1))**0.7 + 0.008
    return loft(spine, radii, wscale=1.5, vscale=0.28, flat=True)

def build_palm(fruit, path):
    P = []
    if fruit:
        seg = [(226,199,170,255)]*8; base_c = (238,226,197,255)
    else:
        seg = [((198,124,79,255) if i%2 else (232,186,126,255)) for i in range(8)]
        base_c = (235,197,133,255)
    P.append(('Base', cyl(0.48, 0.045, [0, 0.022, 0]), base_c))
    y, r = 0.10, 0.125
    for i in range(8):
        P.append((f'Trunk_{i}', ell(r, 0.085, r, [0, y, 0]), seg[i]))
        y += 0.135; r -= 0.006
    crown_y = y - 0.05
    leaf_c = (163,157,102,255)
    for k in range(9):
        yaw = k*2*np.pi/9 + 0.15
        droop = 0.42 if k%2 else 0.30
        L = 0.62 if k%2 else 0.55
        P.append((f'Leaf_{k}', palm_leaf(np.array([0,0,0.03]), yaw, droop, L, crown_y), leaf_c))
    for k in range(4):  # upright center leaves
        yaw = k*np.pi/2 + 0.6
        P.append((f'LeafTop_{k}', palm_leaf(np.array([0,0,0.0]), yaw, 0.10, 0.34, crown_y+0.06), leaf_c))
    if fruit:
        date_c = (205,152,74,255); stalk_c = (150,140,90,255)
        for ci, ang in enumerate([0.35, 1.35, -0.85]):
            bx, bz = 0.16*np.sin(ang), 0.16*np.cos(ang)
            top = np.array([bx, crown_y-0.02, bz])
            P.append((f'Stalk_{ci}', cap(top, top+[0, -0.16, 0.02], 0.012), stalk_c))
            for di in range(7):
                off = np.array([0.03*(-1)**di + 0.015*np.sin(di*2.1),
                                -0.03*di - 0.02, 0.02*np.cos(di*1.7)])
                P.append((f'Date_{ci}_{di}',
                          ell(0.030, 0.042, 0.030, top+off, subdiv=1, flat=True), date_c))
    export(P, path)

# ================================================================ LAMB
def build_lamb(path):
    P = []
    WOOL = (240,233,215,255); FACE = (164,94,70,255)
    HOOF = (130,70,55,255); EYE = (60,40,35,255)
    P.append(('Body', ell(0.30, 0.30, 0.28, [0, 0.52, 0]), WOOL))
    dirs = []
    ga = np.pi*(3-np.sqrt(5))
    for i in range(14):
        yy = 1 - 2*(i+0.5)/14
        rr = np.sqrt(1-yy*yy); th = ga*i
        dirs.append([rr*np.cos(th), yy, rr*np.sin(th)])
    for i, d in enumerate(dirs):
        d = np.array(d)
        c = np.array([0, 0.52, 0]) + d*0.24
        P.append((f'Wool_{i}', ell(0.135, 0.135, 0.13, c), WOOL))
    P.append(('Wool_Cap', ell(0.155, 0.11, 0.13, [0, 0.75, 0.20]), WOOL))
    P.append(('Face', ell(0.125, 0.165, 0.115, [0, 0.58, 0.29]), FACE))
    for s, nm in [(1,'L'),(-1,'R')]:
        e = ell(0.085, 0.045, 0.03, [0,0,0])
        e.apply_transform(trimesh.transformations.euler_matrix(0.2, 0, s*-0.5))
        e.apply_translation([s*0.15, 0.63, 0.25])
        P.append((f'Ear_{nm}', e, FACE))
        P.append((f'Eye_{nm}', ell(0.017,0.017,0.012,[s*0.052,0.63,0.395], subdiv=2), EYE))
    for s, z, nm in [(1,0.10,'FL'),(-1,0.10,'FR'),(1,-0.12,'BL'),(-1,-0.12,'BR')]:
        P.append((f'Leg_{nm}', cyl(0.045, 0.24, [s*0.085, 0.17, z], 16), FACE))
        P.append((f'Hoof_{nm}', cyl(0.048, 0.05, [s*0.085, 0.032, z], 16), HOOF))
    export(P, path)

# ================================================================ CAMEL
def build_camel(path):
    P = []
    BODY = (232,192,148,255); SADDLE = (211,124,90,255)
    GOLD = (200,172,106,255); HOOF = (169,152,100,255)
    EYE = (75,58,52,255); BASE = (186,170,134,255)
    P.append(('Base', cyl(0.55, 0.04, [0, 0.02, -0.05], 36), BASE))
    P.append(('Body', ell(0.20, 0.235, 0.38, [0, 0.70, -0.08]), BODY))
    P.append(('Hump', ell(0.15, 0.17, 0.19, [0, 0.90, -0.12]), BODY))
    P.append(('Saddle', ell(0.185, 0.155, 0.235, [0, 0.925, -0.12]), SADDLE))
    P.append(('Saddle_Trim', torus_xz(0.175, 0.225, 0.022, [0, 0.845, -0.12]), GOLD))
    # neck: S-curved loft
    sp = [[0,0.72,0.18],[0,0.82,0.28],[0,0.95,0.335],[0,1.07,0.36],[0,1.16,0.375]]
    P.append(('Neck', loft(sp, [0.135,0.115,0.10,0.09,0.088], ring_n=18), BODY))
    P.append(('Head', ell(0.10, 0.105, 0.145, [0, 1.21, 0.40]), BODY))
    P.append(('Muzzle', ell(0.075, 0.075, 0.095, [0, 1.185, 0.50]), BODY))
    for s, nm in [(1,'L'),(-1,'R')]:
        P.append((f'Ear_{nm}', ell(0.028,0.05,0.022,[s*0.088,1.29,0.36], subdiv=2), BODY))
        P.append((f'Eye_{nm}', ell(0.022,0.022,0.015,[s*0.078,1.235,0.455], subdiv=2), EYE))
    P.append(('Tail', cap([0,0.80,-0.44],[0.02,0.60,-0.50],0.022), BODY))
    P.append(('Tail_Tuft', ell(0.035,0.05,0.03,[0.02,0.575,-0.51], subdiv=2), HOOF))
    for s, z, nm in [(1,0.16,'FL'),(-1,0.16,'FR'),(1,-0.26,'BL'),(-1,-0.26,'BR')]:
        P.append((f'Leg_{nm}', cap([s*0.115, 0.60, z], [s*0.115, 0.10, z], 0.055), BODY))
        P.append((f'Hoof_{nm}', ell(0.062,0.055,0.082,[s*0.115,0.055,z+0.01]), HOOF))
    export(P, path)

# ================================================================ SECCADE
def build_seccade(path):
    P = []
    RUG=(144,141,90,255); CREAM=(241,232,207,255); GOLD=(211,171,88,255)
    PLANK=(198,110,70,255); SAND=(233,190,124,255); ROPE=(205,115,70,255)
    # ground + plank
    P.append(('Ground', cyl(0.85, 0.05, [0, 0.025, 0], 10), SAND))
    P.append(('Plank', box(1.5, 0.09, 0.42, [0.05, 0.10, 0]), PLANK))
    # ---- flat rug (built lying in XZ, then tilted like the reference) ----
    rug_parts = []
    rug_parts.append(('Rug', box(0.68, 0.035, 1.00, [0,0,0])))
    # cream frame
    fw = 0.045
    for name,(ex,ez,cx,cz) in {'F1':(0.50,fw,0,0.36),'F2':(0.50,fw,0,-0.36),
                               'F3':(fw,0.72+fw,-0.25,0),'F4':(fw,0.72+fw,0.25,0)}.items():
        rug_parts.append((f'Frame_{name}', box(ex,0.02,ez,[cx,0.027,cz])))
    # gold inner frame + arch point
    gold_parts = []
    gw = 0.03
    for name,(ex,ez,cx,cz) in {'G1':(0.36,gw,0,0.27),'G2':(0.36,gw,0,-0.27),
                               'G3':(gw,0.54,-0.18,0),'G4':(gw,0.54,0.18,0)}.items():
        gold_parts.append((f'Gold_{name}', box(ex,0.02,ez,[cx,0.045,cz])))
    for s in (1,-1):
        T = trimesh.transformations.rotation_matrix(s*0.55, [0,1,0])
        gold_parts.append((f'Arch_{"L" if s>0 else "R"}',
                           box(gw,0.02,0.16, [s*0.075,0.045,0.335], T)))
    # fringe
    fringe = []
    for zi, zz in [(0,0.545),(1,-0.545)]:
        for i in range(13):
            x = -0.30 + i*0.05
            fringe.append((f'Fringe_{zi}_{i}',
                cap([x,0.0,zz*0.96],[x+0.008*(-1)**i,0.0,zz+0.045*np.sign(zz)],0.011)))
    # tilt the whole rug assembly like the reference
    T = (trimesh.transformations.translation_matrix([-0.28, 0.53, 0]) @
         trimesh.transformations.rotation_matrix(0.30, [0,1,0]) @
         trimesh.transformations.rotation_matrix(-1.05, [1,0,0]))
    for name, m in rug_parts:
        m.apply_transform(T); P.append((name, m, RUG if name=='Rug' else CREAM))
    for name, m in gold_parts:
        m.apply_transform(T); P.append((name, m, GOLD))
    for name, m in fringe:
        m.apply_transform(T); P.append((name, m, CREAM))
    # ---- rolled mat ----
    RX, RY = 0.55, 0.145  # position on plank
    P.append(('Roll', cyl(0.095, 0.42, [RX, 0.355, 0], 24), RUG))
    P.append(('Roll_Spiral', torus_xz(0.055, 0.055, 0.016, [RX, 0.565, 0], 24), RUG))
    P.append(('Roll_Spiral2', torus_xz(0.022, 0.022, 0.012, [RX, 0.568, 0], 16), RUG))
    for i, yy in enumerate([0.46, 0.26]):
        P.append((f'Roll_Band_{i}', cyl(0.100, 0.045, [RX, yy, 0], 24), CREAM))
        P.append((f'Roll_Rope_{i}', torus_xz(0.102, 0.102, 0.012, [RX, yy-0.045, 0]), ROPE))
    lp = torus_xz(0.05, 0.05, 0.011, [RX+0.115, 0.36, 0.02], 20)
    lp.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [0,0,1],
                       point=[RX+0.115, 0.36, 0.02]))
    P.append(('Roll_Loop', lp, ROPE))
    export(P, path)

# ================================================================ MULBERRY
def build_mulberry(fruit, path):
    P = []
    OL1=(156,150,92,255); OL2=(170,163,100,255)
    TRUNK=(177,110,72,255); BASE=(232,186,126,255)
    BERRY=(94,62,110,255); STEM=(150,140,90,255)
    P.append(('Base', ell(0.50, 0.07, 0.42, [0, 0.03, 0])._slice_plane if False else
              ell(0.50, 0.075, 0.42, [0, 0.065, 0]), BASE))
    # trunk + branches (lofts)
    tr = [[0,0.0,0],[0.02,0.35,0],[-0.02,0.62,0.01],[0.0,0.85,0.0]]
    P.append(('Trunk', loft(tr, [0.11,0.095,0.085,0.075], ring_n=14), TRUNK))
    br = [([[0,0.62,0],[ -0.18,0.82,0.04],[-0.30,0.98,0.06]], [0.06,0.048,0.038], 'Branch_L'),
          ([[0,0.70,0],[ 0.18,0.90,-0.03],[0.32,1.02,-0.05]], [0.055,0.045,0.036], 'Branch_R'),
          ([[0,0.80,0],[ 0.06,1.00,0.10],[0.10,1.12,0.14]], [0.05,0.04,0.032], 'Branch_C')]
    for sp, rr, nm in br:
        P.append((nm, loft(sp, rr, ring_n=12), TRUNK))
    # faceted canopy blobs
    blobs = [(0,1.42,0,0.30),(-0.30,1.28,0.06,0.25),(0.32,1.26,-0.02,0.26),
             (-0.16,1.16,0.20,0.22),(0.16,1.14,0.22,0.21),(-0.42,1.10,-0.10,0.20),
             (0.44,1.08,-0.12,0.20),(0,1.24,-0.26,0.24),(-0.14,1.44,-0.14,0.20),
             (0.18,1.46,0.12,0.19)]
    canopy = []
    for i,(bx,by,bz,br_) in enumerate(blobs):
        col = OL1 if i%2 else OL2
        m = trimesh.creation.icosphere(subdivisions=1, radius=br_)
        m.apply_translation([bx,by,bz]); m.unmerge_vertices()
        P.append((f'Canopy_{i}', m, col))
        canopy.append((np.array([bx,by,bz]), br_))
    if fruit:
        bi = 0
        for c, r in canopy:
            for _ in range(2):
                d = rng.normal(size=3); d[1] = abs(d[1])*0.4 + d[1]*0.3
                d /= np.linalg.norm(d)
                if d[2] < -0.6: d[2] *= -1  # bias to visible sides
                pos = c + d*r*0.99
                b = trimesh.creation.icosphere(subdivisions=1, radius=0.035)
                b.apply_scale([1,1.35,1]); b.apply_translation(pos)
                b.unmerge_vertices()
                P.append((f'Berry_{bi}', b, BERRY))
                P.append((f'BerryStem_{bi}', cap(pos+[0,0.045,0], pos+[0,0.075,0], 0.008, 8), STEM))
                bi += 1
    export(P, path)

# ================================================================ RUN ALL
O = '/home/claude/'
build_palm(False, O+'date_palm_bare.glb')
build_palm(True,  O+'date_palm.glb')
build_lamb(O+'lamb.glb')
build_camel(O+'camel.glb')
build_seccade(O+'seccade.glb')
build_mulberry(False, O+'mulberry_tree_bare.glb')
build_mulberry(True,  O+'mulberry_tree.glb')


"""Build 7 stylized game assets from reference JPGs -> game-ready GLBs (Y-up, grounded)."""
import numpy as np
import trimesh
from trimesh.visual.material import PBRMaterial
from trimesh.visual import TextureVisuals

rng = np.random.default_rng(7)

def M(color, rough=0.85):
    return TextureVisuals(material=PBRMaterial(baseColorFactor=color,
                          roughnessFactor=rough, metallicFactor=0.0))

def ell(rx, ry, rz, c, subdiv=3, flat=False):
    m = trimesh.creation.icosphere(subdivisions=subdiv, radius=1.0)
    m.apply_scale([rx, ry, rz]); m.apply_translation(c)
    if flat: m.unmerge_vertices()
    return m

def cap(p0, p1, r, sec=20):
    p0, p1 = np.array(p0, float), np.array(p1, float)
    v = p1 - p0; h = np.linalg.norm(v)
    m = trimesh.creation.capsule(height=h, radius=r, count=[sec, sec])
    m.apply_transform(trimesh.geometry.align_vectors([0, 0, 1], v / h))
    m.apply_translation((p0 + p1) / 2)
    return m

def cyl(r, h, c, sec=26):
    m = trimesh.creation.cylinder(radius=r, height=h, sections=sec)
    m.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [1, 0, 0]))
    m.apply_translation(c); return m

def box(ex, ey, ez, c, T=None):
    m = trimesh.creation.box(extents=[ex, ey, ez])
    if T is not None: m.apply_transform(T)
    m.apply_translation(c); return m

def torus_xz(rx, rz, minor, c, sec=40):
    m = trimesh.creation.torus(major_radius=1.0, minor_radius=minor,
                               major_sections=sec, minor_sections=12)
    m.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [1, 0, 0]))
    m.apply_scale([rx, 1.0, rz]); m.apply_translation(c); return m

def loft(spine, radii, wscale=1.0, vscale=1.0, ring_n=12, flat=False):
    """Tube along spine with elliptical cross-section (wscale horizontal, vscale vertical)."""
    spine = np.asarray(spine, float); n = len(spine)
    ang = np.linspace(0, 2*np.pi, ring_n, endpoint=False)
    up = np.array([0., 1., 0.]); verts, faces = [], []
    for i in range(n):
        t = spine[min(i+1, n-1)] - spine[max(i-1, 0)]; t /= np.linalg.norm(t)
        ref = up if abs(t @ up) < 0.95 else np.array([1., 0., 0.])
        u = np.cross(t, ref); u /= np.linalg.norm(u); v = np.cross(t, u)
        for a in ang:
            verts.append(spine[i] + radii[i]*(np.cos(a)*u*wscale + np.sin(a)*v*vscale))
    for i in range(n-1):
        for j in range(ring_n):
            a = i*ring_n+j; b = i*ring_n+(j+1)%ring_n
            c = (i+1)*ring_n+(j+1)%ring_n; d = (i+1)*ring_n+j
            faces += [[a,b,c],[a,c,d]]
    verts += [spine[0], spine[-1]]
    b0, t0 = len(verts)-2, len(verts)-1
    for j in range(ring_n):
        faces.append([b0, (j+1)%ring_n, j])
        faces.append([t0, (n-1)*ring_n+j, (n-1)*ring_n+(j+1)%ring_n])
    m = trimesh.Trimesh(np.array(verts), np.array(faces)); m.fix_normals()
    if flat: m.unmerge_vertices()
    return m

def export(parts, path):
    sc = trimesh.Scene(); tri = 0
    for name, mesh, col in parts:
        mesh.visual = M(col)
        sc.add_geometry(mesh, node_name=name, geom_name=name)
        tri += len(mesh.faces)
    sc.export(path)
    print(f'{path.split("/")[-1]:26s} {len(parts):3d} parts {tri:6d} tris')

# ================================================================ DATE PALM
def palm_leaf(base, yaw, droop, L, crown_y):
    n = 14; t = np.linspace(0, 1, n)
    d = np.array([np.sin(yaw), 0, np.cos(yaw)])
    spine = base + np.outer(L*t, d)
    spine[:,1] = crown_y + 0.10*t - droop*t**2
    radii = 0.075*np.sin(np.pi*np.clip(t*0.92+0.08,0,1))**0.7 + 0.008
    return loft(spine, radii, wscale=1.5, vscale=0.28, flat=True)

def build_palm(fruit, path):
    P = []
    if fruit:
        seg = [(226,199,170,255)]*8; base_c = (238,226,197,255)
    else:
        seg = [((198,124,79,255) if i%2 else (232,186,126,255)) for i in range(8)]
        base_c = (235,197,133,255)
    P.append(('Base', cyl(0.48, 0.045, [0, 0.022, 0]), base_c))
    y, r = 0.10, 0.125
    for i in range(8):
        P.append((f'Trunk_{i}', ell(r, 0.085, r, [0, y, 0]), seg[i]))
        y += 0.135; r -= 0.006
    crown_y = y - 0.05
    leaf_c = (163,157,102,255)
    for k in range(9):
        yaw = k*2*np.pi/9 + 0.15
        droop = 0.42 if k%2 else 0.30
        L = 0.62 if k%2 else 0.55
        P.append((f'Leaf_{k}', palm_leaf(np.array([0,0,0.03]), yaw, droop, L, crown_y), leaf_c))
    for k in range(4):  # upright center leaves
        yaw = k*np.pi/2 + 0.6
        P.append((f'LeafTop_{k}', palm_leaf(np.array([0,0,0.0]), yaw, 0.10, 0.34, crown_y+0.06), leaf_c))
    if fruit:
        date_c = (205,152,74,255); stalk_c = (150,140,90,255)
        for ci, ang in enumerate([0.35, 1.35, -0.85]):
            bx, bz = 0.16*np.sin(ang), 0.16*np.cos(ang)
            top = np.array([bx, crown_y-0.02, bz])
            P.append((f'Stalk_{ci}', cap(top, top+[0, -0.16, 0.02], 0.012), stalk_c))
            for di in range(7):
                off = np.array([0.03*(-1)**di + 0.015*np.sin(di*2.1),
                                -0.03*di - 0.02, 0.02*np.cos(di*1.7)])
                P.append((f'Date_{ci}_{di}',
                          ell(0.030, 0.042, 0.030, top+off, subdiv=1, flat=True), date_c))
    export(P, path)

# ================================================================ LAMB
def build_lamb(path):
    P = []
    WOOL = (240,233,215,255); FACE = (164,94,70,255)
    HOOF = (130,70,55,255); EYE = (60,40,35,255)
    P.append(('Body', ell(0.30, 0.30, 0.28, [0, 0.52, 0]), WOOL))
    dirs = []
    ga = np.pi*(3-np.sqrt(5))
    for i in range(14):
        yy = 1 - 2*(i+0.5)/14
        rr = np.sqrt(1-yy*yy); th = ga*i
        dirs.append([rr*np.cos(th), yy, rr*np.sin(th)])
    for i, d in enumerate(dirs):
        d = np.array(d)
        c = np.array([0, 0.52, 0]) + d*0.24
        P.append((f'Wool_{i}', ell(0.135, 0.135, 0.13, c), WOOL))
    P.append(('Wool_Cap', ell(0.155, 0.11, 0.13, [0, 0.75, 0.20]), WOOL))
    P.append(('Face', ell(0.125, 0.165, 0.115, [0, 0.58, 0.29]), FACE))
    for s, nm in [(1,'L'),(-1,'R')]:
        e = ell(0.085, 0.045, 0.03, [0,0,0])
        e.apply_transform(trimesh.transformations.euler_matrix(0.2, 0, s*-0.5))
        e.apply_translation([s*0.15, 0.63, 0.25])
        P.append((f'Ear_{nm}', e, FACE))
        P.append((f'Eye_{nm}', ell(0.017,0.017,0.012,[s*0.052,0.63,0.395], subdiv=2), EYE))
    for s, z, nm in [(1,0.10,'FL'),(-1,0.10,'FR'),(1,-0.12,'BL'),(-1,-0.12,'BR')]:
        P.append((f'Leg_{nm}', cyl(0.045, 0.24, [s*0.085, 0.17, z], 16), FACE))
        P.append((f'Hoof_{nm}', cyl(0.048, 0.05, [s*0.085, 0.032, z], 16), HOOF))
    export(P, path)

# ================================================================ CAMEL
def build_camel(path):
    P = []
    BODY = (232,192,148,255); SADDLE = (211,124,90,255)
    GOLD = (200,172,106,255); HOOF = (169,152,100,255)
    EYE = (75,58,52,255); BASE = (186,170,134,255)
    P.append(('Base', cyl(0.55, 0.04, [0, 0.02, -0.05], 36), BASE))
    P.append(('Body', ell(0.20, 0.235, 0.38, [0, 0.70, -0.08]), BODY))
    P.append(('Hump', ell(0.15, 0.17, 0.19, [0, 0.90, -0.12]), BODY))
    P.append(('Saddle', ell(0.185, 0.155, 0.235, [0, 0.925, -0.12]), SADDLE))
    P.append(('Saddle_Trim', torus_xz(0.175, 0.225, 0.022, [0, 0.845, -0.12]), GOLD))
    # neck: S-curved loft
    sp = [[0,0.72,0.18],[0,0.82,0.28],[0,0.95,0.335],[0,1.07,0.36],[0,1.16,0.375]]
    P.append(('Neck', loft(sp, [0.135,0.115,0.10,0.09,0.088], ring_n=18), BODY))
    P.append(('Head', ell(0.10, 0.105, 0.145, [0, 1.21, 0.40]), BODY))
    P.append(('Muzzle', ell(0.075, 0.075, 0.095, [0, 1.185, 0.50]), BODY))
    for s, nm in [(1,'L'),(-1,'R')]:
        P.append((f'Ear_{nm}', ell(0.028,0.05,0.022,[s*0.088,1.29,0.36], subdiv=2), BODY))
        P.append((f'Eye_{nm}', ell(0.022,0.022,0.015,[s*0.078,1.235,0.455], subdiv=2), EYE))
    P.append(('Tail', cap([0,0.80,-0.44],[0.02,0.60,-0.50],0.022), BODY))
    P.append(('Tail_Tuft', ell(0.035,0.05,0.03,[0.02,0.575,-0.51], subdiv=2), HOOF))
    for s, z, nm in [(1,0.16,'FL'),(-1,0.16,'FR'),(1,-0.26,'BL'),(-1,-0.26,'BR')]:
        P.append((f'Leg_{nm}', cap([s*0.115, 0.60, z], [s*0.115, 0.10, z], 0.055), BODY))
        P.append((f'Hoof_{nm}', ell(0.062,0.055,0.082,[s*0.115,0.055,z+0.01]), HOOF))
    export(P, path)

# ================================================================ SECCADE
def build_seccade(path):
    P = []
    RUG=(144,141,90,255); CREAM=(241,232,207,255); GOLD=(211,171,88,255)
    PLANK=(198,110,70,255); SAND=(233,190,124,255); ROPE=(205,115,70,255)
    # ground + plank
    P.append(('Ground', cyl(0.85, 0.05, [0, 0.025, 0], 10), SAND))
    P.append(('Plank', box(1.5, 0.09, 0.42, [0.05, 0.10, 0]), PLANK))
    # ---- flat rug (built lying in XZ, then tilted like the reference) ----
    rug_parts = []
    rug_parts.append(('Rug', box(0.68, 0.035, 1.00, [0,0,0])))
    # cream frame
    fw = 0.045
    for name,(ex,ez,cx,cz) in {'F1':(0.50,fw,0,0.36),'F2':(0.50,fw,0,-0.36),
                               'F3':(fw,0.72+fw,-0.25,0),'F4':(fw,0.72+fw,0.25,0)}.items():
        rug_parts.append((f'Frame_{name}', box(ex,0.02,ez,[cx,0.027,cz])))
    # gold inner frame + arch point
    gold_parts = []
    gw = 0.03
    for name,(ex,ez,cx,cz) in {'G1':(0.36,gw,0,0.27),'G2':(0.36,gw,0,-0.27),
                               'G3':(gw,0.54,-0.18,0),'G4':(gw,0.54,0.18,0)}.items():
        gold_parts.append((f'Gold_{name}', box(ex,0.02,ez,[cx,0.045,cz])))
    for s in (1,-1):
        T = trimesh.transformations.rotation_matrix(s*0.55, [0,1,0])
        gold_parts.append((f'Arch_{"L" if s>0 else "R"}',
                           box(gw,0.02,0.16, [s*0.075,0.045,0.335], T)))
    # fringe
    fringe = []
    for zi, zz in [(0,0.545),(1,-0.545)]:
        for i in range(13):
            x = -0.30 + i*0.05
            fringe.append((f'Fringe_{zi}_{i}',
                cap([x,0.0,zz*0.96],[x+0.008*(-1)**i,0.0,zz+0.045*np.sign(zz)],0.011)))
    # tilt the whole rug assembly like the reference
    T = (trimesh.transformations.translation_matrix([-0.28, 0.53, 0]) @
         trimesh.transformations.rotation_matrix(0.30, [0,1,0]) @
         trimesh.transformations.rotation_matrix(-1.05, [1,0,0]))
    for name, m in rug_parts:
        m.apply_transform(T); P.append((name, m, RUG if name=='Rug' else CREAM))
    for name, m in gold_parts:
        m.apply_transform(T); P.append((name, m, GOLD))
    for name, m in fringe:
        m.apply_transform(T); P.append((name, m, CREAM))
    # ---- rolled mat ----
    RX, RY = 0.55, 0.145  # position on plank
    P.append(('Roll', cyl(0.095, 0.42, [RX, 0.355, 0], 24), RUG))
    P.append(('Roll_Spiral', torus_xz(0.055, 0.055, 0.016, [RX, 0.565, 0], 24), RUG))
    P.append(('Roll_Spiral2', torus_xz(0.022, 0.022, 0.012, [RX, 0.568, 0], 16), RUG))
    for i, yy in enumerate([0.46, 0.26]):
        P.append((f'Roll_Band_{i}', cyl(0.100, 0.045, [RX, yy, 0], 24), CREAM))
        P.append((f'Roll_Rope_{i}', torus_xz(0.102, 0.102, 0.012, [RX, yy-0.045, 0]), ROPE))
    lp = torus_xz(0.05, 0.05, 0.011, [RX+0.115, 0.36, 0.02], 20)
    lp.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [0,0,1],
                       point=[RX+0.115, 0.36, 0.02]))
    P.append(('Roll_Loop', lp, ROPE))
    export(P, path)

# ================================================================ MULBERRY
def build_mulberry(fruit, path):
    P = []
    OL1=(156,150,92,255); OL2=(170,163,100,255)
    TRUNK=(177,110,72,255); BASE=(232,186,126,255)
    BERRY=(94,62,110,255); STEM=(150,140,90,255)
    P.append(('Base', ell(0.50, 0.07, 0.42, [0, 0.03, 0])._slice_plane if False else
              ell(0.50, 0.075, 0.42, [0, 0.065, 0]), BASE))
    # trunk + branches (lofts)
    tr = [[0,0.0,0],[0.02,0.35,0],[-0.02,0.62,0.01],[0.0,0.85,0.0]]
    P.append(('Trunk', loft(tr, [0.11,0.095,0.085,0.075], ring_n=14), TRUNK))
    br = [([[0,0.62,0],[ -0.18,0.82,0.04],[-0.30,0.98,0.06]], [0.06,0.048,0.038], 'Branch_L'),
          ([[0,0.70,0],[ 0.18,0.90,-0.03],[0.32,1.02,-0.05]], [0.055,0.045,0.036], 'Branch_R'),
          ([[0,0.80,0],[ 0.06,1.00,0.10],[0.10,1.12,0.14]], [0.05,0.04,0.032], 'Branch_C')]
    for sp, rr, nm in br:
        P.append((nm, loft(sp, rr, ring_n=12), TRUNK))
    # faceted canopy blobs
    blobs = [(0,1.42,0,0.30),(-0.30,1.28,0.06,0.25),(0.32,1.26,-0.02,0.26),
             (-0.16,1.16,0.20,0.22),(0.16,1.14,0.22,0.21),(-0.42,1.10,-0.10,0.20),
             (0.44,1.08,-0.12,0.20),(0,1.24,-0.26,0.24),(-0.14,1.44,-0.14,0.20),
             (0.18,1.46,0.12,0.19)]
    canopy = []
    for i,(bx,by,bz,br_) in enumerate(blobs):
        col = OL1 if i%2 else OL2
        m = trimesh.creation.icosphere(subdivisions=1, radius=br_)
        m.apply_translation([bx,by,bz]); m.unmerge_vertices()
        P.append((f'Canopy_{i}', m, col))
        canopy.append((np.array([bx,by,bz]), br_))
    if fruit:
        bi = 0
        for c, r in canopy:
            for _ in range(2):
                d = rng.normal(size=3); d[1] = abs(d[1])*0.4 + d[1]*0.3
                d /= np.linalg.norm(d)
                if d[2] < -0.6: d[2] *= -1  # bias to visible sides
                pos = c + d*r*0.99
                b = trimesh.creation.icosphere(subdivisions=1, radius=0.035)
                b.apply_scale([1,1.35,1]); b.apply_translation(pos)
                b.unmerge_vertices()
                P.append((f'Berry_{bi}', b, BERRY))
                P.append((f'BerryStem_{bi}', cap(pos+[0,0.045,0], pos+[0,0.075,0], 0.008, 8), STEM))
                bi += 1
    export(P, path)

# ================================================================ RUN ALL
O = '/home/claude/'
build_palm(False, O+'date_palm_bare.glb')
build_palm(True,  O+'date_palm.glb')
build_lamb(O+'lamb.glb')
build_camel(O+'camel.glb')
build_seccade(O+'seccade.glb')
build_mulberry(False, O+'mulberry_tree_bare.glb')
build_mulberry(True,  O+'mulberry_tree.glb')


"""Batch 2: item pack (coin pouch, waterskin, bread, wool, milk, mulberry, dates),
characters (shepherd, neighbor, orphan) and tent -> game-ready GLBs (Y-up, grounded)."""
import numpy as np
import trimesh
from trimesh.visual.material import PBRMaterial
from trimesh.visual import TextureVisuals

rng = np.random.default_rng(11)

def M(c, rough=0.85):
    return TextureVisuals(material=PBRMaterial(baseColorFactor=c, roughnessFactor=rough,
                                               metallicFactor=0.0))
def ell(rx, ry, rz, c, subdiv=3, flat=False):
    m = trimesh.creation.icosphere(subdivisions=subdiv, radius=1.0)
    m.apply_scale([rx, ry, rz]); m.apply_translation(c)
    if flat: m.unmerge_vertices()
    return m
def cap(p0, p1, r, sec=18):
    p0, p1 = np.array(p0, float), np.array(p1, float)
    v = p1 - p0; h = np.linalg.norm(v)
    m = trimesh.creation.capsule(height=h, radius=r, count=[sec, sec])
    m.apply_transform(trimesh.geometry.align_vectors([0, 0, 1], v / h))
    m.apply_translation((p0 + p1) / 2); return m
def cyl(r, h, c, sec=26):
    m = trimesh.creation.cylinder(radius=r, height=h, sections=sec)
    m.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [1, 0, 0]))
    m.apply_translation(c); return m
def box(ex, ey, ez, c, T=None):
    m = trimesh.creation.box(extents=[ex, ey, ez])
    if T is not None: m.apply_transform(T)
    m.apply_translation(c); return m
def torus_xz(rx, rz, minor, c, sec=36):
    m = trimesh.creation.torus(major_radius=1.0, minor_radius=minor,
                               major_sections=sec, minor_sections=12)
    m.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [1, 0, 0]))
    m.apply_scale([rx, 1.0, rz]); m.apply_translation(c); return m
def rotZ(a): return trimesh.transformations.rotation_matrix(a, [0,0,1])
def rotX(a): return trimesh.transformations.rotation_matrix(a, [1,0,0])
def rotY(a): return trimesh.transformations.rotation_matrix(a, [0,1,0])
def export(P, path):
    sc = trimesh.Scene(); t = 0
    for n, m, c in P:
        m.visual = M(c); sc.add_geometry(m, node_name=n, geom_name=n); t += len(m.faces)
    sc.export(path); print(f'{path.split("/")[-1]:24s} {len(P):3d} parts {t:6d} tris')

TAN=(233,196,150,255); CREAM=(240,232,208,255); GOLD=(200,175,100,255)
TERRA=(196,110,74,255); OLIVE=(148,146,92,255); SKIN=(233,176,126,255)
EYE=(85,60,45,255)

# ---------------------------------------------------------------- COIN POUCH
def coin_pouch(path):
    P=[('Mat', box(1.0,0.045,0.75,[0,0.022,0]), TAN)]
    P.append(('Pouch_Body', ell(0.30,0.30,0.29,[0,0.33,0]), TERRA))
    P.append(('Pouch_Neck', ell(0.155,0.14,0.15,[0,0.63,0]), TERRA))
    P.append(('Pouch_Rim', torus_xz(0.135,0.13,0.045,[0,0.71,0],28), TERRA))
    P.append(('Rope', torus_xz(0.165,0.16,0.028,[0,0.585,0]), CREAM))
    P.append(('Rope_Bead', ell(0.045,0.04,0.04,[0,0.545,0.155],2), (140,135,80,255)))
    P.append(('Rope_End1', cap([0,0.53,0.16],[-0.035,0.42,0.185],0.02), CREAM))
    P.append(('Rope_End2', cap([0,0.53,0.16],[0.04,0.43,0.175],0.02), CREAM))
    for i,(cx,cz,tilt) in enumerate([(0.42,0.18,0.18),(0.55,0.28,-0.12),(0.50,0.05,0.25)]):
        c = cyl(0.11,0.035,[0,0,0],24); c.apply_transform(rotZ(tilt)); c.apply_transform(rotY(i*0.7))
        c.apply_translation([cx,0.062,cz]); P.append((f'Coin_{i}', c, GOLD))
        r = torus_xz(0.075,0.075,0.008,[0,0.02,0],20); r.apply_transform(rotZ(tilt))
        r.apply_transform(rotY(i*0.7)); r.apply_translation([cx,0.062,cz])
        P.append((f'Coin_Rim_{i}', r, GOLD))
    export(P, path)

# ---------------------------------------------------------------- WATERSKIN
def waterskin(path):
    P=[('Pedestal', box(0.9,0.5,0.7,[0,0.25,0]), (226,180,125,255))]
    T=rotZ(-0.12)
    body = ell(0.24,0.30,0.21,[0,0,0]); body.apply_transform(T); body.apply_translation([0,0.80,0])
    P.append(('Body', body, (191,102,66,255)))
    top = ell(0.14,0.20,0.13,[0,0,0]); top.apply_transform(T); top.apply_translation([0.045,1.10,0])
    P.append(('Body_Top', top, (191,102,66,255)))
    P.append(('Neck_Ring', torus_xz(0.085,0.08,0.035,[0.085,1.27,0],24), (191,102,66,255)))
    P.append(('Cork', cyl(0.055,0.11,[0.10,1.36,0],18), (229,183,120,255)))
    for s,nm in [(1,'L'),(-1,'R')]:
        r = torus_xz(0.055,0.05,0.022,[0,0,0],20); r.apply_transform(rotX(np.pi/2))
        r.apply_translation([s*0.20,1.02,0.0]); P.append((f'Ring_{nm}', r, (140,140,88,255)))
        for k in range(4):
            a=-0.5+k*0.33
            P.append((f'Tassel_{nm}_{k}', cap([s*0.21,0.95,0.0],
                     [s*(0.21+0.05*np.sin(a)),0.82,0.05*np.cos(a)],0.014), (208,172,96,255)))
    # shoulder strap: large thin loop draped to the side
    st = trimesh.creation.torus(major_radius=0.42, minor_radius=0.016,
                                major_sections=48, minor_sections=8)
    st.apply_scale([1,0.75,1]); st.apply_transform(rotY(0.25)); st.apply_transform(rotZ(0.1))
    st.apply_translation([0.10,0.78,0.10]); P.append(('Strap', st, CREAM))
    export(P, path)

# ---------------------------------------------------------------- BREAD
def bread(path):
    P=[('Board', box(1.5,0.05,1.1,[0,0.025,0]), (226,178,118,255))]
    P.append(('Loaf', ell(0.46,0.20,0.40,[0,0.24,0]), (240,214,168,255)))
    for i,(bx,bz,br) in enumerate([(-0.18,0.12,0.16),(0.22,0.05,0.18),(0.02,-0.22,0.14)]):
        P.append((f'Blush_{i}', ell(br,0.075,br*0.75,[bx,0.365,bz]), (216,142,96,255)))
    for i,(bx,bz,a) in enumerate([(-0.16,-0.05,0.5),(0.05,0.10,0.4),(0.24,-0.12,0.55)]):
        s = ell(0.10,0.02,0.035,[0,0,0]); s.apply_transform(rotY(a))
        s.apply_translation([bx,0.425,bz]); P.append((f'Score_{i}', s, (196,176,88,255)))
    export(P, path)

# ---------------------------------------------------------------- WOOL
def wool(path):
    P=[('Mat', box(1.1,0.05,0.85,[0,0.025,0]), (229,185,130,255))]
    P.append(('Core', ell(0.30,0.30,0.30,[0,0.36,0]), (242,235,215,255)))
    ga=np.pi*(3-np.sqrt(5))
    for i in range(22):
        yy=1-2*(i+0.5)/22; rr=np.sqrt(1-yy*yy); th=ga*i
        d=np.array([rr*np.cos(th),yy,rr*np.sin(th)])
        c=np.array([0,0.36,0])+d*0.26
        m=trimesh.creation.icosphere(subdivisions=1, radius=0.115+0.02*rng.random())
        m.apply_translation(c); m.unmerge_vertices()
        P.append((f'Tuft_{i}', m, (242,235,215,255)))
    export(P, path)

# ---------------------------------------------------------------- MILK JUG
def milk(path):
    P=[('Mat', box(1.05,0.05,0.85,[0,0.025,0]), TAN)]
    P.append(('Jug_Body', ell(0.28,0.28,0.27,[0,0.34,0]), (198,106,64,255)))
    P.append(('Jug_Neck', cyl(0.175,0.16,[0,0.60,0]), (198,106,64,255)))
    P.append(('Jug_Rim', torus_xz(0.175,0.17,0.035,[0,0.685,0],28), (198,106,64,255)))
    P.append(('Spout', ell(0.055,0.035,0.06,[0,0.685,0.185],2), (198,106,64,255)))
    P.append(('Milk', cyl(0.15,0.02,[0,0.675,0],24), (245,240,228,255)))
    P.append(('Band', torus_xz(0.185,0.18,0.016,[0,0.60,0]), (198,170,90,255)))
    h = trimesh.creation.torus(major_radius=0.14, minor_radius=0.035,
                               major_sections=32, minor_sections=12)
    h.apply_transform(rotX(np.pi/2))  # keep in... rotate to vertical plane
    h.apply_transform(rotY(np.pi/2)); h.apply_translation([0.26,0.46,0])
    P.append(('Handle', h, (229,180,120,255)))
    kb = box(0.06,0.07,0.025,[0.19,0.575,0.09], rotZ(0.3)); P.append(('Ribbon_Knot', kb, (140,140,85,255)))
    tl = box(0.045,0.16,0.02,[0.21,0.46,0.10], rotZ(-0.25)); P.append(('Ribbon_Tail', tl, (140,140,85,255)))
    export(P, path)

# ---------------------------------------------------------------- MULBERRY
def mulberry(path):
    P=[('Platform_Low', box(0.75,0.09,0.65,[0,0.045,0]), (226,180,120,255)),
       ('Platform_Top', box(0.60,0.09,0.50,[0,0.135,0]), (196,116,80,255))]
    core_c=np.array([0,0.62,0]); P.append(('Core', ell(0.16,0.30,0.16,core_c), (99,89,120,255)))
    ga=np.pi*(3-np.sqrt(5))
    for i in range(26):
        yy=1-2*(i+0.5)/26; rr=np.sqrt(1-yy*yy); th=ga*i
        d=np.array([rr*np.cos(th),yy,rr*np.sin(th)])
        c=core_c+d*np.array([0.14,0.28,0.14])
        P.append((f'Drupe_{i}', ell(0.065,0.065,0.065,c,2), (99,89,120,255)))
    st=box(0.05,0.16,0.05,[0.02,1.02,0], rotZ(0.25)); st.unmerge_vertices()
    P.append(('Stem', st, (198,120,85,255)))
    for k in range(4):
        a=k*np.pi/2+0.4
        lf=ell(0.16,0.02,0.06,[0,0,0],2,flat=True); lf.apply_transform(rotY(a))
        lf.apply_transform(rotZ(0.1*(-1)**k))
        lf.apply_translation([0.10*np.sin(a),0.945,0.10*np.cos(a)])
        P.append((f'Leaf_{k}', lf, (150,150,95,255)))
    export(P, path)

# ---------------------------------------------------------------- DATES
def dates(path):
    P=[('Tray', box(1.15,0.06,0.85,[0,0.03,0]), (231,190,145,255))]
    pos=[(-0.28,0.06,0.13,0.3),(0.0,0.06,0.16,-0.2),(0.28,0.06,0.12,0.5),
         (-0.14,0.06,-0.14,-0.5),(0.16,0.06,-0.15,0.15),
         (-0.10,0.20,0.02,0.7),(0.14,0.20,0.0,-0.4)]
    for i,(dx,dy,dz,a) in enumerate(pos):
        col=(198,152,84,255) if i%2 else (208,166,96,255)
        d=ell(0.135,0.085,0.085,[0,0,0]); d.apply_transform(rotY(a))
        d.apply_translation([dx,0.06+dy,dz]); P.append((f'Date_{i}', d, col))
    export(P, path)

# ---------------------------------------------------------------- SHEPHERD
def shepherd(path):
    P=[('Base', box(0.85,0.07,0.5,[0,0.035,0.02]), (198,120,84,255))]
    COAT=(206,124,88,255); ROBE=(204,160,110,255)
    P.append(('Body_Coat', ell(0.17,0.35,0.14,[0,0.53,0.01]), COAT))
    P.append(('Robe_Front', ell(0.075,0.32,0.135,[0,0.51,0.035]), ROBE))
    P.append(('Head', ell(0.115,0.12,0.11,[0,1.02,0.03]), SKIN))
    P.append(('Nose', ell(0.014,0.022,0.02,[0,1.0,0.135],2), SKIN))
    for s,nm in [(1,'L'),(-1,'R')]:
        P.append((f'Eye_{nm}', ell(0.014,0.018,0.01,[s*0.045,1.025,0.125],2), EYE))
        P.append((f'Brow_{nm}', cap([s*0.065,1.065,0.115],[s*0.025,1.07,0.12],0.007,8), (180,120,70,255)))
    P.append(('Scarf_Top', ell(0.13,0.09,0.125,[0,1.10,0.02]), CREAM))
    P.append(('Scarf_Band', torus_xz(0.122,0.117,0.018,[0,1.075,0.02]), (196,164,130,255)))
    for s,nm in [(1,'L'),(-1,'R')]:
        P.append((f'Scarf_Side_{nm}', box(0.05,0.24,0.09,[s*0.118,0.95,0.0]), CREAM))
    P.append(('Scarf_Back', box(0.19,0.24,0.045,[0,0.95,-0.085]), CREAM))
    # left arm down, right arm holds staff
    P.append(('Sleeve_L', cap([-0.15,0.80,0.04],[-0.26,0.55,0.06],0.05), COAT))
    P.append(('Hand_L', ell(0.045,0.05,0.045,[-0.27,0.50,0.07],2), SKIN))
    P.append(('Sleeve_R', cap([0.15,0.80,0.04],[0.27,0.63,0.10],0.05), COAT))
    P.append(('Hand_R', ell(0.05,0.055,0.05,[0.30,0.58,0.115],2), SKIN))
    P.append(('Staff', cyl(0.025,1.22,[0.30,0.68,0.13],14), (140,140,85,255)))
    for s,nm in [(1,'L'),(-1,'R')]:
        P.append((f'Foot_{nm}', ell(0.05,0.04,0.09,[s*0.08,0.105,0.09],2), SKIN))
        P.append((f'Sandal_{nm}', ell(0.058,0.018,0.105,[s*0.08,0.078,0.095],2), (180,130,85,255)))
    export(P, path)

# ---------------------------------------------------------------- NEIGHBOR
def neighbor(path):
    P=[]
    COAT=(150,150,98,255)
    P.append(('Body_Coat', ell(0.165,0.34,0.14,[0,0.50,0]), COAT))
    P.append(('Robe_Front', ell(0.07,0.31,0.13,[0,0.48,0.035]), CREAM))
    P.append(('Belt', box(0.145,0.05,0.03,[0,0.46,0.135]), (190,175,105,255)))
    P.append(('Head', ell(0.115,0.12,0.11,[0,0.98,0.03]), (230,170,120,255)))
    P.append(('Nose', ell(0.013,0.02,0.018,[0,0.96,0.135],2), (230,170,120,255)))
    for s,nm in [(1,'L'),(-1,'R')]:
        P.append((f'Eye_{nm}', ell(0.014,0.018,0.01,[s*0.045,0.985,0.125],2), EYE))
        P.append((f'Brow_{nm}', cap([s*0.062,1.025,0.115],[s*0.024,1.03,0.12],0.007,8), (200,120,75,255)))
    # ginger hair under the scarf
    for i,(hx,a) in enumerate([(-0.05,0.3),(0.0,-0.2),(0.05,0.4)]):
        h=ell(0.045,0.02,0.03,[0,0,0],2,flat=True); h.apply_transform(rotZ(a))
        h.apply_translation([hx,1.045,0.115]); P.append((f'Bang_{i}', h, (200,120,75,255)))
    for s,nm in [(1,'L'),(-1,'R')]:
        P.append((f'Hair_Side_{nm}', box(0.035,0.16,0.07,[s*0.105,0.90,0.045]), (200,120,75,255)))
    P.append(('Scarf_Top', ell(0.128,0.085,0.122,[0,1.06,0.02]), CREAM))
    P.append(('Scarf_Band', torus_xz(0.12,0.115,0.016,[0,1.035,0.02]), (200,175,110,255)))
    for s,nm in [(1,'L'),(-1,'R')]:
        P.append((f'Scarf_Side_{nm}', box(0.045,0.22,0.08,[s*0.117,0.91,-0.01]), CREAM))
    P.append(('Scarf_Back', box(0.18,0.22,0.04,[0,0.91,-0.085]), CREAM))
    for s,nm in [(1,'L'),(-1,'R')]:  # open welcoming arms
        P.append((f'Sleeve_{nm}', cap([s*0.14,0.76,0.05],[s*0.30,0.60,0.14],0.048), COAT))
        hd=ell(0.05,0.028,0.06,[s*0.33,0.575,0.165],2); P.append((f'Hand_{nm}', hd, (230,170,120,255)))
    for s,nm in [(1,'L'),(-1,'R')]:
        P.append((f'Leg_{nm}', cyl(0.04,0.13,[s*0.06,0.09,0.03],14), (230,170,120,255)))
        P.append((f'Sandal_{nm}', ell(0.052,0.018,0.095,[s*0.06,0.02,0.06],2), (196,116,80,255)))
    export(P, path)

# ---------------------------------------------------------------- ORPHAN
def orphan(path):
    P=[('Base', box(0.55,0.05,0.4,[0,0.025,0.02]), (222,176,128,255))]
    SK=(226,166,112,255); HAIR=(216,170,110,255)
    P.append(('Tunic', ell(0.13,0.245,0.11,[0,0.37,0.02]), CREAM))
    P.append(('Trim_V1', cap([-0.03,0.575,0.10],[0,0.53,0.115],0.009,8), (200,110,75,255)))
    P.append(('Trim_V2', cap([0.03,0.575,0.10],[0,0.53,0.115],0.009,8), (200,110,75,255)))
    P.append(('Head', ell(0.115,0.115,0.105,[0,0.72,0.03]), SK))
    P.append(('Nose', ell(0.011,0.016,0.015,[0,0.695,0.13],2), SK))
    for s,nm in [(1,'L'),(-1,'R')]:
        P.append((f'Eye_{nm}', ell(0.02,0.027,0.012,[s*0.046,0.715,0.125],2), EYE))
        # gently worried brows (inner ends raised)
        P.append((f'Brow_{nm}', cap([s*0.068,0.762,0.115],[s*0.028,0.775,0.122],0.006,8), (170,120,70,255)))
    P.append(('Hair_Cap', ell(0.12,0.075,0.112,[0,0.785,0.02]), HAIR))
    for i in range(6):  # messy spikes
        a=-0.9+i*0.36
        sp=ell(0.05,0.018,0.03,[0,0,0],2,flat=True)
        sp.apply_transform(rotZ(0.35*(-1)**i)); sp.apply_transform(rotY(a))
        sp.apply_translation([0.09*np.sin(a),0.845,0.02+0.09*np.cos(a)])
        P.append((f'Hair_Spike_{i}', sp, HAIR))
    for s,nm in [(1,'L'),(-1,'R')]:
        P.append((f'Sleeve_{nm}', cap([s*0.11,0.52,0.03],[s*0.225,0.42,0.06],0.036), CREAM))
        P.append((f'Cuff_{nm}', cap([s*0.222,0.423,0.059],[s*0.235,0.412,0.062],0.037,10), (200,110,75,255)))
        P.append((f'Hand_{nm}', ell(0.032,0.036,0.032,[s*0.25,0.40,0.068],2), SK))
    for s,nm in [(1,'L'),(-1,'R')]:
        P.append((f'Leg_{nm}', cyl(0.035,0.12,[s*0.05,0.105,0.03],14), SK))
        P.append((f'Sandal_{nm}', ell(0.045,0.016,0.08,[s*0.05,0.042,0.055],2), (160,150,95,255)))
    export(P, path)

# ---------------------------------------------------------------- TENT
def tent(path):
    P=[('Ground', box(2.3,0.07,1.5,[0,0.035,0.05]), (235,190,145,255))]
    ROOF=(206,120,86,255); EDGE=(235,180,140,255); WALL=(190,100,62,255)
    POLE=(150,140,85,255)
    ang=np.arctan2(0.80,0.78)
    for s,nm in [(1,'R'),(-1,'L')]:
        r=box(1.16,0.05,1.05,[0,0,0], rotZ(-s*ang)); r.apply_translation([s*0.39,0.665,0])
        P.append((f'Roof_{nm}', r, ROOF))
        e=box(1.16,0.03,1.09,[0,0,0], rotZ(-s*ang)); e.apply_translation([s*0.40,0.645,0])
        P.append((f'Roof_Edge_{nm}', e, EDGE))
    rg=cap([0,1.07,-0.53],[0,1.07,0.53],0.055); P.append(('Ridge', rg, ROOF))
    P.append(('Back_Wall', box(1.30,0.78,0.05,[0,0.43,-0.44]), WALL))
    for i,sx in enumerate([-0.38,0.0,0.38]):
        P.append((f'Stripe_{i}', box(0.16,0.78,0.055,[sx,0.43,-0.44]), (218,150,105,255)))
    P.append(('Pole_Center', cyl(0.038,1.02,[0,0.53,0.12],14), POLE))
    for s,nm in [(1,'R'),(-1,'L')]:
        P.append((f'Pole_Front_{nm}', cyl(0.032,0.78,[s*0.60,0.42,0.42],12), POLE))
        stub=cyl(0.03,0.28,[0,0,0],10); stub.apply_transform(rotZ(-s*0.35))
        stub.apply_translation([s*0.66,1.02,0.30]); P.append((f'Pole_Top_{nm}', stub, POLE))
        fl=box(0.56,0.05,0.80,[0,0,0], rotZ(-s*1.15) @ rotY(s*0.55))
        fl.apply_translation([s*0.42,0.46,0.42]); P.append((f'Flap_{nm}', fl, EDGE))
        for zz,pz in [(0.35,0.62),(-0.35,-0.55)]:
            P.append((f'Rope_{nm}_{zz>0}', cap([s*0.72,0.78,zz],[s*1.02,0.10,pz],0.013,10),
                      (222,170,120,255)))
            pg=cyl(0.028,0.13,[0,0,0],10); pg.apply_transform(rotZ(s*0.35))
            pg.apply_translation([s*1.03,0.08,pz]); P.append((f'Peg_{nm}_{zz>0}', pg, CREAM))
            kn=ell(0.035,0.02,0.035,[s*1.05,0.145,pz],1); P.append((f'PegTop_{nm}_{zz>0}', kn, CREAM))
    export(P, path)

O='/home/claude/'
coin_pouch(O+'item_coin.glb'); waterskin(O+'item_waterskin.glb')
bread(O+'item_bread.glb');     wool(O+'item_wool.glb')
milk(O+'item_milk.glb');       mulberry(O+'item_mulberry.glb')
dates(O+'item_date.glb');      shepherd(O+'shepherd.glb')
neighbor(O+'neighbor.glb');    orphan(O+'orphan.glb')
tent(O+'tent.glb')


"""Batch 3: Medina-era buildings & market props -> game-ready GLBs (Y-up, grounded)."""
import numpy as np
import trimesh
from trimesh.visual.material import PBRMaterial
from trimesh.visual import TextureVisuals

rng = np.random.default_rng(21)

def M(c, rough=0.85):
    return TextureVisuals(material=PBRMaterial(baseColorFactor=c, roughnessFactor=rough,
                                               metallicFactor=0.0))
def ell(rx, ry, rz, c, subdiv=3, flat=False):
    m = trimesh.creation.icosphere(subdivisions=subdiv, radius=1.0)
    m.apply_scale([rx, ry, rz]); m.apply_translation(c)
    if flat: m.unmerge_vertices()
    return m
def cap(p0, p1, r, sec=16):
    p0, p1 = np.array(p0, float), np.array(p1, float)
    v = p1 - p0; h = np.linalg.norm(v)
    m = trimesh.creation.capsule(height=h, radius=r, count=[sec, sec])
    m.apply_transform(trimesh.geometry.align_vectors([0, 0, 1], v / h))
    m.apply_translation((p0 + p1) / 2); return m
def cyl(r, h, c, sec=24, axis='y'):
    m = trimesh.creation.cylinder(radius=r, height=h, sections=sec)
    if axis == 'y': m.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2,[1,0,0]))
    elif axis == 'x': m.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2,[0,1,0]))
    m.apply_translation(c); return m
def box(ex, ey, ez, c, T=None):
    m = trimesh.creation.box(extents=[ex, ey, ez])
    if T is not None: m.apply_transform(T)
    m.apply_translation(c); return m
def torus_xz(rx, rz, minor, c, sec=32):
    m = trimesh.creation.torus(major_radius=1.0, minor_radius=minor,
                               major_sections=sec, minor_sections=10)
    m.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2,[1,0,0]))
    m.apply_scale([rx, 1.0, rz]); m.apply_translation(c); return m
def rotX(a): return trimesh.transformations.rotation_matrix(a,[1,0,0])
def rotY(a): return trimesh.transformations.rotation_matrix(a,[0,1,0])
def rotZ(a): return trimesh.transformations.rotation_matrix(a,[0,0,1])
def export(P, path):
    sc = trimesh.Scene(); t = 0
    for n, m, c in P:
        m.visual = M(c); sc.add_geometry(m, node_name=n, geom_name=n); t += len(m.faces)
    sc.export(path); print(f'{path.split("/")[-1]:22s} {len(P):3d} parts {t:6d} tris')

TAN=(233,196,150,255); CREAM=(240,232,208,255); GOLD=(203,175,100,255)
TERRA=(199,112,74,255); OLIVE=(150,148,94,255); SAND=(236,203,150,255)
PEACH=(230,170,125,255)

def frond(base, yaw, L, droop, y0, W=0.11):
    """flat faceted palm leaf for roofs"""
    lf = ell(L, 0.022, W, [0,0,0], 2, flat=True)
    lf.apply_transform(rotZ(-droop))
    lf.apply_transform(rotY(yaw))
    lf.apply_translation([base[0]+L*0.8*np.sin(yaw+np.pi/2)*0, 0, 0])  # noop
    d = np.array([np.cos(yaw), 0, -np.sin(yaw)])
    lf.apply_translation([base[0]+d[0]*L*0.75, y0, base[2]+d[2]*L*0.75])
    return lf

# ================================================================ SUFFA
def suffa(path):
    P=[]
    # platform planks on stub feet
    for i,(zz,col) in enumerate([( 0.28,PEACH),(0.0,(216,150,105,255)),(-0.28,PEACH)]):
        P.append((f'Plank_{i}', box(1.25,0.14,0.30,[0,0.20,zz]), col))
    for sx in (1,-1):
        for sz in (1,-1):
            P.append((f'Foot_{sx}_{sz}', box(0.16,0.13,0.16,[sx*0.48,0.065,sz*0.38]), (206,124,86,255)))
    # segmented palm-trunk posts
    for pi,(px,pz) in enumerate([(0.48,0.32),(-0.48,0.32),(0.48,-0.32),(-0.48,-0.32)]):
        y=0.34
        for k in range(5):
            P.append((f'Post{pi}_{k}', ell(0.075,0.075,0.075,[px,y,pz]), (238,220,190,255)))
            y+=0.13
    top=0.34+5*0.13
    # terracotta frame + diagonals
    P.append(('Beam_F', box(1.15,0.09,0.10,[0,top,0.32]), (206,124,86,255)))
    P.append(('Beam_B', box(1.15,0.09,0.10,[0,top,-0.32]), (206,124,86,255)))
    P.append(('Beam_L', box(0.10,0.09,0.74,[-0.48,top,0]), (206,124,86,255)))
    P.append(('Beam_R', box(0.10,0.09,0.74,[0.48,top,0]), (206,124,86,255)))
    P.append(('Brace_1', cap([-0.45,top-0.02,-0.28],[0.45,top-0.02,0.28],0.045), (206,124,86,255)))
    P.append(('Brace_2', cap([-0.45,top-0.02,0.28],[0.45,top-0.02,-0.28],0.045), (206,124,86,255)))
    # layered palm-frond roof
    for k in range(12):
        yaw=k*2*np.pi/12
        P.append((f'Frond_{k}', frond([0,0,0], yaw, 0.55, 0.18, top+0.10), OLIVE))
    for k in range(8):
        yaw=k*2*np.pi/8+0.3
        P.append((f'FrondTop_{k}', frond([0,0,0], yaw, 0.40, 0.10, top+0.17), (162,158,100,255)))
    P.append(('Roof_Cap', ell(0.16,0.035,0.16,[0,top+0.20,0],2,flat=True), OLIVE))
    export(P, path)

# ================================================================ WELL
def well(path):
    P=[('Sand_Mound', ell(0.55,0.10,0.30,[0.55,0.07,0.45]), SAND)]
    cols=[(224,158,110,255),(206,124,86,255),(233,186,138,255)]
    for ring,(ry,n,r0) in enumerate([(0.10,9,0.40),(0.27,9,0.40),(0.44,9,0.40)]):
        for k in range(n):
            a=k*2*np.pi/n + ring*0.35
            b=box(0.30,0.16,0.15,[0,0,0], rotY(-a))
            b.apply_translation([r0*np.sin(a),ry,r0*np.cos(a)])
            P.append((f'Brick_{ring}_{k}', b, cols[(k+ring)%3]))
    for k in range(9):  # top rim
        a=k*2*np.pi/9+0.2
        b=box(0.27,0.13,0.14,[0,0,0], rotY(-a))
        b.apply_translation([0.37*np.sin(a),0.585,0.37*np.cos(a)])
        P.append((f'Rim_{k}', b, (231,178,128,255)))
    # posts + beam + braces
    for s,nm in [(1,'R'),(-1,'L')]:
        P.append((f'Post_{nm}', box(0.11,1.0,0.13,[s*0.42,1.0,0]), (196,102,66,255)))
    P.append(('Crossbeam', box(1.25,0.13,0.15,[0,1.55,0]), (196,102,66,255)))
    P.append(('Brace', cap([-0.40,1.0,0.0],[-0.02,1.48,0.0],0.014,10), (196,102,66,255)))
    # pulley + rope + bucket
    P.append(('Pulley_Bracket', box(0.04,0.14,0.10,[0,1.44,0]), GOLD))
    w=cyl(0.085,0.05,[0,1.36,0],20,axis='x'); P.append(('Pulley_Wheel', w, (206,124,86,255)))
    P.append(('Rope', cap([0,1.36,0.0],[0.05,1.06,0.0],0.012,10), (206,124,86,255)))
    P.append(('Hook', torus_xz(0.035,0.035,0.010,[0.05,1.03,0],16), (238,220,190,255)))
    P.append(('Bucket', cyl(0.115,0.17,[0.05,0.90,0],20), (238,220,190,255)))
    P.append(('Bucket_In', cyl(0.09,0.02,[0.05,0.985,0],18), (210,185,150,255)))
    h=trimesh.creation.torus(major_radius=0.10,minor_radius=0.013,major_sections=24,minor_sections=8)
    h.apply_transform(rotY(np.pi/2)); h.apply_translation([0.05,0.99,0])
    P.append(('Bucket_Handle', h, (238,220,190,255)))
    tw=box(0.09,0.13,0.02,[0.05,0.93,0.115], rotX(0.15)); P.append(('Towel', tw, OLIVE))
    for i,(gx,gz) in enumerate([(-0.45,0.30),(0.42,0.38),(-0.30,-0.42)]):
        for j in range(3):
            g=ell(0.02,0.10,0.045,[0,0,0],1,flat=True)
            g.apply_transform(rotZ(0.4*(j-1))); g.apply_translation([gx+0.04*j,0.09,gz])
            P.append((f'Grass_{i}_{j}', g, OLIVE))
    export(P, path)

# ================================================================ MASJID
def masjid(path):
    P=[('Base', box(3.3,0.09,2.7,[0,0.045,0.1]), SAND)]
    BLD=(231,172,122,255); IN=(216,150,105,255)
    def building(nm,ex,ez,cx,cz,h=0.85):
        P.append((nm, box(ex,h,ez,[cx,h/2+0.09,cz]), BLD))
        P.append((nm+'_Top', box(ex*0.78,0.06,ez*0.7,[cx,h+0.09,cz]), IN))
    building('B_Back',1.5,0.6,0,-0.95,0.95)
    building('B_BL',1.0,0.55,-1.05,-0.9); building('B_BR',1.0,0.55,1.05,-0.9)
    building('B_L',0.62,1.35,-1.28,0.15); building('B_R',0.62,1.35,1.28,0.15)
    # colonnades + folded cream canopies
    def canopy(nm,cx,cz,w,depth,yaw=0.0,n=5,y=0.78):
        for i in range(n):
            off=(i-(n-1)/2)*(w/n)
            s=box(w/n+0.02,0.025,depth,[0,0,0], rotY(yaw) @ rotZ(0.10*(-1)**i))
            dx,dz=off*np.cos(yaw), -off*np.sin(yaw)
            s.apply_translation([cx+dx,y+0.02*(i%2),cz+dz])
            P.append((f'{nm}_{i}', s, (244,236,210,255)))
    canopy('Can_Back',0,-0.42,1.5,0.55)
    canopy('Can_L',-0.82,0.15,1.1,0.5,yaw=np.pi/2,n=4)
    canopy('Can_R',0.82,0.15,1.1,0.5,yaw=np.pi/2,n=4)
    for i in range(6):
        px=-0.62+i*0.25
        P.append((f'Col_B_{i}', cyl(0.05,0.62,[px,0.40,-0.30],12), BLD))
    for s,nm in [(1,'R'),(-1,'L')]:
        for i in range(4):
            pz=-0.28+i*0.30
            P.append((f'Col_{nm}_{i}', cyl(0.05,0.62,[s*0.72,0.40,pz],12), BLD))
    # front walls + gate
    for s,nm in [(1,'R'),(-1,'L')]:
        P.append((f'Wall_{nm}', box(0.85,0.30,0.10,[s*0.72,0.24,1.05]), BLD))
        P.append((f'Gate_{nm}', box(0.15,0.44,0.15,[s*0.27,0.31,1.05]), BLD))
    for i in range(8):  # rooftop plants
        bx,bz=[(-1.05,-0.9),(1.05,-0.9),(0.4,-0.95),(-0.5,-0.95),(-1.28,0.5),(1.28,0.5),(-1.28,-0.2),(1.28,-0.2)][i]
        for j in range(3):
            g=ell(0.02,0.08,0.04,[0,0,0],1,flat=True); g.apply_transform(rotZ(0.5*(j-1)))
            g.apply_translation([bx+0.035*(j-1),1.02,bz])
            P.append((f'Plant_{i}_{j}', g, (198,198,140,255)))
    export(P, path)

# ================================================================ RUG (mosaic)
def rug_market(path):
    P=[]
    R=(211,120,86,255); C=(242,233,208,255); F=(235,183,130,255)
    G=(160,155,100,255); Y=(216,178,96,255)
    # outer terracotta border
    for s in (1,-1):
        for i in range(4):
            P.append((f'Bd_{s}_{i}', box(0.42,0.05,0.16,[-0.66+i*0.44,0.025,s*0.72]), R))
        for i in range(3):
            P.append((f'Bs_{s}_{i}', box(0.16,0.05,0.42,[s*0.90,0.025,-0.44+i*0.44]), R))
    # cream inner frame
    for s in (1,-1):
        P.append((f'Cf_h_{s}', box(1.28,0.045,0.11,[0,0.024,s*0.535]), C))
        P.append((f'Cf_v_{s}', box(0.11,0.045,0.90,[s*0.695,0.024,0]), C))
    # field panels
    for s in (1,-1):
        P.append((f'Field_{s}', box(1.24,0.04,0.40,[0,0.022,s*0.26]), F))
    # olive corners
    for sx in (1,-1):
        for sz in (1,-1):
            P.append((f'Corner_{sx}_{sz}', box(0.16,0.045,0.13,[sx*0.56,0.024,sz*0.40]), G))
    # center diamond mosaic
    P.append(('Center', box(0.26,0.05,0.26,[0,0.026,0], rotY(np.pi/4)), G))
    for k,(dx,dz) in enumerate([(0.26,0),( -0.26,0),(0,0.26),(0,-0.26)]):
        P.append((f'DiaG_{k}', box(0.13,0.048,0.13,[dx*1.35,0.025,dz*1.35], rotY(np.pi/4)), G))
    for k,(dx,dz) in enumerate([(0.20,0.10),(0.20,-0.10),(-0.20,0.10),(-0.20,-0.10),
                                 (0.10,0.20),(-0.10,0.20),(0.10,-0.20),(-0.10,-0.20)]):
        P.append((f'DiaY_{k}', box(0.11,0.046,0.11,[dx,0.024,dz], rotY(np.pi/4)), Y))
    export(P, path)

# ================================================================ JAR (amphora)
def jar(path):
    P=[]
    b=trimesh.creation.icosphere(subdivisions=2, radius=1.0)
    b.apply_scale([0.30,0.36,0.30]); b.apply_translation([0,0.36,0]); b.unmerge_vertices()
    P.append(('Body', b, (204,110,70,255)))
    nk=trimesh.creation.icosphere(subdivisions=2, radius=1.0)
    nk.apply_scale([0.14,0.18,0.14]); nk.apply_translation([0,0.72,0]); nk.unmerge_vertices()
    P.append(('Neck', nk, (204,110,70,255)))
    P.append(('Rim', torus_xz(0.155,0.155,0.045,[0,0.84,0],28), (229,180,120,255)))
    P.append(('Cork', cyl(0.085,0.10,[0,0.89,0],18), (243,235,215,255)))
    h=trimesh.creation.torus(major_radius=0.155,minor_radius=0.038,major_sections=28,minor_sections=10)
    h.apply_transform(rotY(np.pi/2)); h.apply_translation([0.29,0.58,0])
    P.append(('Handle', h, (229,180,120,255)))
    export(P, path)

# ================================================================ SCALE
def scale(path):
    P=[('Base', box(0.62,0.14,0.42,[0,0.07,0]), (204,110,74,255)),
       ('Base_Trim', box(0.30,0.05,0.24,[0,0.165,0]), CREAM),
       ('Base_Step', box(0.22,0.08,0.18,[0,0.22,0]), (204,110,74,255))]
    P.append(('Hinge_Low', box(0.14,0.18,0.09,[0,0.32,0]), (216,196,160,255)))
    P.append(('Pin_Low', cyl(0.035,0.02,[0,0.34,0.05],14,axis='y'), CREAM))
    P.append(('Column', cyl(0.05,0.75,[0,0.70,0],16), GOLD))
    P.append(('Hinge_Top', box(0.13,0.20,0.09,[0,1.05,0]), (186,162,96,255)))
    P.append(('Pin_Top', ell(0.035,0.035,0.02,[0,1.07,0.05],2), CREAM))
    P.append(('Beam', box(1.30,0.07,0.09,[0,1.09,0]), GOLD))
    P.append(('Cap', cyl(0.04,0.10,[0,1.20,0],12), GOLD))
    for s,nm in [(1,'R'),(-1,'L')]:
        lp=trimesh.creation.torus(major_radius=0.05,minor_radius=0.018,major_sections=20,minor_sections=8)
        lp.apply_transform(rotY(np.pi/2)); lp.apply_translation([s*0.60,1.10,0])
        P.append((f'Loop_{nm}', lp, CREAM))
        top=np.array([s*0.60,1.06,0])
        for k,off in enumerate([(-0.13,-0.05),(0.13,-0.05),(0,0.13)]):
            P.append((f'Str_{nm}_{k}', cap(top, [s*0.60+off[0],0.55,off[1]],0.012,8), CREAM))
        pan=trimesh.creation.icosphere(subdivisions=2, radius=1.0)
        pan.apply_scale([0.24,0.10,0.20]); pan.apply_translation([s*0.60,0.50,0]); pan.unmerge_vertices()
        P.append((f'Pan_{nm}', pan, (186,162,96,255)))
    P.append(('Weight', cyl(0.055,0.09,[0.42,0.045,0.16],14), (140,140,88,255)))
    P.append(('Weight_Knob', ell(0.03,0.035,0.03,[0.42,0.115,0.16],2), (140,140,88,255)))
    export(P, path)

# ================================================================ SACK
def sack(path):
    P=[('Spot', cyl(0.55,0.02,[0,0.01,0],36), (244,224,188,255))]
    B=(226,178,118,255)
    P.append(('Body_Low', ell(0.40,0.36,0.36,[0,0.36,0]), B))
    P.append(('Body_Mid', ell(0.32,0.32,0.29,[0,0.60,0]), B))
    P.append(('Neck', ell(0.155,0.16,0.15,[0,0.92,0]), B))
    P.append(('Top_Flare', ell(0.20,0.11,0.18,[0,1.06,0]), B))
    P.append(('Rope1', torus_xz(0.165,0.16,0.028,[0,0.90,0]), (208,128,100,255)))
    P.append(('Rope2', torus_xz(0.160,0.155,0.026,[0,0.855,0]), (208,128,100,255)))
    P.append(('Rope_T1', cap([0.02,0.86,0.15],[0.06,0.70,0.185],0.022), (208,128,100,255)))
    P.append(('Rope_T2', cap([0.02,0.86,0.15],[-0.05,0.72,0.18],0.022), (208,128,100,255)))
    export(P, path)

# ================================================================ BASKET
def basket(path):
    P=[('Bottom', cyl(0.29,0.05,[0,0.03,0],28), (229,175,120,255))]
    W1=(229,175,120,255); W2=(243,229,196,255)
    for k in range(5):  # horizontal weave rings
        col=W1 if k%2==0 else W2
        r=0.30+0.012*k
        P.append((f'Weave_{k}', torus_xz(r,r,0.045,[0,0.08+k*0.082,0],28), col))
    for k in range(12):  # vertical strips
        a=k*2*np.pi/12
        s=box(0.075,0.46,0.045,[0,0,0], rotY(-a))
        r=0.315+0.012*2
        s.apply_translation([r*np.sin(a),0.26,r*np.cos(a)])
        P.append((f'Strip_{k}', s, W1))
    P.append(('Rim', torus_xz(0.345,0.345,0.055,[0,0.50,0],32), (214,128,92,255)))
    for s,nm in [(1,'R'),(-1,'L')]:
        h=trimesh.creation.torus(major_radius=0.07,minor_radius=0.025,major_sections=20,minor_sections=8)
        h.apply_translation([s*0.38,0.42,0])
        P.append((f'Handle_{nm}', h, (214,128,92,255)))
    fills=[(214,128,92,255),(243,229,196,255),(226,150,110,255)]
    for i in range(12):
        a=rng.uniform(0,2*np.pi); r=rng.uniform(0,0.24)
        d=ell(0.085,0.055,0.055,[0,0,0]); d.apply_transform(rotY(a))
        d.apply_translation([r*np.cos(a),0.56+0.05*rng.random(),r*np.sin(a)*0.8])
        P.append((f'Fill_{i}', d, fills[i%3]))
    for i,(fx,fz,col) in enumerate([(0.10,0.12,(214,110,84,255)),(0.22,-0.05,(216,178,96,255)),(-0.05,-0.1,(198,170,96,255))]):
        P.append((f'Fruit_{i}', ell(0.075,0.07,0.075,[fx,0.635,fz]), col))
        P.append((f'FStem_{i}', cap([fx,0.70,fz],[fx+0.02,0.745,fz],0.010,8), (150,140,80,255)))
    export(P, path)

# ================================================================ MARKET STALL
def market_stall(path):
    P=[('Base', box(1.9,0.05,1.35,[0,0.025,0.05]), SAND)]
    WOOD=(229,168,112,255)
    for s,nm in [(1,'R'),(-1,'L')]:
        P.append((f'Leg_F_{nm}', cyl(0.055,1.45,[s*0.75,0.775,0.45],14), WOOD))
        P.append((f'Leg_B_{nm}', cyl(0.055,1.45,[s*0.75,0.775,-0.35],14), WOOD))
        P.append((f'Wrap_{nm}', torus_xz(0.065,0.065,0.016,[s*0.75,0.90,0.45],16), (243,229,196,255)))
        P.append((f'Wrap2_{nm}', torus_xz(0.065,0.065,0.016,[s*0.75,0.86,0.45],16), (243,229,196,255)))
        P.append((f'Roll_{nm}', cyl(0.055,0.28,[0,1.52,0.52-0.87*(nm=='L')],12,axis='x'), WOOD)) if False else None
    P.append(('Roll_F', cyl(0.055,1.75,[0,1.50,0.55],14,axis='x'), WOOD))
    P.append(('Roll_B', cyl(0.055,1.75,[0,1.58,-0.42],14,axis='x'), WOOD))
    # striped awning: sloped strips + scalloped front
    for i in range(7):
        col=(214,110,92,255) if i%2==0 else (243,229,196,255)
        s=box(0.25,0.035,1.05,[0,0,0], rotX(0.10))
        s.apply_translation([-0.75+i*0.25,1.56,0.06])
        P.append((f'Awning_{i}', s, col))
        sc=cyl(0.05,0.24,[-0.75+i*0.25,1.50,0.575],12,axis='x')
        P.append((f'Scallop_{i}', sc, col))
    # counter
    P.append(('Counter', box(1.35,0.08,0.55,[0,0.72,0.10]), WOOD))
    for s in (1,-1):
        P.append((f'CLeg_{s}', cyl(0.05,0.68,[s*0.55,0.36,0.10],12), WOOD))
    P.append(('CRail', cyl(0.04,1.05,[0,0.22,0.10],10,axis='x'), WOOD))
    bowls=[(-0.42,(214,110,84,255)),(-0.12,(150,148,94,255)),(0.22,(150,148,94,255)),(0.50,(243,229,196,255))]
    for i,(bx,fc) in enumerate(bowls):
        P.append((f'Bowl_{i}', cyl(0.135 if i in(0,2) else 0.10,0.09,[bx,0.805,0.10],18), (206,124,86,255)))
        for j in range(5 if i in(0,2) else 3):
            a=j*2.1; r=0.06 if i in(0,2) else 0.04
            P.append((f'Prod_{i}_{j}', ell(0.045,0.035,0.03,
                     [bx+r*np.cos(a),0.865,0.10+r*np.sin(a)],2), fc))
    export(P, path)

# ================================================================ DATE CLUSTER
def date_cluster(path):
    P=[('Mound', ell(0.42,0.10,0.35,[0,0.09,0]), (226,178,118,255))]
    st=box(0.09,0.32,0.06,[0.01,1.32,0], rotZ(0.05)); st.unmerge_vertices()
    P.append(('Stem', st, OLIVE))
    for s in (1,-1):
        f=box(0.05,0.18,0.05,[s*0.06,1.13,0], rotZ(-s*0.35)); f.unmerge_vertices()
        P.append((f'Fork_{s}', f, OLIVE))
    cols=[(216,168,90,255),(206,120,84,255),(240,224,192,255),(226,186,120,255)]
    core=np.array([0,0.72,0])
    ga=np.pi*(3-np.sqrt(5))
    P.append(('Core', ell(0.14,0.34,0.12,core), (206,150,90,255)))
    for i in range(34):
        yy=1-2*(i+0.5)/34; rr=np.sqrt(1-yy*yy); th=ga*i
        d=np.array([rr*np.cos(th),yy,rr*np.sin(th)])
        c=core+d*np.array([0.16,0.36,0.14])
        dt=ell(0.075,0.10,0.075,[0,0,0]); dt.apply_transform(rotZ(rng.uniform(-0.4,0.4)))
        dt.apply_translation(c)
        P.append((f'Date_{i}', dt, cols[i%4]))
    P.append(('Date_Btm', ell(0.07,0.095,0.07,[0.01,0.30,0]), cols[0]))
    export(P, path)

# ================================================================ WHEAT
def wheat(path):
    P=[('Mound', ell(0.48,0.14,0.42,[0,0.13,0],2,flat=True), (233,178,120,255))]
    scols=[(226,178,100,255),(240,224,190,255),(216,166,92,255)]
    gcols=[(233,196,130,255),(243,228,190,255),(226,180,110,255)]
    n=9
    for k in range(n):
        a=k*2*np.pi/n
        col=scols[k%3]
        b=np.array([0.10*np.cos(a),0.20,0.10*np.sin(a)*0.8])
        t=np.array([0.17*np.cos(a),0.95+0.06*(k%3),0.17*np.sin(a)*0.8])
        P.append((f'Stalk_{k}', cap(b,t,0.022,10), col))
        gc=gcols[k%3]
        hb=t.copy()
        for r in range(4):
            for s in (1,-1):
                g=ell(0.035,0.05,0.028,[0,0,0],1,flat=True)
                g.apply_translation(hb+[s*0.030+0.5*(t[0]-0)*0.0,0.055*r+0.03,0])
                # lean grains outward slightly
                P.append((f'Grain_{k}_{r}_{s}', g, gc))
        tip=ell(0.032,0.055,0.026,[0,0,0],1,flat=True); tip.apply_translation(hb+[0,0.245,0])
        P.append((f'Tip_{k}', tip, gc))
    P.append(('Band', torus_xz(0.135,0.115,0.045,[0,0.52,0],24), (216,132,96,255)))
    for k in range(6):  # flaring leaf blades
        a=k*np.pi/3+0.2
        lf=ell(0.03,0.16,0.02,[0,0,0],2,flat=True)
        lf.apply_transform(rotZ(0.55*np.cos(a))); lf.apply_transform(rotY(a))
        lf.apply_translation([0.16*np.cos(a),0.62,0.13*np.sin(a)])
        P.append((f'Blade_{k}', lf, (229,186,110,255)))
    export(P, path)

O='/home/claude/'
suffa(O+'suffa.glb'); well(O+'well.glb'); masjid(O+'masjid_nabawi.glb')
rug_market(O+'rug_market.glb'); jar(O+'jar.glb'); scale(O+'scale.glb')
sack(O+'sack.glb'); basket(O+'basket.glb'); market_stall(O+'market_stall.glb')
date_cluster(O+'date_cluster.glb'); wheat(O+'wheat.glb')
"""Batch 4: palm fence panel + chicken -> game-ready GLBs (Y-up, grounded)."""
import numpy as np
import trimesh
from trimesh.visual.material import PBRMaterial
from trimesh.visual import TextureVisuals

def M(c): return TextureVisuals(material=PBRMaterial(baseColorFactor=c,
                                roughnessFactor=0.85, metallicFactor=0.0))
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
def box(ex,ey,ez,c,T=None):
    m=trimesh.creation.box(extents=[ex,ey,ez])
    if T is not None: m.apply_transform(T)
    m.apply_translation(c); return m
def rotZ(a): return trimesh.transformations.rotation_matrix(a,[0,0,1])
def rotY(a): return trimesh.transformations.rotation_matrix(a,[0,1,0])
def export(P,path):
    sc=trimesh.Scene(); t=0
    for n,m,c in P:
        m.visual=M(c); sc.add_geometry(m,node_name=n,geom_name=n); t+=len(m.faces)
    sc.export(path); print(f'{path.split("/")[-1]:18s} {len(P):3d} parts {t:6d} tris')

WOOD=(235,190,130,255); ROPE=(214,126,92,255)
OLIVE=(152,148,90,255); CREAM=(240,231,203,255)

# ================================================================ PALM FENCE
def palm_fence(path):
    P=[('Sand', ell(0.95,0.05,0.45,[0.05,0.045,0.05]), (238,198,135,255))]
    for s,nm in [(1,'R'),(-1,'L')]:
        P.append((f'Post_{nm}', box(0.13,1.42,0.13,[s*0.78,0.71,0]), WOOD))
    P.append(('Rail_Top', box(1.95,0.11,0.10,[0,1.16,0.02]), WOOD))
    P.append(('Rail_Btm', box(1.95,0.11,0.10,[0,0.32,0.02]), WOOD))
    # rope X lashings at the 4 joints
    for sx,nm1 in [(1,'R'),(-1,'L')]:
        for yy,nm2 in [(1.16,'T'),(0.32,'B')]:
            P.append((f'RopeA_{nm1}{nm2}', cap([sx*0.78-0.12,yy-0.11,0.09],
                     [sx*0.78+0.12,yy+0.11,0.09],0.030), ROPE))
            P.append((f'RopeB_{nm1}{nm2}', cap([sx*0.78-0.12,yy+0.11,0.09],
                     [sx*0.78+0.12,yy-0.11,0.09],0.030), ROPE))
    # weave: horizontal olive strips
    for i in range(5):
        yy=0.46+i*0.145
        P.append((f'Weft_{i}', box(1.38,0.085,0.05,[0,yy,0.02*(-1)**i]), OLIVE))
    # cream wavy horizontals (two offset segments each)
    for k,(yy,zo) in enumerate([(0.62,0.05),(0.90,-0.04)]):
        P.append((f'Wave_{k}a', box(0.62,0.10,0.055,[-0.36,yy,zo], rotZ(0.10)), CREAM))
        P.append((f'Wave_{k}b', box(0.62,0.10,0.055,[0.28,yy+0.05,zo], rotZ(-0.14)), CREAM))
    # diagonals
    diag=[( 0.10,0.80,0.66,OLIVE,0.06),(-0.16,0.78,-0.72,OLIVE,-0.03),
          ( 0.34,0.80,0.72,CREAM,-0.06),(0.05,0.76,-0.60,CREAM,0.08)]
    for k,(cx,cy,a,col,zo) in enumerate(diag):
        P.append((f'Diag_{k}', box(0.10,0.82,0.055,[cx,cy,zo], rotZ(a)), col))
    # verticals hooked over the top rail
    for k,(vx,col) in enumerate([(-0.08,CREAM),(0.22,OLIVE),(0.42,OLIVE)]):
        P.append((f'Vert_{k}', box(0.10,0.80,0.055,[vx,0.84,0.07]), col))
        P.append((f'Vert_{k}_hook', box(0.10,0.14,0.16,[vx,1.20,0.0]), col))
    export(P,path)

# ================================================================ CHICKEN
def chicken(path):
    P=[]
    BODY=(242,235,214,255); RED=(224,110,100,255); ORANGE=(214,130,90,255)
    # egg silhouette from stacked ellipsoids
    P.append(('Body', ell(0.26,0.32,0.24,[0,0.50,0]), BODY))
    P.append(('Chest', ell(0.22,0.26,0.20,[0,0.68,0.02]), BODY))
    P.append(('Head', ell(0.165,0.20,0.155,[0,0.88,0.03]), BODY))
    # comb: 3 faceted spikes
    for k,(cx,h) in enumerate([(-0.05,0.10),(0.0,0.135),(0.05,0.10)]):
        c=ell(0.030,h,0.045,[0,0,0],1,flat=True)
        c.apply_transform(rotZ(0.15*(1-k)))
        c.apply_translation([cx,1.07,0.02])
        P.append((f'Comb_{k}', c, RED))
    # face
    bk=ell(0.055,0.045,0.06,[0,0.86,0.185],1,flat=True)
    P.append(('Beak', bk, ORANGE))
    for s,nm in [(1,'L'),(-1,'R')]:
        P.append((f'Eye_{nm}', ell(0.018,0.022,0.014,[s*0.075,0.90,0.145],2), (196,120,80,255)))
        P.append((f'Wattle_{nm}', ell(0.028,0.042,0.026,[s*0.028,0.785,0.16],2), RED))
    # wings: flattened rounded shape + feather notches
    for s,nm in [(1,'L'),(-1,'R')]:
        w=ell(0.045,0.115,0.15,[s*0.245,0.58,-0.02])
        P.append((f'Wing_{nm}', w, (238,229,205,255)))
        for j in range(2):
            P.append((f'Wing_{nm}_f{j}', ell(0.035,0.045,0.05,
                     [s*0.255,0.50+0.0*j,-0.14-0.05*j],2), (238,229,205,255)))
    P.append(('Tail', ell(0.09,0.13,0.07,[0,0.62,-0.24]), BODY))
    # legs + three-toed feet
    for s,nm in [(1,'L'),(-1,'R')]:
        P.append((f'Leg_{nm}', cyl(0.018,0.22,[s*0.07,0.13,0.0],10), ORANGE))
        for k,a in enumerate([-0.5,0.0,0.5]):
            P.append((f'Toe_{nm}_{k}', cap([s*0.07,0.022,0.0],
                     [s*0.07+0.09*np.sin(a)*0.6,0.022,0.10*np.cos(a)],0.016,8), ORANGE))
        P.append((f'Heel_{nm}', cap([s*0.07,0.022,0.0],[s*0.07,0.022,-0.05],0.016,8), ORANGE))
    for n,m,c in P: m.apply_scale(0.35)
    export(P,path)

O='/home/claude/'
palm_fence(O+'palm_fence.glb')
chicken(O+'chicken.glb')

"""Build 7 stylized game assets from reference JPGs -> game-ready GLBs (Y-up, grounded)."""
import numpy as np
import trimesh
from trimesh.visual.material import PBRMaterial
from trimesh.visual import TextureVisuals

rng = np.random.default_rng(7)

def M(color, rough=0.85):
    return TextureVisuals(material=PBRMaterial(baseColorFactor=color,
                          roughnessFactor=rough, metallicFactor=0.0))

def ell(rx, ry, rz, c, subdiv=3, flat=False):
    m = trimesh.creation.icosphere(subdivisions=subdiv, radius=1.0)
    m.apply_scale([rx, ry, rz]); m.apply_translation(c)
    if flat: m.unmerge_vertices()
    return m

def cap(p0, p1, r, sec=20):
    p0, p1 = np.array(p0, float), np.array(p1, float)
    v = p1 - p0; h = np.linalg.norm(v)
    m = trimesh.creation.capsule(height=h, radius=r, count=[sec, sec])
    m.apply_transform(trimesh.geometry.align_vectors([0, 0, 1], v / h))
    m.apply_translation((p0 + p1) / 2)
    return m

def cyl(r, h, c, sec=26):
    m = trimesh.creation.cylinder(radius=r, height=h, sections=sec)
    m.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [1, 0, 0]))
    m.apply_translation(c); return m

def box(ex, ey, ez, c, T=None):
    m = trimesh.creation.box(extents=[ex, ey, ez])
    if T is not None: m.apply_transform(T)
    m.apply_translation(c); return m

def torus_xz(rx, rz, minor, c, sec=40):
    m = trimesh.creation.torus(major_radius=1.0, minor_radius=minor,
                               major_sections=sec, minor_sections=12)
    m.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [1, 0, 0]))
    m.apply_scale([rx, 1.0, rz]); m.apply_translation(c); return m

def loft(spine, radii, wscale=1.0, vscale=1.0, ring_n=12, flat=False):
    """Tube along spine with elliptical cross-section (wscale horizontal, vscale vertical)."""
    spine = np.asarray(spine, float); n = len(spine)
    ang = np.linspace(0, 2*np.pi, ring_n, endpoint=False)
    up = np.array([0., 1., 0.]); verts, faces = [], []
    for i in range(n):
        t = spine[min(i+1, n-1)] - spine[max(i-1, 0)]; t /= np.linalg.norm(t)
        ref = up if abs(t @ up) < 0.95 else np.array([1., 0., 0.])
        u = np.cross(t, ref); u /= np.linalg.norm(u); v = np.cross(t, u)
        for a in ang:
            verts.append(spine[i] + radii[i]*(np.cos(a)*u*wscale + np.sin(a)*v*vscale))
    for i in range(n-1):
        for j in range(ring_n):
            a = i*ring_n+j; b = i*ring_n+(j+1)%ring_n
            c = (i+1)*ring_n+(j+1)%ring_n; d = (i+1)*ring_n+j
            faces += [[a,b,c],[a,c,d]]
    verts += [spine[0], spine[-1]]
    b0, t0 = len(verts)-2, len(verts)-1
    for j in range(ring_n):
        faces.append([b0, (j+1)%ring_n, j])
        faces.append([t0, (n-1)*ring_n+j, (n-1)*ring_n+(j+1)%ring_n])
    m = trimesh.Trimesh(np.array(verts), np.array(faces)); m.fix_normals()
    if flat: m.unmerge_vertices()
    return m

def export(parts, path):
    sc = trimesh.Scene(); tri = 0
    for name, mesh, col in parts:
        mesh.visual = M(col)
        sc.add_geometry(mesh, node_name=name, geom_name=name)
        tri += len(mesh.faces)
    sc.export(path)
    print(f'{path.split("/")[-1]:26s} {len(parts):3d} parts {tri:6d} tris')

# ================================================================ DATE PALM
def palm_leaf(base, yaw, droop, L, crown_y):
    n = 14; t = np.linspace(0, 1, n)
    d = np.array([np.sin(yaw), 0, np.cos(yaw)])
    spine = base + np.outer(L*t, d)
    spine[:,1] = crown_y + 0.10*t - droop*t**2
    radii = 0.075*np.sin(np.pi*np.clip(t*0.92+0.08,0,1))**0.7 + 0.008
    return loft(spine, radii, wscale=1.5, vscale=0.28, flat=True)

def build_palm(fruit, path):
    P = []
    if fruit:
        seg = [(226,199,170,255)]*8; base_c = (238,226,197,255)
    else:
        seg = [((198,124,79,255) if i%2 else (232,186,126,255)) for i in range(8)]
        base_c = (235,197,133,255)
    P.append(('Base', cyl(0.48, 0.045, [0, 0.022, 0]), base_c))
    y, r = 0.10, 0.125
    for i in range(8):
        P.append((f'Trunk_{i}', ell(r, 0.085, r, [0, y, 0]), seg[i]))
        y += 0.135; r -= 0.006
    crown_y = y - 0.05
    leaf_c = (163,157,102,255)
    for k in range(9):
        yaw = k*2*np.pi/9 + 0.15
        droop = 0.42 if k%2 else 0.30
        L = 0.62 if k%2 else 0.55
        P.append((f'Leaf_{k}', palm_leaf(np.array([0,0,0.03]), yaw, droop, L, crown_y), leaf_c))
    for k in range(4):  # upright center leaves
        yaw = k*np.pi/2 + 0.6
        P.append((f'LeafTop_{k}', palm_leaf(np.array([0,0,0.0]), yaw, 0.10, 0.34, crown_y+0.06), leaf_c))
    if fruit:
        date_c = (205,152,74,255); stalk_c = (150,140,90,255)
        for ci, ang in enumerate([0.35, 1.35, -0.85]):
            bx, bz = 0.16*np.sin(ang), 0.16*np.cos(ang)
            top = np.array([bx, crown_y-0.02, bz])
            P.append((f'Stalk_{ci}', cap(top, top+[0, -0.16, 0.02], 0.012), stalk_c))
            for di in range(7):
                off = np.array([0.03*(-1)**di + 0.015*np.sin(di*2.1),
                                -0.03*di - 0.02, 0.02*np.cos(di*1.7)])
                P.append((f'Date_{ci}_{di}',
                          ell(0.030, 0.042, 0.030, top+off, subdiv=1, flat=True), date_c))
    export(P, path)

# ================================================================ LAMB
def build_lamb(path):
    P = []
    WOOL = (240,233,215,255); FACE = (164,94,70,255)
    HOOF = (130,70,55,255); EYE = (60,40,35,255)
    P.append(('Body', ell(0.30, 0.30, 0.28, [0, 0.52, 0]), WOOL))
    dirs = []
    ga = np.pi*(3-np.sqrt(5))
    for i in range(14):
        yy = 1 - 2*(i+0.5)/14
        rr = np.sqrt(1-yy*yy); th = ga*i
        dirs.append([rr*np.cos(th), yy, rr*np.sin(th)])
    for i, d in enumerate(dirs):
        d = np.array(d)
        c = np.array([0, 0.52, 0]) + d*0.24
        P.append((f'Wool_{i}', ell(0.135, 0.135, 0.13, c), WOOL))
    P.append(('Wool_Cap', ell(0.155, 0.11, 0.13, [0, 0.75, 0.20]), WOOL))
    P.append(('Face', ell(0.125, 0.165, 0.115, [0, 0.58, 0.29]), FACE))
    for s, nm in [(1,'L'),(-1,'R')]:
        e = ell(0.085, 0.045, 0.03, [0,0,0])
        e.apply_transform(trimesh.transformations.euler_matrix(0.2, 0, s*-0.5))
        e.apply_translation([s*0.15, 0.63, 0.25])
        P.append((f'Ear_{nm}', e, FACE))
        P.append((f'Eye_{nm}', ell(0.017,0.017,0.012,[s*0.052,0.63,0.395], subdiv=2), EYE))
    for s, z, nm in [(1,0.10,'FL'),(-1,0.10,'FR'),(1,-0.12,'BL'),(-1,-0.12,'BR')]:
        P.append((f'Leg_{nm}', cyl(0.045, 0.24, [s*0.085, 0.17, z], 16), FACE))
        P.append((f'Hoof_{nm}', cyl(0.048, 0.05, [s*0.085, 0.032, z], 16), HOOF))
    export(P, path)

# ================================================================ CAMEL
def build_camel(path):
    P = []
    BODY = (232,192,148,255); SADDLE = (211,124,90,255)
    GOLD = (200,172,106,255); HOOF = (169,152,100,255)
    EYE = (75,58,52,255); BASE = (186,170,134,255)
    P.append(('Base', cyl(0.55, 0.04, [0, 0.02, -0.05], 36), BASE))
    P.append(('Body', ell(0.20, 0.235, 0.38, [0, 0.70, -0.08]), BODY))
    P.append(('Hump', ell(0.15, 0.17, 0.19, [0, 0.90, -0.12]), BODY))
    P.append(('Saddle', ell(0.185, 0.155, 0.235, [0, 0.925, -0.12]), SADDLE))
    P.append(('Saddle_Trim', torus_xz(0.175, 0.225, 0.022, [0, 0.845, -0.12]), GOLD))
    # neck: S-curved loft
    sp = [[0,0.72,0.18],[0,0.82,0.28],[0,0.95,0.335],[0,1.07,0.36],[0,1.16,0.375]]
    P.append(('Neck', loft(sp, [0.135,0.115,0.10,0.09,0.088], ring_n=18), BODY))
    P.append(('Head', ell(0.10, 0.105, 0.145, [0, 1.21, 0.40]), BODY))
    P.append(('Muzzle', ell(0.075, 0.075, 0.095, [0, 1.185, 0.50]), BODY))
    for s, nm in [(1,'L'),(-1,'R')]:
        P.append((f'Ear_{nm}', ell(0.028,0.05,0.022,[s*0.088,1.29,0.36], subdiv=2), BODY))
        P.append((f'Eye_{nm}', ell(0.022,0.022,0.015,[s*0.078,1.235,0.455], subdiv=2), EYE))
    P.append(('Tail', cap([0,0.80,-0.44],[0.02,0.60,-0.50],0.022), BODY))
    P.append(('Tail_Tuft', ell(0.035,0.05,0.03,[0.02,0.575,-0.51], subdiv=2), HOOF))
    for s, z, nm in [(1,0.16,'FL'),(-1,0.16,'FR'),(1,-0.26,'BL'),(-1,-0.26,'BR')]:
        P.append((f'Leg_{nm}', cap([s*0.115, 0.60, z], [s*0.115, 0.10, z], 0.055), BODY))
        P.append((f'Hoof_{nm}', ell(0.062,0.055,0.082,[s*0.115,0.055,z+0.01]), HOOF))
    export(P, path)

# ================================================================ SECCADE
def build_seccade(path):
    P = []
    RUG=(144,141,90,255); CREAM=(241,232,207,255); GOLD=(211,171,88,255)
    PLANK=(198,110,70,255); SAND=(233,190,124,255); ROPE=(205,115,70,255)
    # ground + plank
    P.append(('Ground', cyl(0.85, 0.05, [0, 0.025, 0], 10), SAND))
    P.append(('Plank', box(1.5, 0.09, 0.42, [0.05, 0.10, 0]), PLANK))
    # ---- flat rug (built lying in XZ, then tilted like the reference) ----
    rug_parts = []
    rug_parts.append(('Rug', box(0.68, 0.035, 1.00, [0,0,0])))
    # cream frame
    fw = 0.045
    for name,(ex,ez,cx,cz) in {'F1':(0.50,fw,0,0.36),'F2':(0.50,fw,0,-0.36),
                               'F3':(fw,0.72+fw,-0.25,0),'F4':(fw,0.72+fw,0.25,0)}.items():
        rug_parts.append((f'Frame_{name}', box(ex,0.02,ez,[cx,0.027,cz])))
    # gold inner frame + arch point
    gold_parts = []
    gw = 0.03
    for name,(ex,ez,cx,cz) in {'G1':(0.36,gw,0,0.27),'G2':(0.36,gw,0,-0.27),
                               'G3':(gw,0.54,-0.18,0),'G4':(gw,0.54,0.18,0)}.items():
        gold_parts.append((f'Gold_{name}', box(ex,0.02,ez,[cx,0.045,cz])))
    for s in (1,-1):
        T = trimesh.transformations.rotation_matrix(s*0.55, [0,1,0])
        gold_parts.append((f'Arch_{"L" if s>0 else "R"}',
                           box(gw,0.02,0.16, [s*0.075,0.045,0.335], T)))
    # fringe
    fringe = []
    for zi, zz in [(0,0.545),(1,-0.545)]:
        for i in range(13):
            x = -0.30 + i*0.05
            fringe.append((f'Fringe_{zi}_{i}',
                cap([x,0.0,zz*0.96],[x+0.008*(-1)**i,0.0,zz+0.045*np.sign(zz)],0.011)))
    # tilt the whole rug assembly like the reference
    T = (trimesh.transformations.translation_matrix([-0.28, 0.53, 0]) @
         trimesh.transformations.rotation_matrix(0.30, [0,1,0]) @
         trimesh.transformations.rotation_matrix(-1.05, [1,0,0]))
    for name, m in rug_parts:
        m.apply_transform(T); P.append((name, m, RUG if name=='Rug' else CREAM))
    for name, m in gold_parts:
        m.apply_transform(T); P.append((name, m, GOLD))
    for name, m in fringe:
        m.apply_transform(T); P.append((name, m, CREAM))
    # ---- rolled mat ----
    RX, RY = 0.55, 0.145  # position on plank
    P.append(('Roll', cyl(0.095, 0.42, [RX, 0.355, 0], 24), RUG))
    P.append(('Roll_Spiral', torus_xz(0.055, 0.055, 0.016, [RX, 0.565, 0], 24), RUG))
    P.append(('Roll_Spiral2', torus_xz(0.022, 0.022, 0.012, [RX, 0.568, 0], 16), RUG))
    for i, yy in enumerate([0.46, 0.26]):
        P.append((f'Roll_Band_{i}', cyl(0.100, 0.045, [RX, yy, 0], 24), CREAM))
        P.append((f'Roll_Rope_{i}', torus_xz(0.102, 0.102, 0.012, [RX, yy-0.045, 0]), ROPE))
    lp = torus_xz(0.05, 0.05, 0.011, [RX+0.115, 0.36, 0.02], 20)
    lp.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [0,0,1],
                       point=[RX+0.115, 0.36, 0.02]))
    P.append(('Roll_Loop', lp, ROPE))
    export(P, path)

# ================================================================ MULBERRY
def build_mulberry(fruit, path):
    P = []
    OL1=(156,150,92,255); OL2=(170,163,100,255)
    TRUNK=(177,110,72,255); BASE=(232,186,126,255)
    BERRY=(94,62,110,255); STEM=(150,140,90,255)
    P.append(('Base', ell(0.50, 0.07, 0.42, [0, 0.03, 0])._slice_plane if False else
              ell(0.50, 0.075, 0.42, [0, 0.065, 0]), BASE))
    # trunk + branches (lofts)
    tr = [[0,0.0,0],[0.02,0.35,0],[-0.02,0.62,0.01],[0.0,0.85,0.0]]
    P.append(('Trunk', loft(tr, [0.11,0.095,0.085,0.075], ring_n=14), TRUNK))
    br = [([[0,0.62,0],[ -0.18,0.82,0.04],[-0.30,0.98,0.06]], [0.06,0.048,0.038], 'Branch_L'),
          ([[0,0.70,0],[ 0.18,0.90,-0.03],[0.32,1.02,-0.05]], [0.055,0.045,0.036], 'Branch_R'),
          ([[0,0.80,0],[ 0.06,1.00,0.10],[0.10,1.12,0.14]], [0.05,0.04,0.032], 'Branch_C')]
    for sp, rr, nm in br:
        P.append((nm, loft(sp, rr, ring_n=12), TRUNK))
    # faceted canopy blobs
    blobs = [(0,1.42,0,0.30),(-0.30,1.28,0.06,0.25),(0.32,1.26,-0.02,0.26),
             (-0.16,1.16,0.20,0.22),(0.16,1.14,0.22,0.21),(-0.42,1.10,-0.10,0.20),
             (0.44,1.08,-0.12,0.20),(0,1.24,-0.26,0.24),(-0.14,1.44,-0.14,0.20),
             (0.18,1.46,0.12,0.19)]
    canopy = []
    for i,(bx,by,bz,br_) in enumerate(blobs):
        col = OL1 if i%2 else OL2
        m = trimesh.creation.icosphere(subdivisions=1, radius=br_)
        m.apply_translation([bx,by,bz]); m.unmerge_vertices()
        P.append((f'Canopy_{i}', m, col))
        canopy.append((np.array([bx,by,bz]), br_))
    if fruit:
        bi = 0
        for c, r in canopy:
            for _ in range(2):
                d = rng.normal(size=3); d[1] = abs(d[1])*0.4 + d[1]*0.3
                d /= np.linalg.norm(d)
                if d[2] < -0.6: d[2] *= -1  # bias to visible sides
                pos = c + d*r*0.99
                b = trimesh.creation.icosphere(subdivisions=1, radius=0.035)
                b.apply_scale([1,1.35,1]); b.apply_translation(pos)
                b.unmerge_vertices()
                P.append((f'Berry_{bi}', b, BERRY))
                P.append((f'BerryStem_{bi}', cap(pos+[0,0.045,0], pos+[0,0.075,0], 0.008, 8), STEM))
                bi += 1
    export(P, path)

# ================================================================ RUN ALL
O = '/home/claude/'
build_palm(False, O+'date_palm_bare.glb')
build_palm(True,  O+'date_palm.glb')
build_lamb(O+'lamb.glb')
build_camel(O+'camel.glb')
build_seccade(O+'seccade.glb')
build_mulberry(False, O+'mulberry_tree_bare.glb')
build_mulberry(True,  O+'mulberry_tree.glb')

