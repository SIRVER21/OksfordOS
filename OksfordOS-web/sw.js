const CACHE_NAME = 'oksfordos-v2';
const urlsToCache = [
    '/',
    '/index.html',
    '/manifest.json',
    '/sw.js',
    '/logo.png'  // jeśli masz
];

self.addEventListener('install', event => {
    self.skipWaiting();  // Aktywuj natychmiast
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('Cache opened');
                return cache.addAll(urlsToCache);
            })
    );
});

self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== CACHE_NAME) {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});

self.addEventListener('fetch', event => {
    // Cache-first dla plików statycznych
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                // Zwróć z cache jeśli istnieje
                if (response) {
                    return response;
                }
                // Fallback do sieci
                return fetch(event.request).catch(() => {
                    // Offline fallback - pokaż stronę główną
                    return caches.match('/index.html');
                });
            })
    );
});

