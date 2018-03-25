const cacheName = 'bhagavadgita';

const staticAssets = [
  './',
  '/static/styles/app.css',
  '/static/webassets-external/e2004f5e6d9cac08c7960d53c9848148_bootstrap.min.css',
  '/static/webassets-external/f02fdd49f14a7ca24df9629e39fc75bd_mdb.min.css',
  '/static/webassets-external/0cebf0022b3ceead7531e7da3d9cac78_select2.min.css',
  '/static/webassets-external/a967f73b8ac0a718e732152b9e904771_font-awesome.min.css',
  '/static/webassets-external/b54b4ca42f274426735df5e793a90a1b_bootstrap-social.min.css',
  './fallback.json'
];

self.addEventListener('install', async function () {
  const cache = await caches.open(cacheName);
  cache.addAll(staticAssets);
});

self.addEventListener('activate', event => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', event => {
  const request = event.request;
  const url = new URL(request.url);
  if (url.origin === location.origin) {
    event.respondWith(cacheFirst(request));
  } else {
    event.respondWith(networkFirst(request));
  }
});

async function cacheFirst(request) {
  const cachedResponse = await caches.match(request);
  return cachedResponse || fetch(request);
}

async function networkFirst(request) {
  const dynamicCache = await caches.open('bhagavadgita');
  try {
    const networkResponse = await fetch(request);
    dynamicCache.put(request, networkResponse.clone());
    return networkResponse;
  } catch (err) {
    const cachedResponse = await dynamicCache.match(request);
    return cachedResponse || await caches.match('./fallback.json');
  }
}
