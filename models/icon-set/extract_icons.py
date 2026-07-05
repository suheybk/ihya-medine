#!/usr/bin/env python3
"""İhya ikon sayfalarını (JPG, dama-tahtası arka plan) tek tek şeffaf PNG'ye çıkarır.
Dama-tahtası nötr gri (176/208) → kenardan flood-fill ile keylenir; ızgaraya göre kesilir."""
import os, numpy as np
from PIL import Image
from scipy import ndimage

SRC = 'models/icon-set'
OUT = 'icons'
os.makedirs(OUT, exist_ok=True)

# Sayfa düzenleri: (dosya, cols, rows, labeled, [isimler satır-satır; None=atla])
# labeled=True → hücrede alt etiket bandı var (kırpılır); False → etiketsiz (tam hücre).
SHEETS = [
    ('Durum Arayuz', 7, 4, True, [
        'check','lock','unlock','streak','nur','sparkle',None,     # 2. sparkle dup atla
        'arrow','exam','warn','mood_sad','mood_happy','zulm',None, # 2. zulm dup atla
        'sound_on','sound_off','market','bag','toilet','door',None,# 2. door dup atla
        'wudu','fountain','city','strength','ear','nose',None,
    ]),
    ('İbadet', 6, 3, True, [
        'mosque','kaaba','pray_sit','ruku','dua','quran',
        'book_closed','tesbih','ihram','selam','qibla','tiras',
        'vakit_clock','hourglass',None,None,None,None,
    ]),
    # Öncelik: etiketsiz 8×6. Yinelenenler (check/lock/mosque/... Durum+İbadet'te var) atlanır;
    # yalnız YENİ ikonlar çıkarılır (senaryo + tabiat + hayır). Tabiat Hasat sayfası kullanıcı kararıyla ATLANDI.
    ('Oncelik', 8, 6, False, [
        None,None,None,None,None,None,None,None,                              # R1 dup: check/lock/sparkle/nur/arrow/warn/streak/streak
        None,None,None,None,None,None,None,None,                              # R2 dup: mosque/pray_sit/dua/quran/quran/kaaba/qibla/qibla
        'moon','sun','sunrise','dirhem',None,None,None,'traveler_bag',        # R3: (market/bag dup, cap belirsiz atla)
        'water','bread','milk','wool','sheep','date_palm',None,'flower',      # R4: (col7 belirsiz atla)
        'brotherhood','justice','sadaka','trust_key','invite','peace','benefit','camel',  # R5: SENARYO ikonları
        'plant','tent','tree',None,None,None,None,None,                       # R6: (frond/kule/deve belirsiz atla)
    ]),
]

def keyout(arr):
    """RGB arr → alpha mask (True=opak). Dama-tahtası (nötr gri, açık) kenardan flood-fill."""
    r,g,b = arr[...,0].astype(int), arr[...,1].astype(int), arr[...,2].astype(int)
    mx = np.maximum(np.maximum(r,g),b); mn = np.minimum(np.minimum(r,g),b)
    neutral = (mx-mn) <= 26                 # gri (R≈G≈B)
    light   = ((r+g+b)/3) >= 150            # dama-tahtası aydınlığı
    bgcand  = neutral & light
    lbl,n = ndimage.label(bgcand)
    bright = (r+g+b)/3.0
    border = set(lbl[0,:]) | set(lbl[-1,:]) | set(lbl[:,0]) | set(lbl[:,-1])
    border.discard(0)
    bgids = set(border)
    # KAPALI DELİKLER (kilit sapı, tesbih halkası): kenara değmeyen ama İÇİNDE dama-tahtası olan bileşenler.
    # Dama-tahtası = yüksek-frekanslı alternasyon (kare kenarlarında ani 176↔208 sıçraması). Düz-gölgeli gri
    # ikon parçaları (makas bıçağı, gri kılıç) YUMUŞAK gradyandır → alternasyon düşük → KORUNUR.
    if n>0:
        gx=np.abs(np.diff(bright,axis=1,append=bright[:,-1:])); gy=np.abs(np.diff(bright,axis=0,append=bright[-1:,:]))
        alt=((gx>18)|(gy>18)).astype(float)
        fr = ndimage.mean(alt, lbl, range(1,n+1))
        chroma=(mx-mn).astype(float)
        chrm = ndimage.mean(chroma, lbl, range(1,n+1))
        brm  = ndimage.mean(bright, lbl, range(1,n+1))
        for i in range(n):
            # dama-tahtası: ya alternasyonlu (f>0.07) YA DA tek-tonlu ama çok-nötr (chroma<=6) VE dama parlaklığında
            # (165-215) → beyaz ihram (~250) ve sıcak krem kâğıt (chroma~25) korunur
            if fr[i]>0.07 or (chrm[i]<=6 and 165<=brm[i]<=215): bgids.add(i+1)
    bg = np.isin(lbl, list(bgids))
    bg = ndimage.binary_dilation(bg, iterations=1)   # 1px kenar püskülünü temizle
    return ~bg

def autocrop_and_save(cell_rgb, name):
    alpha = keyout(cell_rgb)
    if alpha.sum() < 200:   # boş hücre
        return False
    # küçük metin/parazit lekelerini at (hücre zaten etiket bandı olmadan kırpıldı); ikon parçaları >=40px kalır
    lbl,n = ndimage.label(alpha)
    if n>0:
        sizes = ndimage.sum(alpha, lbl, range(1,n+1))
        keep = [i+1 for i,sz in enumerate(sizes) if sz>=40]
        if keep: alpha = np.isin(lbl, keep)
    ys,xs = np.where(alpha)
    y0,y1,x0,x1 = ys.min(),ys.max()+1, xs.min(),xs.max()+1
    rgb = cell_rgb[y0:y1, x0:x1]
    a   = (alpha[y0:y1, x0:x1]*255).astype(np.uint8)
    rgba = np.dstack([rgb, a])
    im = Image.fromarray(rgba, 'RGBA')
    # kareye ortala (%10 boşluk)
    w,h = im.size; s = int(max(w,h)*1.18)
    canvas = Image.new('RGBA',(s,s),(0,0,0,0))
    canvas.paste(im, ((s-w)//2,(s-h)//2), im)
    canvas = canvas.resize((256,256), Image.LANCZOS)
    canvas.save(os.path.join(OUT, name+'.png'))
    return True

total=0
for fname, cols, rows, labeled, names in SHEETS:
    im = Image.open(os.path.join(SRC, fname+'.jpg')).convert('RGB')
    W,H = im.size; arr = np.asarray(im)
    cw, ch = W//cols, H//rows
    # etiketli sayfa: üst %7 (üst satır sızması) + alt %18 (kendi etiketi) kırp. Etiketsiz: sadece ince kenar payı.
    top_m, bot_m = (int(ch*0.07), int(ch*0.82)) if labeled else (int(ch*0.03), int(ch*0.97))
    for idx,name in enumerate(names):
        if name is None: continue
        r,c = divmod(idx, cols)
        cell = arr[r*ch+top_m : r*ch+bot_m, c*cw:(c+1)*cw]
        if autocrop_and_save(cell, name):
            total+=1; print('  ✓', name)
        else:
            print('  ∅ boş:', name)
print('Toplam:', total, 'ikon →', OUT)
