# 3D Model Prompt Listesi — İhya / Medine

Bu promptlar mevcut oyunun **claymorphism low-poly** stiline (Blender `ihya_world.blend`,
`models/*.glb`) uyacak şekilde yazıldı. Text-to-3D araçlarına (Meshy, Tripo, Rodin, Luma)
ya da referans görsel üretip Blender'da modellemek için kullanılabilir.

---

## 🎨 ORTAK STİL (her prompta ekle)
> **Style:** cute low-poly *claymorphism*, soft rounded beveled edges, smooth "clay finisher"
> look, matte surfaces, gentle warm lighting, friendly toy-like proportions. Flat-shade
> foliage/cloth/domes; smooth-shade bodies. Low triangle count (~60–200 tris). Solid vertex
> colors or simple materials, **no textures/text/logos**. Neutral A-pose, facing +Z.
> **Technical:** single object, origin at **base center (feet on ground)**, **Y-up**, real-world
> scale ~**1 m** tall unless noted, clean manifold mesh, export **GLB** (Draco'suz).
> **Palette:** warm sand, terracotta, olive-green, cream, muted gold — Medine/çöl-vaha hissi.

> **Adlandırma:** dosyaları koddaki `MODELS` dizisine uygun kısa isimle ver
> (ör. `sheep.glb`, `date_palm.glb`). Aşağıda her modelin önerilen dosya adı verildi.

---

## 🐑 1) Hayvanlar (çobanlık + random spawn)
Not: Hareket için gövde tek parça yeter; ama **bacaklar ayrı node** olursa (player gibi:
`legFL/legFR/legBL/legBR`) yürüme animasyonu yapabiliriz — mümkünse ayır.

1. **`sheep.glb` — Koyun**: fluffy woolly sheep, cream/off-white rounded wool body (bumpy
   low-poly wool), small dark face, tiny legs, stubby. Very cute, ~0.7 m.
2. **`goat.glb` — Keçi**: small tan/brown goat, little curved horns, short beard, slim legs,
   alert pose. ~0.7 m.
3. **`camel.glb` — Deve**: friendly one-hump (dromedary) camel, sandy-beige, long neck, calm
   expression, saddle blanket optional (muted red). ~1.8 m tall.
4. **`lamb.glb` — Kuzu** (opsiyonel): tiny baby version of sheep, softer, ~0.4 m.
5. **`chicken.glb` — Tavuk** (opsiyonel): little rounded hen, cream+red comb. ~0.35 m.

## 🌴 2) Meyve Ağaçları & Bitkiler (hasat/tekrarlanan iş)
1. **`date_palm.glb` — Hurma ağacı**: tall date palm, textured beige trunk (stacked ring
   segments), radial fan of flat-shaded green fronds at top, **clusters of golden-brown dates**
   hanging under the crown. Iconic Medine tree. ~3 m.
2. **`date_palm_bare.glb` — Hurma ağacı (hasat edilmiş)**: same palm **without date clusters**
   (topladıktan sonraki hali; tekrar büyüme için). ~3 m.
3. **`mulberry_tree.glb` — Dut ağacı**: rounded leafy tree, olive/green flat-shaded canopy
   clumps, brown trunk, **small dark-purple mulberries** dotting the canopy. ~2 m.
4. **`mulberry_tree_bare.glb` — Dut ağacı (toplanmış)**: same tree, berries removed. ~2 m.
5. **`wheat.glb` — Ekin/buğday demeti**: small golden wheat cluster/sheaf tuft on soil. ~0.5 m.
6. **`date_cluster.glb` — Hurma salkımı** (pickup): standalone hanging cluster of dates.

## 🛒 3) Medine Pazarı (Sûk)
1. **`market_stall.glb` — Pazar tezgâhı**: simple wooden market stall with striped cloth awning
   (muted red/cream), a flat counter, a couple of goods baskets on top. ~2 m.
2. **`basket.glb` — Sepet**: round woven basket (tan), optionally filled with dates/fruit. ~0.4 m.
3. **`sack.glb` — Çuval**: tied burlap grain sack, beige, slightly slumped. ~0.5 m.
4. **`scale.glb` — Terazi**: classic two-pan balance scale (muted gold/bronze) on a small
   stand — ticaret/ölçü sembolü. ~0.6 m.
5. **`jar.glb` — Testi/küp**: clay amphora/water jug, terracotta, rounded. ~0.6 m.
6. **`rug_market.glb` — Sergi kilimi** (opsiyonel): small patterned flat rug for goods display.

## 🏛️ 4) Yapılar
1. **`masjid_nabawi.glb` — Mescid-i Nebevî (sade)**: humble early mosque — **mud-brick (kerpiç)
   low walls**, **palm-trunk columns**, palm-frond flat roof, small open courtyard, NO minaret,
   NO dome (tarihe sadık, mütevazı). Warm sand tones. ~3–4 m wide. *(Mevcut `mosque.glb`'nin
   yerini alacak — daha sahih.)*
2. **`well.glb` — Kuyu**: round stone well with a small wooden frame/pulley and a bucket.
   Medine kuyuları. ~1.2 m.
3. **`suffa.glb` — Suffa (gölgelik)**: shaded low platform/bench with palm-frond canopy on
   simple posts (Ashâb-ı Suffa için). ~2 m.
4. **`tent.glb` — Çadır**: bedouin/muhâcir tent, muted striped cloth, open front. ~2 m.
5. **`palm_fence.glb` — Hurma bahçesi çiti** (opsiyonel): low woven palm-frond fence segment.

## 🧍 5) NPC Karakterler
Stil: mevcut `player.glb` ile aynı sadelik (yuvarlak, sevimli, low-poly). **Animasyon için
uzuvları ayrı node yap** (player'daki gibi `legL/legR/armL/armR/upper`).
1. **`orphan.glb` — Yetim çocuk**: small child, simple modest tunic (cream/earth tone), gentle
   sad-but-hopeful posture. ~0.7 m.
2. **`neighbor.glb` — Komşu / Ensâr**: adult in simple robe (olive/earth), welcoming pose. ~1 m.
3. **`merchant.glb` — Tüccar**: adult in slightly nicer robe + head wrap, standing behind
   goods. ~1 m.
4. **`shepherd.glb` — Çoban**: adult with a simple staff (asâ), earth-tone robe. ~1 m.
5. **`traveler.glb` — Muhâcir**: adult with a small shoulder bundle/bag, road-worn robe. ~1 m.

## 🎒 6) Toplanabilir Eşyalar & Envanter (pickup/ikon)
Küçük, tek nesne, zeminde/elde durabilir; envanterde ikon olarak da kullanılabilir.
1. **`item_date.glb` — Hurma**: a few golden-brown dates / small pile.
2. **`item_mulberry.glb` — Dut**: cluster of dark-purple mulberries.
3. **`item_milk.glb` — Süt testisi**: small clay jug with milk.
4. **`item_wool.glb` — Yün**: soft cream wool tuft/ball.
5. **`item_bread.glb` — Ekmek**: round flatbread / small loaf.
6. **`item_waterskin.glb` — Su kırbası**: leather waterskin.
7. **`seccade.glb` — Seccade**: rolled-up prayer rug **and/or** unrolled version (envanterden
   çıkarıp serme fikri için ideali: iki hali — `seccade_rolled` / `seccade_open`). Muted
   red/green with simple mihrab motif (no text). ~1.1 m açıkken.
8. **`item_coin.glb` — Dirhem/kese**: small coin purse or a few silver coins (dirhem).

---

## 📦 Öncelik Sırası (önce bunlar lazım)
1. `sheep.glb`, `camel.glb`, `goat.glb` (çobanlık)
2. `date_palm.glb` (+bare), `mulberry_tree.glb` (+bare) (hasat/tekrarlanan)
3. `item_date.glb`, `item_mulberry.glb`, `item_bread.glb` (envanter/pickup)
4. `market_stall.glb`, `basket.glb`, `scale.glb` (pazar)
5. `orphan.glb`, `neighbor.glb`, `merchant.glb` (NPC)
6. `seccade.glb`, `well.glb`, `masjid_nabawi.glb`

> Modeller hazır olunca `models/` klasörüne koy; ben `MODELS` dizisine ekleyip (base64 gömme
> dahil) mekaniği kodlayacağım. Gömme için `scratchpad/inline_world.py` akışını kullanırız.

---

## 🆕 Faz 11.27 — Senaryo modelleri (barıştırma + 4 etkinlik)
> Aşağıdaki senaryoların TASARIMI `YAPILACAKLAR.md` Faz 11.27'de. Bu modeller gelince kodlanacak.
> Karakterler diğer NPC'lerle aynı reçete: `Pant_L/R+Shoe/Sole`, `Sleeve_L/R+Hand`, yüz +Z, `lin()`
> renk; mesh adları `<model>_1..6` (1=cübbe, 2=ten, 3=başörtü, 4=koyu aksan). Ortak stil yukarıda.

### 🕊️ Barıştırma (hayra davet — iki kişiyi sulh et)
1. **`arg_villager_a.glb` — Tartışan köylü A**: standing villager, **agitated/angry pose** — one arm
   raised/pointing forward, torso leaning in, brows down. Warm tunic (terracotta). ~1.7 m, facing +Z.
2. **`arg_villager_b.glb` — Tartışan köylü B**: facing counterpart, **defensive/upset pose** — arms
   crossed or one hand up "stop", head turned slightly away. Olive/indigo tunic. ~1.7 m, facing +Z.
   > İkisi birbirine dönük yerleştirilecek; oyuncu araya girince "sulh" pozuna (eller açık, sakin)
   > geçiş kodda yapılabilir — ama istersen **`reconciled_pair.glb`** (el sıkışan/kucaklaşan ikili)
   > ayrı model olarak da verebilirsin (sulh sonrası swap).
3. **`dispute_item.glb`** (opsiyonel): anlaşmazlık konusu — yere düşmüş bir çuval/testi ya da sınır
   taşı (üzerinde kavga edilen mal). ~0.4 m.

### ⚖️ Adil ol, hakkı savun
4. **`qadi.glb` — Kadı/hakem**: dignified seated or standing judge figure, longer robe, calm face,
   maybe a small scale in hand or beside. Muted green/gold. ~1.8 m. (Adalet meclisi için.)
5. **`plaintiff.glb` / `defendant.glb`** (ops.): iki davacı figürü — biri şikâyetçi (elini uzatan),
   biri savunan. `arg_villager_a/b` yeniden kullanılabilir; ayrı istersen bunlar.

### 🤝 Topluma faydalı bir iş yap
6. **`public_fountain.glb` — Halk çeşmesi (sebil)**: small stone public fountain/sebil with a basin
   and spout, water trickling. Warm sandstone. ~1.3 m. (İnşa edilebilir hayır — sadaka-i câriye.)
7. **`shade_bench.glb` — Gölgelik/oturak**: simple palm-thatch shade over a low stone bench (yolcular
   dinlensin). ~2 m. (Alternatif faydalı iş.)

### 📿 Emaneti yerine ulaştır
8. **`trust_pouch.glb` — Emanet kesesi**: sealed cloth pouch / small tied bundle (emanet mal), a bit
   heavier/fuller than `item_coin`. Neutral linen with a wax seal knot. ~0.3 m. (Bir NPC'den alıp
   diğerine götürme görevi — taşıma sırasında elde görünebilir.)
9. **`trust_owner.glb`** (ops.): emaneti bekleyen sahibi — mevcut `traveler.glb`/`neighbor.glb`
   yeniden kullanılabilir; ayrı istersen bekleyen, minnettar poz.

### 🤲 Bir sadaka ver (dilenci)
10. **`beggar.glb` — Dilenci/muhtaç**: humble seated figure by a wall, worn simple robe (muted grey-
    brown), cupped hands or a small bowl in front, gentle downcast face — **not caricatured**,
    dignified. ~1.2 m seated. (Huzur sistemindeki `dilenci1` için görünür NPC; şu an ses/mekanik
    var, model yok. Sadaka verilince minnet pozu/toast.)
12. **`mud_doorway.glb` — Kerpiç kapı/perde (taharet)**: small Medina-style **mud-brick doorway** —
    a low sandstone/adobe arched frame with a simple wooden or cloth privacy screen, warm terracotta.
    Replaces the current generic red `door` model (torii-like, out of place) used by *Tuvalet âdâbı*.
    ~1.8 m. (İstersen tek `mud_doorway.glb` ver, ben `taharet` node'unun modelini onunla değiştiririm.)
### 🆕 Faz 11.29 — İyileştirme promptları (mevcut prosedürel modellerin yerine)
> Bunlar `build_pack5.py` stiliyle (prosedürel low-poly claymorphism, +Z önlü, origin taban-merkez, `lin()` renk,
> Draco'suz GLB) uyumlu. İstersen aynı .py toolkit'ine fonksiyon olarak ekle ve `models/` klasörüne bas — ben
> kodda `tpl` üstünden değiştiririm.

**A) `seated_sahabe.glb` — İlim meclisinde oturan sahabe** (huni+top-takke yerine):
> Dignified low-poly seated companion (Sahabi), **cross-legged (bağdaş)**, sitting upright. Full-length warm
> robe (jubba) draping over the crossed legs; a simple sash at the waist. Head with a **wrapped turban / keffiye**
> (soft rounded cloth, not a ball), gentle calm face (two dot eyes, small nose, faint serene mouth), short beard
> optional. **Hands resting on the knees** (palms down). Origin at seated base center, faces **+Z**. ~0.9 m tall
> seated. Warm palette (olive/cream/terracotta robe, cream turban). Give each part a distinct mesh name
> (Robe/Legs/Head/Turban/Hand_L/Hand_R) so I can tint variants. Hepsi AYNI model — kodda 6'sı çembere dizilip
> merkeze döndürülür + robe/turban renkleri per-kişi değiştirilir. (Not: mevcut `beggar.glb` oturuşuna benzer
> ama dik, üzgün değil sakin, elleri dizde — kucakta kâse yok.)

**B) `hive.glb` — Arı kovanı = PETEK** (piramit/skep değil, HONEYCOMB):
> Low-poly beehive shaped like a **honeycomb**: a cluster of **hexagonal-prism cells** (bal peteği) packed
> together into a rounded slab/disk, golden-amber wax color with slightly darker cell rims; a few filled cells
> glossy honey. Optional: 2-3 tiny stylized bees hovering. NOT a stacked cone/pyramid skep. ~0.5 m. Origin base
> center, matte finish, warm gold palette. (Mevcut prosedürel `buildHiveTemplate` skep'in yerine geçecek —
> `hive.glb` verirsen kodda onu kullanırım.)

**C) Eksik / faydalı ek promptlar:**
- **`kaaba.glb`** (opsiyonel, daha detaylı Kâbe): black cube with the **gold embroidered kiswa band (hizam)**,
  a hint of the door in gold, subtle fabric folds. ~2.6 m. (Şu an prosedürel kutu+bant; istersen değiştiririm.)
- **`vortex_swirl.glb`** (opsiyonel — Umre girdabı görseli): a translucent **spiral funnel / whirlpool** of
  concentric swirling rings narrowing downward, sandy-gold with faint motion streaks. ~2 m çap. (Karakter buna
  kapılır; şu an girdap yalnız hareketle anlatılıyor, görsel huni eklersek daha güçlü olur.)
- **`rooster.glb` / `chicken.glb`** (ayrı, opsiyonel): kümesin dışında dolaşan tekil tavuk/horoz (ses zaten var).
- **`mescid_nabawi.glb`**: Mescid-i Nebevî — green dome (Kubbetü'l-Hadrâ) + minarets + arched courtyard;
  jenerik `mosque` yerine. ~büyük yapı.

11. **`coop.glb` — Kümes (tavuk/horoz)**: small low-poly chicken coop — wooden hut + little fenced
    run, a couple of cream hens + one rooster (red comb) pecking. ~1.2 m. (Hâne adasındaki `FARMYARD`
    ses kümesine görsel; tavuk/horoz sesleri hazır, sadece görsel eksik. İstersen tek `chicken.glb` +
    `rooster.glb` ayrı da olur, ben yerleştiririm.)

---

## 🔨 12) ATÖLYE ADASI — craft istasyonları (Faz 3.5)
Bu üç model **Atölye adasındaki** üretim istasyonları. Kodda `mill/oven/loom` isimleriyle bekleniyor:
GLB'lerini `models/mill.glb`, `models/oven.glb`, `models/loom.glb` olarak verirsen otomatik devreye
girer (yoksa şu an prosedürel placeholder çiziliyor). Origin **taban-merkez, Y-up**, ~1–1.3 m, +Z önlü.

1. **`mill.glb` — Değirmen (el değirmeni)**: rustic hand-operated stone grain mill (Ortaçağ çöl/vaha
   tarzı). Tapered round **stone base** (muted gray), a thick round **millstone disc** on top, a small
   wooden **crank handle** sticking out to the side, a little **flour sack** (cream) leaning at the base
   and a **spilled flour pile** (off-white) in front. Warm, toy-like, claymorphism. ~1.3 m.
2. **`oven.glb` — Tandır (kerpiç fırın)**: traditional clay **tandoor/bread oven** — terracotta clay
   **dome** on a short cylindrical base, a dark arched **fire-mouth** at front (subtle warm ember glow),
   a small **chimney** on top, and a round **bread loaf** (golden) resting beside it. Warm terracotta +
   sand palette, soft rounded clay finish. ~1.2 m.
3. **`loom.glb` — Tezgâh (dokuma tezgâhı / seccade)**: upright wooden **weaving loom** — two vertical
   posts + top & bottom beams, taut vertical **warp threads** (cream), and a **half-woven prayer rug**
   in progress with a few colored horizontal stripes (muted gold, cream, olive-green — Medine kilim
   deseni). Wooden frame warm brown. ~1.5 m tall.

> İleride aynı adaya eklenebilecek istasyonlar (şimdilik gerekmez): `cauldron.glb` (pekmez kazanı —
> dut/bal→pekmez), `brickmold.glb` (kerpiç kalıbı — su+balçık→kerpiç). İstersen bunların da promptunu veririm.

---

## 🎣 13) İLERİDE — Gölet & Balık (plan, henüz yapılmadı)
Kullanıcı isteği: ufak bir **gölet** kurup **balık tutmak**. İleride yapılacak. Gerekebilecek modeller:
- **`pond.glb` — Gölet**: small round low-poly pond — soft blue water disc + reed/cattail tufts + a few
  rocks + lily pads around the rim. Calm, toy-like. ~2 m çap.
- **`fish.glb` — Balık** (opsiyonel): tiny cute fish (silver/orange), for a caught-fish pickup icon/pop.
- **`rod.glb` — Olta** (opsiyonel): simple wooden fishing rod + line; ya da oyuncu eline prosedürel çubuk.

**Mekanik fikri:** göletin kenarında "Balık tut" etkileşimi → kısa bekleme/olta animasyonu → `balik` (fish)
ürünü (FOOD, pazarda değerli). Craft: balık → (tandırda) "balık ızgara/kızartma" ya da doğrudan muhtaca ikram.
Atölye/Hâne yakınına küçük bir gölet dekoru; ya da yeni küçük bir "Gölet" side-alanı.
