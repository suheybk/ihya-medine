/* İhya — Service Worker
 * AMAÇ: kullanıcı deploy sonrası HER ZAMAN en son sürümü görsün (eski cache derdi biter),
 *       ama internet yokken de oyun açılsın (offline).
 * STRATEJİ:
 *   - HTML (oyun sayfaları): NETWORK-FIRST → online ise taze indir, offline ise cache'ten ver.
 *     Böylece bozuk/eski bir cache ONLINE'da ASLA kalıcı olmaz; her açılış kendini iyileştirir.
 *   - Diğer varlıklar (three.js CDN, modeller, ikonlar): CACHE-FIRST → hızlı + offline.
 * SÜRÜM ARTIR: yeni deploy'da CACHE adını (v###) artır → activate eski cache'leri siler.
 * ACİL KAPATMA: bu dosyayı, içinde sadece
 *     self.addEventListener('install',()=>self.skipWaiting());
 *     self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(k=>Promise.all(k.map(x=>caches.delete(x)))).then(()=>self.registration.unregister())));
 *   olacak şekilde deploy et → tüm cache temizlenir, SW kendini kaldırır.
 */
const CACHE = 'ihya-v1200';

self.addEventListener('install', (e) => {
  // Yeni SW'yi beklemeye almadan hemen etkinleştir → kullanıcı takılıp kalmaz
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil((async () => {
    // eski sürüm cache'lerini temizle
    const keys = await caches.keys();
    await Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)));
    await self.clients.claim();   // açık sayfaları hemen kontrol et
  })());
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;                 // yalnız GET'i yönet
  let url;
  try { url = new URL(req.url); } catch (_) { return; }
  const sameOrigin = url.origin === self.location.origin;
  const isHTML = req.mode === 'navigate' ||
                 url.pathname.endsWith('.html') ||
                 url.pathname.endsWith('/');

  // ---- HTML → NETWORK-FIRST (online'da her zaman taze) ----
  if (sameOrigin && isHTML) {
    e.respondWith((async () => {
      try {
        const fresh = await fetch(req, { cache: 'no-store' });  // HTTP cache'i atla, gerçekten taze
        if (fresh && fresh.ok) {
          const cache = await caches.open(CACHE);
          cache.put(req, fresh.clone());                        // offline için sakla
        }
        return fresh;
      } catch (err) {
        // internet yok → cache'ten ver (tam eşleşme yoksa oyun sayfasına düş)
        const cached = await caches.match(req);
        return cached
            || await caches.match('ihya3d.html')
            || await caches.match('./ihya3d.html')
            || Response.error();
      }
    })());
    return;
  }

  // ---- Diğer (models/*.glb, three.js CDN, ikon, manifest) → CACHE-FIRST (offline + hız) ----
  e.respondWith((async () => {
    const cached = await caches.match(req);
    if (cached) return cached;
    try {
      const resp = await fetch(req);
      // yalnız sağlıklı yanıtları sakla (opak/hatalıyı değil)
      if (resp && resp.ok && (resp.type === 'basic' || resp.type === 'cors')) {
        const cache = await caches.open(CACHE);
        cache.put(req, resp.clone());
      }
      return resp;
    } catch (err) {
      return cached || Response.error();
    }
  })());
});
