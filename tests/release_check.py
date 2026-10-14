#!/usr/bin/env python3
"""Sequential real-browser release checks. Requires websocket-client and Pillow.
Desktop: python3 tests/release_check.py
Connected Android: python3 tests/release_check.py --phone
Use CUTOUT_URL to select a preview. Outputs go to /tmp/cutout-release-*.
"""
import base64, io, json, os, pathlib, subprocess, sys, tempfile, time, urllib.request, zipfile
import websocket
from PIL import Image

PHONE = '--phone' in sys.argv
URL = os.environ.get('CUTOUT_URL', 'http://localhost:8091/')
OUT = pathlib.Path(tempfile.mkdtemp(prefix='cutout-release-phone-' if PHONE else 'cutout-release-desktop-'))
PHOTO = pathlib.Path(os.environ.get('CUTOUT_PHOTO', '/tmp/cutout-test-portrait.jpg'))
BRAVE = os.environ.get('CUTOUT_BROWSER', '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser')
PORT = 9222 if PHONE else 9396
checks, events, serial = [], [], 0
browser = None

def check(name, truth, detail=''):
    checks.append({'test':name, 'passed':bool(truth), 'detail':detail})
    print(('PASS ' if truth else 'FAIL ') + name + (' — ' + str(detail) if detail else ''), flush=True)
    if not truth: raise AssertionError(name + ': ' + str(detail))

def cmd(method, **params):
    global serial
    serial += 1
    ws.send(json.dumps({'id':serial,'method':method,'params':params}))
    while True:
        reply = json.loads(ws.recv())
        if reply.get('id') == serial:
            if 'error' in reply: raise RuntimeError(str(reply['error']))
            return reply.get('result', {})
        events.append(reply)

def ev(js, **kwargs):
    result = cmd('Runtime.evaluate', expression=js, returnByValue=True, userGesture=True, **kwargs)
    if 'exceptionDetails' in result:
        raise RuntimeError(str(result['exceptionDetails']))
    return result.get('result',{}).get('value')

def wait(js, seconds=15):
    start=time.monotonic()
    while time.monotonic()-start < seconds:
        if ev(js): return time.monotonic()-start
        time.sleep(.25)
    raise TimeoutError(js[:100])

def inject(name='portrait.jpg', data=None, mime='image/jpeg'):
    b64=base64.b64encode(PHOTO.read_bytes() if data is None else data).decode()
    ev("""(()=>{const s=atob(%s), b=Uint8Array.from(s,c=>c.charCodeAt(0));
      const dt=new DataTransfer();dt.items.add(new File([b],%s,{type:%s}));
      const input=document.getElementById('file');input.files=dt.files;
      input.dispatchEvent(new Event('change',{bubbles:true}));})()""" % (json.dumps(b64),json.dumps(name),json.dumps(mime)))
    wait("document.getElementById('overlay').classList.contains('on')")

def click(selector): ev('document.querySelector(%s).click()' % json.dumps(selector))

def run(mode, limit=90):
    check(mode+' offered', not ev("document.getElementById('opt%s').disabled" % mode.title()))
    click('#opt'+mode.title()); click('#mGo')
    if mode=='ultra':
        check('Ultra explicit confirmation', ev("document.getElementById('mGo').textContent.includes('I understand')"))
        click('#mGo')
    start=time.monotonic()
    wait("!document.body.classList.contains('busy')",limit)
    elapsed=time.monotonic()-start
    error=ev("(document.querySelector('.meta .err')||{}).textContent||''")
    check(mode+' completes', not error, error or ('%.2f s end-to-end' % elapsed))
    wait("!!document.querySelector('.result:not([hidden])') && document.querySelector('.result').naturalWidth>0")
    alpha=ev("""(()=>{const img=[...document.querySelectorAll('.result')].at(-1),c=document.createElement('canvas');
      c.width=img.naturalWidth;c.height=img.naturalHeight;const ctx=c.getContext('2d');ctx.drawImage(img,0,0);
      const d=ctx.getImageData(0,0,c.width,c.height).data;let clear=0,solid=0;
      for(let i=3;i<d.length;i+=4){if(d[i]<8)clear++;if(d[i]>247)solid++;}
      return {w:c.width,h:c.height,clear:clear/(d.length/4),solid:solid/(d.length/4)};})()""")
    check(mode+' meaningful transparent output', alpha['clear']>.02 and alpha['solid']>.05,alpha)
    check(mode+' original resolution', (alpha['w'],alpha['h']) == Image.open(PHOTO).size)
    check(mode+' busy controls restored',not ev("document.getElementById('batchClear').disabled || document.querySelector('.acts button').disabled"))
    screenshot(mode+'-result')
    raw=ev("""(()=>{const img=[...document.querySelectorAll('.result')].at(-1),c=document.createElement('canvas');
      c.width=img.naturalWidth;c.height=img.naturalHeight;c.getContext('2d').drawImage(img,0,0);return c.toDataURL('image/png').split(',')[1]})()""")
    (OUT/(mode+'.png')).write_bytes(base64.b64decode(raw))
    return elapsed

