// Service Worker for RSS Affiliate News Site
// Optimized for performance and offline support

const CACHE_NAME = 'tech-news-v1.2';
const STATIC_CACHE = 'static-v1.2';
const DYNAMIC_CACHE = 'dynamic-v1.2';

// Critical resources to cache immediately
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/spa.html',
  '/articles.json',
  '/favicon.ico',
  '/sitemap.xml',
  '/robots.txt'
];

// API endpoints and dynamic content
const DYNAMIC_PATTERNS = [
  /\/articles\.json$/,
  /\/sitemap\.xml$/,
  /\/performance\.json$/,
  /\/news_sitemap\.xml$/,
  /\/sitemap_index\.xml$/
];

// External resources to cache
const EXTERNAL_RESOURCES = [
  'https://www.googletagmanager.com/gtag/js',
  'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js'
];

// Install event - cache static assets
self.addEventListener('install', event => {
  console.log('Service Worker: Installing...');
  
  event.waitUntil(
    Promise.all([
      // Cache static assets
      caches.open(STATIC_CACHE).then(cache => {
        console.log('Service Worker: Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      }),
      
      // Cache external resources
      caches.open(DYNAMIC_CACHE).then(cache => {
        console.log('Service Worker: Caching external resources');
        return Promise.allSettled(
          EXTERNAL_RESOURCES.map(url => 
            cache.add(url).catch(err => console.warn('Failed to cache:', url, err))
          )
        );
      })
    ]).then(() => {
      console.log('Service Worker: Installation complete');
      return self.skipWaiting();
    })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  console.log('Service Worker: Activating...');
  
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== STATIC_CACHE && 
              cacheName !== DYNAMIC_CACHE && 
              cacheName !== CACHE_NAME) {
            console.log('Service Worker: Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      console.log('Service Worker: Activation complete');
      return self.clients.claim();
    })
  );
});

// Fetch event - implement caching strategies
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }
  
  // Skip chrome-extension and non-http(s) requests
  if (!url.protocol.startsWith('http')) {
    return;
  }
  
  event.respondWith(handleRequest(request));
});

async function handleRequest(request) {
  const url = new URL(request.url);
  
  try {
    // Strategy 1: Network First for dynamic content (articles, sitemaps)
    if (isDynamicContent(url.pathname)) {
      return await networkFirstStrategy(request);
    }
    
    // Strategy 2: Cache First for static assets
    if (isStaticAsset(url.pathname)) {
      return await cacheFirstStrategy(request);
    }
    
    // Strategy 3: Stale While Revalidate for external resources
    if (isExternalResource(url.href)) {
      return await staleWhileRevalidateStrategy(request);
    }
    
    // Default: Network First with fallback
    return await networkFirstStrategy(request);
    
  } catch (error) {
    console.error('Service Worker: Fetch error:', error);
    return await handleOfflineFallback(request);
  }
}

// Network First Strategy - for dynamic content
async function networkFirstStrategy(request) {
  try {
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      const cache = await caches.open(DYNAMIC_CACHE);
      cache.put(request.clone(), networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('Network failed, trying cache:', request.url);
    const cachedResponse = await caches.match(request);
    
    if (cachedResponse) {
      return cachedResponse;
    }
    
    throw error;
  }
}

// Cache First Strategy - for static assets
async function cacheFirstStrategy(request) {
  const cachedResponse = await caches.match(request);
  
  if (cachedResponse) {
    return cachedResponse;
  }
  
  try {
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      const cache = await caches.open(STATIC_CACHE);
      cache.put(request.clone(), networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.error('Cache First failed:', request.url, error);
    throw error;
  }
}

// Stale While Revalidate Strategy - for external resources
async function staleWhileRevalidateStrategy(request) {
  const cachedResponse = await caches.match(request);
  
  // Update cache in background
  const networkPromise = fetch(request).then(response => {
    if (response.ok) {
      const cache = caches.open(DYNAMIC_CACHE);
      cache.then(c => c.put(request.clone(), response.clone()));
    }
    return response;
  }).catch(err => {
    console.warn('Background update failed:', request.url, err);
  });
  
  // Return cached version immediately if available
  if (cachedResponse) {
    return cachedResponse;
  }
  
  // Otherwise wait for network
  return await networkPromise;
}

// Offline fallback handler
async function handleOfflineFallback(request) {
  const url = new URL(request.url);
  
  // For navigation requests, return cached index.html
  if (request.mode === 'navigate') {
    const cachedIndex = await caches.match('/index.html') || 
                       await caches.match('/');
    
    if (cachedIndex) {
      return cachedIndex;
    }
  }
  
  // For API requests, return cached version or offline message
  if (url.pathname.endsWith('.json')) {
    const cachedResponse = await caches.match(request);
    
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return offline indicator
    return new Response(
      JSON.stringify({
        error: 'Offline',
        message: 'オフライン中です。キャッシュされたコンテンツを表示しています。',
        timestamp: new Date().toISOString()
      }),
      {
        status: 503,
        statusText: 'Service Unavailable',
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
  
  throw new Error('No offline fallback available');
}

// Helper functions
function isDynamicContent(pathname) {
  return DYNAMIC_PATTERNS.some(pattern => pattern.test(pathname));
}

function isStaticAsset(pathname) {
  return pathname.endsWith('.html') || 
         pathname.endsWith('.ico') || 
         pathname.endsWith('.txt') ||
         pathname === '/';
}

function isExternalResource(url) {
  return EXTERNAL_RESOURCES.some(resource => url.includes(resource));
}

// Background sync for analytics and performance data
self.addEventListener('sync', event => {
  if (event.tag === 'performance-sync') {
    event.waitUntil(syncPerformanceData());
  }
});

async function syncPerformanceData() {
  try {
    // Sync any cached performance data when back online
    const cache = await caches.open(DYNAMIC_CACHE);
    const requests = await cache.keys();
    
    for (const request of requests) {
      if (request.url.includes('analytics') || request.url.includes('gtag')) {
        try {
          await fetch(request.clone());
        } catch (error) {
          console.warn('Failed to sync:', request.url);
        }
      }
    }
  } catch (error) {
    console.error('Performance sync failed:', error);
  }
}

// Handle push notifications (for future use)
self.addEventListener('push', event => {
  if (event.data) {
    const data = event.data.json();
    
    const options = {
      body: data.body || '新しいテックニュースが更新されました',
      icon: '/favicon.ico',
      badge: '/favicon.ico',
      tag: 'tech-news-update',
      renotify: true,
      requireInteraction: false,
      actions: [
        {
          action: 'view',
          title: '記事を見る'
        },
        {
          action: 'close',
          title: '閉じる'
        }
      ]
    };
    
    event.waitUntil(
      self.registration.showNotification(
        data.title || '日本のテックニュース速報',
        options
      )
    );
  }
});

// Handle notification clicks
self.addEventListener('notificationclick', event => {
  event.notification.close();
  
  if (event.action === 'view') {
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});

console.log('Service Worker: Loaded successfully');