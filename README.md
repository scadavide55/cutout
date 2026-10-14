# Cutout

**Status: public beta.** Feature-complete and working, with four engines. It has been
tested on a MacBook and on one mid-range Android phone, not yet on enough real devices,
so see [Beta status](#beta-status).

Remove image backgrounds in the browser. Free, no account, no upload: the AI model runs
on the visitor's own device, so photos never leave it.

No build step, no installed dependencies, no server-side anything. The whole site is one
static HTML file with inline CSS and JavaScript, plus a tiny service worker.

## The point

I wanted a background remover that is entirely free and private, without an account,
a subscription or a server receiving your images.

Most background removers upload your photo to a server, process it there, and then charge
per image, cap the preview resolution, watermark the result, or keep copies. Cutout has
no backend and charges nothing for exports. Its image-size limits are only there to keep
the visitor's own browser tab from running out of memory.

## Features

- Drag, click, paste (⌘V) or drop images: up to **20 at once**, **30 MB each**
- Choose an engine on upload: **Low**, **Medium**, **High** or **Ultra**
- Transparent PNG at the **full original resolution**, not a capped preview
- Optional background: a colour from the palette, a custom picker, or your own photo
- Export PNG (keeps transparency) or JPG (flattened)
- Copy the result straight to the clipboard as a real PNG
- Download the whole batch as one `.zip`, or clear everything at once
- Retry failed images without picking the files again
- Hold the eye button on a result to compare against the original
- Change the engine on a result without uploading again; keep the old cutout if refinement fails
- Compact engine choices, in-visit engine memory, and mobile-sized export controls
- Download progress, explicit engine preparation, stalled-download errors, and releasable blob previews
- Follows the visitor's system light/dark theme
- Keyboard and touch accessible

## The four engines

| | Low | Medium | High | Ultra |
|---|---|---|---|---|
| Model | MODNet | BEN2 compact (int8) | BEN2 base | BEN2 base, two passes |
| Download | 6.6 MB | 130 MB | 223 MB | 223 MB (shared with High) |
| Runs on | processor | desktop GPU, or desktop processor | GPU only | desktop GPU only |
| Licence | Apache-2.0 | MIT | MIT | MIT |
| Input | 512 px | 1024 px | 1024 px | 1024 px, twice |
| Best for | people, portraits | the best balance | hair, fur, products | the cleanest edges, on a fast computer |

Read the [model guide](MODEL%20GUIDE.md) to choose between them.

- **Medium** is BEN2 with its weights stored as int8, one scale per output channel. It is
  hosted at [Davide531/ben2-int8](https://huggingface.co/Davide531/ben2-int8). The
  dequantisation is written as plain `Cast` and `Mul` nodes, because ONNX Runtime's WebGPU
  engine mishandles the standard `DequantizeLinear` operator. It uses desktop WebGPU when
  there is sufficient buffer headroom, without relying on privacy-clamped CPU-core hints.
  It falls back to the desktop processor otherwise. **Medium is disabled on mobile**:
  its CPU preparation left the Galaxy A25 test tab unresponsive, so it is not safe to offer
  that path as working.
- **High** needs WebGPU. On the processor its memory use exceeds what a browser tab can
  allocate.
- **Ultra** runs the High model on the image and on its mirror image, flips the second
  result back and averages the two. That settles edges where the model changed its mind
  between the two views. It costs about twice High's time, it is offered only on a
  high-end computer (WebGPU, 8+ cores, 8 GB+ memory if reported), and it asks for
  confirmation before it starts.

Conservative guards check the GPU's per-allocation limit with 15% desktop / 25% mobile headroom, mobile status,
and browser memory hints. Ineligible engines are disabled with a reason. These are safety
checks, **not a guarantee** that every driver can execute the model. Only one model session
is retained; switching engines releases the previous graph, while High and Ultra share one.

Decoded images are limited to **24 MP on desktop**, **12 MP on mobile or low-memory devices**,
and **8192 pixels per side**. A batch is limited to 48 MP on desktop or 24 MP on mobile.
Accepted images export at their original resolution; oversized images get a readable error,
not a silent downscale. Low's inference input is bounded to a 1024-pixel longest edge to
prevent panoramic inputs from creating enormous tensors. Existing input transparency is preserved.

### What was not possible

BiRefNet (MIT) would be a real step above BEN2 for Ultra. Its full model fails inside
ONNX Runtime's WebGPU engine (shader errors on 1.24.3 and 1.26.0, and memory failures
in earlier testing). It is not used. RMBG-1.4 and RMBG-2.0 need a paid agreement with BRIA, and
ISNet's DIS5K dataset terms forbid commercial use, so they were rejected on licence
grounds.

## Loading behaviour

- **Nothing is preloaded.** Neither the ONNX runtime nor a model is fetched on page open.
  The runtime loads when "Cut out" is pressed, then the chosen model.
- **One startup request:** a ~300 byte probe to the host serving the models, so a Hugging
  Face outage or rate limit is reported in plain language instead of surfacing as a slow
  failed download. If the probe fails, "Check again" retries it.
- **Caching is the browser's.** The models are served from Hugging Face with the CDN's
  normal cache headers. There is no offline mode, and a hard reload may re-download.
- **A small service worker (`sw.js`)** adds two response headers
  (`Cross-Origin-Opener-Policy` and `Cross-Origin-Embedder-Policy`) so WebAssembly can use
  several threads, which GitHub Pages cannot send itself. The first visit reloads once to
  switch it on. It caches nothing and does not touch your images.

Runtime and models come from third-party CDNs at use time:

| Piece | Source |
|---|---|
| MODNet (quantized) | `huggingface.co/Xenova/modnet` |
| BEN2 compact (int8) | `huggingface.co/Davide531/ben2-int8` |
| BEN2 base | `huggingface.co/PramaLLC/BEN2` |
| ONNX Runtime Web 1.24.3 | `cdn.jsdelivr.net/npm/onnxruntime-web` |

> **Why the runtime version is pinned.** ONNX Runtime Web 1.22.0 computed both BEN2 models
> wrongly on the GPU (a mostly-foreground mask for Medium, stray background for High). The
> models were fine: run natively they agree. 1.24.3 is the version verified to match.
> Newer releases have not been validated for this release. Re-test these graphs before
> changing the pinned runtime.

## Privacy

No analytics, no cookies, no accounts, no telemetry. Images are decoded, processed and
encoded in memory on the visitor's own device. **Cutout does not store your pictures**: the
site is a static page on GitHub Pages, and the only thing it downloads is the model, from
Hugging Face, onto your device. Nothing is uploaded, because there is nowhere to upload to.
Be aware the page still makes the CDN requests listed above, and those reveal to the CDNs
that the page was used, like any site that loads a library.

## Browser support

- Low runs on the processor. Medium uses desktop WebGPU or falls back to the desktop processor.
- Every engine tries WebGPU first; CPU is a last resort, only where safe. Low uses a 25.9 MB float model on the GPU (6.6 MB quantized model as CPU fallback); on the Galaxy A25 it ran on the GPU in about 2 s warm. Medium is off on low-memory phones because it froze the A25 tab.
- High and Ultra require WebGPU. Without it they are shown as unavailable.
- WebGPU requires a **secure context**: `https://`, or `localhost`. Plain `http://` on a
  LAN address cannot expose it, even on a Mac.
- The status line reports the browser's own capability answers. It deliberately does not
  display CPU count or RAM: browsers clamp those values, so they would be misleading.

## Run it locally

Two optional servers are included for local testing. Neither is needed to deploy; they
exist because browsers restrict some features on `file://` pages. Both serve only the
site's own files.

```sh
python3 server.py 8080          # this machine only, http://127.0.0.1:8080/
python3 server_lan.py 8080      # also reachable from a phone on the same Wi-Fi
```

Both send the two isolation headers directly. `server_lan.py` binds to `0.0.0.0` and
prints the LAN address to open on a phone.

## Deploy

Any static host works. Keep `index.html`, `sw.js` and `og.png` together at the root.

**GitHub Pages** (free for public repositories):

1. Keep `index.html` at the **repository root**.
2. Push to the `main` branch.
3. Settings → Pages → Source: *Deploy from a branch* → Branch: `main` → Folder: **`/ (root)`**.

GitHub Pages cannot send custom headers, which is why `sw.js` exists. Cloudflare Pages and
Netlify can send them natively and do not need it.

## How it is built

- **One page.** `index.html` holds the markup, CSS and JavaScript. No framework, no
  bundler, no npm install, no generated output.
- **System fonts and inline SVG** for the interface. No web fonts, no icon library.
- **Hand-written ZIP writer** (~60 lines, store-only, CRC-32) instead of a ~100 KB archive
  library. The PNGs are already compressed, so storing them costs nothing in size.
- **Crash marker.** A tab killed for memory cannot report anything, so a heavy engine is
  marked in `sessionStorage` before it loads and unmarked when a result lands. The next
  visit can then say the last attempt was cut off. Only two words and a byte count are
  stored, never an image.

## Beta status

See the [14 October 2026 release check](RELEASE%20CHECK.md) for the exact results and
remaining gaps, and [tests/README.md](tests/README.md) to reproduce the checks.

Verified: portrait cutouts through all four engines on a MacBook Air (M5, WebGPU), output
alpha and resolution, custom and flat backgrounds, JPG flattening, clipboard output, batch
ZIP export, and the engine guard on a simulated weak device.

On 14 Oct 2026 the revised build was tested on a Samsung Galaxy A25 (5 GB RAM). Low
produced clean 600 × 600 cutouts in both first and repeated runs, and the phone layout had
no horizontal overflow. Medium's CPU preparation did not complete and the tab became
unresponsive; Medium is therefore disabled on mobile. The final phone check confirmed
that Medium, High and Ultra are blocked and Low remains usable.

Not yet verified well enough to call stable:

- Phones and GPUs other than the two above. Medium is not offered on mobile.
- High-resolution mixed batches near the decoded-pixel safety limits.
- Safari, Firefox, and older drivers: full cross-browser inference remains unverified.

Treat results as good enough to use, not as guaranteed. Report bugs in the repository's
Issues tab.

## Licence

The website code in this repository is **Apache-2.0**; see [LICENSE](LICENSE).

The models and libraries Cutout downloads at runtime are separate works under their own
licences, and those licences apply to them, not to this repository:

| Component | Licence |
|---|---|
| MODNet model weights | Apache-2.0 |
| BEN2 compact (int8) | MIT, this project's quantisation of BEN2 |
| BEN2 model weights | MIT |
| ONNX Runtime Web | MIT |

All the models are permissive and usable commercially. That is one of the reasons they were
chosen over alternatives with non-commercial terms.

## Credits

Built by **scadavide55**.

Model weights by the MODNet and BEN2 authors, repackaged for the browser by
[Xenova](https://huggingface.co/Xenova) (MODNet) and
[PramaLLC](https://huggingface.co/PramaLLC) (BEN2). Inference powered by
[ONNX Runtime Web](https://onnxruntime.ai/).
