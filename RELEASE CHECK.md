# Release check — 14 October 2026

**Verdict: ready for a public-beta release, not a fully validated stable cross-browser product.**
No GitHub publication was performed during validation. Keep the Beta label.

Tested website code: local commit `46dc5c4`.
HTML SHA-256: `26294677c44dbfdeeccced0fed6659f185fb348eade6e57531f3102bc95b57b8`.

## Verified

- **67/67 desktop release checks passed** on the M5 MacBook Air in Chromium/Brave.
- **15/15 final phone checks passed** on the connected Samsung Galaxy A25.
- **7/7 focused batch checks passed**, including twenty duplicate filenames in one ZIP.
- **8 fast JavaScript checks passed**, plus independent Python verification of the Unicode ZIP.
- JavaScript/Python syntax, Git whitespace checks, sharing image dimensions (1200 × 630),
  server privacy allowlists, and concurrent preview requests passed.

The desktop high-end scenario set only the browser CPU-concurrency hint to 10 to exercise
Ultra's gate on the physically capable M5. GPU and RAM were not emulated. This does not
prove Ultra availability or performance on other browsers/devices.

### Models — 600 × 600 portrait

| Engine | End-to-end desktop run | Outcome |
|---|---:|---|
| Low | 3.54 s | Valid alpha, original resolution |
| Medium | 9.75 s | Valid alpha, original resolution |
| High | 12.98 s | Valid alpha, original resolution |
| Ultra | 4.34 s | Valid alpha; reused High's already-loaded session |

These are sequential measured runs, **not comparable cold-start benchmarks**. Low/Medium/High
include preparation and downloads in a fresh browser profile; Ultra reuses the loaded High
graph and therefore avoids that overhead. Downloads depend on the connection.

Medium/High mask agreement on this portrait: **IoU 0.9996**, at an alpha threshold of 0.5.
This is one test image, not a general accuracy claim.

Final A25 Low runs: **12.66 s first run**, **6.26 s repeat**, both at the original 600 × 600
resolution with meaningful transparent/opaque regions. A25 Medium, High and Ultra are blocked.

### UI and exports

Native primary file chooser; keyboard engine navigation; PNG alpha/resolution; JPG flattening;
PNG clipboard copy; palette, custom-colour and custom-photo backgrounds; hold-to-compare;
change-engine refinement; old result retained after a simulated model outage; real blocked
model request followed by retry; corrupt-image errors; cancellation preserving earlier failures;
clear-all; 320/390/1280 px layouts in light/dark themes; mobile-width engine dialogs; safe
rejection of a 9000-pixel-wide fixture; 21 inputs capped at 20; twenty-image sequential processing;
unique valid ZIP entries; and original input-alpha preservation all passed.

A headerless localhost preview verified that `sw.js` enables cross-origin isolation without
host-provided headers. No runtime was preloaded. No image-upload or POST request was observed
in the desktop test's page-network trace.

## Problems found and addressed

1. **Medium mobile CPU preparation did not finish; the A25 tab became unresponsive.**
   Medium is now disabled on mobile. Do not claim it works on phones.
2. Switching engines retained multiple heavy sessions. The previous graph is now released;
   High/Ultra share one session.
3. Cancelling Retry removed earlier failed inputs. Cancel now removes only the new upload.
4. Applying a matte replaced existing input transparency. Alpha is now multiplied instead.
5. Panoramic Low inputs and full-resolution canvases could allocate unbounded memory.
   Inference input, image dimensions, decoded pixels and batch pixels now have safety limits.
6. Base64 previews and duplicate download buffers inflated memory. Releasable blob previews
   and direct streamed-buffer writes replace them; abandoned backgrounds are closed.
7. Core-count hints sent some desktops down the slow CPU path. Medium now uses eligible
   desktop WebGPU without relying on those privacy-clamped hints.
8. A blanket 25% GPU buffer margin hid working High on the M5. Verified desktop headroom
   is 15%; mobile remains 25%, with separate mobile/RAM guards.
9. The single-threaded temporary/local preview could stall behind an idle connection.
   Concurrent servers passed the idle-connection regression and private-file 404 checks.

## Remaining coverage gaps

- Full inference/export validation in Safari, Firefox, iOS, older drivers, and more GPUs.
- High-resolution mixed batches near the decoded-pixel limits; 20-image testing used repeated
  600 × 600 fixtures, not twenty maximum-size photos.
- Quality review across more subjects. The model guide's earlier six-photo comparison is
  separate from this release's one-portrait runtime/UI validation.
- A safe higher-quality mobile engine. Low remains a portrait-oriented model.
- Live GitHub Pages deployment/cache and social preview verification after an approved push.

Capability checks are conservative safety hints, not proof that a particular driver can run
every graph. The release is suitable as a clearly labelled public beta, not an unconditional
“works everywhere” promise. See `tests/README.md` for reproducing the checks.
