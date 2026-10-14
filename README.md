# Cutout

**Status: public beta.** Feature-complete and working, but not yet exercised on
enough real devices — see [Beta status](#beta-status).

Remove image backgrounds in the browser. Free, no account, no upload: the AI
model runs on the visitor's own device, so photos never leave it.

No build step, no installed dependencies, no server-side anything. The whole
site is one static HTML file with inline CSS and JavaScript.

## The point

Most background removers — Remove.bg among them — upload your photo to a
server, process it there, and either charge per image, cap the resolution,
watermark the result, or keep copies. Cutout does none of it. There is no
backend to send anything to.

It also costs nothing to run, so there is no reason to limit it.

## Features

- Drag, click, paste (⌘V) or drop images — up to **20 at once**, **30 MB each**
- Choose an engine on upload: **FAST** or **PRO**
- Transparent PNG at the **full original resolution**, not a capped preview
- Optional background: a colour from the palette, a custom picker, or your own photo
- Export PNG (keeps transparency) or JPG (flattened)
- Copy the result straight to the clipboard as a real PNG
- Download the whole batch as one `.zip`, or clear everything at once
- Retry failed images without picking the files again
- Hold the eye button on a result to compare against the original
- Follows the visitor's system light/dark theme
- Keyboard and touch accessible

## The two engines

| | FAST | PRO |
|---|---|---|
| Model | MODNet | BEN2 base |
| Download | 6.6 MB | 223 MB (one-time) |
| Licence | Apache-2.0 | MIT |
| Input | 512 px | 1024 px |
| Measured time | ~0.5 s | ~3.3 s |
| Best for | people, portraits | hair, fur, products, busy backgrounds |

Timings measured on an M5 MacBook Air through WebGPU. FAST is the default
choice and is good enough for most portraits; PRO is worth the download when
edges are the hard part.

PRO is never blocked on weak devices. On a device without GPU acceleration the
dialog warns that it will be slow and may run out of memory, then lets the
visitor decide.

## Loading behaviour

- **Nothing is preloaded.** Neither the ONNX runtime nor a model is fetched on
  page open. The runtime loads when “Cut out” is pressed, then the chosen model.
- **One startup request only:** a ~300 byte probe to the host serving the
  models, so a Hugging Face outage or rate limit is reported in plain language
  instead of surfacing as a slow failed download. It holds nothing back if the
  probe fails — “Check again” retries.
- **Caching is the browser's, not ours.** The models are served from Hugging
  Face over the CDN's normal cache headers. There is no service worker and no
  offline guarantee; a hard reload may re-download.

Runtime and models come from third-party CDNs at use time:

| Piece | Source |
|---|---|
| MODNet (quantized) | `huggingface.co/Xenova/modnet` |
| BEN2 base | `huggingface.co/PramaLLC/BEN2` |
| ONNX Runtime Web 1.22.0 | `cdn.jsdelivr.net/npm/onnxruntime-web` |

## Privacy

No analytics, no cookies, no accounts, no telemetry. Images are decoded,
processed and encoded in memory on the visitor's own device. Nothing is
uploaded, because there is nowhere to upload to — but be aware the page still
makes the CDN requests listed above, and those reveal to the CDNs that the page
was used, like any site that loads a library.

## Browser support

- WebGPU is used when available, with an automatic fallback to WebAssembly.
- Without WebGPU, PRO is far slower. The page says so rather than failing.
- WebGPU requires a **secure context**: `https://`, or `localhost`. Plain
  `http://` on a LAN address cannot expose it, even on a Mac.
- The status line reports the browser's own capability answers. It
  deliberately does not display CPU count or RAM: browsers clamp those values,
  so they would be misleading rather than informative.

## Run it locally

Two optional servers are included for local testing. Neither is needed to
deploy — they exist because browsers restrict some features on `file://` pages.

```sh
python3 server.py 8080          # this machine only, http://127.0.0.1:8080/
python3 server_lan.py 8080      # also reachable from a phone on the same Wi-Fi
```

Both send `Cross-Origin-Opener-Policy` and `Cross-Origin-Embedder-Policy`,
which enable multi-threaded WebAssembly and speed up inference. `server_lan.py`
binds to `0.0.0.0` and prints the LAN address to open on a phone.

## Deploy

Any static host works; the site is one HTML file.

**GitHub Pages** (free for public repositories):

1. Keep `index.html` at the **repository root**.
2. Push to the `main` branch.
3. Settings → Pages → Source: *Deploy from a branch* → Branch: `main` → Folder: **`/ (root)`**.

The folder picker offers only `/ (root)` and `/docs`. A subfolder such as
`/public` cannot be selected — which is why the file lives at the root.

> **Note on hosting:** GitHub Pages cannot send custom response headers, so the
> COOP/COEP headers are missing there and the page runs single-threaded WASM,
> which is noticeably slower than the numbers above. It still works correctly.
> Cloudflare Pages and Netlify allow those two headers and restore
> multi-threading.

## How it is built

- **One file.** `index.html` holds the markup, CSS and JavaScript. No
  framework, no bundler, no npm install, no generated output.
- **System fonts and inline SVG** for the interface. No web fonts, no icon
  library, no decorative looping animation.
- **Hand-written ZIP writer** (~60 lines, store-only, CRC-32) instead of a
  ~100 KB archive library. The PNGs are already compressed, so storing them
  costs nothing in size.
- **Interface states.** The landing page collapses into a compact workspace
  once images are added; originals show immediately while processing runs.

## Beta status

What is verified: portrait cutouts through both engines, output alpha and
resolution, custom and flat backgrounds, JPG flattening, clipboard output, and
batch ZIP export.

What is not yet verified well enough to call stable:

- Real phone testing. Phone layout is checked at several widths, but PRO
  runtime and the file picker on an actual handset have not been measured.
- Very large batches with a mix of failures and retries.
- Safari and Firefox on older hardware.

Treat results as good enough to use, not as guaranteed. Report bugs in the
repository's Issues tab.

## Licence

The website code in this repository is **Apache-2.0** — see [LICENSE](LICENSE).

The models and libraries Cutout downloads at runtime are separate works under
their own licences, and those licences apply to them, not to this repository:

| Component | Licence |
|---|---|
| MODNet model weights | Apache-2.0 |
| BEN2 model weights | MIT |
| ONNX Runtime Web | MIT |

Both models are permissive and usable commercially. This is one of the reasons
they were chosen over alternatives with non-commercial terms.

## Credits

Built by **scadavide55**.

Model weights by the MODNet and BEN2 authors, repackaged for the browser by
[Xenova](https://huggingface.co/Xenova) (MODNet) and
[PramaLLC](https://huggingface.co/PramaLLC) (BEN2). Inference powered by
[ONNX Runtime Web](https://onnxruntime.ai/).