def screenshot(name):
    if PHONE: return # Android screenshot calls can stall when its display sleeps.
    data=cmd('Page.captureScreenshot',format='png')['data']
    (OUT/(name+'.png')).write_bytes(base64.b64decode(data))

def refine():
    click('.refine');wait("document.getElementById('overlay').classList.contains('on')")

def download(selector, name):
    click(selector)
    wait("true",1)
    start=time.monotonic()
    while time.monotonic()-start<12:
        files=list(OUT.glob(name))
        if files: return files[0]
        time.sleep(.2)
    raise TimeoutError('download '+name)

def batch_check():
    b64=base64.b64encode(PHOTO.read_bytes()).decode()
    ev("""(()=>{const b=Uint8Array.from(atob(%s),c=>c.charCodeAt(0)),dt=new DataTransfer();
      for(let n=0;n<21;n++)dt.items.add(new File([b],'batch.jpg',{type:'image/jpeg'}));
      const i=document.getElementById('file');i.files=dt.files;i.dispatchEvent(new Event('change',{bubbles:true}));})()"""%json.dumps(b64))
    wait("document.getElementById('overlay').classList.contains('on')")
    check('21 inputs capped at 20',ev("document.querySelectorAll('.card').length===20"))
    click('#optLow');click('#mGo');wait("!document.body.classList.contains('busy')",60)
    check('20-image batch completes sequentially',ev("document.querySelectorAll('.result:not([hidden])').length===20 && !document.querySelector('.meta .err')"))
    (OUT/'cutout-images.zip').unlink(missing_ok=True)
    archive=download('#batchZip','cutout-images.zip')
    with zipfile.ZipFile(archive) as z:
        check('20 duplicate names have distinct valid ZIP entries',z.testzip() is None and len(z.namelist())==20 and len(set(z.namelist()))==20)
        for name in z.namelist():
            image=Image.open(io.BytesIO(z.read(name)))
            assert image.size==Image.open(PHOTO).size and image.mode=='RGBA'
        check('all 20 archived PNGs keep resolution and transparency',True)
    click('#batchClear')

