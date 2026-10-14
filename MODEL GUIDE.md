## **Model guide**

_This guide helps you pick the right engine for the job. As of 14 Oct 2026, Cutout offers four engines: **Low**, **Medium**, **High** and **Ultra**._

**Not sure? Start with Low. If the edges are not good enough, run the same image again with High.**

| | Low | Medium | High | Ultra |
|---|---|---|---|---|
| Download | 6.6 MB | 130 MB | 223 MB | 223 MB (shared with High) |
| Runs on | CPU | computer, faster with WebGPU | GPU required | high-end computer GPU |
| Speed on a MacBook Air M5 | ~1 s | ~5 s | ~5 s | ~10 s |
| Portraits | great | great | great | great |
| Hair, fur, animals | weak | very good | very good | best |
| Objects, products | weak | very good | very good | best |
| Works on the tested A25 | yes | disabled | disabled | disabled |

_Speeds are for one 600 × 600 photo, measured on one MacBook Air M5, and include loading the model. They will differ on your device, and the first run is slower because the model has to download once._

---

**Low**
An entry-level model. Use it on very limited devices, or when you need the fastest possible speed.
Pros: Very fast, tiny download, runs on practically anything, strong on portraits and well-focused people.
Cons: Dated, and built for people. On animals, objects and busy scenes it often picks the wrong thing to keep: in our test on six varied photos, its cutouts overlapped High's by only about 32% on average. It also struggles with fur, trees and cramped framing, and leaves traces of hair and stray edges.
Uses the MODNet model.

**Medium**
A compressed version of the High model, just under 60% of its size.
Pros: Nearly High-level results. In our test on six varied photos, Medium's cutouts overlapped High's by about **98%** on average; on five of the six the overlap was above 99.5%, and the weakest was 91%. Far better than Low on animals and objects. Uses desktop WebGPU when the buffers fit, or the desktop processor otherwise.
Cons: A 130 MB download. Its CPU preparation left the Galaxy A25 tab unresponsive in the release check, so **Medium is disabled on mobile**. It is the newest engine and has seen less real-world use than Low and High.
Uses a compressed version of the BEN2 model.
_Note: it is still in beta. It was rebuilt on 14 Oct 2026 after an earlier version produced broken cutouts on some photos._

**High**
The full-weights BEN2 model, and Medium's source. Built for laptops, desktops and strong phones with a GPU.
Pros: Very powerful, with excellent edges on hair, fur and products. The reference that the other engines are measured against.
Cons: A 223 MB download that needs WebGPU. It is not offered on phones that cannot hold it in memory (on one mid-range phone it crashed the tab outright), and it is not offered at all without WebGPU, because the processor cannot hold it.
Uses the full BEN2 model.

**Ultra**
High, run twice: once on your image and once on its mirror image, then the two results are blended.
Pros: Settles stray edges and uneven hair where the model changed its mind between the two views. The cleanest result Cutout can produce.
Cons: About twice High's processing time, and the gain over High is **modest, not dramatic**: it is the same model looking twice, not a bigger model. It is only offered on a high-end computer (WebGPU, 8 or more CPU cores, and 8 GB or more of memory when the browser reports it), and it asks you to confirm before it starts.
Uses the full BEN2 model, so there is no extra download if you have already used High.

---

**Image-size safety**
Accepted images keep their original export resolution. To avoid killing the tab, images are limited to 24 MP on desktop, 12 MP on mobile/low-memory devices, and 8192 pixels per side. Batches are limited to 48 MP on desktop or 24 MP on mobile. Low's inference input is bounded to a 1024-pixel longest edge. Capability checks are conservative hints, not a promise that every GPU driver will work.

**Why not a bigger model?**
Larger models exist, and BiRefNet is the strongest of the freely usable ones. Its full version currently fails inside the browser's AI runtime, so it is not offered. Other well-known models, such as RMBG-1.4 and RMBG-2.0, require a paid commercial agreement, so Cutout does not use them.

**What the comparison numbers mean**
"Overlap" is how much of the area two cutouts agree on: 100% means identical, and 0% means they share nothing. High is the reference. The test used six different photos on one computer, so treat the figures as a guide, not a guarantee.
