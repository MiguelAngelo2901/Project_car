import webview

HTML = r'''<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"><title>Backrooms Drift — Expediente Eterno</title>
<style>
:root{--bg:#1b170a;--hud:#f6f0c0;--panel:rgba(27,23,10,.6);--paper:#ece3a2;--ink:#2b2510;box-sizing:border-box;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}
@media(prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#120f06;--panel:rgba(18,15,6,.7)}}
:root[data-theme="dark"]{--bg:#120f06;--panel:rgba(18,15,6,.7)}
html{scroll-padding-top:env(safe-area-inset-top,0px)}
html,body{height:100%;margin:0;overflow:hidden;background:var(--bg);color:var(--hud);font-family:"Courier New",Courier,monospace}
canvas{position:fixed;inset:0;width:100%;height:100%;display:block}
.h{position:fixed;background:var(--panel);padding:6px 10px;border-radius:4px;pointer-events:none;text-shadow:0 1px 3px #000}
.h:empty{display:none}
#h-lap{left:12px;top:calc(env(safe-area-inset-top,0px) + 10px);font-size:14px}
#h-score{right:12px;top:calc(env(safe-area-inset-top,0px) + 10px);font-size:18px;font-weight:bold}
#h-ar{right:18px;top:calc(env(safe-area-inset-top,0px) + 52px);font-size:30px;line-height:1}
#h-spd{left:12px;bottom:calc(env(safe-area-inset-bottom,0px) + 14px);font-size:34px;font-weight:bold}
#h-zone{left:50%;top:calc(env(safe-area-inset-top,0px) + 56px);transform:translateX(-50%);max-width:80vw;text-align:center;font-size:16px}
#h-dr{left:50%;top:40%;transform:translateX(-50%);font-size:28px;font-weight:bold;color:#ffe45e}
#h-pa{left:50%;bottom:calc(env(safe-area-inset-bottom,0px) + 14px);transform:translateX(-50%);max-width:70vw;text-align:center;font-style:italic;font-size:15px}
#ov{position:fixed;inset:0;display:flex;align-items:center;justify-content:center;background:rgba(18,15,6,.55);padding:16px}
.memo{background:var(--paper);color:var(--ink);padding:22px 26px;max-width:420px;border-left:8px solid #b8a23a;box-shadow:0 8px 30px #000a;line-height:1.45}
.memo h1{margin:0 0 8px;font-size:32px}.memo p{margin:10px 0;font-size:14px}
.memo button{background:var(--ink);color:var(--paper);border:0;padding:10px 18px;font:inherit;font-size:16px;cursor:pointer;border-radius:3px}
.memo button:focus-visible{outline:3px solid #b8a23a;outline-offset:2px}
</style></head><body>
<div class="h" id="h-lap"></div><div class="h" id="h-score"></div><div class="h" id="h-ar">▲</div><div class="h" id="h-spd"></div><div class="h" id="h-zone"></div><div class="h" id="h-dr"></div><div class="h" id="h-pa"></div>
<div id="ov"><div class="memo"><h1>Expediente Eterno</h1><p>Para: você<br>Assunto: derrapar no escritório</p><p>Nada te persegue. O único risco é a impressora. Contorne os pilares, desvie das cadeiras e siga a seta até fechar a volta.</p><p><b>W A S D</b> ou setas: dirigir<br><b>Espaço</b>: freio de mão (derrapa)<br><b>R</b>: voltar à recepção — <b>M</b>: mudo</p><button id="go">Bater o ponto</button></div></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
const $=i=>document.getElementById(i),S=5,W=52,H=38,G=Array.from({length:H},()=>new Uint8Array(W).fill(1));
const carve=(a,b,c,d,v=0)=>{for(let y=b;y<=d;y++)for(let x=a;x<=c;x++)G[y][x]=v};
[[3,3,48,5],[3,31,48,33],[3,3,5,33],[46,3,48,33],[8,10,26,26],[6,14,7,22],[27,17,29,19],[30,9,44,27],[45,12,45,24]].forEach(r=>carve(...r));
for(let i=0;i<4;i++)for(let k=0;k<2;k++){const x=32+(i%2)*3+k*7;carve(x,12+i*4,Math.min(x+3,43),13+i*4,1)}
for(const x of[10,14,18,22])for(const y of[12,16,20,24])G[y][x]=1;
const solid=(x,y)=>x<0||y<0||x>=W||y>=H||G[y][x]===1;
let sd=7;const rnd=()=>(sd=(sd*16807)%2147483647)/2147483647;
const fl=[];for(let y=0;y<H;y++)for(let x=0;x<W;x++)if(!solid(x,y))fl.push([x,y]);
const R=new THREE.WebGLRenderer({antialias:true});R.setPixelRatio(Math.min(devicePixelRatio,1.5));document.body.prepend(R.domElement);
const scn=new THREE.Scene(),FOG=0xa5963f;scn.background=new THREE.Color(FOG);scn.fog=new THREE.FogExp2(FOG,.011);
const cam=new THREE.PerspectiveCamera(70,1,.3,400);
scn.add(new THREE.AmbientLight(0xfff0b4,.85));const dl=new THREE.DirectionalLight(0xffffff,.35);dl.position.set(.4,1,.2);scn.add(dl);
const hl=new THREE.PointLight(0xfff2c0,1.2,50);scn.add(hl);
const cv=(w,h,f)=>{const c=document.createElement('canvas');c.width=w;c.height=h;f(c.getContext('2d'),w,h);const t=new THREE.CanvasTexture(c);t.wrapS=t.wrapT=THREE.RepeatWrapping;return t};
const mat=c=>new THREE.MeshLambertMaterial({color:c});
const carpet=cv(128,128,(g,w,h)=>{g.fillStyle='#7b6d38';g.fillRect(0,0,w,h);for(let i=0;i<900;i++){g.fillStyle=rnd()<.5?'rgba(40,32,10,.25)':'rgba(170,150,80,.25)';g.fillRect(rnd()*w,rnd()*h,2,2)}});carpet.repeat.set(W*S/5,H*S/5);
const wallT=cv(128,128,(g,w,h)=>{g.fillStyle='#cdb85a';g.fillRect(0,0,w,h);for(let x=0;x<w;x+=16){g.fillStyle='rgba(120,100,30,.18)';g.fillRect(x,0,4,h)}g.fillStyle='rgba(90,70,20,.3)';g.fillRect(0,h-10,w,10)});
const ceilT=cv(64,64,(g,w,h)=>{g.fillStyle='#cfc89a';g.fillRect(0,0,w,h);g.strokeStyle='#a79f70';g.strokeRect(0,0,w,h)});ceilT.repeat.set(W*S/2.5,H*S/2.5);
const pl=(m,y,rx)=>{const p=new THREE.Mesh(new THREE.PlaneGeometry(W*S,H*S),m);p.rotation.x=rx;p.position.set(W*S/2,y,H*S/2);scn.add(p)};
pl(new THREE.MeshLambertMaterial({map:carpet}),0,-Math.PI/2);pl(new THREE.MeshLambertMaterial({map:ceilT}),4,Math.PI/2);
const o=new THREE.Object3D(),wc=[];
for(let y=0;y<H;y++)for(let x=0;x<W;x++)if(G[y][x]&&[[1,0],[-1,0],[0,1],[0,-1],[1,1],[-1,-1],[1,-1],[-1,1]].some(([a,b])=>!solid(x+a,y+b)))wc.push([x,y]);
const wm=new THREE.InstancedMesh(new THREE.BoxGeometry(S,4,S),new THREE.MeshLambertMaterial({map:wallT}),wc.length);wm.frustumCulled=false;
wc.forEach(([x,y],i)=>{o.position.set((x+.5)*S,2,(y+.5)*S);o.updateMatrix();wm.setMatrixAt(i,o.matrix)});scn.add(wm);
// lâmpadas do teto
const LM=[];fl.forEach(([x,y])=>{if(x%3==1&&y%4==0){const n=LM.length;LM.push({x:(x+.5)*S,z:(y+.5)*S,m:n%11==3?0:n%7==2?1:n%13==5?2:(x>=8&&x<=26&&y>=10&&y<=26)?3:4})}});
const lm=new THREE.InstancedMesh(new THREE.BoxGeometry(2.8,.1,1),new THREE.MeshBasicMaterial({color:0xfff6c8}),LM.length);lm.frustumCulled=false;
LM.forEach((l,i)=>{o.position.set(l.x,3.95,l.z);o.updateMatrix();lm.setMatrixAt(i,o.matrix);lm.setColorAt(i,new THREE.Color(1,1,1))});scn.add(lm);
const MORSE=[1,0,1,0,1,0,0,0,1,1,1,0,1,1,1,0,1,1,1,0,0,0,0,0],col=new THREE.Color();
function lights(t){LM.forEach((l,i)=>{let v=1;if(l.m==0)v=.08;else if(l.m==1)v=Math.sin(t*37+i)*Math.sin(t*23.3+i*2)>.5?.12:1;else if(l.m==2)v=MORSE[Math.floor(t*4+i)%MORSE.length]?1:.1;else if(l.m==3)v=(t*2.1)%1<.18?1:.4;else v=Math.sin(t*.7+i*3.1)>.992?.2:1;col.setScalar(v);lm.setColorAt(i,col)});lm.instanceColor.needsUpdate=true}
// cartazes e piadas
const sg=(txt,bg,fg)=>cv(256,128,(g,w,h)=>{g.fillStyle=bg;g.fillRect(0,0,w,h);g.fillStyle=fg;g.font='bold 22px "Courier New"';g.textAlign='center';txt.split('\n').forEach((s,i,a)=>g.fillText(s,w/2,h/2+(i-(a.length-1)/2)*28+7))});
const P={n:(x,y)=>[(x+.5)*S,y*S+.05,0],s:(x,y)=>[(x+.5)*S,(y+1)*S-.05,Math.PI],w:(x,y)=>[x*S+.05,(y+.5)*S,Math.PI/2],e:(x,y)=>[(x+1)*S-.05,(y+.5)*S,-Math.PI/2]};
[['RECEPÇÃO\nLargada e Chegada','#2d5a8c','#fff',8,3,'n'],['TRABALHE EM EQUIPE\n… PARA SEMPRE','#f3ecc0','#3a3210',14,3,'n'],['HOJE É SEXTA!\n(É SEGUNDA)','#f3ecc0','#7a1f1f',22,3,'n'],['SAÍDA  ↑','#1c7a3c','#fff',40,3,'n'],['REUNIÃO ÀS 8H\n(DO MÊS PASSADO)','#f3ecc0','#3a3210',48,12,'e'],['Quem pegou meu\ngrampeador?','#f6e24a','#333',48,26,'e'],['CUIDADO:\nPISO MOLHADO\n(SEMPRE)','#e6c200','#222',20,33,'s'],['Você chegou.\nParabéns?','#f3ecc0','#3a3210',38,33,'s'],['O CAFÉ ACABOU.\nDE NOVO.','#f3ecc0','#7a1f1f',3,24,'w'],['Segunda-feira','#fff','#c33',3,10,'w']].forEach(([t,b,f,x,y,d])=>{const [px,pz,r]=P[d](x,y),m=new THREE.Mesh(new THREE.PlaneGeometry(4.4,2.2),new THREE.MeshBasicMaterial({map:sg(t,b,f)}));m.position.set(px,2.3,pz);m.rotation.y=r;scn.add(m)});
const chk=cv(64,64,g=>{for(let i=0;i<4;i++)for(let j=0;j<4;j++){g.fillStyle=(i+j)%2?'#111':'#fff';g.fillRect(i*16,j*16,16,16)}});chk.repeat.set(1,6);
const sl=new THREE.Mesh(new THREE.PlaneGeometry(2.5,15),new THREE.MeshBasicMaterial({map:chk}));sl.rotation.x=-Math.PI/2;sl.position.set(42.5,.04,22.5);scn.add(sl);
// carro
const car={x:42.5,z:22.5,a:Math.PI/2,vx:0,vz:0,st:0,r:1.6},cn=new THREE.Group(),cg=new THREE.Group();cn.add(cg);scn.add(cn);
const bx=(w,h,d,c,x,y,z)=>{const m=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),mat(c));m.position.set(x,y,z);cg.add(m)};
bx(2.1,.7,4.2,0x2d7dd2,0,.75,0);bx(1.8,.65,2,0x1d4f8a,0,1.4,-.2);bx(1.7,.45,.05,0x101820,0,1.45,.82);bx(.5,.05,4.1,0xffffff,0,1.12,0);bx(2,.1,.5,0x1d4f8a,0,1.7,-2);bx(.4,.2,.1,0xffffcc,-.7,.8,2.12);bx(.4,.2,.1,0xffffcc,.7,.8,2.12);
[[-1,1.4],[1,1.4],[-1,-1.4],[1,-1.4]].forEach(([x,z])=>{const w=new THREE.Mesh(new THREE.CylinderGeometry(.45,.45,.4,12),mat(0x222222));w.rotation.z=Math.PI/2;w.position.set(x*1.05,.45,z);cg.add(w)});
// obstáculos
const props=[],pud=[],ducks=[];
const pick=()=>{for(;;){const[x,y]=fl[Math.floor(rnd()*fl.length)],px=(x+rnd())*S,pz=(y+rnd())*S;if(Math.hypot(px-car.x,pz-car.z)>25)return[px,pz]}};
const addProp=(m,x,z,r,k)=>{m.position.set(x,0,z);scn.add(m);props.push({m,x,z,vx:0,vz:0,r,k,sp:0})};
function chair(){const g=new THREE.Group(),a=(geo,c,x,y,z)=>{const m=new THREE.Mesh(geo,mat(c));m.position.set(x,y,z);g.add(m)};a(new THREE.BoxGeometry(.9,.15,.9),0x2b3140,0,.7,0);a(new THREE.BoxGeometry(.9,.9,.12),0x2b3140,0,1.2,-.42);a(new THREE.CylinderGeometry(.07,.07,.5),0x888888,0,.4,0);a(new THREE.CylinderGeometry(.55,.55,.07,5),0x222222,0,.12,0);return g}
function cone(){const g=new THREE.Group(),c=new THREE.Mesh(new THREE.ConeGeometry(.4,1.1,10),mat(0xff6a1f));c.position.y=.65;g.add(c);const b=new THREE.Mesh(new THREE.BoxGeometry(.9,.08,.9),mat(0x222222));b.position.y=.04;g.add(b);return g}
for(let i=0;i<16;i++){const[x,z]=pick();addProp(chair(),x,z,.9,.8)}
for(let i=0;i<8;i++){addProp(cone(),(18+i*1.5)*S,i%2?19:26,.5,.2);addProp(cone(),i%2?234:241,(10+i*1.5)*S,.5,.2)}
const wmat=new THREE.MeshPhongMaterial({color:0x4f8fb0,transparent:true,opacity:.42,shininess:90});
function duck(x,z){const g=new THREE.Group();[[0,.3,0,.4],[0,.75,.3,.25]].forEach(([a,b,c,r])=>{const m=new THREE.Mesh(new THREE.SphereGeometry(r,10,8),mat(0xffd21f));m.position.set(a,b,c);g.add(m)});const bk=new THREE.Mesh(new THREE.BoxGeometry(.2,.08,.25),mat(0xff7a00));bk.position.set(0,.72,.58);g.add(bk);g.position.set(x,0,z);g.rotation.y=rnd()*6;scn.add(g);ducks.push({g,x,z,h:0,cd:0})}
for(let i=0;i<14;i++){const[x,z]=pick(),r=3+rnd()*3,m=new THREE.Mesh(new THREE.CircleGeometry(r,24),wmat);m.rotation.x=-Math.PI/2;m.position.set(x,.03,z);scn.add(m);pud.push({x,z,r});if(rnd()<.6)duck(x,z)}
const wz=new THREE.Mesh(new THREE.PlaneGeometry(230,15),wmat);wz.rotation.x=-Math.PI/2;wz.position.set(130,.03,162.5);scn.add(wz);for(let i=0;i<8;i++)duck(30+i*28,158+rnd()*10);
const wet=(x,z)=>(z>=155&&z<=170)||pud.some(p=>Math.hypot(x-p.x,z-p.z)<p.r);
// fumaça
const sm=new THREE.InstancedMesh(new THREE.SphereGeometry(.5,6,4),new THREE.MeshBasicMaterial({color:0xefe5ae,transparent:true,opacity:.5}),70),pt=Array.from({length:70},()=>({x:0,y:-9,z:0,l:0}));sm.frustumCulled=false;scn.add(sm);let pi=0;
const puff=(x,z)=>{const p=pt[pi++%70];p.x=x;p.y=.3;p.z=z;p.l=1};
// lâmpadas caindo
const fall=[];let fallT=2;
function spawnFall(dt){fallT-=dt;if(fallT>0||fall.length>3)return;fallT=2+rnd()*2;const d=18+rnd()*22,l=(rnd()-.5)*12,x=car.x+Math.sin(car.a)*d+Math.cos(car.a)*l,z=car.z+Math.cos(car.a)*d-Math.sin(car.a)*l;if(solid(Math.floor(x/S),Math.floor(z/S)))return;
const tb=new THREE.Mesh(new THREE.BoxGeometry(.22,.22,3.4),new THREE.MeshBasicMaterial({color:0xfffbe0}));tb.position.set(x,3.9,z);tb.rotation.y=rnd()*3;const w=new THREE.Mesh(new THREE.RingGeometry(1.3,1.8,24),new THREE.MeshBasicMaterial({color:0xff5533}));w.rotation.x=-Math.PI/2;w.position.set(x,.05,z);scn.add(tb,w);fall.push({tb,w,x,z,t:0,hit:0})}
// colisão com paredes
function wallCollide(q,r,b){let hit=0;const cx=Math.floor(q.x/S),cy=Math.floor(q.z/S);
for(let j=cy-1;j<=cy+1;j++)for(let i=cx-1;i<=cx+1;i++){if(!solid(i,j))continue;const nx=Math.max(i*S,Math.min(q.x,(i+1)*S)),nz=Math.max(j*S,Math.min(q.z,(j+1)*S));let dx=q.x-nx,dz=q.z-nz,d=Math.hypot(dx,dz);
if(d<r){if(d<1e-4){dx=1;dz=0;d=1}dx/=d;dz/=d;q.x+=dx*(r-d);q.z+=dz*(r-d);const vn=q.vx*dx+q.vz*dz;if(vn<0){q.vx-=(1+b)*vn*dx;q.vz-=(1+b)*vn*dz;hit=Math.max(hit,-vn)}}}return hit}
// áudio
let AC,MG,eo,eg,sg2,muted=false;
const tone=(f,g,d,ty,v,dl=0)=>{if(!AC)return;const q=AC.createOscillator(),a=AC.createGain(),t=AC.currentTime+dl;q.type=ty;q.frequency.setValueAtTime(f,t);q.frequency.exponentialRampToValueAtTime(g,t+d);a.gain.setValueAtTime(v,t);a.gain.exponentialRampToValueAtTime(.001,t+d);q.connect(a).connect(MG);q.start(t);q.stop(t+d)};
const sfx={quack(){tone(520,240,.16,'sawtooth',.2);tone(560,300,.12,'square',.08,.1)},boing(){tone(160,600,.3,'sine',.3)},horn(){tone(440,440,.14,'square',.14);tone(350,350,.25,'square',.14,.16)},ding(){tone(1318,1318,.6,'sine',.2);tone(988,988,.8,'sine',.15,.18)}};
const NT=[261.6,329.6,392,493.9,440,392,329.6,293.7];let ni=0,T=0;
function music(){const sp=Math.hypot(car.vx,car.vz);if(AC){const q=AC.createOscillator(),a=AC.createGain(),t=AC.currentTime;q.type='triangle';q.frequency.value=NT[ni++%8]*(1+sp/120);q.detune.value=-30+Math.sin(T)*25;a.gain.setValueAtTime(.06,t);a.gain.exponentialRampToValueAtTime(.001,t+.5);q.connect(a).connect(MG);q.start(t);q.stop(t+.5)}setTimeout(music,Math.max(170,480-sp*7))}
function initAudio(){if(AC)return;AC=new(window.AudioContext||window.webkitAudioContext)();MG=AC.createGain();MG.gain.value=.5;MG.connect(AC.destination);
eo=AC.createOscillator();eo.type='sawtooth';const lp=AC.createBiquadFilter();lp.frequency.value=500;eg=AC.createGain();eg.gain.value=0;eo.connect(lp).connect(eg).connect(MG);eo.start();
const h=AC.createOscillator();h.type='sawtooth';h.frequency.value=60;const hg=AC.createGain();hg.gain.value=.035;const hf=AC.createBiquadFilter();hf.frequency.value=300;h.connect(hf).connect(hg).connect(MG);h.start();
const buf=AC.createBuffer(1,AC.sampleRate,AC.sampleRate),d=buf.getChannelData(0);for(let i=0;i<d.length;i++)d[i]=Math.random()*2-1;
const ns=AC.createBufferSource();ns.buffer=buf;ns.loop=true;const bp=AC.createBiquadFilter();bp.type='bandpass';bp.frequency.value=900;sg2=AC.createGain();sg2.gain.value=0;ns.connect(bp).connect(sg2).connect(MG);ns.start();music()}
// jogo
const ZN={main:'Corredores Principais',plaza:'A Praça dos Pilares — derrape à vontade, pilares não inclusos no seguro',almox:'O Almoxarifado Infinito — o estoque nunca acaba, a paciência sim',agua:'O Corredor Alagado — carpete molhado detectado (sempre)'};
const PA=['Atenção, funcionário: seu turno ainda não acabou.','Lembrete: é proibido derrapar nos corredores. (Mentira.)','A reunião das 3h foi remarcada para 3h… de novo.','Quem estacionou o carro dentro do escritório? Parabéns.','O café acabou. O café sempre acabou.','A saída fica logo ali. Não, ali não.'];
const CP=[[14,4],[30,4],[47,4],[47,18],[47,32],[26,32],[4,32],[4,18],[5,4]].map(([x,y])=>[(x+.5)*S,(y+.5)*S]);
let last=0,run=false,keys={},score=0,pts=0,dtm=0,since=0,lap=1,lapT=0,cpI=0,zone='',zT=0,paT=8,paS=0,pop='',popT=0,ca=car.a;
const say=(t,d=2.2)=>{pop=t;popT=d};
function camUpd(dt,sp){ca+=Math.atan2(Math.sin(car.a-ca),Math.cos(car.a-ca))*Math.min(1,dt*3.2);let d=9+sp*.05;const dx=Math.sin(ca),dz=Math.cos(ca);
while(d>2.5&&solid(Math.floor((car.x-dx*d)/S),Math.floor((car.z-dz*d)/S)))d-=1;cam.position.set(car.x-dx*d,3.4+d*.08,car.z-dz*d);cam.lookAt(car.x+dx*5,1.2,car.z+dz*5);cam.fov=68+sp*.5;cam.updateProjectionMatrix()}
function step(dt){
const up=keys.arrowup||keys.w,dn=keys.arrowdown||keys.s,lf=keys.arrowleft||keys.a,rt=keys.arrowright||keys.d,hb=keys[' '];
let fx=Math.sin(car.a),fz=Math.cos(car.a),vf=car.vx*fx+car.vz*fz;
car.st+=(((lf?1:0)-(rt?1:0))-car.st)*Math.min(1,dt*9);
car.a+=car.st*2.4*Math.max(-1,Math.min(1,vf/9))/(1+Math.abs(vf)/40)*(hb?1.4:1)*dt;
fx=Math.sin(car.a);fz=Math.cos(car.a);const sx=Math.cos(car.a),sz=-Math.sin(car.a);
vf=car.vx*fx+car.vz*fz;let vl=car.vx*sx+car.vz*sz;const w=wet(car.x,car.z);
if(up)vf+=24*dt;if(dn)vf+=(vf>.5?-38:-14)*dt;vf-=vf*(up?.6:.85)*dt;if(hb)vf-=vf*.45*dt;
vl*=Math.exp(-(hb?.9:5.5)*(w?.3:1)*dt);
car.vx=fx*vf+sx*vl;car.vz=fz*vf+sz*vl;car.x+=car.vx*dt;car.z+=car.vz*dt;
const hit=wallCollide(car,car.r,.35),sp=Math.hypot(car.vx,car.vz);
if(hit>5)sfx.boing();if(hit>7&&pts>0){say('Combo perdido! A parede não perdoa.');pts=0;dtm=0}
const dr=Math.abs(vl)>3.2&&sp>8;
if(dr){dtm+=dt;since=0;pts+=Math.abs(vl)*sp*.4*(1+dtm*.4)*dt}else{since+=dt;if(since>.7&&pts>0){const p=Math.round(pts);score+=p;say('+'+p+' pontos');pts=0;dtm=0}}
if(dr||(hb&&sp>6))puff(car.x-fx*1.6+sx*(Math.random()<.5?.9:-.9),car.z-fz*1.6+sz*(Math.random()<.5?.9:-.9));
for(const p of props){p.x+=p.vx*dt;p.z+=p.vz*dt;const k=Math.exp(-1.6*dt);p.vx*=k;p.vz*=k;p.sp*=Math.exp(-2*dt);p.m.rotation.y+=p.sp*dt;wallCollide(p,p.r,.5);
const dx=p.x-car.x,dz=p.z-car.z,d=Math.hypot(dx,dz),m=car.r+p.r;
if(d<m&&d>1e-3){const nx=dx/d,nz=dz/d,rel=(car.vx-p.vx)*nx+(car.vz-p.vz)*nz;if(rel>0){p.vx+=nx*rel*1.5;p.vz+=nz*rel*1.5;car.vx-=nx*rel*.25*p.k;car.vz-=nz*rel*.25*p.k;p.sp+=(Math.random()-.5)*rel*.8;if(rel>5)sfx.boing()}p.x=car.x+nx*m;p.z=car.z+nz*m}
p.m.position.x=p.x;p.m.position.z=p.z}
for(const d of ducks){d.cd-=dt;d.h-=dt*2;if(d.cd<=0&&Math.hypot(d.x-car.x,d.z-car.z)<2.6){sfx.quack();d.h=1;d.cd=1.2}d.g.position.y=Math.max(0,d.h)*1.4+.03*Math.sin(T*2+d.x)}
spawnFall(dt);
for(let i=fall.length-1;i>=0;i--){const f=fall[i];f.t+=dt;if(f.t<1.3)f.w.visible=(f.t*8|0)%2==0;else{f.tb.position.y=Math.max(.12,3.9-(f.t-1.3)*15);if(!f.hit&&f.tb.position.y<=.13){f.hit=1;f.w.visible=false;if(Math.hypot(f.x-car.x,f.z-car.z)<2.8){car.vx*=.55;car.vz*=.55;sfx.horn();say('Lâmpada em queda! (garantia vencida)')}}}
if(f.t>7){scn.remove(f.tb,f.w);fall.splice(i,1)}}
sm.visible=true;pt.forEach((p,i)=>{p.l-=dt*1.4;p.y+=dt*.8;const s=Math.max(0,p.l)*1.6;o.position.set(p.x,p.y,p.z);o.scale.set(s,s,s);o.updateMatrix();sm.setMatrixAt(i,o.matrix)});o.scale.set(1,1,1);sm.instanceMatrix.needsUpdate=true;
const cx=Math.floor(car.x/S),cy=Math.floor(car.z/S),z=(cx>=8&&cx<=26&&cy>=10&&cy<=26)?'plaza':(cx>=30&&cx<=44&&cy>=9&&cy<=27)?'almox':cy>=31?'agua':'main';
if(z!=zone){zone=z;zT=3.2}zT-=dt;
lapT+=dt;if(Math.hypot(car.x-CP[cpI][0],car.z-CP[cpI][1])<13){cpI++;if(cpI==CP.length){cpI=0;sfx.ding();say('Volta '+lap+' completa: '+lapT.toFixed(1)+' s',3.5);lap++;lapT=0}}
paT-=dt;if(paT<=0){const l=PA[Math.floor(Math.random()*PA.length)];paT=30+Math.random()*15;paS=5;$('h-pa').textContent=l;if(!muted)try{const u=new SpeechSynthesisUtterance(l);u.lang='pt-BR';u.pitch=.5;u.rate=.9;speechSynthesis.speak(u)}catch(e){}}
paS-=dt;if(paS<=0)$('h-pa').textContent='';popT-=dt;
cn.position.set(car.x,0,car.z);cn.rotation.y=car.a;cg.rotation.z=-vl*.012;hl.position.set(car.x+fx*4,2.6,car.z+fz*4);
if(AC){eo.frequency.value=40+sp*3.4;eg.gain.value=.04+(up?.06:0);sg2.gain.value=Math.min(.22,Math.abs(vl)*.02+(w&&sp>5?.04:0))}
camUpd(dt,sp);
$('h-spd').textContent=Math.round(sp*3.6)+' km/h';$('h-lap').textContent='Volta '+lap+'   '+lapT.toFixed(1)+' s   ponto '+cpI+'/'+CP.length;$('h-score').textContent='Pontos '+score;
$('h-zone').textContent=zT>0?ZN[zone]:'';$('h-dr').textContent=pts>1?'Drift '+Math.round(pts)+(dtm>2?'  ×'+(1+dtm*.4).toFixed(1):''):popT>0?pop:'';
$('h-ar').style.transform='rotate('+(-(Math.atan2(CP[cpI][0]-car.x,CP[cpI][1]-car.z)-car.a))+'rad)'}
function loop(n){requestAnimationFrame(loop);const dt=Math.min(.05,(n-last)/1000||.016);last=n;T+=dt;if(run)step(dt);lights(T);R.render(scn,cam)}
function resize(){R.setSize(innerWidth,innerHeight);cam.aspect=innerWidth/innerHeight;cam.updateProjectionMatrix()}
addEventListener('resize',resize);resize();camUpd(1,0);
addEventListener('keydown',e=>{const k=e.key.toLowerCase();keys[k]=1;if(k.startsWith('arrow')||k==' ')e.preventDefault();
if(k=='m'){muted=!muted;if(MG)MG.gain.value=muted?0:.5;if(muted)try{speechSynthesis.cancel()}catch(x){}}
if(k=='r'){car.x=42.5;car.z=22.5;car.a=Math.PI/2;car.vx=car.vz=0;cpI=0;lapT=0}});
addEventListener('keyup',e=>{keys[e.key.toLowerCase()]=0});
$('go').onclick=()=>{initAudio();$('ov').style.display='none';run=true};
requestAnimationFrame(loop);
</script></body></html>
'''

if __name__ == '__main__':
    window = webview.create_window(
        'Backrooms Drift — Expediente Eterno',
        html=HTML,
        width=1280,
        height=720,
        resizable=True,
        confirm_close=False
    )
    webview.start()
