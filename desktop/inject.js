(() => {
  const root = document.documentElement;
  root.classList.add('desktop', '__PLATFORM__');
  const set = (sel, html) => { const el = document.querySelector(sel); if (el) el.innerHTML = html; };
  set('.hero h1', 'Remove image backgrounds.<br><span>Fully offline.</span>');
  set('.hero p', 'All AI engines are built in.<br>Nothing is uploaded and nothing is downloaded.');
  set('.chip', '<span class="dot"></span>Works offline');
  set('footer', '<b>Cutout __VERSION__</b><span>Everything stays on this device. ' +
    '<a href="https://github.com/scadavide55/cutout/blob/main/PRIVACY.md">Privacy</a> · ' +
    '<a href="https://github.com/scadavide55/cutout/blob/main/TERMS.md">Terms</a> · ' +
    '<a href="https://github.com/scadavide55/cutout">Source (Apache-2.0)</a></span>');
  // The app never goes online, so the page's connectivity banner must stay quiet.
  document.title = 'Cutout';
})();
