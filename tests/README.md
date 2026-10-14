# Release checks

These are development tools, not dependencies of the website. The site still has no build step.
Tests never upload the selected image. Use a non-sensitive fixture if sharing screenshots.

## Fast helpers

Node 20+:

```sh
node tests/unit_check.js
```

Uses the actual inline functions from `index.html`: target sizing, RGB normalization,
matte normalization, mirrored tensors, ZIP CRC and empty archives, streamed downloads,
HTTP errors, truncated responses, and stalled-download handling with an accelerated clock.
A Unicode ZIP fixture is printed for independent verification.

## Real-browser checks

Requires Python 3.9+, `websocket-client`, Pillow, and a Chromium browser. Brave on macOS
is the default; set `CUTOUT_BROWSER` to another Chromium executable if needed.

Optional isolated development environment:

```sh
python3 -m venv .venv
.venv/bin/pip install websocket-client Pillow
```

Start the allowlisted, concurrent, headerless preview in another terminal:

```sh
python3 tests/preview.py 8091
```

It intentionally omits COOP/COEP so the site's own service worker is exercised. It serves
only the three public assets and binds to localhost, never the LAN or repository internals.

Select an image with `CUTOUT_PHOTO`. For a public fixture:

```sh
curl -L --fail 'https://huggingface.co/datasets/Xenova/transformers.js-docs/resolve/main/woman-with-afro_medium.jpg' -o /tmp/cutout-test-portrait.jpg
```

On a physically capable test computer (8+ cores, 8+ GB RAM, working WebGPU):

```sh
.venv/bin/python tests/release_check.py --high-end
```

`--high-end` overrides only the browser's concurrency hint to 10, because privacy-protecting
browsers clamp it. **It does not emulate a GPU or more RAM. Do not use it to force heavy
models onto weak hardware.** The complete suite expects all four engines to be eligible;
without that flag, an unavailable engine can stop the suite rather than be silently skipped.

Quick 20-image ingestion, duplicate-name ZIP integrity, and full-resolution exports:

```sh
.venv/bin/python tests/release_check.py --batch-only
```

The full suite also covers the native file chooser, keyboard engine selection, PNG/JPG,
clipboard copy, palette/custom colour/photo backgrounds, comparison, failed refinement,
model outage and retry, cancellation, themes, narrow layouts, extreme dimensions, alpha
preservation, and absence of image-upload/POST requests. It runs engines sequentially.
Reports, downloads and screenshots go to a unique system-temporary folder printed at exit.
The temporary browser is always terminated. Browser profiles in those folders are disposable.

## Connected Android

Only use a phone authorized for testing. Keep Chrome in the foreground and the phone unlocked.
Use adb from the Android SDK or platform-tools:

```sh
adb reverse tcp:8091 tcp:8091
adb forward tcp:9222 localabstract:chrome_devtools_remote
.venv/bin/python tests/release_check.py --phone
```

The runner uses the first Chrome page target, navigates it to the preview, checks the engine
guards, runs Low twice, checks alpha/resolution/layout, then leaves that test page blank.
Medium is deliberately not run on the phone: it froze the A25 tab even on the GPU. The test asserts it stays off.
Remove only the forwarding entries created for the test when finished.
