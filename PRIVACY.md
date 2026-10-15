# Privacy policy

**Applies to:** Cutout, the browser background remover at <https://scadavide55.github.io/cutout/>,
to local copies of it (`server.py`, `server_lan.py`), and to the source repository
<https://github.com/scadavide55/cutout>.

**Version:** public beta · **Last updated:** 15 October 2026

Cutout has no backend. There is no server of ours to receive your photos, no account, no analytics
and no cookies. Your images are decoded, processed and encoded inside your own browser tab and are
never uploaded, stored or seen by anyone else. This page explains what that promise means in practice,
including what *does* leave your device when the page loads.

## The short version

- **Your images never leave your device.** They are read from your file system or clipboard, held in
  the tab's memory, and written back out as a download. There is no upload step and no server that
  could receive one.
- **Nothing about you is collected.** No analytics, no telemetry, no cookies, no fingerprinting, no
  accounts, no email addresses, no advertising, no tracking pixels.
- **Two small values are kept in your tab** (`sessionStorage`), and they are erased when you close the
  tab. They help the app not reload in a loop and tell you if a run was interrupted by a crash.
- **Your browser does contact other companies** to download the AI models and the inference runtime,
  and once on load for a small health check. Those requests carry your IP address, like any page that
  loads a library. Section *What leaves your device* below names every host.
- **Your images are never used to train any model.** Not ours, not anyone's: nobody else ever has them.
- **The results are yours.** Cutout claims no rights over your images or your exports.

## What the app does with your images

| Step | Where it happens |
|---|---|
| You drop, paste or pick an image | In the page, in your browser |
| Decoding, resizing for the engine, cutting out | On your own GPU or CPU (WebGPU, WebAssembly) |
| Background colour or your background photo | In the page, in your browser |
| PNG / JPG / ZIP export, clipboard copy | Written by your browser to your Downloads folder or clipboard |

At no point is an image sent over the network. The only network requests the app makes are for its own
code and the model files, never for your pictures, and never carrying image data. For the equivalent
promise about what the code *does*, you can read the source: it is one static `index.html` plus `sw.js`.

Because nothing is uploaded, there is nothing for us to store, back up, share or lose. If you close the
tab or your device crashes, work in progress is gone, and no copy exists anywhere else.

## What is stored in your browser

Cutout sets **no cookies** and uses no `localStorage`. Two session-scoped values are written:

| Key | What it holds | Why | Lifetime |
|---|---|---|---|
| `cutout.coi` | the text `1` | The service worker has to reload the page once so the browser applies the cross-origin isolation headers; this flag stops a reload loop | Until you close the tab |
| `cutout.running` | the name of the engine being loaded and its download size, nothing else | If the tab crashes mid-run, the next visit can say the previous run was interrupted instead of failing silently | Removed when you leave the page normally; gone when you close the tab |

Both live in this tab only, are never transmitted anywhere, and contain no image data.

Your browser will also cache the downloaded models and the inference runtime as ordinary HTTP cache
entries, which is what makes the second run fast. That cache can reach roughly 380 MB if you have used
every engine (Low's GPU model 25.9 MB, Medium 130 MB, High and Ultra sharing 223 MB, plus Low's 6.6 MB
CPU fallback if it was ever fetched). Clearing site data in your browser removes all of it. The service worker registered at `/cutout/sw.js` only adds two response headers so that the CPU
path can use several threads; it **caches nothing** and never sees your images.

## What leaves your device

Loading the page and running a cut-out makes your browser talk to these hosts. Requests carry the
usual things a web request always carries: your IP address, your browser's user-agent string, the
address requested, and the referring page.

| Host | What it serves | When |
|---|---|---|
| `scadavide55.github.io` (GitHub Pages) | the page itself, `sw.js`, `og.png` | Every visit |
| `cdn.jsdelivr.net` (jsDelivr) | ONNX Runtime Web 1.24.3, the inference library | On first cut-out |
| `huggingface.co` and its model CDN | the model files (MODNet, the int8 BEN2 build, BEN2) | On first use of each engine |
| `huggingface.co` | one ~300 byte health check file, to detect an outage before a download fails | Once on page load |

None of these requests contain, reference or describe your images. GitHub, jsDelivr and Hugging Face
each process connection data under **their own** privacy policies as independent providers
([GitHub](https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement),
[jsDelivr](https://www.jsdelivr.com/terms/privacy-policy), [Hugging Face](https://huggingface.co/privacy));
we do not receive their logs, and no account or identifier of yours is passed to them.

Two browser features deserve a word. If you **paste** an image (⌘V / Ctrl+V) the page reads the
clipboard at that moment, because you asked it to; if you press **copy** on a result, the export is
written to your system clipboard, again only at your command. Cutout never reads the clipboard on its
own, and never reads anything from it that is not the image you pasted.

GitHub Pages keeps standard server logs (IP address, request, time) for its own security and abuse
purposes. That is the only processing connected to using Cutout that happens on someone else's
machine, and it is done by GitHub as host, not by us.

## Cookies on our page

There are none. There is nothing to track you with, and no consent banner is needed because nothing is
stored or read for any purpose other than running the app in front of you. If you follow the link from
the site to the GitHub repository, you have left Cutout and GitHub's own cookies and policies apply to
that site.

## Your rights under the GDPR

If you are in the EU/EEA or the UK you have the right to access, correct, delete and restrict
processing of your personal data, to object to it, to data portability, and to complain to your
national data protection authority.

The honest position for Cutout: **we hold no personal data about you at all** — no account, no email,
no usage records, no images, no logs of our own (there is no server to log). There is therefore nothing
for us to hand over, correct or erase. The only processing that relates to your visit is the connection
data held briefly by GitHub, jsDelivr and Hugging Face described above; requests about that data must go
to those providers, as they are its controllers.

If you have a question or a request anyway, or you believe something here is inaccurate, open an issue on
the repository (see *Contact*). Please do not put personal details in an issue: the tracker is public.
Say that you want to discuss something privately and we will find a way to get in touch.

## Children

Cutout is not directed at children, collects no data from anyone, and asks for no age. Because nothing
is collected from any user, nothing personal is collected from a child either. Any use by a minor should
be with the awareness of a parent or guardian, as with any tool that processes photos.

## Security and its limits

The strongest protection here is architectural: there is no server holding your images, so there is no
database to breach. The page is served over HTTPS with strict transport from GitHub Pages, and the
service worker only rewrites response headers.

That said, be realistic about the limits. The models come from third-party hosts and could in principle
be tampered with there; your browser and its extensions, your operating system and your downloads folder
are outside our control; and the code is a public beta, verified on a small number of devices
(see the [release check](https://github.com/scadavide55/cutout/blob/main/RELEASE%20CHECK.md)). Treat
Cutout as a convenience tool, not as a place to keep anything.

## Changes to this policy

When this policy changes, the new version is committed to the repository with the date above updated, so
the history of every change is public. Continued use after a change means the current version applies.

## Contact

Questions, corrections and privacy requests: open an issue at
<https://github.com/scadavide55/cutout/issues>. Remember that issues are public — do not include personal
data, and ask for a private channel if you need one.

## Scope note

This policy covers Cutout's own page and code. It does not cover GitHub, jsDelivr, Hugging Face, your
browser, or any site you reach from the links on the page. The model weights bundled at runtime keep
their own licences and their authors' terms; see the repository README for the full list.
