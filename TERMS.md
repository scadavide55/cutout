# Terms and conditions

**Applies to:** Cutout, the browser background remover at <https://scadavide55.github.io/cutout/>,
and to any local copy of the same code.

**Version:** public beta · **Last updated:** 15 October 2026

## The short version

- Cutout is **free** and has **no account**. Nothing is paid, so nothing is refundable.
- It is a **public beta**: useful, tested, but not verified on every device and browser. Results are not
  guaranteed. **Always keep your original files.**
- **Your images are yours.** Cutout claims no rights over them or over your exports. You may use the
  results commercially.
- It runs **entirely in your browser**. There is no server, no storage and no service-level promise.
- **Use it lawfully**: not to break the law, not to abuse the hosts that serve the models, not to
  mislead people with the images you make.
- The code is **Apache-2.0**; the models keep their own permissive licences.
- **EU consumer law applies** and nothing here takes away rights you have by law. Questions go to the
  repository's issue tracker.

## 1. What Cutout is

Cutout is a free, static web tool that removes the background from images. It is built and maintained by
an independent developer (GitHub: [scadavide55](https://github.com/scadavide55)). It is not a company,
it takes no payments, it sells nothing, and it offers no support contract. There is no account, no
sign-in, no subscription and no uploaded copy of your files.

It is published as open source so that its claims can be checked: the whole app is one `index.html`
and one small `sw.js`. See <https://github.com/scadavide55/cutout>.

## 2. Accepting these terms

By using Cutout you agree to these terms. If you do not agree, do not use it. If you use Cutout on
behalf of an organisation, you confirm you may accept these terms for it.

## 3. Free of charge, no payment, no refunds

Cutout is free and takes no money in any form: no fee, no subscription, no in-app purchase, no
advertising. Since nothing is ever charged, there is nothing to refund or cancel, and no billing or
payment data exists anywhere in the service.

## 4. Your images and your results

You keep everything. Cutout claims no ownership, no licence and no rights over the images you process or
the files you export. Nothing is uploaded, so no copy is made anywhere but on your own device.

You may use your exports for any purpose, including commercial work, subject to the licences of the
models (section 7) and to the law that applies to the content of your own images. You are responsible
for having the right to process the images you load, for example if they show other people or are not
yours.

## 5. Engines, limits and availability

The engines and their limits are part of the service and may change:

| Engine | Model | Download | Practical requirement |
|---|---|---|---|
| Low | MODNet | 25.9 MB (GPU), 6.6 MB (CPU fallback) | works on 4 GB phones |
| Medium | BEN2 int8 | 130 MB | 6 GB+ RAM, off on low-memory phones |
| High | BEN2 | 223 MB | 8 GB+ RAM, GPU |
| Ultra | BEN2, two passes | shares High's download | 12 GB+ RAM, about twice High's time |

Image limits: up to 24 MP per image on desktop, 12 MP on phones and low-memory devices, at most 8192 px
per side; a batch may total 48 MP (desktop) or 24 MP (mobile), 20 images at a time, 30 MB each. Exports
keep the original resolution.

An engine may be shown as unavailable with a reason when the browser lacks WebGPU, reports limited GPU
memory or too little RAM. These are cautious guesses about your device, not guarantees, and a failure can
still happen on a configuration that was expected to work. See the
[model guide](https://github.com/scadavide55/cutout/blob/main/MODEL%20GUIDE.md) for detail.

**Availability.** Cutout needs its model hosts (Hugging Face, jsDelivr) and its own host (GitHub Pages)
to be reachable. Any of them can be down, rate-limited or changed, and the app can simply stop working
for a while. No uptime, no availability and no continuity is promised. The developer may change, move or
withdraw the site at any time, without notice.

## 6. Acceptable use

You agree **not** to:

- use Cutout for anything unlawful, or to process images you have no right to process;
- use it to create misleading or deceptive material, for example passing off an edited image as an
  unedited photograph where that would deceive someone;
- attack, overload or probe the service or the hosts it depends on — including automating bulk downloads
  of the model files from jsDelivr or Hugging Face, or circumventing their rate limits;
- misrepresent Cutout as your own product, or imply that its authors endorse you or your use of it;
- remove or falsify licence, attribution or copyright notices from the code or the model files.

The site is static, so there is no account to suspend. Where a host, a rightsholder or a platform reports
abuse, the developer may withdraw the hosted copy or stop distributing the code at its own discretion.

## 7. Licences: your use of the site, and the code underneath

Using the hosted site is governed by these terms. The **source code** is licensed separately under the
**Apache License 2.0** (see `LICENSE`): if you copy, modify or redistribute the code, that licence — not
these terms — applies to the code, and it requires you to keep the notices intact.

The models and libraries downloaded at runtime are **not** covered by these terms and remain under their
own licences, granted by their authors:

| Component | Licence |
|---|---|
| MODNet (float and quantized weights) | Apache-2.0 |
| BEN2 and the int8 BEN2 build | MIT |
| ONNX Runtime Web 1.24.3 | MIT |

Cutout itself asks nothing of you and takes no royalty for the images you process. It does not use
models that forbid free commercial use, which is why RMBG-1.4 and RMBG-2.0 are not offered.

## 8. Third-party services

The page loads code and models from GitHub Pages, jsDelivr and Hugging Face. Those services are provided
by others under their own terms, and the developer does not control them and is not responsible for
them, for their availability, or for changes they make. Their connection data handling is described in
the [privacy policy](PRIVACY.md).

## 9. No warranty

Cutout is provided **"as is"** and **"as available"**, without warranty of any kind, express or implied,
including any warranty of merchantability, fitness for a particular purpose, accuracy, or
non-infringement. It is a public beta, verified on a limited set of devices and browsers (see the
[release check](https://github.com/scadavide55/cutout/blob/main/RELEASE%20CHECK.md)); Safari, Firefox,
other phones and other GPUs are explicitly not verified.

The developer does not warrant that any cut-out is correct, that hair, fur or fine edges will be handled
well, that a run will finish, that an export will be complete or undamaged, or that the tool will be
available when you need it. **Keep your originals and any important results.** Do not rely on Cutout as
the only copy of anything.

Nothing in this section limits the rights you have by law, in particular your mandatory rights as a
consumer under EU law.

## 10. Limitation of liability

To the widest extent permitted by the law that applies to you, the developer is not liable for any
indirect, incidental, special, consequential or punitive damages, or for any loss of data, images,
files, profit, goodwill or business opportunity, arising from or connected with your use of — or your
inability to use — Cutout.

Because Cutout is provided free of charge and collects nothing from you, the total liability of the
developer for all claims relating to it is limited to the amount you have paid to use it, which is zero.

**Mandatory rights are preserved.** This limitation does not apply where it would be unlawful, and it
does not exclude or limit liability for intent, gross negligence, death or personal injury caused by
negligence, or any other liability that cannot be excluded by the law applicable to you. If you are a
consumer resident in the EU/EEA or the UK, you keep every right your national law gives you, and nothing
in these terms replaces them.

## 11. Changes to these terms

These terms may be updated as the project changes. The current version is always the one committed in the
repository, with the date above updated, so every change is visible in the public history. Continued use
after a change means the updated version applies to you. If you do not accept a change, stop using the
site.

## 12. Governing law and disputes

These terms are governed by the law of the European Union and the applicable law of the country in which
the person using Cutout resides, including that country's mandatory consumer protections. Nothing here
transfers a consumer's rights, and nothing here removes a consumer's right to bring proceedings before
the courts of their own place of residence.

If something goes wrong, please raise it first as a GitHub issue so it can be looked at:
<https://github.com/scadavide55/cutout/issues>. This is a courtesy step, not a condition, and it does not
prevent you from going to a consumer body or a court at any time.

## 13. Contact

<https://github.com/scadavide55/cutout/issues> — issues are public, so please do not post personal data.

---

*By using Cutout you confirm you have read the [privacy policy](PRIVACY.md) and these terms, and that you
accept them.*
