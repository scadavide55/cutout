# Cutout

A background remover that runs entirely in the browser. No account, no upload,
no server, no cost — the AI model runs on the visitor's own device, so photos
never leave their machine.

One file: `public/index.html`. No build step, no dependencies to install.

## What it does

- Drag, click, paste (⌘V) or drop up to 20 images at once
- On upload, asks which engine to use: **FAST** or **PRO**
- Outputs a transparent PNG at full original resolution
- Optional background: a colour, or your own photo
- Exports PNG (keeps transparency) or JPG (flattened)
- Copy straight to the clipboard
- Batch download all results

## The two engines

| | FAST | PRO |
|---|---|---|
| Model | MODNet | BEN2 base |
| Download | 6.6 MB | 223 MB (one-time) |
| Licence | Apache-2.0 | MIT |
| Input | 512px | 1024px |
| Measured time | ~0.5 s | ~3.3 s |
| Best for | people, portraits | hair, fur, products, busy backgrounds |

Both are free for commercial use, unlike the popular `@imgly/background-removal`
package, whose RMBG-1.4 model is non-commercial and whose code is AGPL-3.0.

Timings above were measured on an M5 MacBook Air via WebGPU. Devices without
WebGPU fall back to CPU automatically and PRO will be considerably slower —
the page warns the visitor when that is the case.

## Run it locally

```sh
python3 server.py 8080
# then open http://127.0.0.1:8080/
```

`server.py` exists because browsers restrict some features on `file://` pages.
It also sends `Cross-Origin-Opener-Policy` and `Cross-Origin-Embedder-Policy`,
which enable multi-threaded WebAssembly and make inference faster.

## Deploy

The whole site is one static file, so any static host works.

**GitHub Pages:** move `public/index.html` to the repo root (or set Pages to
serve the `/public` folder), commit, and enable Pages in the repository
settings.

> **Note on hosting:** GitHub Pages cannot send custom headers, so
> multi-threading will be off there and inference will be slower than the
> numbers above. Cloudflare Pages and Netlify let you set the two COOP/COEP
> headers, which restores it. Single-threaded still works fine everywhere.

## Notes

- **Theme:** follows the visitor's system light/dark setting automatically.
- **Threads:** without the COOP/COEP headers the page falls back to
  single-threaded WASM by itself, with no error.
- **WebGPU:** used for PRO when available, with an automatic fallback to WASM.
- **Privacy:** no analytics, no cookies, no network requests after the models
  are cached. Photos are handled only in memory on the visitor's device.
