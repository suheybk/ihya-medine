#!/usr/bin/env python3
"""Adlandırılmış ikonlardaki (icons/) KAPALI DELİK dama-tahtası kalıntılarını şeffaf yapar.
Dama-tahtası = yüksek-frekanslı alternasyon (176↔208). Düz-gölgeli gri ikon parçaları (hoparlör/kılıç) KORUNUR."""
import glob, numpy as np
from PIL import Image
from scipy import ndimage

for f in sorted(glob.glob('icons/*.png')):
    im = Image.open(f).convert('RGBA'); arr = np.asarray(im).astype(int)
    r,g,b,a = arr[...,0],arr[...,1],arr[...,2],arr[...,3]
    opaque = a>100
    bright = (r+g+b)/3.0; chroma = np.maximum(np.maximum(r,g),b)-np.minimum(np.minimum(r,g),b)
    gx=np.abs(np.diff(bright,axis=1,append=bright[:,-1:])); gy=np.abs(np.diff(bright,axis=0,append=bright[-1:,:]))
    alt=(gx>18)|(gy>18)
    seed = opaque & (chroma<=14) & (bright>=160) & (bright<=218) & alt   # dama-tahtası tohumu
    region = opaque & (chroma<=22) & (bright>=150) & (bright<=226)        # büyüme sınırı (gri-açık)
    if seed.sum()<8:
        continue   # dama-tahtası yok
    grown = ndimage.binary_propagation(seed, mask=region)                 # düz kare merkezlerini de kapsa
    grown = ndimage.binary_dilation(grown, iterations=1) & (opaque)       # 1px kenar temizliği
    if grown.sum()==0: continue
    na = a.copy(); na[grown]=0
    out = np.dstack([arr[...,0],arr[...,1],arr[...,2],na]).astype(np.uint8)
    Image.fromarray(out,'RGBA').save(f)
    print('temizlendi', f.split('/')[-1], int(grown.sum()),'px')
print('bitti')
