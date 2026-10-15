# Cutout

Remove image backgrounds in your browser. **Free, no account, no upload, no watermark.**
The AI model runs on your own device, so your photos never leave it.

**Live site:** https://scadavide55.github.io/cutout/

**Status: public beta.** Four engines, tested on a MacBook Air (M5) and a Samsung Galaxy A25.
Not yet verified on enough other devices or browsers, see [Beta status](#beta-status).

There is no build step, no dependency and no backend: one static `index.html` (inline CSS and
JavaScript) plus a tiny service worker.

## Why it exists
**Main Reason : remove.bg is going away and wanted to make my own alternative.**
Most background removers upload your photo to a server, then cap the resolution, add a
watermark, ask for an account or charge per image. Cutout has no server to receive anything
and charges nothing. Its size limits exist only to keep your own browser tab from running out of
memory.

## Features

- Drop, click or paste (⌘V / Ctrl+V) up to **20 images**, **30 MB each**
- Four engines: **Low**, **Medium**, **High**, **Ultra** ([which one?](MODEL%20GUIDE.md))
- Transparent PNG at the **full original resolution**
- Optional background: palette colour, custom colour, or your own photo
- Export PNG or JPG, copy the PNG to the clipboard, or download the batch as one `.zip`
- Change the engine on a finished result without uploading again; if the new run fails, the old
  cutout is kept
- Retry failed images without picking the files again
- Hold the eye button to compare with the original
- Download progress, clear errors, light and dark theme, keyboard and touch friendly,
  phone-sized layout

## Engines at a glance ( Read Model Guide.md for further information)

| | Low | Medium | High | Ultra |
|---|---|---|---|---|
| Model | MODNet | BEN2 compact (int8) | BEN2 | BEN2, two passes |
| Download | 25.9 MB on GPU, 6.6 MB on CPU | 130 MB | 223 MB | 223 MB (shared with High) |
| Runs on | GPU first, CPU fallback | GPU first, computer CPU fallback | GPU only | GPU only |
| Phone (4 GB) | works, GPU | off | off | off |
| Licence | Apache-2.0 | MIT | MIT | MIT |

**Every engine tries WebGPU first. CPU is a last resort**, used only where it is safe:
Low falls back to a small quantized model, Medium falls back on computers only, and High and
Ultra never use the CPU because their memory needs exceed what a tab can allocate.

Details:

- **Low** uses a float MODNet on the GPU, because ONNX Runtime's WebGPU backend does not run
  integer-quantized convolutions. The 6.6 MB quantized model is kept only as the CPU fallback.
- **Medium** is BEN2 with int8 weights (one scale per output channel), hosted at
  [Davide531/ben2-int8](https://huggingface.co/Davide531/ben2-int8). The dequantisation is plain
  `Cast` and `Mul` nodes, because the standard `DequantizeLinear` operator misbehaves on
  ONNX Runtime's WebGPU backend. **It is off on low-memory phones:** on a 4 GB Galaxy A25 it froze the tab even on the GPU.
- **High** is the full BEN2 model.
- **Ultra** runs High on the image and on its mirror, flips the second result back and averages
  the two. It costs about twice High's time and the gain is modest. It asks for confirmation first.

An engine is shown as unavailable, with a reason, when WebGPU is missing, the GPU's buffer limit
is too small, or the browser reports too little memory. These checks are **heuristics, not a
guarantee** that every driver can run the model. Only one model session is kept in memory;
switching engines releases the previous one (High and Ultra share one).

### Size limits

Decoded images may be up to **24 MP on desktop** and **12 MP on phones or low-memory devices**,
at most 8192 px per side. A batch may total 48 MP (desktop) or 24 MP (mobile). Images over the
limit get a readable error rather than a silent downscale. Exports keep the original resolution.

### Models that were ruled out

- **BiRefNet** (MIT) would be a step above BEN2, but its full fp16 graph failed inside ONNX
  Runtime Web's WebGPU backend (shader errors on 1.24.3 and 1.26.0) and ran out of memory on the
  CPU path in earlier tests. A smaller or re-exported variant might work and has not been tried.
- **RMBG-2.0 and RMBG-1.4** are not licensed for free commercial use, so they were not used.

## Loading behaviour

- **Nothing is preloaded.** The ONNX runtime and the model are fetched only when you press
  "Cut out".
- One small health probe to Hugging Face runs on page load, so an outage is reported in plain
  words. "Check again" retries it.
- Caching is the browser's own. There is no offline mode.
- `sw.js` only adds the `Cross-Origin-Opener-Policy` and `Cross-Origin-Embedder-Policy` headers
  that GitHub Pages cannot send, enabling multi-threaded WebAssembly. It caches nothing and never
  sees your images. The first visit may reload once.

| Piece | Source |
|---|---|
| MODNet (float and quantized) | `huggingface.co/Xenova/modnet` |
| BEN2 compact (int8) | `huggingface.co/Davide531/ben2-int8` |
| BEN2 | `huggingface.co/PramaLLC/BEN2` |
| ONNX Runtime Web 1.24.3 | `cdn.jsdelivr.net/npm/onnxruntime-web` |

> **Why the runtime is pinned.** ONNX Runtime Web 1.22 computed BEN2 wrongly on the GPU
> (corrupted masks) while the same models were fine natively. 1.24.3 is the version verified
> here. Re-test before changing it.

## Privacy

No analytics, no cookies, no accounts, no telemetry. Images are decoded, processed and encoded
in memory on your device and are never uploaded or stored. The page does contact the CDNs above
to fetch the runtime and models, which tells them the site was used, like any site that loads
a library.

## Browser support

- WebGPU needs a **secure context**: `https://` or `localhost`. Plain `http://` on a LAN address
  cannot use it.
- Without WebGPU, Low and (on computers) Medium use the CPU; High and Ultra are unavailable.
- Tested: Chromium-based browsers on macOS and Chrome on Android. Safari and Firefox are not verified.

## Run it locally

```sh
python3 server.py 8080          # this machine only
python3 server_lan.py 8080      # also reachable from a phone on the same Wi-Fi
```

Both serve only the site's own files and send the isolation headers.

## Deploy

Any static host works. Keep `index.html`, `sw.js` and `og.png` at the root. For GitHub Pages:
push to `main`, then Settings → Pages → *Deploy from a branch* → `main` → `/ (root)`.

## Beta status

Verified on 14 Oct 2026 ([release check](RELEASE%20CHECK.md), reproduce with
[tests/README.md](tests/README.md)):

- **MacBook Air M5:** all four engines, full-resolution alpha output, PNG/JPG/clipboard export,
  backgrounds, a 20-image ZIP batch, failed-run retry, and light/dark layouts at 320, 390 and
  1280 px (69 checks).
- **Galaxy A25:** Low on the GPU (about 2 s warm), no horizontal overflow, heavier engines off.

Not verified: other phones and GPUs, Safari, Firefox, older drivers, and mixed batches near the
size limits. Results are good enough to use, not guaranteed. Please report bugs in Issues.

## Licence

Website code: **Apache-2.0**, see [LICENSE](LICENSE). The models and libraries downloaded at
runtime keep their own licences (MODNet Apache-2.0; BEN2, the int8 BEN2 build and ONNX Runtime
Web MIT).

## Credits

Built by **scadavide55**. Model weights by the MODNet and BEN2 authors, repackaged for the
browser by [Xenova](https://huggingface.co/Xenova) and [PramaLLC](https://huggingface.co/PramaLLC).
Inference by [ONNX Runtime Web](https://onnxruntime.ai/).
