// Builds desktop/assets (models + ONNX runtime) and desktop/app (the website). Safe to re-run.
const fs = require('fs');
const path = require('path');
const https = require('https');

const root = path.join(__dirname, '..');
const cfg = require('../assets.json');

function download(url, dest, redirects = 0) {
  return new Promise((resolve, reject) => {
    https.get(url, { headers: { 'User-Agent': 'cutout-desktop-build' } }, res => {
      if ([301, 302, 303, 307, 308].includes(res.statusCode) && res.headers.location && redirects < 8) {
        res.resume();
        return resolve(download(new URL(res.headers.location, url).href, dest, redirects + 1));
      }
      if (res.statusCode !== 200) { res.resume(); return reject(new Error(res.statusCode + ' ' + url)); }
      const tmp = dest + '.part';
      const out = fs.createWriteStream(tmp);
      res.pipe(out);
      out.on('finish', () => out.close(() => { fs.renameSync(tmp, dest); resolve(); }));
      out.on('error', reject);
      res.on('error', reject);
    }).on('error', reject);
  });
}

async function main() {
  // 1. website
  const app = path.join(root, 'app');
  fs.mkdirSync(app, { recursive: true });
  for (const f of ['index.html', 'og.png']) fs.copyFileSync(path.join(root, '..', f), path.join(app, f));

  // 2. models
  for (const [url, rel] of Object.entries(cfg.models)) {
    const dest = path.join(root, 'assets', rel);
    fs.mkdirSync(path.dirname(dest), { recursive: true });
    if (fs.existsSync(dest) && fs.statSync(dest).size > 1e6) { console.log('have', rel); continue; }
    console.log('downloading', rel);
    await download(url, dest);
  }

  // 3. ONNX Runtime (version pinned in package.json, same as the website)
  const dist = path.join(root, 'node_modules', 'onnxruntime-web', 'dist');
  if (!fs.existsSync(dist)) throw new Error('Run npm install first');
  const ort = path.join(root, 'assets', 'ort');
  fs.mkdirSync(ort, { recursive: true });
  for (const f of fs.readdirSync(dist)) {
    if (f === 'ort.webgpu.min.js' || /^ort-wasm-simd-threaded.*\.(mjs|wasm)$/.test(f)) fs.copyFileSync(path.join(dist, f), path.join(ort, f));
  }
  // Third-party notices travel with the models.
  fs.copyFileSync(path.join(root, 'THIRD_PARTY.md'), path.join(root, 'assets', 'THIRD_PARTY.md'));
  console.log('assets ready');
}
main().catch(e => { console.error(e); process.exit(1); });
