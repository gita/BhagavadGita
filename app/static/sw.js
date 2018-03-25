

const staticAssets = [
  './',
  './app.js',
  './styles.css',
  './fallback.json',
  './images/fetch-dog.jpg'
];

self.addEventListener('install', async function () {
  console.log("Krishna")
});

self.addEventListener('fetch', event => {
  console.log("Radha")
});
