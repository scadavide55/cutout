# Cutout Desktop

Electron app with all four engines and the ONNX runtime bundled. It never goes online.
The website (`../index.html`) is not modified: `main.js` serves it from `app://cutout/` and
answers its model and runtime URLs from local files. `inject.css` / `inject.js` add the
desktop-only look and wording.

```sh
cd desktop
npm install
npm start          # downloads the models once (about 380 MB), then opens the app
npm run dist:mac   # or dist:win / dist:linux, output in desktop/dist
```

Builds are unsigned: macOS shows a Gatekeeper warning (right-click, Open) and Windows shows
SmartScreen. Linux needs working Vulkan for WebGPU. See `THIRD_PARTY.md` for licences.
