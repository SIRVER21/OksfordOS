const CACHE_NAME = 'oksfordos-v5';
const urlsToCache = [
    '/',
    '/index.html',
    '/manifest.json',
 // '/sw.js',
    '/logo.png'
];

self.addEventListener('install', event => {
    self.skipWaiting();
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => cache.addAll(urlsToCache))
    );
});

self.addEventListener('activate', event => {
    event.waitUntil(
        Promise.all([
            // Usuń stare cache
            caches.keys().then(cacheNames =>
                Promise.all(
                    cacheNames.map(name => {
                        if (name !== CACHE_NAME) return caches.delete(name);
                    })
                )
            ),
            // Przejmij kontrolę natychmiast
            self.clients.claim()
        ])
    );
});

self.addEventListener('fetch', event => {
    const url = new URL(event.request.url);

    // Dla HTML – zawsze próbuj sieci, cache tylko jako fallback offline
    if (event.request.mode === 'navigate' || url.pathname.endsWith('.html') || url.pathname === '/') {
        event.respondWith(
            fetch(event.request)
                .then(response => {
                    // Zaktualizuj cache świeżą wersją
                    const clone = response.clone();
                    caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
                    return response;
                })
                .catch(() => caches.match(event.request))
        );
        return;
    }

    // Dla reszty – cache-first (manifest, logo, sw.js)
    event.respondWith(
        caches.match(event.request).then(response => response || fetch(event.request))
    );
});
