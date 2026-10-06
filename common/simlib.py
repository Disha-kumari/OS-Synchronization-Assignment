"""simlib.py - shared helper: records events from the REAL threads and
writes a self-contained HTML replay of that exact trace."""
import json, threading, time


class Recorder:
    """Thread-safe event log. Every state change in the sync code calls this."""

    def __init__(self):
        self._lock = threading.Lock()   # protects the log only (not the problem's resource)
        self._t0 = time.time()
        self.events = []

    def _add(self, e):
        with self._lock:
            e["t"] = round(time.time() - self._t0, 3)
            self.events.append(e)

    def state(self, actor, state, note=""):
        self._add({"type": "state", "actor": actor, "state": state, "note": note})

    def fork(self, fork_id, owner):          # owner = "P1" or None (free)
        self._add({"type": "fork", "fork": fork_id, "owner": owner})


def write_html(path, title, kind, events, actors, nforks=0, notes=()):
    data = {"title": title, "kind": kind, "events": events,
            "actors": actors, "nforks": nforks, "notes": list(notes)}
    html = TEMPLATE.replace("__DATA__", json.dumps(data))
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print("HTML written ->", path)


TEMPLATE = r'''<!DOCTYPE html><html><head><meta charset="utf-8"><title>Simulation</title>
<style>
body{font-family:system-ui,sans-serif;max-width:900px;margin:20px auto;padding:0 12px}
.cards{display:flex;flex-wrap:wrap;gap:10px}.card{padding:10px;border-radius:8px;min-width:110px;text-align:center;border:1px solid #333}
.res{font-size:18px;margin:10px 0;padding:10px;background:#eef;border-radius:8px}
#log{font:12px monospace;background:#111;color:#cfc;padding:8px;height:200px;overflow:auto;border-radius:8px}
button,select{padding:6px 12px;margin:4px}input[type=range]{width:300px}.note{color:#555;font-size:13px}
</style></head><body>
<h2 id="t"></h2><div id="notes" class="note"></div>
<div><button onclick="play()">&#9654; Start</button><button onclick="pause()">&#10074;&#10074; Pause</button>
<button onclick="pause();idx=0;render()">&#8635; Reset</button>
Speed <select id="spd"><option>0.5</option><option selected>1</option><option>2</option><option>5</option></select>
<input id="sl" type="range" min="0" value="0"> <span id="pos"></span></div>
<div id="stage"></div><h4>Event log (from program trace)</h4><div id="log"></div>
<script>
const D=__DATA__;
const COL={idle:'#d1d5db',thinking:'#d1d5db',waiting:'#fbbf24',hungry:'#fbbf24',reading:'#34d399',
 writing:'#f87171',acquiring:'#60a5fa',eating:'#34d399',releasing:'#a78bfa'};
let idx=0,timer=null;
document.getElementById('t').textContent=D.title;
document.getElementById('notes').innerHTML=D.notes.join('<br>');
sl.max=D.events.length;
function compute(n){const st={},fk=Array(D.nforks).fill(null);
 D.actors.forEach(a=>st[a.name]={s:D.kind==='rw'?'idle':'thinking',note:''});
 for(let k=0;k<n;k++){const e=D.events[k];
  if(e.type==='state')st[e.actor]={s:e.state,note:e.note};else fk[e.fork]=e.owner;}
 return {st,fk};}
function render(){
 const {st,fk}=compute(idx);let h='';
 if(D.kind==='rw'){
  const w=D.actors.filter(a=>st[a.name].s==='writing').length,r=D.actors.filter(a=>st[a.name].s==='reading').length;
  h+='<div class=res>Shared resource: <b>'+(w?'WRITING (exclusive)':r?'READ by '+r+' reader(s)':'FREE')+'</b></div><div class=cards>';
  D.actors.forEach(a=>{h+='<div class=card style="background:'+COL[st[a.name].s]+'"><b>'+a.name+'</b><br>'+a.role+'<br>'+st[a.name].s+'<br><small>'+st[a.name].note+'</small></div>';});
  h+='</div>';
 }else{
  const cx=220,cy=220;
  h+='<svg viewBox="0 0 440 440" width="440"><circle cx="220" cy="220" r="70" fill="#a9743a"/>';
  D.actors.forEach((a,i)=>{const g=(i*90-90)*Math.PI/180,x=cx+150*Math.cos(g),y=cy+150*Math.sin(g);
   h+='<circle cx="'+x+'" cy="'+y+'" r="42" fill="'+COL[st[a.name].s]+'" stroke="#333"/>'
    +'<text x="'+x+'" y="'+(y-4)+'" text-anchor="middle" font-size="14" font-weight="bold">'+a.name+'</text>'
    +'<text x="'+x+'" y="'+(y+14)+'" text-anchor="middle" font-size="12">'+st[a.name].s+'</text>';});
  for(let i=0;i<D.nforks;i++){const g=((i+0.5)*90-90)*Math.PI/180,x=cx+90*Math.cos(g),y=cy+90*Math.sin(g);
   h+='<rect x="'+(x-30)+'" y="'+(y-12)+'" width="60" height="24" rx="6" fill="'+(fk[i]===null?'#fff':'#fde047')+'" stroke="#333"/>'
    +'<text x="'+x+'" y="'+(y+4)+'" text-anchor="middle" font-size="11">F'+i+(fk[i]===null?' free':' '+fk[i])+'</text>';}
  h+='</svg>';
 }
 stage.innerHTML=h;sl.value=idx;pos.textContent=idx+' / '+D.events.length;
 let l='';for(let k=Math.max(0,idx-40);k<idx;k++){const e=D.events[k];
  l+=e.t.toFixed(3)+'s  '+(e.type==='state'?e.actor+' -> '+e.state+(e.note?' ('+e.note+')':''):'Fork F'+e.fork+(e.owner===null?' released':' taken by '+e.owner))+'<br>';}
 log.innerHTML=l;log.scrollTop=log.scrollHeight;}
function step(){if(idx<D.events.length){idx++;render();}else pause();}
function play(){if(timer)return;if(idx>=D.events.length)idx=0;timer=setInterval(step,500/+spd.value);}
function pause(){clearInterval(timer);timer=null;}
spd.onchange=()=>{if(timer){pause();play();}};
sl.oninput=()=>{pause();idx=+sl.value;render();};
render();
</script></body></html>'''
