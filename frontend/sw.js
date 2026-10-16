// ════════════════════════════════════════════════════════════════════════════
// First-Gen AI Career Navigator — Progressive Web App (PWA) Service Worker
// Version: 1.0.0
// Offline roadmap caching, study notes persistence & network-resilient fallbacks
// ════════════════════════════════════════════════════════════════════════════

const CACHE_NAME = 'careernav-shell-v1.0';
const DATA_CACHE_NAME = 'careernav-data-v1.0';

// Core shell assets to pre-cache during installation
const PRECACHE_ASSETS = [
  './',
  './index.html',
  './dashboard.html',
  './roadmap.html',
  './chatbot.html',
  './quiz.html',
  './internships.html',
  './portfolio.html',
  './verify.html',
  './interview.html',
  './login.html',
  './register.html',
  './settings.html',
  './careers.html',
  './style.css',
  './dashboard.css',
  './roadmap.css',
  './chatbot.css',
  './quiz.css',
  './auth.css',
  './careers.css',
  './progress.css',
  './api.js',
  './manifest.json',
  './icons/icon.svg',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/icon-maskable.png'
];

// ─────────────────────────────────────────────────────────────
// 1. INSTALL EVENT — Pre-cache critical application shell
// ─────────────────────────────────────────────────────────────
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('[ServiceWorker] Pre-caching application shell...');
        return cache.addAll(PRECACHE_ASSETS);
      })
      .then(() => self.skipWaiting())
      .catch(err => {
        console.warn('[ServiceWorker] Pre-cache warning (some assets may be dynamic):', err);
        return self.skipWaiting();
      })
  );
});

// ─────────────────────────────────────────────────────────────
// 2. ACTIVATE EVENT — Clean up outdated caches
// ─────────────────────────────────────────────────────────────
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(key => {
          if (key !== CACHE_NAME && key !== DATA_CACHE_NAME) {
            console.log('[ServiceWorker] Removing obsolete cache:', key);
            return caches.delete(key);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// ─────────────────────────────────────────────────────────────
// 3. FETCH EVENT — Intelligent Network & Offline Strategies
// ─────────────────────────────────────────────────────────────
self.addEventListener('fetch', event => {
  const req = event.request;
  const url = new URL(req.url);

  // Skip non-GET requests (POST, PUT, DELETE should hit server or fail gracefully)
  if (req.method !== 'GET') {
    return;
  }

  // A. Roadmap & Study Notes API Data (Runtime Cache for Offline Study)
  if (url.pathname.includes('/api/v1/roadmap/') || 
      url.pathname.includes('/api/v1/progress/') ||
      url.pathname.includes('/api/v1/certificates/')) {
    event.respondWith(
      fetch(req)
        .then(res => {
          // Clone and cache the successful API response for offline access
          if (res && res.status === 200) {
            const resClone = res.clone();
            caches.open(DATA_CACHE_NAME).then(cache => {
              cache.put(req, resClone);
            });
          }
          return res;
        })
        .catch(async () => {
          // Network failed — retrieve cached response from offline ledger
          const cachedData = await caches.match(req);
          if (cachedData) {
            console.log('[ServiceWorker] Serving cached roadmap/study data offline for:', url.pathname);
            return cachedData;
          }
          // Return fallback offline JSON
          return new Response(
            JSON.stringify({
              success: false,
              offline: true,
              message: 'You are currently offline. Viewing cached roadmap study data.'
            }),
            { headers: { 'Content-Type': 'application/json' } }
          );
        })
    );
    return;
  }

  // B. HTML Navigation Requests (Network First -> Fallback to Cache)
  if (req.mode === 'navigate' || req.headers.get('accept')?.includes('text/html')) {
    event.respondWith(
      fetch(req)
        .then(res => {
          if (res && res.status === 200) {
            const resClone = res.clone();
            caches.open(CACHE_NAME).then(cache => cache.put(req, resClone));
          }
          return res;
        })
        .catch(async () => {
          // Offline fallback
          const cachedPage = await caches.match(req);
          if (cachedPage) {
            return cachedPage;
          }
          // Match by page name without search queries
          const fallback = await caches.match(url.pathname.split('/').pop() || 'index.html');
          if (fallback) return fallback;
          return caches.match('./index.html');
        })
    );
    return;
  }

  // C. Static Assets: CSS, JS, Images, Icons, Fonts (Cache First -> Network Fallback)
  event.respondWith(
    caches.match(req).then(cachedResponse => {
      if (cachedResponse) {
        // Fetch in background to update cache for next load (stale-while-revalidate style)
        fetch(req)
          .then(networkRes => {
            if (networkRes && networkRes.status === 200) {
              caches.open(CACHE_NAME).then(cache => cache.put(req, networkRes));
            }
          })
          .catch(() => {});
        return cachedResponse;
      }

      // Not in cache: fetch from network and cache
      return fetch(req)
        .then(networkRes => {
          if (networkRes && networkRes.status === 200) {
            const resClone = networkRes.clone();
            caches.open(CACHE_NAME).then(cache => cache.put(req, resClone));
          }
          return networkRes;
        })
        .catch(() => {
          // If offline and request is an icon/image, return SVG icon placeholder
          if (req.destination === 'image') {
            return caches.match('./icons/icon.svg');
          }
          return new Response('', { status: 408, statusText: 'Request timed out offline' });
        });
    })
  );
});

// ─────────────────────────────────────────────────────────────
// 4. MESSAGE EVENT — Force skip waiting on update
// ─────────────────────────────────────────────────────────────
self.addEventListener('message', event => {
  if (event.data && event.data.action === 'skipWaiting') {
    self.skipWaiting();
  }
});
