'use strict';
const cacheName = 'bhagavadgita';
const startPage = 'https://bhagavadgita.io/';
const offlinePage = 'https://bhagavadgita.io/';
const fallbackImage = 'https://bhagavadgita.io/static/images/sribhagavadgita.jpg';
const filesToCache = [startPage, offlinePage, fallbackImage];
const neverCacheUrls = ['/register', '/favourite/', '/get-favourite/'];

self.addEventListener('install', function(e) {
    console.log('BhagavadGita service worker installation');
    e.waitUntil(caches.open(cacheName).then(function(cache) {
        console.log('BhagavadGita service worker caching dependencies');
        return cache.addAll(filesToCache);
    }));
});
self.addEventListener('activate', function(e) {
    console.log('BhagavadGita service worker activation');
    e.waitUntil(caches.keys().then(function(keyList) {
        return Promise.all(keyList.map(function(key) {
            if (key !== cacheName) {
                console.log('BhagavadGita old cache removed', key);
                return caches.delete(key);
            }
        }));
    }));
    return self.clients.claim();
});
self.addEventListener('fetch', function(e) {
    if (!neverCacheUrls.every(checkNeverCacheList, e.request.url)) {
        console.log('BhagavadGita: Current page is excluded from cache');
        return;
    }
    if (!e.request.url.match(/^(http|https):\/\//i))
        return;
    if (new URL(e.request.url).origin !== location.origin)
        return;
    if (e.request.method !== 'GET') {
        e.respondWith(fetch(e.request).catch(function() {
            return caches.match(offlinePage);
        }));
        return;
    }
    if (e.request.mode === 'navigate' && navigator.onLine) {
        e.respondWith(fetch(e.request).then(function(response) {
            return caches.open(cacheName).then(function(cache) {
                cache.put(e.request, response.clone());
                return response;
            });
        }));
        return;
    }
    e.respondWith(caches.match(e.request).then(function(response) {
        return response || fetch(e.request).then(function(response) {
            return caches.open(cacheName).then(function(cache) {
                cache.put(e.request, response.clone());
                return response;
            });
        });
    }).catch(function() {
        return caches.match(offlinePage);
    }));
});

function checkNeverCacheList(url) {
    if (this.match(url)) {
        return false;
    }
    return true;
}
