#!/usr/bin/env node
// Fast checks of the actual inline helpers; no packages, GPU or model download.
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const html = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');
const source = html.match(/<script>\s*\(function\(\)\{([\s\S]*?)<\/script>/)[1];
const extract = name => {
  let start = source.indexOf('function ' + name + '(');
  if (start < 0) throw Error('Missing helper: ' + name);
  if (source.slice(start - 6, start) === 'async ') start -= 6;
  return source.slice(start, source.indexOf('\n}', start) + 2);
};
const context = vm.createContext({
  AbortController, Response, Headers, Uint8Array, Float32Array, Blob, TextEncoder,
  setTimeout: (fn, ms) => setTimeout(fn, ms === 45000 ? 5 : ms), clearTimeout,
  ort: { Tensor: class { constructor(type, data, dims) { Object.assign(this, { type, data, dims }); } } }
});
vm.runInContext(['targetSize','matteFrom','toTensor','flipTensor','fetchWithProgress'].map(extract).join('\n'), context);
const zipStart = source.indexOf('const CRC_TABLE');
const zipEnd = source.indexOf('async function downloadZip');
vm.runInContext(source.slice(zipStart, zipEnd), context);
const plain = x => JSON.parse(JSON.stringify(x));
const pass = name => console.log('PASS ' + name);

async function main() {
  const model = { square:false, size:512 };
  assert.deepEqual(plain(context.targetSize(600,600,model)), { w:512,h:512 });
  for (const [w,h] of [[100000,100],[100,100000],[8192,1],[1,8192],[300,600]]) {
    const t=context.targetSize(w,h,model);
    assert(t.w<=1024 && t.h<=1024 && t.w>=32 && t.h>=32);
    assert(t.w%32===0 && t.h%32===0);
  }
  assert.deepEqual(plain(context.targetSize(100,1000,{square:true,size:1024})),{w:1024,h:1024});
  pass('target sizes bounded and divisible by 32');

  assert.deepEqual([...context.matteFrom({data:[-2,0,2]},{output:'minmax'})],[0,.5,1]);
  assert.deepEqual([...context.matteFrom({data:[2,2]},{output:'minmax'})],[0,0]);
  const alpha=context.matteFrom({data:[0,.5,1]},{output:'sigmoid'});
  assert.deepEqual([...alpha],[0,.5,1]);
  const logits=context.matteFrom({data:[-3,0,3]},{output:'sigmoid'});
  assert(logits[0]<.05 && logits[1]===.5 && logits[2]>.95);
  pass('matte normalization, constant outputs and logits');

  const input={data:new Uint8Array([255,0,127,255]),width:1,height:1};
  const t=context.toTensor(input,{normalise:'mean05'});
  assert(t.data[0]===1 && t.data[1]===-1 && Math.abs(t.data[2]+1/255)<1e-6);
  const unit=context.toTensor(input,{normalise:'unit'});
  assert(unit.data[0]===1 && unit.data[1]===0 && Math.abs(unit.data[2]-127/255)<1e-6);
  pass('RGB to CHW preprocessing');

  const tensor={dims:[1,1,2,3],data:new Float32Array([1,2,3,4,5,6])};
  const flipped=context.flipTensor(tensor);
  assert.deepEqual([...flipped.data],[3,2,1,6,5,4]);
  assert.deepEqual([...context.flipTensor(flipped).data],[1,2,3,4,5,6]);
  pass('horizontal mirror and round trip');

  assert.equal(context.crc32(new TextEncoder().encode('123456789')),0xcbf43926);
  assert.equal((await context.makeZip([]).arrayBuffer()).byteLength,22);
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'cutout-unit-'));
  const archive=context.makeZip([{name:'café.png',data:new Uint8Array([1,2,3])}]);
  fs.writeFileSync(path.join(dir,'unicode.zip'),Buffer.from(await archive.arrayBuffer()));
  pass('ZIP checksum and empty archive');
  console.log('ZIP fixture: '+path.join(dir,'unicode.zip'));

  let progress=0;
  context.fetch=async()=>new Response(new Uint8Array([1,2,3]),{headers:{'content-length':'3'}});
  assert.deepEqual([...await context.fetchWithProgress('test',v=>progress=v)],[1,2,3]);
  assert.equal(progress,1);
  pass('streamed download with progress');

  context.fetch=async()=>new Response(new Uint8Array([1,2,3]),{headers:{'content-length':'4'}});
  await assert.rejects(()=>context.fetchWithProgress('test',()=>{}),/interrupted/);
  context.fetch=async()=>new Response(null,{status:503});
  await assert.rejects(()=>context.fetchWithProgress('test',()=>{}),/503/);
  pass('truncated download and HTTP errors');

  context.fetch=(_,opts)=>new Promise((resolve,reject)=>opts.signal.addEventListener('abort',()=>reject(Error('abort'))));
  await assert.rejects(()=>context.fetchWithProgress('test',()=>{}),/download stalled/);
  pass('stalled download timeout (clock accelerated)');
}
main().catch(err=>{ console.error(err); process.exitCode=1; });
