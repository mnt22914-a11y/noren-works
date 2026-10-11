import subprocess, os, http.server, threading, socketserver, functools, json, re
root=os.path.expanduser('~/Projects/noren-works'); PORT=8769
class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*a): pass
class Q(socketserver.TCPServer): allow_reuse_address=True
srv=Q(("127.0.0.1",PORT),functools.partial(H,directory=root)); threading.Thread(target=srv.serve_forever,daemon=True).start()
HT=7000
wrap=os.path.join(root,'_wrap_ig.html')
open(wrap,'w').write('''<!doctype html><html><body style="margin:0;background:#000">
<iframe id="f" src="works/2026-10-05_gym-nightbase/index.html" style="width:375px;height:%dpx;border:0;display:block"></iframe>
<script>
var f=document.getElementById('f');
f.addEventListener('load',function(){setTimeout(function(){
  var w=f.contentWindow,d=w.document;
  try{ if(w.ScrollTrigger){w.ScrollTrigger.getAll().forEach(function(st){ if(st.animation && !st.vars.scrub) st.animation.progress(1); }); } }catch(e){}
  try{ var i=d.querySelector('.intro'); if(i) i.style.display='none'; }catch(e){}
  try{ w.gsap && w.gsap.globalTimeline.progress(1); }catch(e){}
  var out={};
  ['.hero','.hours','.crowd','.safe','.price-sec','.bar','.live','.hero .wrap'].forEach(function(s){var el=d.querySelector(s); if(el){var r=el.getBoundingClientRect(); out[s]=[Math.round(r.top+w.scrollY),Math.round(r.height)];}});
  document.title='POS:'+JSON.stringify(out);
},3500)});
</script></body></html>'''%HT)
chrome='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
base=[chrome,'--headless=new','--disable-gpu','--hide-scrollbars','--no-first-run','--user-data-dir=/tmp/claude-501/chrome-prof-ig',f'--window-size=375,{HT}','--virtual-time-budget=15000']
url=f'http://127.0.0.1:{PORT}/_wrap_ig.html'
r=subprocess.run(base+['--dump-dom',url],capture_output=True,text=True,timeout=90)
m=re.search(r'POS:(\{.*?\})</title>',r.stdout); pos=json.loads(m.group(1)) if m else {}
print('pos',pos)
subprocess.run(base+['--screenshot=ig/full.png',url],capture_output=True,text=True,timeout=90)
os.remove(wrap); srv.shutdown()
from PIL import Image
im=Image.open('ig/full.png').convert('RGB'); print(im.size)
def crop(name,y,h,pad=0):
    y=max(0,y-pad); im.crop((0,y,375,min(im.height,y+h+2*pad))).save(f'ig/{name}.png'); print(name,y,h)
crop('hero',0,812)
if '.safe' in pos: crop('safe',pos['.safe'][0],pos['.safe'][1])
if '.crowd' in pos: crop('crowd',pos['.crowd'][0],pos['.crowd'][1],60)
if '.price-sec' in pos: crop('price',pos['.price-sec'][0],pos['.price-sec'][1])
json.dump(pos,open('ig/pos.json','w'))
