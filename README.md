# İhya — Evden Dünyaya

> 🎮 **Hemen oyna:** https://suheybk.github.io/ihya-oyun/
> 🏁 **Bölüm 1** (git etiketi `bolum-1`): 5 ada, imtihan meydanı, çobanlık/hasat,
> zekât, seccade, gün/Cuma. Bitirince **"İhya Etmeye Devam Et"** → yaş/cinsiyet
> profiline göre **kişiselleştirilmiş** (mükellefiyete uygun) devam.

Mobil tarayıcıda **indirmeden** oynanan, 3D İslami "ihyâ" oyunu. Kendi nefsinden başlayarak
hâneyi, bahçeyi, mahalleyi, camiyi ve şehri Allah'ın rızâsıyla ihyâ etme şuurunu oyunlaştırır.
Her görevde âyet/hadis delili vardır.

> **Gayret bizden, tevfîk Allah'tandır.**

## Oynanış
- 🕹️ Sanal joystick (mobil) / WASD (masaüstü) ile yürüyen karakter
- ➡️ Soldan sağa doğrusal ada zinciri: **Hâne → Bahçe → Mahalle → Cami → Şehir**
- 📿 Hâne'de SABİT günlük müfredat (tuvalet âdâbı → abdest → namaz → Kur'an → dua);
  vakit değişince dersler **silinmez**, sadece "namaz" dersi o vaktin namazına göre güncellenir
- 📖 **Adım adım öğretim**: abdest (10 adım) ve namaz (9 adım) ilk kez yapılırken fıkhen
  sıralı rehber açılır (niyet, kıble, farzlar işaretli); öğrenilince kısa moda geçer,
  "Adımları göster" ile tekrar izlenir
- 📝 **İmtihan Meydanı**: her adanın sonunda, öğrenilenlerden çoktan seçmeli sınav
  (🕌 Hadis Okulu / ⚖️ Fıkıh Okulu). Dersler meydanı açar; **sınavı geçmek adayı fetheder**
- ↺ Sınavı geçemezsen "Tekrar Dene" ya da "Dersleri Tekrar Et" (dersler sıfırlanır, baştan öğrenilir)
- 🔒 Kilit/fetih: bir ada sınavla fethedilmeden sonraki açılmaz (kilitli adalar silik + sisli)
- ✨ "Ölü → diri": tamamlanan nesne griden renge döner; ada fethedilince kutlama
- ⏳ **Namaz vakti çıkıyor uyarısı**: farz vaktin son diliminde namaz kılınmamışsa
  uyarı (vakit göstergesi kırmızı yanıp söner + toast/banner + uyarı tonu)
- 🌅 Gün/gece döngüsü ve **semâ saati** HUD: güneş/ay gökyüzü kavsinde doğar-batar
  (doğu→zirve→batı), gökyüzü rengi + yıldızlar + ufuk canlı değişir, altında vakit adı (Kur'an 10:5)
- 🌌 Atmosfer: gece **yıldızlar** + adaların üzerinde salınan **nûr zerreleri**,
  gündüz güneşte süzülen **nûr tozları** (gün/gece'ye göre belirir-solar)
- 🔊 Web Audio ile sentezlenmiş ses: görev çınlaması, fetih fanfarı, **vakit girince
  tefekkür tınısı** (Hicaz motifi), gün/gece ambient (gündüz kuş, gece cırcır böceği),
  HUD'da **ses aç/kapat** düğmesi (tercih kalıcı)
- 🔁 Günlük görev sıfırlama (fetihler kalıcı kalır)
- 📿 **İstikamet zinciri (streak)**: ardışık günlerde Hâne ibadetini tamamlama sayacı
  (🔥, kaçırınca sıfırlanır, bonus nûr) + 🌟 **nûr rütbeleri** (Niyet → … → İhyâ Ustası)
- 🤲 **Hayır Çeşmesi**: nûrunu sadaka-i câriyeye dönüştür (ağaç diktir, kandil yaktır,
  çeşme yaptır, mushaf vakfet — her biri sahih delille); dünya kalıcı güzelleşir,
  kandiller geceleyin yanar
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
