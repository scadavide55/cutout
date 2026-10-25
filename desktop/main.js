const { app, BrowserWindow, Menu, protocol, net, shell, session } = require('electron');
const path = require('path');
const fs = require('fs');
const { pathToFileURL } = require('url');
const cfg = require('./assets.json');
app.setName('Cutout');

// The website is served from app://cutout/ so it is a secure, cross-origin-isolated page
// (WebAssembly threads work without the website's service worker).
protocol.registerSchemesAsPrivileged([
  { scheme: 'app', privileges: { standard: true, secure: true, supportFetchAPI: true, corsEnabled: true, stream: true } }
]);

const ASSETS = app.isPackaged ? path.join(process.resourcesPath, 'assets') : path.join(__dirname, 'assets');
const SITE = path.join(__dirname, 'app');

// WebGPU is what makes the larger engines usable. It is on by default on macOS and Windows;
// Linux needs Vulkan and the unsafe flag.
app.commandLine.appendSwitch('enable-unsafe-webgpu');
if (process.platform === 'linux') app.commandLine.appendSwitch('enable-features', 'Vulkan,WebGPU');

const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.wasm': 'application/wasm',
  '.png': 'image/png', '.json': 'application/json', '.onnx': 'application/octet-stream' };

const ISOLATION = {
  'Cross-Origin-Opener-Policy': 'same-origin',
  'Cross-Origin-Embedder-Policy': 'require-corp',
  'Cross-Origin-Resource-Policy': 'cross-origin'
};

// Serve a local file with a real Content-Length, so the page's download progress bar works.
async function serveFile(file) {
  const resolved = path.resolve(file);
  if (!fs.existsSync(resolved) || !fs.statSync(resolved).isFile()) return new Response('Not found', { status: 404 });
  const upstream = await net.fetch(pathToFileURL(resolved).href);
  const headers = new Headers(ISOLATION);
  headers.set('Content-Type', MIME[path.extname(resolved).toLowerCase()] || 'application/octet-stream');
  const len = upstream.headers.get('content-length');
  if (len) headers.set('Content-Length', len);
  return new Response(upstream.body, { status: 200, headers });
}

function inside(base, rel) {
  const p = path.resolve(base, rel);
  return p.startsWith(path.resolve(base) + path.sep) ? p : null;
}

function installHandlers(ses) {
  ses.protocol.handle('app', req => {
    const u = new URL(req.url);
    const rel = decodeURIComponent(u.pathname === '/' ? 'index.html' : u.pathname.slice(1));
    const p = inside(SITE, rel);
    return p ? serveFile(p) : new Response('Forbidden', { status: 403 });
  });

  // The page asks for its models and runtime at their public URLs. Answer those from disk,
  // and refuse every other network request: the desktop app never goes online.
  ses.protocol.handle('https', req => {
    const url = req.url.split('?')[0];
    if (cfg.models[url]) return serveFile(path.join(ASSETS, cfg.models[url]));
    if (url.startsWith(cfg.ortBase)) {
      const p = inside(path.join(ASSETS, 'ort'), url.slice(cfg.ortBase.length));
      return p ? serveFile(p) : new Response('Forbidden', { status: 403 });
    }
    if (url === cfg.ping.split('?')[0]) return new Response('{}', { status: 200, headers: ISOLATION });
    return new Response('Offline', { status: 503 });
  });
}

function createWindow() {
  const win = new BrowserWindow({
    width: 1200, height: 860, minWidth: 380, minHeight: 560,
    backgroundColor: '#0d0e14', title: 'Cutout', icon: path.join(__dirname, 'build', 'icon.png'),
    ...(process.platform === 'darwin' ? { titleBarStyle: 'hiddenInset', trafficLightPosition: { x: 18, y: 18 } } : {}),
    ...(process.platform === 'win32' ? { titleBarStyle: 'hidden', titleBarOverlay: { color: '#0d0e14', symbolColor: '#b0b6cd', height: 62 } } : {}),
    webPreferences: { contextIsolation: true, nodeIntegration: false, sandbox: true, spellcheck: false }
  });
  win.setMenuBarVisibility(false);
  win.webContents.on('dom-ready', () => {
    win.webContents.insertCSS(fs.readFileSync(path.join(__dirname, 'inject.css'), 'utf8'));
    const platform = process.platform === 'darwin' ? 'mac' : process.platform === 'win32' ? 'win' : 'linux';
    win.webContents.executeJavaScript(fs.readFileSync(path.join(__dirname, 'inject.js'), 'utf8')
      .replace('__PLATFORM__', platform).replace('__VERSION__', 'v' + app.getVersion().replace(/\.0$/, '')));
  });
  win.loadURL('app://cutout/index.html');

  // Links (GitHub, privacy, terms) open in the real browser; the app itself never navigates away.
  win.webContents.setWindowOpenHandler(({ url }) => {
    if (/^https:\/\//.test(url)) shell.openExternal(url);
    return { action: 'deny' };
  });
  win.webContents.on('will-navigate', (e, url) => { if (!url.startsWith('app://cutout/')) e.preventDefault(); });
}

app.whenReady().then(() => {
  if (process.platform === 'darwin' && app.dock) app.dock.setIcon(path.join(__dirname, 'build', 'icon.png'));
  installHandlers(session.defaultSession);
  Menu.setApplicationMenu(Menu.buildFromTemplate([
    ...(process.platform === 'darwin' ? [{ role: 'appMenu' }] : []),
    { role: 'editMenu' },
    { label: 'View', submenu: [{ role: 'reload' }, { role: 'togglefullscreen' }, { role: 'toggleDevTools' }] },
    { role: 'windowMenu' }
  ]));
  createWindow();
  app.on('activate', () => { if (BrowserWindow.getAllWindows().length === 0) createWindow(); });
});

app.on('window-all-closed', () => { if (process.platform !== 'darwin') app.quit(); });