try:
    if not PHONE:
        browser=subprocess.Popen([BRAVE,'--headless=new','--remote-debugging-port='+str(PORT),
          '--user-data-dir='+str(OUT/'browser-profile'),'--no-first-run','--remote-allow-origins=*','about:blank'],
          stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    for attempt in range(50):
        try:
            tabs=json.load(urllib.request.urlopen('http://127.0.0.1:%d/json/list'%PORT))
            tab=next(x for x in tabs if x.get('type')=='page');break
        except Exception: time.sleep(.2)
    ws=websocket.create_connection(tab['webSocketDebuggerUrl'],timeout=150,suppress_origin=True)
    cmd('Runtime.enable');cmd('Page.enable');cmd('Network.enable');cmd('Page.bringToFront')
    if PHONE: ws.settimeout(20)
    if not PHONE:
        if '--high-end' in sys.argv:
            cmd('Emulation.setHardwareConcurrencyOverride',hardwareConcurrency=10)
            print('High-end scenario: browser concurrency hint set to 10; GPU and RAM are not emulated.',flush=True)
        cmd('Emulation.setDeviceMetricsOverride',width=1280,height=900,deviceScaleFactor=1,mobile=False)
        cmd('Browser.setDownloadBehavior',behavior='allow',downloadPath=str(OUT))
        cmd('Browser.grantPermissions',origin=URL.rstrip('/'),permissions=['clipboardReadWrite','clipboardSanitizedWrite'])
    cmd('Page.navigate',url=URL)
    wait("document.getElementById('capText') && !document.getElementById('capText').textContent.includes('Checking')")
    wait('crossOriginIsolated',15)
    check('service worker enables isolation without host headers',ev('crossOriginIsolated'))
    check('no runtime preload',ev("typeof ort==='undefined'"))
    time.sleep(1)
    check('startup has no uncaught JS errors',not any(x.get('method')=='Runtime.exceptionThrown' for x in events))
    screenshot('landing-dark')
    if '--batch-only' in sys.argv:
        batch_check()
    elif PHONE:
        inject()
        options=ev("Object.fromEntries([...document.querySelectorAll('.opt')].map(o=>[o.id,o.disabled]))")
        check('phone blocks Medium, High and Ultra',options['optMedium'] and options['optHigh'] and options['optUltra'],options)
        run('low',45)
        refine();run('low',30)
        check('phone layout has no horizontal overflow',ev('document.documentElement.scrollWidth <= innerWidth'))
    else:
        # Click the real picker button and satisfy its native file chooser through CDP.
        cmd('Page.setInterceptFileChooserDialog',enabled=True)
        click('#drop')
        check('native image picker opens',any(x.get('method')=='Page.fileChooserOpened' for x in events))
        root=cmd('DOM.getDocument')['root']['nodeId']
        node=cmd('DOM.querySelector',nodeId=root,selector='#file')['nodeId']
        cmd('DOM.setFileInputFiles',files=[str(PHOTO)],nodeId=node)
        wait("document.getElementById('overlay').classList.contains('on')")
        # Keyboard cycle and focus trapping, including the model-guide link.
        cmd('Input.dispatchKeyEvent',type='keyDown',key='ArrowDown',code='ArrowDown',windowsVirtualKeyCode=40)
        check('keyboard changes engine',ev("document.getElementById('optMedium').getAttribute('aria-checked')==='true'"))
        screenshot('engine-dialog')
        run('low')
        check('preview uses releasable blob URL',ev("document.querySelector('.result').src.startsWith('blob:')"))
        png=download('.acts button:nth-child(1)','*-cutout.png')
        im=Image.open(png)
        check('PNG export full size and alpha',im.size==Image.open(PHOTO).size and im.mode=='RGBA')
        jpg=download('.acts button:nth-child(2)','*-cutout.jpg')
        im=Image.open(jpg)
        check('JPG export flattened',im.mode=='RGB' and im.size==Image.open(PHOTO).size)
        click('.acts button:nth-child(3)')
        wait("document.querySelector('.acts button:nth-child(3)').textContent.includes('Copied')")
        check('PNG clipboard copy',True)
        before=ev("document.querySelector('.result').src")
        click('.sw[data-c="b"]')
        wait("document.querySelector('.result').src!=="+json.dumps(before))
        check('background change reuses result',ev("document.querySelector('.sw[data-c=\"b\"]').classList.contains('sel')"))
        colour=ev("document.querySelector('.result').src")
        ev("const i=document.querySelector('.sw[data-c=custom] input');i.value='#cc33aa';i.dispatchEvent(new Event('input',{bubbles:true}))")
        wait("document.querySelector('.result').src!=="+json.dumps(colour))
        check('custom colour updates background',ev("document.querySelector('.sw[data-c=custom]').classList.contains('sel')"))
        root=cmd('DOM.getDocument')['root']['nodeId']
        node=cmd('DOM.querySelector',nodeId=root,selector='.card > input[type=file]')['nodeId']
        cmd('DOM.setFileInputFiles',files=[str(PHOTO)],nodeId=node)
        wait("document.querySelector('.sw[data-c=image]').classList.contains('sel')")
        check('own-photo background works',True)
        click('.sw[data-c="t"]')
        ev("document.querySelector('[data-act=compare]').dispatchEvent(new PointerEvent('pointerdown',{bubbles:true}))")
        check('hold-to-compare activates',ev("document.querySelector('.stage').classList.contains('compare')"))
        ev("document.querySelector('[data-act=compare]').dispatchEvent(new PointerEvent('pointerup',{bubbles:true}))")
        check('hold-to-compare releases',not ev("document.querySelector('.stage').classList.contains('compare')"))
        # A failed refinement must keep the previous successful output.
        refine()
        ev("window.__originalFetch=window.fetch;window.fetch=(input,opts)=>String(input).includes('ben2-int8')?Promise.reject(new TypeError('Simulated model outage')):window.__originalFetch(input,opts)")
        click('#optMedium');click('#mGo');wait("!document.body.classList.contains('busy')")
        check('failed refinement keeps the old cutout',ev("document.querySelector('.meta .err').textContent.includes('Previous cutout kept') && !document.querySelector('.result').hidden && !document.querySelector('.acts button').disabled"))
        ev('window.fetch=window.__originalFetch;delete window.__originalFetch')
        for mode in ['medium','high','ultra']:
            refine();run(mode)
        a=Image.open(OUT/'medium.png').getchannel('A');b=Image.open(OUT/'high.png').getchannel('A')
        av=list(a.getdata());bv=list(b.getdata())
        union=sum(x>127 or y>127 for x,y in zip(av,bv));intersection=sum(x>127 and y>127 for x,y in zip(av,bv))
        check('Medium agrees with High on test portrait',intersection/union>.95,'IoU %.4f'%(intersection/union))
        # Add the same name again to test batch exports and filename collisions.
        inject();run('low')
        archive=download('#batchZip','cutout-images.zip')
        with zipfile.ZipFile(archive) as z:
            check('ZIP integrity and unique filenames',z.testzip() is None and len(z.namelist())==2 and len(set(z.namelist()))==2,z.namelist())
        click('#batchClear')
        check('Clear all restores landing',ev("document.getElementById('workspace').hidden && document.querySelectorAll('.card').length===0"))
        # Corrupt file and cancellation: failures must survive opening/cancelling Retry.
        inject('broken.png',b'not an image','image/png');click('#mGo')
        wait("!document.body.classList.contains('busy')")
        check('corrupt input has actionable error',bool(ev("(document.querySelector('.meta .err')||{}).textContent")))
        click('#retryFailed');wait("document.getElementById('overlay').classList.contains('on')");click('#mCancel')
        check('Cancel Retry preserves failed image',ev("document.querySelectorAll('.card').length===1"))
        inject();click('#mCancel')
        check('Cancel new upload preserves old failure',ev("document.querySelectorAll('.card').length===1"))
        click('#batchClear')
        # A genuine failed model request, then retry after unblocking the server.
        cmd('Page.navigate',url=URL+'?retry-test=1')
        wait("!!document.getElementById('file')")
        cmd('Network.setBlockedURLs',urls=['*model_quantized.onnx*'])
        inject();click('#mGo');wait("!document.body.classList.contains('busy')",45)
        check('network failure is shown',bool(ev("(document.querySelector('.meta .err')||{}).textContent")))
        cmd('Network.setBlockedURLs',urls=[])
        click('#retryFailed');wait("document.getElementById('overlay').classList.contains('on')");run('low')
        click('#batchClear')
        # Check rendering, not just a CSS media query.
        for scheme in ['light','dark']:
            cmd('Emulation.setEmulatedMedia',features=[{'name':'prefers-color-scheme','value':scheme}])
            for width in [320,390,1280]:
                cmd('Emulation.setDeviceMetricsOverride',width=width,height=844,deviceScaleFactor=1,mobile=width<500)
                check('%s layout %d px has no horizontal overflow'%(scheme,width),ev('document.documentElement.scrollWidth<=innerWidth'))
                screenshot('landing-%s-%d'%(scheme,width))
        # Inspect the compact dialog at phone widths, then cancel the upload.
        inject()
        for width in [320,390]:
            cmd('Emulation.setDeviceMetricsOverride',width=width,height=844,deviceScaleFactor=1,mobile=True)
            check('dialog %d px has no horizontal overflow'%width,ev('document.documentElement.scrollWidth<=innerWidth'))
            screenshot('dialog-%d'%width)
        click('#mCancel')
        # A tiny compressed image with an extreme dimension must fail before inference.
        data=io.BytesIO();Image.new('RGB',(9000,1)).save(data,format='PNG')
        inject('too-wide.png',data.getvalue(),'image/png');click('#optLow');click('#mGo')
        wait("!document.body.classList.contains('busy')")
        check('oversized dimension rejected safely',ev("(document.querySelector('.meta .err')||{}).textContent.includes('8192')"))
        click('#batchClear')
        # Full supported batch and filename collisions, without parallel inference.
        batch_check()
        # Pure helpers from the real source, evaluated without loading another graph.
        source=ev("[...document.scripts].find(s=>s.textContent.includes('function targetSize')).textContent")
        def function(name):
            start=source.index('function '+name+'('); end=source.index('\n}',start)+2
            return source[start:end]
        size=ev(function('targetSize')+";targetSize(100000,100,{square:false,size:512})")
        check('panoramic Low input bounded',size['w']<=1024 and size['h']>=32,size)
        alpha=ev(function('makeCanvas')+';'+function('drawCover')+';'+function('compose')+""";
          (()=>{const c=makeCanvas(2,1),x=c.getContext('2d');x.fillStyle='rgba(255,0,0,.5)';x.fillRect(0,0,1,1);
          const out=compose(c,new Float32Array([1,1]),2,1,2,1,null);return [...out.getContext('2d').getImageData(0,0,2,1).data]})()""")
        check('original transparency preserved',127<=alpha[3]<=128 and alpha[7]==0,alpha)
        uploads=[x['params']['request']['url'] for x in events if x.get('method')=='Network.requestWillBeSent' and x['params']['request']['method'] not in ['GET','HEAD','OPTIONS']]
        check('no image uploads or POST requests',not uploads,uploads)
    print('Artifacts: '+str(OUT),flush=True)
finally:
    error = sys.exc_info()[1]
    if error and all(c['passed'] for c in checks):
        checks.append({'test':'test completes within deadline','passed':False,'detail':str(error)})
    (OUT/'report.json').write_text(json.dumps({'phone':PHONE,'url':URL,'high_end_hint':'--high-end' in sys.argv,'status':'failed' if error else 'passed','checks':checks},indent=2))
    if PHONE:
        try:cmd('Page.navigate',url='about:blank')
        except Exception:pass
    if browser:
        browser.terminate()
        try:browser.wait(timeout=5)
        except subprocess.TimeoutExpired:browser.kill()
    print('Report: '+str(OUT/'report.json'),flush=True)
