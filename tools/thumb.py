#!/usr/bin/env python3
"""作品のサムネイルを作る。
使い方: python3 tools/thumb.py <slug> [<slug> ...]   (引数なし = index.json の approved/pending すべて)
出力:   works/<slug>/thumb.jpg (PC 1280×800) と works/<slug>/thumb_sp.jpg (スマホ 375×812)
仕組み: リポジトリをローカル配信し、iframe で包んだ確認ページを headless Chrome で撮る。
        ?static=1 を付け、さらに ScrollTrigger の「スクロール連動でない」tween だけ終了状態にしてから撮る
        (scrub の tween まで進めるとヒーローの文字が消えるため)。オープニング(.intro)は隠す。
必要:   Google Chrome、Pillow(python3 -m pip install pillow)
"""
import sys, os, json, subprocess, http.server, threading, socketserver, functools
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
PORT=8790
class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*a): pass
class Q(socketserver.TCPServer): allow_reuse_address=True
WRAP='''<!doctype html><html><body style="margin:0;background:#000">
<iframe id="f" src="works/%s/index.html?static=1" style="width:%dpx;height:%dpx;border:0;display:block"></iframe>
<script>var f=document.getElementById('f');f.addEventListener('load',function(){setTimeout(function(){
 var w=f.contentWindow,d=w.document;
 try{var i=d.querySelector('.intro');if(i)i.style.display='none';}catch(e){}
 try{if(w.ScrollTrigger){w.ScrollTrigger.getAll().forEach(function(st){if(st.animation&&!st.vars.scrub)st.animation.progress(1);});}}catch(e){}
 try{w.gsap&&w.gsap.globalTimeline.progress(1);}catch(e){}
 try{w.scrollTo(0,0);}catch(e){}
},2500)});</script></body></html>'''
def shoot(slug):
    from PIL import Image
    out=os.path.join(ROOT,'works',slug)
    for name,(w,h) in {'thumb.jpg':(1280,800),'thumb_sp.jpg':(375,812)}.items():
        wrap=os.path.join(ROOT,f'_wrap_{w}.html'); open(wrap,'w').write(WRAP%(slug,w,h))
        png=os.path.join(out,'_tmp.png')
        cmd=[CHROME,'--headless=new','--disable-gpu','--hide-scrollbars','--no-first-run',f'--user-data-dir=/tmp/noren-thumb-{w}',
             f'--window-size={w},{h}','--virtual-time-budget=12000',f'--screenshot={png}',f'http://127.0.0.1:{PORT}/_wrap_{w}.html']
        try: subprocess.run(cmd,capture_output=True,text=True,timeout=90)
        except subprocess.TimeoutExpired: print(slug,name,'timeout'); continue
        finally: os.path.exists(wrap) and os.remove(wrap)
        if os.path.exists(png):
            Image.open(png).convert('RGB').save(os.path.join(out,name),quality=82,optimize=True); os.remove(png); print(slug,name,'ok')
        else: print(slug,name,'failed')
def main():
    slugs=sys.argv[1:]
    if not slugs:
        d=json.load(open(os.path.join(ROOT,'works','index.json'),encoding='utf-8'))
        slugs=[w['slug'] for w in d['works'] if w.get('status') in ('approved','pending')]
    srv=Q(('127.0.0.1',PORT),functools.partial(H,directory=ROOT)); threading.Thread(target=srv.serve_forever,daemon=True).start()
    try:
        for s in slugs: shoot(s)
    finally: srv.shutdown()
if __name__=='__main__': main()
