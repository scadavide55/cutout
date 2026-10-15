# Model guide

Cutout has four engines: **Low**, **Medium**, **High** and **Ultra**. All of them run on your
device and try your **GPU first**. The CPU is used only as a last resort, and only where it is safe.


**Not sure? Start with Low. If the edges are not good enough, change the engine on the result and run
it again with Medium or High.**

| | Low | Medium | High | Ultra |
|---|---|---|---|---|
| Download | 25.9 MB (GPU), 6.6 MB (CPU) | 130 MB | 223 MB | 223 MB, shared with High |
| Runs on | GPU, CPU fallback | GPU, computer CPU fallback | GPU only | GPU only |
| Portraits | very good  | very good | very good | very good |
| Hair, fur, animals | weak | decent | very good | very good, slightly cleaner |
| Objects, products | weak | very good | very good | very good, slightly cleaner |
| Relative time | fastest | medium | medium-slow | about 2× High |
| Tested on Galaxy A25 (4 GB) | works, GPU | off | off | off |

## TL;DR : Low=absolute minimum , runs everywhere ; Medium : most balanced , high-level quality while being much faster (high still does better ) ; High : max quality most people need , needs high-end device. Ultra: runs high two times on the same image , so it takes two times the time.  

*Timings are not given as numbers because they depend heavily on your device, and the first run
includes the one-time model download. As a rough reference on a MacBook Air M5, a 600 × 600 photo took
a few seconds including loading.*

## Low

MODNet. The quickest option, and a good one for portraits and well-focused people.

- **Pros:** small download, very fast, works on phones.
- **Cons:** built for people. On animals, objects and busy scenes it often keeps the wrong thing; in a
  six-photo test its cutouts agreed with High's by only about 32% on average. Weak on fur and fine hair.
- **How it runs:** a float version on the GPU (the quantized one cannot run on WebGPU); the 6.6 MB
  quantized version is the CPU fallback.

## Medium

A compressed (int8) version of BEN2, about 58% of High's size while retaining ~91% of the quality ( tested on custom benchmark . Retains ~98% of quality on simple scenarios and ~83% on very difficult scenarios )  .

- **Pros:** close to High. In the same six-photo test its cutouts agreed with High's by about 91% on
  average (above 99.5% on five of six, 83,91% on the weakest). Far better than Low on animals and objects.
- **Cons:** 130 MB download; newer and less battle-tested. It is **off on low-memory phones**: on a
  4 GB Galaxy A25 it froze the tab even on the GPU.
- **How it runs:** GPU first; on computers it can fall back to the CPU, which is slow.
It does run on a 8GB ram phone like a Samsung Galaxy A37 5G , ran in  ~21 seconds.  Doesn't work on less than 6GB of ram. 
## High

The full BEN2 model, and the reference for the others.

- **Pros:** excellent edges on hair, fur and products.
- **Cons:** 223 MB, and it needs a GPU with enough memory. Without one it is not offered, because the
  CPU cannot hold it. On one mid-range phone it crashed the tab.
  Doesn't work under 8GB of ram . Tested on Samsung Galaxy A37 with 8GB of ram. It ran  in ~30 seconds.
  

## Ultra

High, run twice: on your image and on its mirror, then the results are averaged.

- **Pros:** smooths stray edges where the model changed its mind between the two views.
- **Cons:** about twice High's time, and the gain is **modest and not guaranteed**: it is the same model
  looking twice, not a bigger one. It asks you to confirm before starting.
- No extra download if you already used High.
- Doesn't work on less than 12GB of ram . Crashed on the A37 . 

## Why an engine may be unavailable

Cutout checks for WebGPU, the GPU's buffer limit and the memory the browser reports, and disables an
engine with a reason if it would probably not fit. These are cautious guesses, not guarantees, and a
different driver might behave differently.

## Image-size safety

Exports keep the original resolution. To protect the tab, images are limited to 24 MP on desktop, 12 MP
on phones or low-memory devices, and 8192 px per side; batches to 48 MP (desktop) or 24 MP (mobile).
Low's processing input is capped at 1024 px on the longest edge.

## Why not a bigger model?

BiRefNet is a strong, freely licensed model, but its full version failed inside the browser's AI runtime
(WebGPU shader errors, and out-of-memory on the CPU), so it is not offered. A smaller or re-exported
variant might work and has not been tried. RMBG-1.4 and RMBG-2.0 are not licensed for free commercial
use, so Cutout does not use them.

## What the comparison numbers mean

"Agreement" is the overlap between two cutouts: 100% means identical, 0% means nothing in common.
High is only the reference, **not the ground truth**, so agreement with High does not measure how
correct a cutout is. The test used six photos on one computer: treat the figures as a rough guide.
