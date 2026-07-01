# İhya — Evden Dünyaya

Mobil tarayıcıda **indirmeden** oynanan, 3D İslami "ihyâ" oyunu. Kendi nefsinden başlayarak
hâneyi, bahçeyi, mahalleyi, camiyi ve şehri Allah'ın rızâsıyla ihyâ etme şuurunu oyunlaştırır.
Her görevde âyet/hadis delili vardır.

> **Gayret bizden, tevfîk Allah'tandır.**

## Oynanış
- 🕹️ Sanal joystick (mobil) / WASD (masaüstü) ile yürüyen karakter
- ➡️ Soldan sağa doğrusal ada zinciri: **Hâne → Bahçe → Mahalle → Cami → Şehir**
- 📿 Günlük ibadet sırası (tuvalet âdâbı → abdest → namaz → Kur'an → dua)
- 🔒 Kilit/fetih: bir ada tamamlanmadan sonraki açılmaz (kilitli adalar silik + sisli)
- ✨ "Ölü → diri": tamamlanan nesne griden renge döner; ada fethedilince kutlama
- 🌅 Gün/gece döngüsü ve vakit göstergesi (Kur'an 10:5)
- 🔊 Web Audio ile sentezlenmiş ses (çınlama, fanfar, ambient)
- 🔁 Günlük görev sıfırlama (fetihler kalıcı kalır)
- 🏁 Bitiş ekranı (niyet, dua, künye)

## Dosyalar
- **`ihya3d.html`** — 3D joystick sürümü (ana oyun). Tek dosya; modeller base64 gömülü,
  klasörden çift tıkla açılır. Three.js CDN'den yüklenir (internet gerekir).
- `ihya.html` — ilk 3D dokun-tabanlı sürüm (sabit kamera).
- `models/` — düşük poligon `.glb` modeller (Blender), referans görseller (`1–11.jpg`),
  gömülü model verileri (`embedded_*.js`).
- `ihya_world.blend` — Blender kaynak dosyası.

## Çalıştırma
`ihya3d.html`'i tarayıcıda aç (çift tık ya da bir statik sunucu). Joystick'e dokununca ses başlar.

## Teknoloji
Three.js (WebGL), tek dosya HTML, düşük poligon claymorphism modeller (Blender), Web Audio.

---
İletişim: suheybk@gmail.com
