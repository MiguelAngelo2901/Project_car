# -*- coding: utf-8 -*-
r"""
Backrooms Drift — Expediente Eterno PRO v7.0
- Novo: botão SAIR funcionando (menu principal, menu de pausa e tecla Ctrl+Q)
- Novo: menu de pausa (ESC) com continuar / mapas / loja / gráficos / tela cheia / sair
- Novo: câmeras reescritas (suavizadas, anti-parede, órbita com mouse, olhar para trás, interior com volante)
- Novo: gráficos (sombras, céu, partículas, marcas de pneu, fumaça suave, qualidade ajustável, minimapa)
- Novo: mapas fora das Backrooms — Deserto, Montanha Nevada, Floresta e Cidade Neon (teclas 1-5)
- Save automático em %APPDATA%\BackroomsDrift\save.json
"""

import os
import json
import threading
import webview

HTML = r'''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Backrooms Drift — Expediente Eterno PRO v7.0</title>
<style>
:root {
  --bg: #12100a;
  --hud: #f5f0d0;
  --panel: rgba(20, 18, 10, 0.72);
  --paper: #f0e8b8;
  --ink: #1f1a0c;
  --accent: #e8c84a;
  --accent2: #ff6b35;
  --border: rgba(232, 200, 74, 0.35);
  --shadow: 0 12px 40px rgba(0,0,0,0.55);
  font-family: "Segoe UI", system-ui, -apple-system, sans-serif;
}
html, body { height: 100%; margin: 0; overflow: hidden; background: var(--bg); color: var(--hud); }
body > canvas { position: fixed; inset: 0; width: 100%; height: 100%; display: block; }
button { font-family: inherit; }

/* ===== HUD ===== */
.h {
  position: fixed; background: var(--panel);
  backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
  padding: 8px 14px; border-radius: 10px; border: 1px solid var(--border);
  pointer-events: none; z-index: 10; text-shadow: 0 1px 4px #000; font-weight: 500;
  box-shadow: var(--shadow);
}
.h:empty { display: none; }
.stack { position: fixed; z-index: 10; display: flex; flex-direction: column; gap: 6px; pointer-events: none; }
.stack .h { position: static; }
#hud-tl { left: 14px; top: calc(env(safe-area-inset-top,0px) + 12px); }
#hud-tr { right: 14px; top: calc(env(safe-area-inset-top,0px) + 12px); align-items: flex-end; }
#h-lap { font-size: 14px; }
#h-cam { font-size: 13px; opacity: .9; }
#h-mode { font-size: 12px; opacity: .9; color: #9f9; }
#h-score { font-size: 18px; font-weight: 700; }
#h-money { font-size: 15px; color: #ffe45e; }
#h-bots { font-size: 12px; opacity: .9; }
#h-ar { left: 50%; top: calc(env(safe-area-inset-top,0px) + 10px); transform: translateX(-50%); font-size: 28px; line-height: 1; padding: 6px 14px; }
#h-zone { left: 50%; top: calc(env(safe-area-inset-top,0px) + 64px); transform: translateX(-50%); max-width: 70vw; text-align: center; font-size: 15px; }
#h-spd { left: 14px; bottom: calc(env(safe-area-inset-bottom,0px) + 16px); font-size: 32px; font-weight: 800; letter-spacing: -0.5px; }
#h-dr { left: 50%; top: 38%; transform: translateX(-50%); font-size: 26px; font-weight: 800; color: #ffe45e; text-shadow: 0 0 20px #ffaa00; }
#h-pa { left: 50%; bottom: calc(env(safe-area-inset-bottom,0px) + 16px); transform: translateX(-50%); max-width: 46vw; text-align: center; font-style: italic; font-size: 14px; opacity: .9; }
.hbtn {
  pointer-events: auto; border: none; border-radius: 10px; padding: 9px 16px;
  font: 700 14px system-ui; cursor: pointer; transition: transform .15s, box-shadow .15s;
}
#shop-open { background: linear-gradient(135deg, #e8c84a, #d4a017); color: #1a1608; box-shadow: 0 4px 18px rgba(232,200,74,.4); }
#menu-open { background: rgba(20,18,10,.85); color: var(--hud); border: 1px solid var(--border); }
.hbtn:hover { transform: translateY(-2px); }
#minimap {
  position: fixed; right: 14px; bottom: calc(env(safe-area-inset-bottom,0px) + 16px); width: 210px;
  border-radius: 10px; border: 1px solid var(--border); background: var(--panel);
  box-shadow: var(--shadow); z-index: 10; pointer-events: none;
}
#fx { position: fixed; inset: 0; pointer-events: none; z-index: 8; --v: .2;
  background: radial-gradient(ellipse at center, rgba(0,0,0,0) 58%, rgba(0,0,0,var(--v)) 100%); }
#cockpit { position: fixed; inset: 0; pointer-events: none; display: none; z-index: 6; }
#cockpit .dash { position: absolute; left: 0; right: 0; bottom: 0; height: 24vh; background: linear-gradient(to top, rgba(6,6,6,.96), rgba(6,6,6,0)); }
#wheel { position: absolute; left: 50%; bottom: -16vh; width: min(48vh, 440px); transform: translateX(-50%); }

/* ===== Loja ===== */
#shop {
  position: fixed; z-index: 40; inset: 0; background: rgba(8,7,3,0.9); display: none;
  align-items: center; justify-content: center; padding: 16px; overflow: auto; backdrop-filter: blur(6px);
}
.shopbox {
  width: min(940px, 100%); max-height: 92vh; overflow: auto;
  background: linear-gradient(160deg, #f5ecd0, #e8dca0); color: #1f1a0c; border-radius: 16px;
  border: 2px solid #c9b04a; box-shadow: var(--shadow); padding: 22px;
}
.shophead { display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap; }
.shophead h2 { margin: 0; font-size: 26px; letter-spacing: -0.5px; }
.shophead button, .carcard button {
  background: #1f1a0c; color: #f5ecd0; border: 0; padding: 10px 16px;
  font: 700 14px system-ui; cursor: pointer; border-radius: 8px; transition: background .15s;
}
.shophead button:hover, .carcard button:hover { background: #3a3220; }
#car-list { margin-top: 18px; }
.carcard { background: #fff9e0; border: 2px solid #c9b04a; border-radius: 14px; padding: 18px; box-shadow: 3px 4px 0 #a18d38; }
.carshow { display: grid; grid-template-columns: minmax(0,1.2fr) minmax(220px,1fr); gap: 20px; align-items: center; }
.previewwrap { position: relative; background: radial-gradient(ellipse at center, #6a6040, #1a180f 75%); border: 3px solid #c9b04a; border-radius: 12px; min-height: 260px; overflow: hidden; }
.previewwrap canvas { position: absolute !important; inset: 0 !important; width: 100% !important; height: 100% !important; }
.carinfo h3 { font-size: 24px; margin: 0 0 10px; }
.carinfo p { margin: 7px 0; font-size: 14.5px; }
.carinfo button { width: 100%; margin-top: 14px; padding: 13px; border-radius: 8px; }
.carinfo button:disabled { opacity: .5; cursor: default; }
.cararrows { display: flex; justify-content: space-between; align-items: center; gap: 12px; margin-top: 14px; }
.cararrows button { background: #1f1a0c; color: #f5ecd0; border: 0; border-radius: 50%; width: 48px; height: 48px; font-size: 24px; cursor: pointer; transition: transform .12s; }
.cararrows button:hover { transform: scale(1.08); }
.shopnote { font-size: 12.5px; line-height: 1.5; margin-bottom: 0; opacity: .85; }
@media (max-width: 560px) {
  .carshow { grid-template-columns: 1fr; }
  .previewwrap { min-height: 210px; }
  .carinfo h3 { font-size: 20px; }
}

/* ===== Overlays / menus ===== */
#ov { position: fixed; inset: 0; display: flex; align-items: center; justify-content: center; background: rgba(12,10,5,.6); padding: 16px; z-index: 25; backdrop-filter: blur(4px); }
.memo { background: var(--paper); color: var(--ink); padding: 24px 28px; max-width: 480px; width: 100%; border-radius: 14px; border-left: 6px solid var(--accent); box-shadow: var(--shadow); line-height: 1.5; max-height: 90vh; overflow-y: auto; }
#tracks-memo { max-width: 700px; }
.memo h1 { margin: 0 0 8px; font-size: 28px; letter-spacing: -.5px; }
.memo p { margin: 10px 0; font-size: 14.5px; }
.memo button { background: var(--ink); color: var(--paper); border: 0; padding: 11px 18px; font: 600 14.5px system-ui; cursor: pointer; border-radius: 8px; margin: 5px 5px 0 0; transition: background .15s, transform .12s; }
.memo button:hover { background: #3a3220; transform: translateY(-1px); }
.memo button.sel { outline: 2px solid var(--accent); background: #4a3f1a; }
.menu-section { margin: 14px 0 6px; font-weight: 700; border-bottom: 1px solid #c9b04a; padding-bottom: 4px; font-size: 14px; }
.track-btn, .bot-btn { display: block; width: 100%; text-align: left; margin: 5px 0 !important; }
.map-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(190px, 1fr)); gap: 8px; }
.map-grid button { margin: 0 !important; text-align: left; }
.map-grid .key { opacity: .6; font-weight: 500; font-size: 12px; }
.map-grid .desc, .track-btn .desc, .bot-btn .desc { font-size: 12px; opacity: .75; font-weight: 400; }

#mm, #pause {
  position: fixed; inset: 0; display: flex; align-items: center; justify-content: center; z-index: 30;
  background: radial-gradient(ellipse at center, rgba(40,34,12,.55), rgba(8,7,3,.9));
}
#pause { z-index: 28; display: none; background: rgba(8,7,3,.62); backdrop-filter: blur(3px); }
.mm-box { text-align: center; background: var(--panel); backdrop-filter: blur(14px); padding: 32px 44px; border-radius: 18px; border: 1px solid var(--border); box-shadow: var(--shadow); }
.mm-box h1 { margin: 0 0 4px; font-size: 36px; color: #ffd700; text-shadow: 0 2px 12px #000; letter-spacing: -1px; }
.mm-box .sub { font-size: 13.5px; opacity: .85; margin: 0 0 20px; }
.mm-btn {
  display: block; width: 270px; margin: 8px auto; text-align: center; font-size: 16px; font-weight: 700;
  background: linear-gradient(135deg, #2a2410, #1a160c); color: #f5ecd0; border: 1px solid var(--border);
  border-radius: 10px; padding: 12px 18px; cursor: pointer; transition: all .18s;
}
.mm-btn:hover { outline: 2px solid #ffd700; transform: translateY(-2px); background: linear-gradient(135deg, #3a3220, #2a2410); }
.mm-btn.danger:hover { outline-color: #ff6b35; }
.mm-foot { margin-top: 14px; font-size: 11.5px; opacity: .7; line-height: 1.55; }
#loading { position: fixed; inset: 0; z-index: 50; display: none; align-items: center; justify-content: center; background: rgba(8,7,3,.82); }
.ld-box { text-align: center; font-size: 17px; font-weight: 600; }
.spin { width: 38px; height: 38px; margin: 0 auto 14px; border-radius: 50%; border: 4px solid rgba(232,200,74,.25); border-top-color: var(--accent); animation: sp .8s linear infinite; }
@keyframes sp { to { transform: rotate(360deg); } }
@media (prefers-reduced-motion: reduce) { .spin { animation-duration: 2s; } }
</style>
</head>
<body>
<div id="hud">
  <div id="fx"></div>
  <div id="cockpit">
    <div class="dash"></div>
    <svg id="wheel" viewBox="-100 -100 200 200">
      <circle r="84" fill="none" stroke="#0d0d0d" stroke-width="18"/>
      <circle r="84" fill="none" stroke="#2e2e2e" stroke-width="10"/>
      <rect x="-5" y="-92" width="10" height="16" fill="#e8c84a"/>
      <path d="M-80 0 H-22 M80 0 H22 M0 22 V80" stroke="#151515" stroke-width="14" stroke-linecap="round"/>
      <circle r="22" fill="#101010" stroke="#3a3a3a" stroke-width="3"/>
    </svg>
  </div>
  <div class="stack" id="hud-tl">
    <div class="h" id="h-lap"></div>
    <div class="h" id="h-cam"></div>
    <div class="h" id="h-mode"></div>
  </div>
  <div class="stack" id="hud-tr">
    <div class="h" id="h-score"></div>
    <div class="h" id="h-money">Dinheiro: $0</div>
    <div class="h" id="h-bots"></div>
    <button class="hbtn" id="shop-open" type="button">🚗 LOJA</button>
    <button class="hbtn" id="menu-open" type="button">☰ MENU (ESC)</button>
  </div>
  <div class="h" id="h-ar">▲</div>
  <div class="h" id="h-zone"></div>
  <div class="h" id="h-spd"></div>
  <div class="h" id="h-dr"></div>
  <div class="h" id="h-pa"></div>
  <canvas id="minimap" width="208" height="152"></canvas>
</div>

<!-- Menu Principal -->
<div id="mm">
  <div class="mm-box">
    <h1>EXPEDIENTE ETERNO</h1>
    <p class="sub">Backrooms Drift — PRO v7.0</p>
    <button class="mm-btn" id="mm-play">▶ JOGAR</button>
    <button class="mm-btn" id="mm-tracks">🗺️ MAPAS & PISTAS</button>
    <button class="mm-btn" id="mm-bots">🤖 BOTS</button>
    <button class="mm-btn" id="mm-garage">🚗 LOJA</button>
    <button class="mm-btn" id="mm-gfx">⚙ GRÁFICOS</button>
    <button class="mm-btn danger" id="mm-quit">⏻ SAIR DO JOGO</button>
    <p class="mm-foot" id="mm-cash">Dinheiro: $0</p>
    <p class="mm-foot">WASD dirigir • Espaço freio de mão • C câmera • B olhar para trás<br>1-5 trocar mapa • T trocar pista • G loja • R recepção • M mudo • F tela cheia • ESC pausa</p>
  </div>
</div>

<!-- Pausa -->
<div id="pause">
  <div class="mm-box">
    <h1>PAUSADO</h1>
    <p class="sub">O expediente espera por você.</p>
    <button class="mm-btn" id="pz-resume">▶ CONTINUAR</button>
    <button class="mm-btn" id="pz-maps">🗺️ MAPAS & PISTAS</button>
    <button class="mm-btn" id="pz-garage">🚗 LOJA</button>
    <button class="mm-btn" id="pz-gfx">⚙ GRÁFICOS</button>
    <button class="mm-btn" id="pz-full">🖥 TELA CHEIA</button>
    <button class="mm-btn" id="pz-menu">🏠 MENU PRINCIPAL</button>
    <button class="mm-btn danger" id="pz-quit">⏻ SAIR DO JOGO</button>
  </div>
</div>

<div id="ov" style="display:none">
  <div class="memo" id="tracks-memo" style="display:none">
    <div style="display:flex;justify-content:space-between;align-items:center">
      <h1 style="margin:0;font-size:24px">🗺️ Mapas & Pistas</h1>
      <button id="btn-close-tracks">✕</button>
    </div>
    <div class="menu-section">Mapa (atalhos 1 a 5 durante o jogo)</div>
    <div class="map-grid" id="map-list-menu"></div>
    <div class="menu-section">Pista</div>
    <div id="track-list-menu"></div>
    <button id="btn-play-track" style="margin-top:14px">▶ Jogar neste mapa</button>
  </div>
  <div class="memo" id="bots-memo" style="display:none">
    <div style="display:flex;justify-content:space-between;align-items:center">
      <h1 style="margin:0;font-size:24px">🤖 Bots</h1>
      <button id="btn-close-bots">✕</button>
    </div>
    <p style="font-size:13px">Selecione os oponentes e spawne. Eles seguem os checkpoints da pista.</p>
    <div class="menu-section">Oponentes IA</div>
    <div id="bot-list-menu"></div>
    <button id="btn-spawn-bots" style="margin-top:12px">▶ Spawnar e Jogar</button>
  </div>
</div>

<!-- Loja -->
<div id="shop">
  <div class="shopbox">
    <div class="shophead">
      <h2>🏁 GARAGEM & LOJA</h2>
      <b id="shop-cash">Saldo: $0</b>
      <button id="shop-close" type="button">FECHAR ✕</button>
    </div>
    <p class="shopnote">Compre carros com o dinheiro ganho derrapando. Carros melhores aumentam o pagamento dos drifts e a potência. Cada carro comprado fica desbloqueado.</p>
    <div id="car-list">
      <div class="carcard">
        <div class="carshow">
          <div>
            <div class="previewwrap" id="previewwrap"></div>
            <div class="cararrows">
              <button id="car-prev" aria-label="Carro anterior">❮</button>
              <span id="car-index">1 / 12</span>
              <button id="car-next" aria-label="Próximo carro">❯</button>
            </div>
          </div>
          <div class="carinfo" id="car-info"></div>
        </div>
      </div>
    </div>
  </div>
</div>

<div id="loading"><div class="ld-box"><div class="spin"></div><div id="loading-t">Carregando…</div></div></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
/* =====================================================================
   BASE
   ===================================================================== */
const $ = i => document.getElementById(i);
const S = 5, W = 52, H = 38, CX = W*S/2, CZ = H*S/2;
const clamp = (v,a,b) => Math.max(a, Math.min(b, v));
const angDiff = (a,b) => Math.atan2(Math.sin(a-b), Math.cos(a-b));
const hexs = n => '#' + n.toString(16).padStart(6,'0');
let G = [], fl = [];
const solid = (x,y) => x<0||y<0||x>=W||y>=H||G[y][x]===1;
const gridInit = v => { G = Array.from({length:H}, () => new Uint8Array(W).fill(v)); };
const carve = (a,b,c,d,v=0) => { for(let y=b;y<=d;y++) for(let x=a;x<=c;x++) G[y][x]=v; };
const calcFloor = () => { fl = []; for(let y=0;y<H;y++) for(let x=0;x<W;x++) if(!solid(x,y)) fl.push([x,y]); };
let sd = 7;
const rnd = () => (sd = (sd * 16807) % 2147483647) / 2147483647;
gridInit(1);

/* qualidade gráfica */
const QUALS = [
  {name:'BAIXA', pr:1,    sh:0,    an:1,  smoke:28,  wx:.3,  skid:160},
  {name:'MÉDIA', pr:1.25, sh:1024, an:4,  smoke:48,  wx:.55, skid:320},
  {name:'ALTA',  pr:1.6,  sh:2048, an:8,  smoke:72,  wx:1,   skid:520},
  {name:'ULTRA', pr:2,    sh:4096, an:16, smoke:110, wx:1.5, skid:900}
];
let qIdx = 2;
const Q = () => QUALS[qIdx];

/* =====================================================================
   RENDERER / CENA / LUZES
   ===================================================================== */
const R = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
R.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.prepend(R.domElement);
const scn = new THREE.Scene();
const cam = new THREE.PerspectiveCamera(70, 1, 0.3, 1400);
const amb = new THREE.AmbientLight(0xfff0b4, .85);
const hemi = new THREE.HemisphereLight(0xffffff, 0x444444, 0);
const dl = new THREE.DirectionalLight(0xffffff, .35); dl.position.set(.4,1,.2);
const sun = new THREE.DirectionalLight(0xffffff, 0);
const hl = new THREE.PointLight(0xfff2c0, 1.2, 50);
const head = new THREE.SpotLight(0xfff0d0, 0, 90, .5, .55, 1);
scn.add(amb, hemi, dl, sun, sun.target, hl, head, head.target);
const SHR = 55;
Object.assign(sun.shadow.camera, {left:-SHR, right:SHR, top:SHR, bottom:-SHR, near:1, far:300});
sun.shadow.camera.updateProjectionMatrix();
sun.shadow.bias = -0.0004; sun.shadow.normalBias = .05;
const sunDir = new THREE.Vector3(0,1,0);
const world = new THREE.Group(); scn.add(world);
const _o = new THREE.Object3D();
const _P = new THREE.Object3D(), _C = new THREE.Object3D(); _P.add(_C);

/* ---------- helpers de textura / instâncias ---------- */
const cv = (w,h,f,rep=true) => {
  const c = document.createElement('canvas'); c.width=w; c.height=h;
  f(c.getContext('2d'), w, h);
  const t = new THREE.CanvasTexture(c);
  if(rep) t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.anisotropy = Math.min(Q().an, R.capabilities.getMaxAnisotropy());
  return t;
};
const radial = stops => cv(64,64,g => {
  const r = g.createRadialGradient(32,32,0,32,32,32);
  stops.forEach(([o,c]) => r.addColorStop(o,c));
  g.fillStyle = r; g.fillRect(0,0,64,64);
}, false);
const glowTex = () => radial([[0,'rgba(255,255,255,1)'],[.25,'rgba(255,255,255,.45)'],[1,'rgba(255,255,255,0)']]);
const mat = c => new THREE.MeshLambertMaterial({ color: c });
function disposeObj(g){
  g.traverse(o => {
    if(o.geometry) o.geometry.dispose();
    const ms = o.material ? (Array.isArray(o.material) ? o.material : [o.material]) : [];
    ms.forEach(m => { ['map','emissiveMap','alphaMap'].forEach(k => { if(m[k]) m[k].dispose(); }); m.dispose(); });
  });
}
function inst(geo, material, n){
  const m = new THREE.InstancedMesh(geo, material, Math.max(1,n));
  m.count = n; m.frustumCulled = false; m.castShadow = true; m.receiveShadow = true;
  world.add(m); return m;
}
function setInst(mesh, i, px,pz,ry,sc, lx,ly,lz, lrx=0,lrz=0){
  _P.position.set(px,0,pz); _P.rotation.set(0,ry,0); _P.scale.setScalar(sc);
  _C.position.set(lx,ly,lz); _C.rotation.set(lrx,0,lrz);
  _P.updateMatrixWorld(true);
  mesh.setMatrixAt(i, _C.matrixWorld);
}

/* =====================================================================
   AMBIENTES (iluminação, céu, clima, física por superfície)
   ===================================================================== */
const ENVS = {
  backrooms:{ bg:0xa5963f, fog:0xa5963f, fd:.011, amb:[0xfff0b4,.85], dl:.35, hl:[1.2,50], weather:'motes', wxc:0xfff2b0,
    smoke:0xefe5ae, skid:0x000000, bulbs:true, ceil:4, wetBand:true, mm:['#3a3520','#9a8d52'], pa:'backrooms' },
  nokio:{ bg:0x0a0a18, fog:0x0a0a18, fd:.014, amb:[0xfff0b4,.22], dl:.1, hl:[2.2,70], head:1.6, weather:'motes', wxc:0xcfc0ff,
    smoke:0xcfc0ff, skid:0x000000, bulbs:true, ceil:4, wetBand:true, tint:[0xff4fd8,0x4fd8ff], mm:['#2a1646','#7a4fd0'], pa:'backrooms' },
  desert:{ sky:[0x2f78cc,0x8fbfee,0xf2d9a8], fog:0xe9cf9e, fd:.0042, amb:[0xfff0d8,.42], dl:0, hemi:[0xbfdcff,0xc89a5a,.75],
    sun:[0xfff0d2,1.45,[-70,100,45]], disc:[0xfff4cf,170], weather:'dust', wxc:0xe8d3a5, smoke:0xe5cb98, skid:0x5a3c1a,
    road:true, slide:.85, offSlide:.85, offDrag:1.3, offAcc:.85, mm:['#6b4a28','#d9b27a'] },
  snow:{ sky:[0x6f9fd6,0xb9d4ef,0xe8f1fa], fog:0xdbe8f4, fd:.0068, amb:[0xdfe9ff,.5], dl:0, hemi:[0xd8e8ff,0x8a99b0,.8],
    sun:[0xfff6e6,1.05,[60,80,-50]], disc:[0xffffff,120], weather:'snow', wxc:0xffffff, smoke:0xffffff, skid:0x6d7f93,
    road:true, slide:.5, offSlide:.45, offDrag:1.6, offAcc:.7, mm:['#7f93aa','#eef5fb'] },
  forest:{ sky:[0x4f86c4,0x9cc4e6,0xe4e6c4], fog:0xc3d3b2, fd:.0075, amb:[0xf2f5dc,.5], dl:0, hemi:[0xd4ecff,0x4a5a2a,.75],
    sun:[0xfff0cc,1.1,[-50,70,60]], disc:[0xfff2c8,110], weather:'dust', wxc:0xf2e7a0, smoke:0xcdbf9c, skid:0x2a1c10,
    road:true, slide:.78, offSlide:.8, offDrag:1.35, offAcc:.8, mm:['#2f4a28','#a0864f'] },
  city:{ sky:[0x03040f,0x120c2c,0x2a1650], fog:0x1a1236, fd:.0055, amb:[0x6a74ff,.45], dl:0, hemi:[0x7a8cff,0x2a1a40,.55],
    sun:[0x93a8ff,.5,[-40,80,30]], disc:[0xdfe6ff,90], stars:1, head:2.2, hl:[1.3,45], weather:'rain', wxc:0xaab8ff,
    smoke:0xb8b8d8, skid:0x000000, slide:.82, mm:['#232338','#6a6a88'] }
};
let envKey = 'backrooms';
let ENV = Object.assign({slide:1,offSlide:1,offDrag:1,offAcc:1,road:false}, ENVS.backrooms);

let skyG = null;
function buildSky(e){
  if(skyG){ scn.remove(skyG); disposeObj(skyG); skyG = null; }
  if(!e.sky) return;
  skyG = new THREE.Group();
  const t = cv(4,512,(g,w,h) => {
    const gr = g.createLinearGradient(0,0,0,h);
    gr.addColorStop(0,hexs(e.sky[0])); gr.addColorStop(.42,hexs(e.sky[1])); gr.addColorStop(.5,hexs(e.sky[2]));
    gr.addColorStop(.56,hexs(e.sky[2])); gr.addColorStop(1,hexs(e.fog));
    g.fillStyle = gr; g.fillRect(0,0,w,h);
  }, false);
  const dome = new THREE.Mesh(new THREE.SphereGeometry(1000,24,16), new THREE.MeshBasicMaterial({ map:t, side:THREE.BackSide, fog:false, depthWrite:false }));
  dome.renderOrder = -10; skyG.add(dome);
  if(e.disc){
    const d = new THREE.Sprite(new THREE.SpriteMaterial({ map:glowTex(), color:e.disc[0], fog:false, depthWrite:false, transparent:true, blending:THREE.AdditiveBlending }));
    d.position.copy(sunDir).multiplyScalar(900); d.scale.set(e.disc[1]*2,e.disc[1]*2,1); d.renderOrder = -9; skyG.add(d);
  }
  if(e.stars){
    const n = 700, p = new Float32Array(n*3);
    for(let i=0;i<n;i++){
      const a = Math.random()*6.283, b = Math.random()*1.35 + .05;
      p[i*3] = Math.cos(a)*Math.cos(b)*900; p[i*3+1] = Math.sin(b)*900; p[i*3+2] = Math.sin(a)*Math.cos(b)*900;
    }
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(p,3));
    const st = new THREE.Points(g, new THREE.PointsMaterial({ color:0xffffff, size:1.8, sizeAttenuation:false, fog:false, transparent:true, opacity:.85, depthWrite:false }));
    st.renderOrder = -9; skyG.add(st);
  }
  scn.add(skyG);
}

function applyEnv(e){
  scn.background = new THREE.Color(e.bg !== undefined ? e.bg : e.fog);
  scn.fog = new THREE.FogExp2(e.fog, e.fd);
  amb.color.setHex(e.amb[0]); amb.intensity = e.amb[1];
  dl.intensity = e.dl;
  if(e.hemi){ hemi.color.setHex(e.hemi[0]); hemi.groundColor.setHex(e.hemi[1]); hemi.intensity = e.hemi[2]; } else hemi.intensity = 0;
  if(e.sun){ sun.color.setHex(e.sun[0]); sun.intensity = e.sun[1]; sunDir.set(e.sun[2][0],e.sun[2][1],e.sun[2][2]).normalize(); sun.visible = true; }
  else { sun.intensity = 0; sun.visible = false; }
  const h = e.hl || [0,1]; hl.intensity = h[0]; hl.distance = h[1];
  head.intensity = e.head || 0;
  buildSky(e);
}

function applyQuality(){
  const q = Q();
  R.setPixelRatio(Math.min(window.devicePixelRatio || 1, q.pr));
  R.shadowMap.enabled = q.sh > 0;
  if(q.sh > 0 && sun.shadow.mapSize.x !== q.sh){
    sun.shadow.mapSize.set(q.sh, q.sh);
    if(sun.shadow.map){ sun.shadow.map.dispose(); sun.shadow.map = null; }
  }
  sun.castShadow = q.sh > 0 && !!ENV.sun;
  blob.visible = !sun.castShadow;
  resize();
  scn.traverse(o => { if(o.material) (Array.isArray(o.material) ? o.material : [o.material]).forEach(m => { m.needsUpdate = true; }); });
}

/* =====================================================================
   CLIMA (neve, chuva, poeira) / FUMAÇA / MARCAS DE PNEU
   ===================================================================== */
let wx = null; const WB = 70;
function buildWeather(type){
  if(wx){ scn.remove(wx.o); wx.o.geometry.dispose(); wx.o.material.dispose(); wx = null; }
  if(!type) return;
  const base = {snow:900, rain:900, dust:520, motes:260}[type];
  const n = Math.max(20, Math.round(base * Q().wx)), seg = type === 'rain';
  const X = new Float32Array(n), Y = new Float32Array(n), Z = new Float32Array(n);
  for(let i=0;i<n;i++){ X[i] = Math.random()*WB; Y[i] = Math.random()*WB*.55; Z[i] = Math.random()*WB; }
  const pos = new Float32Array(n * (seg ? 6 : 3));
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos,3));
  let o;
  if(seg) o = new THREE.LineSegments(g, new THREE.LineBasicMaterial({ color:ENV.wxc, transparent:true, opacity:.38 }));
  else {
    const size = {snow:.34, dust:.26, motes:.14}[type];
    o = new THREE.Points(g, new THREE.PointsMaterial({ color:ENV.wxc, size, map:glowTex(), transparent:true, opacity:type==='motes'?.55:.8, depthWrite:false, sizeAttenuation:true }));
  }
  o.frustumCulled = false; scn.add(o);
  wx = { o, n, X, Y, Z, pos, type, seg };
}
const relw = (v,c,L) => { let d = v - c; d -= L*Math.round(d/L); return c + d; };
function updWeather(dt){
  if(!wx) return;
  const { n, X, Y, Z, pos, type, seg } = wx, Hh = WB*.55;
  const cx = cam.position.x, cz = cam.position.z, by = Math.max(0, cam.position.y - 8) + Hh/2;
  for(let i=0;i<n;i++){
    let vx, vy;
    if(type==='snow'){ vx = 1.2 + Math.sin(T+i)*.7; vy = -3.2; }
    else if(type==='rain'){ vx = -3; vy = -48; }
    else if(type==='dust'){ vx = 10; vy = Math.sin(T*.5+i)*.5; }
    else { vx = .3; vy = .15 + Math.sin(T*.4+i)*.1; }
    X[i] += vx*dt; Y[i] += vy*dt; Z[i] += (type==='snow' ? Math.cos(T*.8+i)*.5 : 0)*dt;
    const x = relw(X[i],cx,WB), y = relw(Y[i],by,Hh), z = relw(Z[i],cz,WB);
    if(seg){ pos[i*6]=x; pos[i*6+1]=y; pos[i*6+2]=z; pos[i*6+3]=x+.18; pos[i*6+4]=y+1.7; pos[i*6+5]=z; }
    else { pos[i*3]=x; pos[i*3+1]=y; pos[i*3+2]=z; }
  }
  wx.o.geometry.attributes.position.needsUpdate = true;
}

let smokes = [], smI = 0;
function buildSmoke(){
  const tex = radial([[0,'rgba(255,255,255,.9)'],[.5,'rgba(255,255,255,.4)'],[1,'rgba(255,255,255,0)']]);
  smokes = []; smI = 0;
  for(let i=0;i<Q().smoke;i++){
    const s = new THREE.Sprite(new THREE.SpriteMaterial({ map:tex, color:ENV.smoke, transparent:true, depthWrite:false, opacity:0 }));
    s.visible = false; world.add(s); smokes.push({ s, l:0, vx:0, vy:0, vz:0 });
  }
}
function puff(x,z,vx,vz){
  if(!smokes.length) return;
  const p = smokes[smI++ % smokes.length];
  p.l = 1; p.vx = vx*.2 + (Math.random()-.5)*1.4; p.vz = vz*.2 + (Math.random()-.5)*1.4; p.vy = .9 + Math.random()*.5;
  p.s.position.set(x,.45,z); p.s.visible = true;
}
function updSmoke(dt){
  for(const p of smokes){
    if(p.l <= 0) continue;
    p.l -= dt*.85;
    if(p.l <= 0){ p.s.visible = false; continue; }
    p.s.position.x += p.vx*dt; p.s.position.y += p.vy*dt; p.s.position.z += p.vz*dt;
    const sc = 1.3 + (1-p.l)*3.8; p.s.scale.set(sc,sc,1);
    p.s.material.opacity = Math.min(.5, p.l*.65);
  }
}

let skid = null, skidI = 0, skidAcc = 0;
function buildSkid(){
  const n = Q().skid;
  skid = new THREE.InstancedMesh(new THREE.PlaneGeometry(.34,1.1).rotateX(-Math.PI/2),
    new THREE.MeshBasicMaterial({ color:ENV.skid, transparent:true, opacity:.38, depthWrite:false, polygonOffset:true, polygonOffsetFactor:-2, polygonOffsetUnits:-2 }), n);
  skid.frustumCulled = false; skid.userData.n = n; skidI = 0;
  const z = new THREE.Matrix4().makeScale(0,0,0);
  for(let i=0;i<n;i++) skid.setMatrixAt(i, z);
  skid.instanceMatrix.needsUpdate = true; world.add(skid);
}
function addSkid(x,z,yaw){
  _o.position.set(x,.06,z); _o.rotation.set(0,yaw,0); _o.scale.set(1,1,1); _o.updateMatrix();
  skid.setMatrixAt(skidI++ % skid.userData.n, _o.matrix); skid.instanceMatrix.needsUpdate = true;
}

/* =====================================================================
   CONSTRUÇÃO DE MUNDO — utilitários
   ===================================================================== */
let LM = [], lm = null, lmPool = null;
let props = [], pud = [], ducks = [], statics = [], fall = [];
let ST = {x:42.5, z:22.5, a:Math.PI/2};
let CP = [], ROADSEG = [], ROADHALF = 0;
let bk = null, bkRing = null, bkH = 4;

function clearWorld(){
  disposeObj(world);
  while(world.children.length) world.remove(world.children[0]);
  props = []; pud = []; ducks = []; statics = []; fall = []; LM = []; lm = null; lmPool = null; skid = null; smokes = [];
}
function flatPlane(m,y,rx,w=W*S,h=H*S){
  const p = new THREE.Mesh(new THREE.PlaneGeometry(w,h), m);
  p.rotation.x = rx; p.position.set(CX,y,CZ); p.receiveShadow = true; world.add(p); return p;
}
function buildWalls(o){
  const cells = [];
  for(let y=0;y<H;y++) for(let x=0;x<W;x++)
    if(G[y][x] && [[1,0],[-1,0],[0,1],[0,-1],[1,1],[-1,-1],[1,-1],[-1,1]].some(([a,b]) => !solid(x+a,y+b))) cells.push([x,y,0]);
  if(o.ring) for(let y=-o.ring;y<H+o.ring;y++) for(let x=-o.ring;x<W+o.ring;x++) if(x<0||y<0||x>=W||y>=H) cells.push([x,y,1]);
  const m = new THREE.InstancedMesh(new THREE.BoxGeometry(S,1,S), o.material, cells.length);
  m.frustumCulled = false; m.castShadow = !!o.cast; m.receiveShadow = true;
  const c = new THREE.Color();
  cells.forEach(([x,y,out],i) => {
    const h = o.hmin + (o.hmax - o.hmin) * rnd() * (out ? 1.35 : 1);
    _o.position.set((x+.5)*S, h/2, (y+.5)*S); _o.rotation.set(0,0,0); _o.scale.set(1,h,1); _o.updateMatrix();
    m.setMatrixAt(i, _o.matrix);
    if(o.tint){ c.setHex(o.tint); c.multiplyScalar(.8 + rnd()*.35); m.setColorAt(i,c); }
  });
  world.add(m); return m;
}
function addProp(m,x,z,r,k){
  m.position.set(x,0,z); m.traverse(o => { if(o.isMesh) o.castShadow = true; }); world.add(m);
  props.push({ m, x, z, vx:0, vz:0, r, k, sp:0 });
}
function chair(){
  const g = new THREE.Group();
  const a = (geo,c,x,y,z) => { const m = new THREE.Mesh(geo,mat(c)); m.position.set(x,y,z); g.add(m); };
  a(new THREE.BoxGeometry(.9,.15,.9),0x2b3140,0,.7,0);
  a(new THREE.BoxGeometry(.9,.9,.12),0x2b3140,0,1.2,-.42);
  a(new THREE.CylinderGeometry(.07,.07,.5),0x888888,0,.4,0);
  a(new THREE.CylinderGeometry(.55,.55,.07,5),0x222222,0,.12,0);
  return g;
}
function cone(){
  const g = new THREE.Group();
  const c = new THREE.Mesh(new THREE.ConeGeometry(.4,1.1,10), mat(0xff6a1f)); c.position.y = .65; g.add(c);
  const b = new THREE.Mesh(new THREE.BoxGeometry(.9,.08,.9), mat(0x222222)); b.position.y = .04; g.add(b);
  return g;
}
function barrel(col){
  const g = new THREE.Group();
  const b = new THREE.Mesh(new THREE.CylinderGeometry(.5,.5,1.1,14), mat(col)); b.position.y = .55; g.add(b);
  const r = new THREE.Mesh(new THREE.CylinderGeometry(.52,.52,.1,14), mat(0x222222)); r.position.y = .8; g.add(r);
  return g;
}
function addPatch(x,z,r,col,op){
  const m = new THREE.Mesh(new THREE.CircleGeometry(r,28), new THREE.MeshPhongMaterial({ color:col, transparent:true, opacity:op, shininess:100, depthWrite:false }));
  m.rotation.x = -Math.PI/2; m.position.set(x,.05,z); world.add(m); pud.push({x,z,r}); return m;
}
function duck(x,z){
  const g = new THREE.Group();
  [[0,.3,0,.4],[0,.75,.3,.25]].forEach(([a,b,c,r]) => { const m = new THREE.Mesh(new THREE.SphereGeometry(r,10,8),mat(0xffd21f)); m.position.set(a,b,c); g.add(m); });
  const bk2 = new THREE.Mesh(new THREE.BoxGeometry(.2,.08,.25), mat(0xff7a00)); bk2.position.set(0,.72,.58); g.add(bk2);
  g.position.set(x,0,z); g.rotation.y = rnd()*6; world.add(g); ducks.push({g,x,z,h:0,cd:0});
}
const pickFl = (min=25) => {
  for(let n=0;n<400;n++){
    const [x,y] = fl[Math.floor(rnd()*fl.length)]; const px = (x+rnd())*S, pz = (y+rnd())*S;
    if(Math.hypot(px-ST.x, pz-ST.z) > min) return [px,pz];
  }
  return [ST.x+40, ST.z];
};
const wet = (x,z) => (ENV.wetBand && z>=155 && z<=170) || pud.some(p => Math.hypot(x-p.x, z-p.z) < p.r);

/* estrada (mapas abertos) */
function setRoad(){
  ROADSEG = [];
  for(let i=0;i<CP.length;i++){ const a = CP[i], b = CP[(i+1)%CP.length]; ROADSEG.push([a[0],a[1],b[0],b[1]]); }
}
function roadDist(x,z){
  let best = 1e9;
  for(const [ax,az,bx,bz] of ROADSEG){
    const dx = bx-ax, dz = bz-az, l2 = dx*dx + dz*dz || 1;
    const t = clamp(((x-ax)*dx + (z-az)*dz)/l2, 0, 1);
    const d = Math.hypot(x-(ax+dx*t), z-(az+dz*t));
    if(d < best) best = d;
  }
  return best;
}
function roadPoint(edge){
  for(let t=0;t<30;t++){
    const s = ROADSEG[(rnd()*ROADSEG.length)|0], u = .1 + rnd()*.8, dx = s[2]-s[0], dz = s[3]-s[1], l = Math.hypot(dx,dz) || 1;
    const off = (rnd()<.5 ? -1 : 1) * (ROADHALF - 1.2 - rnd()*edge*3);
    const x = s[0] + dx*u - dz/l*off, z = s[1] + dz*u + dx/l*off;
    if(solid(Math.floor(x/S), Math.floor(z/S)) || Math.hypot(x-ST.x, z-ST.z) < 20) continue;
    return [x,z];
  }
  return null;
}
function roadProps(nCones, nBarrels){
  for(let i=0;i<nCones;i++){ const p = roadPoint(1); if(p) addProp(cone(), p[0], p[1], .5, .2); }
  for(let i=0;i<nBarrels;i++){ const p = roadPoint(.7); if(p) addProp(barrel(i%2 ? 0xd04020 : 0x2b6fd4), p[0], p[1], .6, .5); }
}
function scatter(n, ok){
  const out = []; let t = 0;
  while(out.length < n && t < n*60){
    t++;
    const x = (3.2 + rnd()*(W-6.4))*S, z = (3.2 + rnd()*(H-6.4))*S;
    if(solid(Math.floor(x/S), Math.floor(z/S))) continue;
    if(ok && !ok(x,z)) continue;
    out.push([x,z]);
  }
  return out;
}
const offRoad = m => (x,z) => roadDist(x,z) > ROADHALF + m && Math.hypot(x-ST.x, z-ST.z) > 22;

/* texturas */
const strata = cols => cv(128,256,(g,w,h) => {
  let y = 0;
  while(y < h){ const bh = 6 + rnd()*20; g.fillStyle = cols[(rnd()*cols.length)|0]; g.fillRect(0,y,w,bh); y += bh; }
  for(let i=0;i<900;i++){ g.fillStyle = rnd()<.5 ? 'rgba(0,0,0,.07)' : 'rgba(255,255,255,.06)'; g.fillRect(rnd()*w, rnd()*h, 2+rnd()*4, 1+rnd()*2); }
  const gr = g.createLinearGradient(0,0,0,h); gr.addColorStop(0,'rgba(255,255,255,.12)'); gr.addColorStop(1,'rgba(0,0,0,.18)');
  g.fillStyle = gr; g.fillRect(0,0,w,h);
});
function tileTex(cfg){
  return cv(256,256,(g,w,h) => {
    g.fillStyle = cfg.base; g.fillRect(0,0,w,h);
    for(let i=0;i<3200;i++){ g.fillStyle = cfg.cols[(rnd()*cfg.cols.length)|0]; g.fillRect(rnd()*w, rnd()*h, 2, 2); }
  });
}
function paintField(cfg){
  const cw = 2048, ch = 1536, kx = cw/(W*S), kz = ch/(H*S);
  const c = document.createElement('canvas'); c.width = cw; c.height = ch; const g = c.getContext('2d');
  g.fillStyle = cfg.base; g.fillRect(0,0,cw,ch);
  for(let i=0;i<260;i++){ g.fillStyle = cfg.blob[(rnd()*cfg.blob.length)|0]; g.beginPath(); g.ellipse(rnd()*cw, rnd()*ch, 40+rnd()*140, 25+rnd()*80, rnd()*3, 0, 6.283); g.fill(); }
  for(let i=0;i<cfg.n;i++){ g.fillStyle = cfg.cols[(rnd()*cfg.cols.length)|0]; g.fillRect(rnd()*cw, rnd()*ch, 2+rnd()*3, 2+rnd()*3); }
  g.lineJoin = 'round'; g.lineCap = 'round';
  const path = () => { g.beginPath(); CP.forEach(([x,z],i) => { if(i) g.lineTo(x*kx,z*kz); else g.moveTo(x*kx,z*kz); }); g.closePath(); };
  g.strokeStyle = cfg.shoulder; g.lineWidth = (ROADHALF*2 + 7)*kx; path(); g.stroke();
  g.strokeStyle = cfg.road; g.lineWidth = ROADHALF*2*kx; path(); g.stroke();
  for(let i=0;i<45000;i++){
    const x = rnd()*W*S, z = rnd()*H*S;
    if(roadDist(x,z) < ROADHALF - 1){ g.fillStyle = cfg.rcols[(rnd()*cfg.rcols.length)|0]; g.fillRect(x*kx, z*kz, 2+rnd()*3, 2+rnd()*3); }
  }
  if(cfg.dash){ g.setLineDash([14*kx, 10*kx]); g.strokeStyle = cfg.dash; g.lineWidth = .6*kx; path(); g.stroke(); g.setLineDash([]); }
  const t = new THREE.CanvasTexture(c); t.anisotropy = Math.min(Q().an, R.capabilities.getMaxAnisotropy());
  return t;
}
function openBase(cfg){
  gridInit(0); carve(0,0,W-1,2,1); carve(0,H-3,W-1,H-1,1); carve(0,0,2,H-1,1); carve(W-3,0,W-1,H-1,1);
  for(let n=0;n<(cfg.clusters||0);n++){
    for(let t=0;t<40;t++){
      const w = 3 + ((rnd()*2)|0), h = 2 + ((rnd()*2)|0), x = 4 + ((rnd()*(W-12))|0), y = 4 + ((rnd()*(H-10))|0);
      let ok = true;
      for(let yy=y-1; yy<=y+h && ok; yy++) for(let xx=x-1; xx<=x+w; xx++){
        const px = (xx+.5)*S, pz = (yy+.5)*S;
        if(roadDist(px,pz) < ROADHALF + 8 || Math.hypot(px-ST.x, pz-ST.z) < 30){ ok = false; break; }
      }
      if(ok){ carve(x,y,x+w-1,y+h-1,1); break; }
    }
  }
  calcFloor();
  const field = new THREE.Mesh(new THREE.PlaneGeometry(W*S,H*S), new THREE.MeshLambertMaterial({ map: paintField(cfg.field) }));
  field.rotation.x = -Math.PI/2; field.position.set(CX,.01,CZ); field.receiveShadow = true; world.add(field);
  const ot = tileTex(cfg.tile); ot.repeat.set(2400/36, 2400/36);
  const outer = flatPlane(new THREE.MeshLambertMaterial({ map: ot }), -.02, -Math.PI/2, 2400, 2400);
  buildWalls({ material: new THREE.MeshLambertMaterial({ map: cfg.wallTex() }), hmin: cfg.wh[0], hmax: cfg.wh[1], ring: 3, cast: true, tint: 0xffffff });
}
function staticCollide(q, r, b){
  let hit = 0;
  for(const s of statics){
    const dx = q.x - s.x, dz = q.z - s.z, m = r + s.r;
    if(Math.abs(dx) > m || Math.abs(dz) > m) continue;
    const d2 = dx*dx + dz*dz; if(d2 >= m*m) continue;
    const d = Math.sqrt(d2) || 1e-3, nx = dx/d, nz = dz/d;
    q.x = s.x + nx*m; q.z = s.z + nz*m;
    const vn = q.vx*nx + q.vz*nz;
    if(vn < 0){ q.vx -= (1+b)*vn*nx; q.vz -= (1+b)*vn*nz; hit = Math.max(hit, -vn); }
  }
  return hit;
}
function wallCollide(q, r, b){
  let hit = 0;
  const cx = Math.floor(q.x/S), cy = Math.floor(q.z/S);
  for(let j=cy-1;j<=cy+1;j++) for(let i=cx-1;i<=cx+1;i++){
    if(!solid(i,j)) continue;
    const nx = Math.max(i*S, Math.min(q.x, (i+1)*S));
    const nz = Math.max(j*S, Math.min(q.z, (j+1)*S));
    let dx = q.x-nx, dz = q.z-nz, d = Math.hypot(dx,dz);
    if(d < r){
      if(d < 1e-4){ dx = 1; dz = 0; d = 1; }
      dx /= d; dz /= d;
      q.x += dx*(r-d); q.z += dz*(r-d);
      const vn = q.vx*dx + q.vz*dz;
      if(vn < 0){ q.vx -= (1+b)*vn*dx; q.vz -= (1+b)*vn*dz; hit = Math.max(hit, -vn); }
    }
  }
  return hit;
}

/* =====================================================================
   MAPA 1 — BACKROOMS
   ===================================================================== */
const MORSE = [1,0,1,0,1,0,0,0,1,1,1,0,1,1,1,0,1,1,1,0,0,0,0,0];
const _c = new THREE.Color(), _c2 = new THREE.Color();
function setLampTint(){
  LM.forEach((l,i) => l.tint.setHex(ENV.tint ? ENV.tint[i%2] : 0xffffff));
}
function lights(t){
  if(!lm || !LM.length) return;
  for(let i=0;i<LM.length;i++){
    const l = LM[i]; let v = 1;
    if(l.m===0) v = 0.08;
    else if(l.m===1) v = Math.sin(t*37+i)*Math.sin(t*23.3+i*2) > 0.5 ? 0.12 : 1;
    else if(l.m===2) v = MORSE[Math.floor(t*4+i)%MORSE.length] ? 1 : 0.1;
    else if(l.m===3) v = (t*2.1)%1 < 0.18 ? 1 : 0.4;
    else v = Math.sin(t*0.7+i*3.1) > 0.992 ? 0.2 : 1;
    _c.copy(l.tint).multiplyScalar(v); lm.setColorAt(i,_c);
    if(lmPool){ _c2.copy(_c).multiplyScalar(.5); lmPool.setColorAt(i,_c2); }
  }
  lm.instanceColor.needsUpdate = true;
  if(lmPool) lmPool.instanceColor.needsUpdate = true;
}
const sg = (txt,bg,fg) => cv(256,128,(g,w,h) => {
  g.fillStyle = bg; g.fillRect(0,0,w,h);
  g.fillStyle = fg; g.font = 'bold 22px "Courier New"'; g.textAlign = 'center';
  txt.split('\n').forEach((s,i,a) => g.fillText(s, w/2, h/2 + (i-(a.length-1)/2)*28 + 7));
});
function buildBackrooms(tr){
  sd = 7; gridInit(1);
  [[3,3,48,5],[3,31,48,33],[3,3,5,33],[46,3,48,33],[8,10,26,26],[6,14,7,22],[27,17,29,19],[30,9,44,27],[45,12,45,24]].forEach(r => carve(...r));
  for(let i=0;i<4;i++) for(let k=0;k<2;k++){ const x = 32+(i%2)*3+k*7; carve(x,12+i*4,Math.min(x+3,43),13+i*4,1); }
  for(const x of [10,14,18,22]) for(const y of [12,16,20,24]) G[y][x] = 1;
  calcFloor();

  const carpet = cv(256,256,(g,w,h) => {
    g.fillStyle = '#7b6d38'; g.fillRect(0,0,w,h);
    for(let i=0;i<2600;i++){ g.fillStyle = rnd()<.5 ? 'rgba(40,32,10,.22)' : 'rgba(170,150,80,.22)'; g.fillRect(rnd()*w, rnd()*h, 2, 2); }
    for(let i=0;i<16;i++){ g.strokeStyle = 'rgba(60,48,16,.10)'; g.beginPath(); const y = rnd()*h; g.moveTo(0,y); g.lineTo(w, y+(rnd()-.5)*6); g.stroke(); }
    for(let i=0;i<5;i++){ g.fillStyle = 'rgba(55,42,12,.07)'; g.beginPath(); g.arc(30+rnd()*(w-60), 30+rnd()*(h-60), 10+rnd()*22, 0, 6.3); g.fill(); }
  });
  carpet.repeat.set(W*S/5, H*S/5);
  const wallT = cv(256,256,(g,w,h) => {
    g.fillStyle = '#cdb85a'; g.fillRect(0,0,w,h);
    for(let x=0;x<w;x+=32){ g.fillStyle = 'rgba(120,100,30,.18)'; g.fillRect(x,0,8,h); }
    for(let i=0;i<1200;i++){ g.fillStyle = rnd()<.5 ? 'rgba(255,240,150,.05)' : 'rgba(70,55,10,.05)'; g.fillRect(rnd()*w, rnd()*h, 2, 3); }
    const gr = g.createLinearGradient(0,0,0,h); gr.addColorStop(0,'rgba(0,0,0,.18)'); gr.addColorStop(.25,'rgba(0,0,0,0)');
    g.fillStyle = gr; g.fillRect(0,0,w,h);
    g.fillStyle = 'rgba(90,70,20,.35)'; g.fillRect(0,h-20,w,20);
  });
  const ceilT = cv(128,128,(g,w,h) => {
    g.fillStyle = '#cfc89a'; g.fillRect(0,0,w,h);
    for(let i=0;i<500;i++){ g.fillStyle = rnd()<.5 ? 'rgba(0,0,0,.05)' : 'rgba(255,255,255,.06)'; g.fillRect(rnd()*w, rnd()*h, 2, 2); }
    g.strokeStyle = '#a79f70'; g.lineWidth = 2; g.strokeRect(0,0,w,h);
  });
  ceilT.repeat.set(W*S/2.5, H*S/2.5);
  flatPlane(new THREE.MeshLambertMaterial({ map: carpet }), 0, -Math.PI/2);
  flatPlane(new THREE.MeshLambertMaterial({ map: ceilT }), 4, Math.PI/2).receiveShadow = false;
  buildWalls({ material: new THREE.MeshLambertMaterial({ map: wallT }), hmin: 4, hmax: 4 });

  fl.forEach(([x,y]) => {
    if(x%3===1 && y%4===0){
      const n = LM.length;
      LM.push({ x:(x+.5)*S, z:(y+.5)*S, tint:new THREE.Color(1,1,1),
        m: n%11===3?0 : n%7===2?1 : n%13===5?2 : (x>=8&&x<=26&&y>=10&&y<=26)?3 : 4 });
    }
  });
  lm = new THREE.InstancedMesh(new THREE.BoxGeometry(2.8,.1,1), new THREE.MeshBasicMaterial({ color:0xfff6c8 }), LM.length);
  lm.frustumCulled = false;
  lmPool = new THREE.InstancedMesh(new THREE.PlaneGeometry(9,9).rotateX(-Math.PI/2),
    new THREE.MeshBasicMaterial({ map:glowTex(), color:0xfff0b0, transparent:true, blending:THREE.AdditiveBlending, depthWrite:false }), LM.length);
  lmPool.frustumCulled = false;
  LM.forEach((l,i) => {
    _o.position.set(l.x,3.95,l.z); _o.rotation.set(0,0,0); _o.scale.set(1,1,1); _o.updateMatrix(); lm.setMatrixAt(i,_o.matrix); lm.setColorAt(i,_c.setRGB(1,1,1));
    _o.position.set(l.x,.035,l.z); _o.updateMatrix(); lmPool.setMatrixAt(i,_o.matrix); lmPool.setColorAt(i,_c.setRGB(.5,.5,.5));
  });
  world.add(lm, lmPool); setLampTint();

  const P = {
    n: (x,y) => [(x+.5)*S, y*S+.05, 0], s: (x,y) => [(x+.5)*S, (y+1)*S-.05, Math.PI],
    w: (x,y) => [x*S+.05, (y+.5)*S, Math.PI/2], e: (x,y) => [(x+1)*S-.05, (y+.5)*S, -Math.PI/2]
  };
  [['RECEPÇÃO\nLargada e Chegada','#2d5a8c','#fff',8,3,'n'],
   ['TRABALHE EM EQUIPE\n… PARA SEMPRE','#f3ecc0','#3a3210',14,3,'n'],
   ['HOJE É SEXTA!\n(É SEGUNDA)','#f3ecc0','#7a1f1f',22,3,'n'],
   ['SAÍDA  ↑','#1c7a3c','#fff',40,3,'n'],
   ['REUNIÃO ÀS 8H\n(DO MÊS PASSADO)','#f3ecc0','#3a3210',48,12,'e'],
   ['Quem pegou meu\ngrampeador?','#f6e24a','#333',48,26,'e'],
   ['CUIDADO:\nPISO MOLHADO\n(SEMPRE)','#e6c200','#222',20,33,'s'],
   ['Você chegou.\nParabéns?','#f3ecc0','#3a3210',38,33,'s'],
   ['O CAFÉ ACABOU.\nDE NOVO.','#f3ecc0','#7a1f1f',3,24,'w'],
   ['Segunda-feira','#fff','#c33',3,10,'w'],
   ['BEM-VINDO A\nN O K I O\n(population: drifting)','#12043a','#ffe45e',48,20,'e'],
   ['NOKIO DRIFT\nFESTIVAL\n(todos os dias)','#2a0a52','#7ef9ff',4,16,'w']
  ].forEach(([t,b,f,x,y,d]) => {
    const [px,pz,r] = P[d](x,y);
    const m = new THREE.Mesh(new THREE.PlaneGeometry(4.4,2.2), new THREE.MeshBasicMaterial({ map: sg(t,b,f) }));
    m.position.set(px,2.3,pz); m.rotation.y = r; world.add(m);
  });

  for(let i=0;i<16;i++){ const [x,z] = pickFl(); addProp(chair(),x,z,.9,.8); }
  for(let i=0;i<8;i++){ addProp(cone(),(18+i*1.5)*S, i%2?19:26, .5,.2); addProp(cone(), i%2?234:241, (10+i*1.5)*S, .5,.2); }
  for(let i=0;i<14;i++){
    const [x,z] = pickFl(), r = 3+rnd()*3;
    addPatch(x,z,r,0x4f8fb0,.42);
    if(rnd()<.6) duck(x,z);
  }
  const wz = new THREE.Mesh(new THREE.PlaneGeometry(230,15), new THREE.MeshPhongMaterial({ color:0x4f8fb0, transparent:true, opacity:.42, shininess:90, depthWrite:false }));
  wz.rotation.x = -Math.PI/2; wz.position.set(130,.03,162.5); world.add(wz);
  for(let i=0;i<8;i++) duck(30+i*28, 158+rnd()*10);
}
let fallT = 2;
function spawnFall(dt){
  fallT -= dt; if(fallT>0 || fall.length>3) return;
  fallT = 2 + rnd()*2;
  const d = 18+rnd()*22, l = (rnd()-.5)*12;
  const x = car.x + Math.sin(car.a)*d + Math.cos(car.a)*l;
  const z = car.z + Math.cos(car.a)*d - Math.sin(car.a)*l;
  if(solid(Math.floor(x/S), Math.floor(z/S))) return;
  const tb = new THREE.Mesh(new THREE.BoxGeometry(.22,.22,3.4), new THREE.MeshBasicMaterial({ color:0xfffbe0 }));
  tb.position.set(x,3.9,z); tb.rotation.y = rnd()*3;
  const w = new THREE.Mesh(new THREE.RingGeometry(1.3,1.8,24), new THREE.MeshBasicMaterial({ color:0xff5533 }));
  w.rotation.x = -Math.PI/2; w.position.set(x,.05,z); world.add(tb,w);
  fall.push({tb,w,x,z,t:0,hit:0});
}

/* =====================================================================
   MAPAS ABERTOS — DESERTO / NEVE / FLORESTA
   ===================================================================== */
const DESERT_CFG = {
  clusters:7, wh:[7,13], wallTex:() => strata(['#b5693a','#c4783f','#a45a30','#d28d52','#8f4f2b']),
  tile:{ base:'#d1a867', cols:['rgba(110,75,35,.2)','rgba(255,230,175,.22)','rgba(90,60,25,.15)'] },
  field:{ base:'#d1a867', blob:['rgba(160,110,50,.10)','rgba(255,230,170,.12)','rgba(120,80,35,.08)'], n:110000,
    cols:['rgba(110,75,35,.2)','rgba(255,230,175,.22)','rgba(90,60,25,.15)'], shoulder:'rgba(120,80,40,.55)', road:'#b98a52',
    rcols:['rgba(80,50,20,.18)','rgba(235,200,150,.18)'], dash:'rgba(255,240,200,.28)' }
};
const SNOW_CFG = {
  clusters:5, wh:[5,9], wallTex:() => strata(['#cfe6f7','#bcd9ee','#a8c9e2','#e6f3fb']),
  tile:{ base:'#f2f7fc', cols:['rgba(170,195,225,.25)','rgba(255,255,255,.5)'] },
  field:{ base:'#f2f7fc', blob:['rgba(190,210,235,.18)','rgba(255,255,255,.35)','rgba(160,185,215,.12)'], n:90000,
    cols:['rgba(170,195,225,.25)','rgba(255,255,255,.5)'], shoulder:'rgba(150,175,205,.55)', road:'#d4dfeb',
    rcols:['rgba(120,145,175,.2)','rgba(255,255,255,.35)'], dash:'rgba(110,140,175,.35)' }
};
const FOREST_CFG = {
  clusters:5, wh:[9,16], wallTex:() => strata(['#4b5a3c','#56633f','#3c4a30','#625f4a']),
  tile:{ base:'#4d5b2c', cols:['rgba(200,110,30,.35)','rgba(160,60,20,.3)','rgba(30,45,15,.3)'] },
  field:{ base:'#4d5b2c', blob:['rgba(30,50,15,.18)','rgba(120,90,30,.14)','rgba(70,100,35,.12)'], n:120000,
    cols:['rgba(200,110,30,.35)','rgba(160,60,20,.3)','rgba(220,180,50,.3)','rgba(30,45,15,.3)'], shoulder:'rgba(50,35,15,.55)', road:'#7b5a35',
    rcols:['rgba(50,32,15,.25)','rgba(180,140,90,.2)'], dash:null }
};
const col = new THREE.Color(), white = new THREE.Color(1,1,1);
function buildDesert(tr){
  sd = 11 + currentTrack*5; openBase(DESERT_CFG);
  const pts = scatter(70, offRoad(5)), cm = mat(0x3f8040);
  const trunk = inst(new THREE.CylinderGeometry(.42,.5,3.4,10), cm, pts.length);
  const armH = inst(new THREE.CylinderGeometry(.26,.26,1.1,8), cm, pts.length);
  const armV = inst(new THREE.CylinderGeometry(.24,.28,1.5,8), cm, pts.length);
  pts.forEach(([x,z],i) => {
    const sc = .75 + rnd()*.8, ry = rnd()*6.28, sd2 = rnd()<.5 ? 1 : -1;
    setInst(trunk,i,x,z,ry,sc, 0,1.7,0);
    setInst(armH,i,x,z,ry,sc, sd2*.75,1.5,0, 0,Math.PI/2);
    setInst(armV,i,x,z,ry,sc, sd2*1.25,2.2,0);
    statics.push({ x, z, r:.65*sc });
  });
  const rp = scatter(55, offRoad(3));
  const rocks = inst(new THREE.IcosahedronGeometry(1,1), new THREE.MeshLambertMaterial({ color:0xffffff, flatShading:true }), rp.length);
  const rc = [0x9a7b5a,0xa88860,0x8a6a4a,0xb09070];
  rp.forEach(([x,z],i) => {
    const s = .9 + rnd()*2.2;
    _o.position.set(x,s*.38,z); _o.rotation.set(rnd()*3,rnd()*6,rnd()*3); _o.scale.set(s*(1+rnd()*.5), s*(.6+rnd()*.5), s*(1+rnd()*.4)); _o.updateMatrix();
    rocks.setMatrixAt(i,_o.matrix); rocks.setColorAt(i, col.setHex(rc[(rnd()*4)|0]));
    statics.push({ x, z, r:s*.85 });
  });
  const mesas = inst(new THREE.BoxGeometry(1,1,1), new THREE.MeshLambertMaterial({ color:0xffffff }), 22);
  const mc = [0xb5693a,0xc4783f,0xa45a30];
  for(let i=0;i<22;i++){
    const a = rnd()*6.283, d = 360 + rnd()*240, sy = 40 + rnd()*60;
    _o.position.set(CX+Math.cos(a)*d, sy/2-4, CZ+Math.sin(a)*d); _o.rotation.set(0,rnd()*3,0); _o.scale.set(60+rnd()*80, sy, 50+rnd()*60); _o.updateMatrix();
    mesas.setMatrixAt(i,_o.matrix); mesas.setColorAt(i, col.setHex(mc[(rnd()*3)|0])); 
  }
  mesas.castShadow = false;
  const dunes = inst(new THREE.SphereGeometry(1,14,8), new THREE.MeshLambertMaterial({ color:0xd9b27a }), 18);
  for(let i=0;i<18;i++){
    const a = rnd()*6.283, d = 300 + rnd()*300;
    _o.position.set(CX+Math.cos(a)*d, -10, CZ+Math.sin(a)*d); _o.rotation.set(0,rnd()*3,0); _o.scale.set(150+rnd()*110, 30+rnd()*30, 100+rnd()*80); _o.updateMatrix();
    dunes.setMatrixAt(i,_o.matrix);
  }
  dunes.castShadow = false;
  roadProps(14,10);
}
function buildSnow(tr){
  sd = 23 + currentTrack*5; openBase(SNOW_CFG);
  const pts = scatter(120, offRoad(4)), n = pts.length;
  const tm = mat(0x4a3320), gm = new THREE.MeshLambertMaterial({ color:0xffffff });
  const trunk = inst(new THREE.CylinderGeometry(.25,.35,2.2,6), tm, n);
  const c1 = inst(new THREE.ConeGeometry(1.9,2.6,8), gm, n), c2 = inst(new THREE.ConeGeometry(1.45,2.4,8), gm, n), c3 = inst(new THREE.ConeGeometry(1,2,8), gm, n);
  const gc = [0x1f5a3a,0x266b45,0x1a4d33,0x2f7a50];
  pts.forEach(([x,z],i) => {
    const sc = .8 + rnd()*.9, ry = rnd()*6.28;
    setInst(trunk,i,x,z,ry,sc, 0,1.1,0); setInst(c1,i,x,z,ry,sc, 0,2.9,0); setInst(c2,i,x,z,ry,sc, 0,4.3,0); setInst(c3,i,x,z,ry,sc, 0,5.5,0);
    col.setHex(gc[(rnd()*4)|0]).lerp(white, .22 + rnd()*.25);
    c1.setColorAt(i,col); c2.setColorAt(i,col); c3.setColorAt(i,col);
    statics.push({ x, z, r:.55*sc });
  });
  const rp = scatter(32, offRoad(3));
  const rocks = inst(new THREE.IcosahedronGeometry(1,1), new THREE.MeshLambertMaterial({ color:0xffffff, flatShading:true }), rp.length);
  rp.forEach(([x,z],i) => {
    const s = .9 + rnd()*1.8;
    _o.position.set(x,s*.35,z); _o.rotation.set(rnd()*3,rnd()*6,rnd()*3); _o.scale.set(s*(1+rnd()*.4), s*(.6+rnd()*.4), s*(1+rnd()*.3)); _o.updateMatrix();
    rocks.setMatrixAt(i,_o.matrix); rocks.setColorAt(i, col.setHex(0x8c96a0).lerp(white, rnd()*.5));
    statics.push({ x, z, r:s*.85 });
  });
  for(let i=0;i<7;i++){ const p = roadPoint(0); if(p) addPatch(p[0], p[1], 6+rnd()*3, 0x9fd8ff, .5); }
  const ms = [];
  for(let i=0;i<26;i++){ const a = rnd()*6.283, d = 380 + rnd()*240; ms.push([CX+Math.cos(a)*d, CZ+Math.sin(a)*d, 90+rnd()*130, 130+rnd()*190]); }
  const mA = inst(new THREE.ConeGeometry(1,1,6), new THREE.MeshLambertMaterial({ color:0x7d8aa3, flatShading:true }), ms.length);
  const mB = inst(new THREE.ConeGeometry(1,1,6), new THREE.MeshLambertMaterial({ color:0xffffff, flatShading:true }), ms.length);
  mA.castShadow = false; mB.castShadow = false;
  ms.forEach(([x,z,r,h],i) => {
    _o.position.set(x,h/2-8,z); _o.rotation.set(0,i,0); _o.scale.set(r,h,r); _o.updateMatrix(); mA.setMatrixAt(i,_o.matrix);
    const ch = h*.38;
    _o.position.set(x,h-8-ch/2,z); _o.scale.set(r*.38,ch,r*.38); _o.updateMatrix(); mB.setMatrixAt(i,_o.matrix);
  });
  roadProps(14,8);
}
function buildForest(tr){
  sd = 37 + currentTrack*5; openBase(FOREST_CFG);
  const pts = scatter(150, offRoad(4)), n = pts.length;
  const trunk = inst(new THREE.CylinderGeometry(.35,.5,4,7), mat(0x4a3320), n);
  const k1 = inst(new THREE.IcosahedronGeometry(2.4,1), new THREE.MeshLambertMaterial({ color:0xffffff, flatShading:true }), n);
  const k2 = inst(new THREE.IcosahedronGeometry(1.8,1), new THREE.MeshLambertMaterial({ color:0xffffff, flatShading:true }), n);
  const ac = [0xd9792b,0xc43e1c,0xe5b02f,0x6c8f2e,0x3f7a2a];
  pts.forEach(([x,z],i) => {
    const sc = .8 + rnd()*.7, ry = rnd()*6.28;
    setInst(trunk,i,x,z,ry,sc, 0,2,0); setInst(k1,i,x,z,ry,sc, 0,5.3,0); setInst(k2,i,x,z,ry,sc, .6,6.9,.3);
    col.setHex(ac[(rnd()*5)|0]); k1.setColorAt(i,col); k2.setColorAt(i,col.multiplyScalar(.9));
    statics.push({ x, z, r:.6*sc });
  });
  const rp = scatter(26, offRoad(3));
  const rocks = inst(new THREE.IcosahedronGeometry(1,1), new THREE.MeshLambertMaterial({ color:0xffffff, flatShading:true }), rp.length);
  rp.forEach(([x,z],i) => {
    const s = .9 + rnd()*1.6;
    _o.position.set(x,s*.35,z); _o.rotation.set(rnd()*3,rnd()*6,rnd()*3); _o.scale.set(s*(1+rnd()*.4), s*(.6+rnd()*.4), s*(1+rnd()*.3)); _o.updateMatrix();
    rocks.setMatrixAt(i,_o.matrix); rocks.setColorAt(i, col.setHex(0x6d7560).lerp(white, rnd()*.2));
    statics.push({ x, z, r:s*.85 });
  });
  const hills = inst(new THREE.SphereGeometry(1,14,10), new THREE.MeshLambertMaterial({ color:0xffffff }), 22);
  const hc = [0x3d6b34,0x4a7a3a,0x35602e];
  for(let i=0;i<22;i++){
    const a = rnd()*6.283, d = 320 + rnd()*260;
    _o.position.set(CX+Math.cos(a)*d, -30, CZ+Math.sin(a)*d); _o.rotation.set(0,rnd()*3,0); _o.scale.set(160+rnd()*100, 70+rnd()*60, 160+rnd()*100); _o.updateMatrix();
    hills.setMatrixAt(i,_o.matrix); hills.setColorAt(i, col.setHex(hc[(rnd()*3)|0]));
  }
  hills.castShadow = false;
  roadProps(14,8);
}

/* =====================================================================
   MAPA — CIDADE NEON
   ===================================================================== */
function facade(h, lit){
  const rows = Math.max(2, Math.round(h/3.5)), cols = 4;
  return cv(128, rows*32, (g,w,hh) => {
    if(!lit){
      g.fillStyle = '#14151f'; g.fillRect(0,0,w,hh);
      for(let i=0;i<500;i++){ g.fillStyle = rnd()<.5 ? 'rgba(255,255,255,.03)' : 'rgba(0,0,0,.12)'; g.fillRect(rnd()*w, rnd()*hh, 2, 2); }
      g.fillStyle = '#080a12';
      for(let r=0;r<rows;r++) for(let c=0;c<cols;c++) g.fillRect(c*32+5, r*32+7, 22, 17);
    } else {
      g.fillStyle = '#000'; g.fillRect(0,0,w,hh);
      const pal = ['#ffd27a','#ffd27a','#ffe9b0','#7ef3ff','#ff7ad9','#a8b4ff'];
      for(let r=0;r<rows;r++) for(let c=0;c<cols;c++) if(rnd()<.42){ g.fillStyle = pal[(rnd()*pal.length)|0]; g.fillRect(c*32+5, r*32+7, 22, 17); }
    }
  }, false);
}
function paintCity(){
  const cw = 2048, ch = 1536, kx = cw/(W*S), kz = ch/(H*S);
  const c = document.createElement('canvas'); c.width = cw; c.height = ch; const g = c.getContext('2d');
  g.fillStyle = '#4d4f5c'; g.fillRect(0,0,cw,ch);
  for(let i=0;i<40000;i++){ g.fillStyle = rnd()<.5 ? 'rgba(255,255,255,.05)' : 'rgba(0,0,0,.12)'; g.fillRect(rnd()*cw, rnd()*ch, 3, 3); }
  g.fillStyle = '#1d1e26';
  fl.forEach(([x,y]) => g.fillRect(x*S*kx, y*S*kz, S*kx+1, S*kz+1));
  for(let i=0;i<70000;i++){
    const [x,y] = fl[(rnd()*fl.length)|0];
    g.fillStyle = rnd()<.5 ? 'rgba(255,255,255,.05)' : 'rgba(0,0,0,.25)';
    g.fillRect((x+rnd())*S*kx, (y+rnd())*S*kz, 2, 2);
  }
  g.strokeStyle = '#9a9aae'; g.lineWidth = 5;
  fl.forEach(([x,y]) => {
    const x0 = x*S*kx, y0 = y*S*kz, x1 = (x+1)*S*kx, y1 = (y+1)*S*kz;
    g.beginPath();
    if(solid(x-1,y)){ g.moveTo(x0,y0); g.lineTo(x0,y1); }
    if(solid(x+1,y)){ g.moveTo(x1,y0); g.lineTo(x1,y1); }
    if(solid(x,y-1)){ g.moveTo(x0,y0); g.lineTo(x1,y0); }
    if(solid(x,y+1)){ g.moveTo(x0,y1); g.lineTo(x1,y1); }
    g.stroke();
  });
  g.setLineDash([22,18]); g.strokeStyle = 'rgba(255,214,90,.85)'; g.lineWidth = 4;
  [5,18,31,44].forEach(cx => {
    const px = (cx+.5)*S*kx;
    g.beginPath();
    if(cx===18 || cx===31){ g.moveTo(px,4*S*kz); g.lineTo(px,20*S*kz); g.moveTo(px,30*S*kz); g.lineTo(px,33*S*kz); }
    else { g.moveTo(px,4*S*kz); g.lineTo(px,33*S*kz); }
    g.stroke();
  });
  [5,18,31].forEach(cy => {
    const py = (cy+.5)*S*kz;
    g.beginPath();
    if(cy===18){ g.moveTo(4*S*kx,py); g.lineTo(20*S*kx,py); g.moveTo(30*S*kx,py); g.lineTo(46*S*kx,py); }
    else { g.moveTo(4*S*kx,py); g.lineTo(46*S*kx,py); }
    g.stroke();
  });
  g.setLineDash([]);
  g.strokeStyle = 'rgba(255,255,255,.7)'; g.lineWidth = 5; g.beginPath(); g.arc(125*kx,125*kz,22*kx,0,6.283); g.stroke();
  g.strokeStyle = 'rgba(255,63,180,.7)'; g.lineWidth = 7; g.beginPath(); g.arc(125*kx,125*kz,32*kx,0,6.283); g.stroke();
  const t = new THREE.CanvasTexture(c); t.anisotropy = Math.min(Q().an, R.capabilities.getMaxAnisotropy());
  return t;
}
function buildCity(tr){
  sd = 53 + currentTrack*5; gridInit(1);
  const vx = [5,18,31,44], hy = [5,18,31];
  hy.forEach(c => carve(4,c-1,45,c+1));
  vx.forEach(c => carve(c-1,4,c+1,32));
  carve(20,20,29,29); carve(24,24,25,25,1);
  calcFloor();

  const field = new THREE.Mesh(new THREE.PlaneGeometry(W*S,H*S), new THREE.MeshStandardMaterial({ map:paintCity(), roughness:.62, metalness:.08 }));
  field.rotation.x = -Math.PI/2; field.position.set(CX,.01,CZ); field.receiveShadow = true; world.add(field);
  const ot = tileTex({ base:'#33343e', cols:['rgba(255,255,255,.05)','rgba(0,0,0,.2)'] }); ot.repeat.set(2400/36,2400/36);
  flatPlane(new THREE.MeshLambertMaterial({ map:ot }), -.02, -Math.PI/2, 2400, 2400);

  const HC = [14,24,38,58], bl = [[],[],[],[]], isMono = (x,y) => x>=24 && x<=25 && y>=24 && y<=25;
  const place = (x,y,out) => {
    let k = (Math.floor(x/3)*7 + Math.floor(y/3)*13 + Math.floor(x/3)*Math.floor(y/3) + 400) % 4;
    if(out) k = Math.min(3, k+1);
    bl[k].push([x,y]);
  };
  for(let y=0;y<H;y++) for(let x=0;x<W;x++) if(G[y][x]===1 && !isMono(x,y)) place(x,y,x<4||x>45||y<4||y>32);
  for(let y=-3;y<H+3;y++) for(let x=-3;x<W+3;x++) if(x<0||y<0||x>=W||y>=H) place(x,y,true);
  const tints = [0xffffff,0xe6d8ff,0xd8e8ff,0xffe0f0], roofM = mat(0x1b1b26);
  bl.forEach((cells,k) => {
    if(!cells.length) return;
    const fm = new THREE.MeshLambertMaterial({ map:facade(HC[k],false), emissiveMap:facade(HC[k],true), emissive:0xffffff, emissiveIntensity:1.15 });
    const m = new THREE.InstancedMesh(new THREE.BoxGeometry(S-.3,HC[k],S-.3), [fm,fm,roofM,roofM,fm,fm], cells.length);
    m.frustumCulled = false; m.castShadow = true; m.receiveShadow = true;
    cells.forEach(([x,y],i) => {
      _o.position.set((x+.5)*S, HC[k]/2, (y+.5)*S); _o.rotation.set(0,0,0); _o.scale.set(1,1,1); _o.updateMatrix();
      m.setMatrixAt(i,_o.matrix); m.setColorAt(i, col.setHex(tints[(rnd()*4)|0]));
    });
    world.add(m);
  });

  /* neon + postes */
  const NEON = [0xff3fb4,0x2ee6ff,0xffe14a,0x7bff6a,0xff7a3a], dirs = [[1,0],[-1,0],[0,1],[0,-1]];
  const signs = [], lamps = [], glow = [];
  fl.forEach(([x,y]) => dirs.forEach(([dx,dz],di) => {
    if(!solid(x+dx,y+dz) || isMono(x+dx,y+dz)) return;
    if(rnd() < .07) signs.push([(x+.5)*S + dx*(S/2+.05), 4+rnd()*12, (y+.5)*S + dz*(S/2+.05), Math.atan2(-dx,-dz), NEON[(rnd()*5)|0]]);
    if((x*5 + y*3 + di) % 7 === 0) lamps.push([(x+.5)*S + dx*(S/2-.5), (y+.5)*S + dz*(S/2-.5)]);
  }));
  const sm2 = inst(new THREE.BoxGeometry(3.6,1.2,.12), new THREE.MeshBasicMaterial({ color:0xffffff }), signs.length);
  sm2.castShadow = false; sm2.receiveShadow = false;
  signs.forEach(([x,y,z,ry,c],i) => {
    _o.position.set(x,y,z); _o.rotation.set(0,ry,0); _o.scale.set(1,1,1); _o.updateMatrix();
    sm2.setMatrixAt(i,_o.matrix); sm2.setColorAt(i, col.setHex(c)); glow.push([x,y,z,c]);
  });
  const poles = inst(new THREE.CylinderGeometry(.09,.12,7,6), mat(0x222233), lamps.length);
  const heads = inst(new THREE.SphereGeometry(.38,8,6), new THREE.MeshBasicMaterial({ color:0xfff0c0 }), lamps.length);
  heads.castShadow = false;
  lamps.forEach(([x,z],i) => {
    _o.position.set(x,3.5,z); _o.rotation.set(0,0,0); _o.scale.set(1,1,1); _o.updateMatrix(); poles.setMatrixAt(i,_o.matrix);
    _o.position.set(x,7.1,z); _o.updateMatrix(); heads.setMatrixAt(i,_o.matrix); glow.push([x,7.1,z,0xffd9a0]);
  });
  const gp = new Float32Array(glow.length*3), gc = new Float32Array(glow.length*3);
  glow.forEach(([x,y,z,c],i) => { gp.set([x,y,z],i*3); col.setHex(c); gc.set([col.r,col.g,col.b],i*3); });
  const gg = new THREE.BufferGeometry(); gg.setAttribute('position', new THREE.BufferAttribute(gp,3)); gg.setAttribute('color', new THREE.BufferAttribute(gc,3));
  const gl = new THREE.Points(gg, new THREE.PointsMaterial({ size:9, map:glowTex(), vertexColors:true, transparent:true, blending:THREE.AdditiveBlending, depthWrite:false, sizeAttenuation:true }));
  gl.frustumCulled = false; world.add(gl);

  /* monumento da praça */
  const mx = 25*S, mz = 25*S;
  const add = (geo,m,x,y,z) => { const o = new THREE.Mesh(geo,m); o.position.set(x,y,z); o.castShadow = true; world.add(o); return o; };
  add(new THREE.CylinderGeometry(5.2,5.2,.6,28), mat(0x2a2a3a), mx,.3,mz);
  add(new THREE.CylinderGeometry(4.2,4.2,.9,28), new THREE.MeshBasicMaterial({ color:0x1f6fd0 }), mx,.75,mz);
  add(new THREE.BoxGeometry(2.6,18,2.6), new THREE.MeshLambertMaterial({ color:0x0a2a3a, emissive:0x22e0ff, emissiveIntensity:.8 }), mx,9.3,mz);
  const r1 = add(new THREE.TorusGeometry(4.6,.18,8,40), new THREE.MeshBasicMaterial({ color:0xff3fb4 }), mx,1.5,mz); r1.rotation.x = Math.PI/2;
  const r2 = add(new THREE.TorusGeometry(3.4,.14,8,40), new THREE.MeshBasicMaterial({ color:0x2ee6ff }), mx,11,mz); r2.rotation.x = Math.PI/2;

  /* skyline distante */
  const sk = inst(new THREE.BoxGeometry(1,1,1), new THREE.MeshLambertMaterial({ map:facade(60,false), emissiveMap:facade(60,true), emissive:0xffffff, emissiveIntensity:1 }), 60);
  sk.castShadow = false; sk.receiveShadow = false;
  for(let i=0;i<60;i++){
    const a = rnd()*6.283, d = 230 + rnd()*120, sy = 70 + rnd()*150;
    _o.position.set(CX+Math.cos(a)*d, sy/2, CZ+Math.sin(a)*d); _o.rotation.set(0,rnd()*3,0); _o.scale.set(18+rnd()*18, sy, 18+rnd()*18); _o.updateMatrix();
    sk.setMatrixAt(i,_o.matrix); sk.setColorAt(i, col.setHex(tints[(rnd()*4)|0]));
  }
  for(let i=0;i<10;i++){ const [x,z] = pickFl(18); addProp(cone(), x, z, .5, .2); }
  for(let i=0;i<8;i++){ const [x,z] = pickFl(18); addProp(barrel(i%2 ? 0xd04020 : 0x2b6fd4), x, z, .6, .5); }
}

/* =====================================================================
   PISTAS / MAPAS (dados)
   ===================================================================== */
const BR_START = [42.5, 22.5, Math.PI/2];
const MAPS = [
  { id:'backrooms', env:'backrooms', name:'Backrooms', icon:'🟨', build:buildBackrooms,
    desc:'O escritório infinito. Carpete úmido, luz zumbindo.',
    zone:(cx,cy) => (cx>=8&&cx<=26&&cy>=10&&cy<=26) ? 'plaza' : (cx>=30&&cx<=44&&cy>=9&&cy<=27) ? 'almox' : cy>=31 ? 'agua' : 'main',
    tracks:[
      {name:'Escritório Padrão', desc:'O circuito clássico: corredores externos e volta completa', start:BR_START, cp:[[14,4],[30,4],[47,4],[47,18],[47,32],[26,32],[4,32],[4,18],[5,4]]},
      {name:'Circuito da Praça', desc:'Só a praça dos pilares — drift livre', start:BR_START, cp:[[10,12],[22,12],[22,24],[10,24],[10,12]]},
      {name:'Almoxarifado Turbo', desc:'Corredores estreitos do estoque', start:BR_START, cp:[[32,10],[42,10],[42,26],[32,26],[32,10]]},
      {name:'Corredor Alagado', desc:'Piso sempre molhado + patos', start:BR_START, cp:[[10,32],[25,32],[40,32],[40,33],[25,33],[10,33]]},
      {name:'Volta Extrema', desc:'Todos os checkpoints da planta inteira', start:BR_START, cp:[[14,4],[30,4],[47,4],[47,18],[47,32],[26,32],[4,32],[4,18],[5,4],[14,4]]},
      {name:'NOKIO 🌃', desc:'Cidade neon à noite dentro das Backrooms. Modo noturno!', night:true, start:BR_START, cp:[[47,5],[47,18],[43,18],[35,18],[35,12],[32,12],[32,18],[27,18],[26,26],[20,26],[20,20],[12,20],[12,12],[8,12],[8,18],[6,18],[5,18],[5,32],[20,32],[47,32]]}
    ]},
  { id:'desert', env:'desert', name:'Deserto de Cobre', icon:'🏜️', build:buildDesert,
    desc:'Areia solta, cactos e rochas. Estrada de terra e drift à vontade.',
    tracks:[
      {name:'Rota do Cânion', desc:'Volta larga entre os mesas', cp:[[9,9],[25,6],[41,9],[46,19],[40,29],[26,32],[11,29],[6,19]]},
      {name:'Anel das Dunas', desc:'Chicanes e curvas fechadas', cp:[[8,8],[17,15],[26,8],[39,8],[46,16],[39,23],[46,30],[30,31],[22,23],[14,31],[6,25],[6,15]]}
    ]},
  { id:'snow', env:'snow', name:'Montanha Nevada', icon:'❄️', build:buildSnow,
    desc:'Neve fofa, pinheiros e placas de gelo. Aderência mínima.',
    tracks:[
      {name:'Pico Branco', desc:'Volta grande pela montanha', cp:[[10,8],[26,6],[43,10],[46,23],[34,31],[20,27],[10,31],[5,20]]},
      {name:'Lago Congelado', desc:'Circuito interno, curvas longas', cp:[[14,10],[24,8],[34,12],[38,22],[32,30],[22,26],[14,30],[10,20]]}
    ]},
  { id:'forest', env:'forest', name:'Floresta de Outono', icon:'🍂', build:buildForest,
    desc:'Trilha de terra entre árvores alaranjadas. Folhas molhadas.',
    tracks:[
      {name:'Trilha dos Ipês', desc:'Trilha longa e sinuosa', cp:[[8,8],[22,5],[40,8],[46,18],[38,26],[44,32],[28,32],[16,26],[6,30],[5,18]]},
      {name:'Clareira', desc:'Hexágono rápido ao redor da clareira', cp:[[12,12],[26,7],[40,12],[40,26],[26,31],[12,26]]}
    ]},
  { id:'city', env:'city', name:'Cidade Neon', icon:'🌃', build:buildCity,
    desc:'Ruas molhadas, neon e uma praça com monumento. Noite eterna.',
    tracks:[
      {name:'Avenida Neon', desc:'Volta pelo perímetro da cidade', cp:[[5,5],[18,5],[31,5],[44,5],[44,18],[44,31],[31,31],[18,31],[5,31],[5,18]]},
      {name:'Rotatória Central', desc:'Gire em volta do monumento da praça', cp:[[31,25],[29,30],[24,31],[19,29],[18,24],[20,19],[25,18],[30,20]]}
    ]}
];
let currentMap = 0, currentTrack = 0;
const curTrack = () => MAPS[currentMap].tracks[currentTrack];
function getCP(){ return curTrack().cp.map(([x,y]) => [(x+.5)*S, (y+.5)*S]); }
function startOf(tr){
  if(tr.start) return { x:tr.start[0], z:tr.start[1], a:tr.start[2] };
  const a = CP[CP.length-1], b = CP[0];
  return { x:a[0]+(b[0]-a[0])*.55, z:a[1]+(b[1]-a[1])*.55, a:Math.atan2(b[0]-a[0], b[1]-a[1]) };
}
const ZN = {
  main:'Corredores Principais', plaza:'A Praça dos Pilares — derrape à vontade', almox:'O Almoxarifado Infinito', agua:'O Corredor Alagado — carpete molhado',
  desert:'Deserto de Cobre — areia solta, sem acostamento', snow:'Montanha Nevada — gelo, silêncio e derrapagem',
  forest:'Floresta de Outono — folhas molhadas na pista', city:'Cidade Neon — a noite nunca acaba'
};
const PAS = {
  backrooms:[
    'Atenção, funcionário: seu turno ainda não acabou.', 'Lembrete: é proibido derrapar nos corredores. (Mentira.)',
    'A reunião das 3h foi remarcada para 3h… de novo.', 'Quem estacionou o carro dentro do escritório? Parabéns.',
    'O café acabou. O café sempre acabou.', 'A saída fica logo ali. Não, ali não.', 'Em NOKIO a noite nunca acaba. Nem o expediente.'],
  desert:['Aviso: o deserto não possui acostamento.','Hidratação é importante. Derrapagem também.','Se você viu um cacto andando, foi só o vento.','O GPS diz: continue em frente. Há quarenta minutos.'],
  snow:['Atenção: gelo na pista. Ou melhor, pista no gelo.','Boneco de neve não é obstáculo. Ainda.','Correntes são recomendadas. Coragem também.','O inverno chegou. O seu freio, não.'],
  forest:['As árvores não têm seguro. Você também não.','Lembrete: esquilos têm preferência.','Folhas molhadas: derrapagem garantida.','Perdido? A trilha é a parte marrom.'],
  city:['Semáforos são sugestões criativas.','O neon é grátis. A multa não.','Rodízio de hoje: só carros derrapantes.','A praça é de todos. A rotatória é sua.']
};

/* =====================================================================
   CARRO (modelo)
   ===================================================================== */
const car = { x:42.5, z:22.5, a:Math.PI/2, vx:0, vz:0, st:0, r:1.6 };
const cn = new THREE.Group(), cg = new THREE.Group();
cn.add(cg); scn.add(cn);
const blob = new THREE.Mesh(new THREE.PlaneGeometry(4.4,7.2).rotateX(-Math.PI/2),
  new THREE.MeshBasicMaterial({ map: radial([[0,'rgba(0,0,0,.85)'],[.6,'rgba(0,0,0,.4)'],[1,'rgba(0,0,0,0)']]), transparent:true, opacity:.6, depthWrite:false, polygonOffset:true, polygonOffsetFactor:-1 }));
blob.position.y = .07; cn.add(blob);

function buildCarModel(group, c, scale=1){
  while(group.children.length){
    const old = group.children[0]; group.remove(old);
    if(old.geometry) old.geometry.dispose();
    if(old.material && !Array.isArray(old.material)) old.material.dispose();
  }
  group.position.set(0,0,0); group.rotation.set(0,0,0);
  group.userData = { tails:[], wheels:[], noSpin:false };
  const UD = group.userData;
  const id = c.id, paint = c.color, dark = 0x15191d, glass = 0x162b38, chrome = 0x9ba6ad;
  const mat3 = (color, metalness=.35, roughness=.38) => new THREE.MeshStandardMaterial({ color, metalness, roughness, side: THREE.DoubleSide });
  const part = (w,h,d,color,x,y,z,opts={}) => {
    const m = new THREE.Mesh(new THREE.BoxGeometry(w*scale, h*scale, d*scale), mat3(color, opts.metalness??.35, opts.roughness??.38));
    m.position.set(x*scale, y*scale, z*scale); m.castShadow = true; group.add(m); return m;
  };
  const lamp = (w,h,d,color,x,y,z,tail=false) => {
    const m = new THREE.Mesh(new THREE.BoxGeometry(w*scale, h*scale, d*scale), new THREE.MeshBasicMaterial({ color }));
    m.position.set(x*scale, y*scale, z*scale); group.add(m); if(tail) UD.tails.push(m); return m;
  };
  function hull(sections, color, metal=.45){
    const verts=[], indices=[];
    for(const [z,w,bottom,shoulder,top,topW] of sections){
      const ring = [[-w/2,bottom],[w/2,bottom],[w/2,shoulder],[topW/2,top],[-topW/2,top],[-w/2,shoulder]];
      for(const [x,y] of ring) verts.push(x*scale, y*scale, z*scale);
    }
    for(let j=0;j<sections.length-1;j++) for(let k=0;k<6;k++){
      const a=j*6+k, b=j*6+(k+1)%6, d=(j+1)*6+k, e=(j+1)*6+(k+1)%6;
      indices.push(a,b,d, b,e,d);
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(verts,3));
    g.setIndex(indices); g.computeVertexNormals();
    const m = new THREE.Mesh(g, mat3(color, metal, .32)); m.castShadow = true; group.add(m); return m;
  }
  function glassCabin(sections){ hull(sections, glass, .18); }

  const bodyId = id==='b34'||id==='coyota'||id==='nitsubish' ? 'sport' :
                 id==='ximpala' ? 'super' :
                 id==='golfe' ? 'starter' :
                 id==='sabournaitor' ? 'driftpro' : id;

  let wheelZ=1.3, wheelX=1.0, wheelR=.4;

  if(bodyId==='starter'){
    hull([[-1.95,1.78,.35,.64,.67,1.55],[-1.65,2,.35,.82,1.48,1.7],[-.85,2.02,.35,.88,1.58,1.72],[.65,2.02,.35,.86,1.42,1.68],[1.65,1.92,.35,.72,.82,1.55],[1.88,1.72,.35,.62,.64,1.4]], paint);
    glassCabin([[-1.52,1.58,.84,1.0,1.63,1.42],[-1.15,1.58,.84,1.5,1.72,1.36],[-.55,1.58,.84,1.58,1.72,1.36],[.42,1.58,.84,1.42,1.6,1.38],[.82,1.5,.78,1.05,1.12,1.3]]);
    part(1.92,.13,.12,dark,0,.62,-1.92); lamp(.38,.18,.08,0xffefad,-.62,.68,1.84); lamp(.38,.18,.08,0xffefad,.62,.68,1.84);
    lamp(.32,.2,.08,0xc92828,-.62,.68,-1.92,true); lamp(.32,.2,.08,0xc92828,.62,.68,-1.92,true); part(1.05,.16,.1,dark,0,.5,1.92);
    wheelZ=1.25; wheelX=.98; wheelR=.39;
  } else if(bodyId==='sport'){
    hull([[-2.05,1.8,.34,.56,.59,1.5],[-1.62,2,.34,.77,1.22,1.65],[-.8,2.04,.34,.8,1.34,1.65],[.6,2.04,.34,.75,1.18,1.6],[1.65,1.95,.34,.62,.69,1.5],[2.02,1.72,.34,.55,.57,1.38]], paint);
    glassCabin([[-1.42,1.55,.78,.95,1.35,1.3],[-.88,1.55,.78,1.3,1.43,1.3],[-.25,1.55,.78,1.32,1.43,1.3],[.55,1.55,.75,1.1,1.22,1.3],[.95,1.45,.65,.76,.82,1.18]]);
    part(2.08,.13,2.8,dark,0,.43,0); lamp(.46,.13,.08,0xffefad,-.68,.61,1.98); lamp(.46,.13,.08,0xffefad,.68,.61,1.98);
    lamp(.48,.13,.08,0xff2222,-.68,.61,-2,true); lamp(.48,.13,.08,0xff2222,.68,.61,-2,true); part(1.7,.13,.12,0x111111,0,.48,2.04);
    wheelZ=1.38; wheelX=1.02; wheelR=.4;
    if(id==='b34'||id==='coyota'||id==='nitsubish'){
      part(1.9,.09,.34,0x101010,0,1.15,-1.85); part(.1,.4,.14,paint,-.75,.9,-1.7); part(.1,.4,.14,paint,.75,.9,-1.7);
      part(1.3,.08,.1,0x1a1a1a,0,.42,2.0);
    }
  } else if(bodyId==='driftpro'){
    hull([[-2.1,2.05,.38,.72,.8,1.85],[-1.85,2.28,.38,1.0,1.62,2.02],[-.7,2.3,.38,1.02,1.72,2.02],[1.05,2.3,.38,.96,1.48,1.98],[1.85,2.2,.38,.82,.9,1.86],[2.02,2.05,.38,.7,.72,1.72]], paint);
    glassCabin([[-1.72,1.86,1.0,1.32,2.02,1.72],[-1.55,1.86,1.0,1.86,2.05,1.72],[.65,1.86,1.0,1.86,2.05,1.72],[1.12,1.82,.96,1.48,1.62,1.65]]);
    part(1.2,.48,.12,dark,0,.85,2.04); for(let x=-.42;x<=.43;x+=.28) part(.09,.34,.04,chrome,x,.85,2.12);
    lamp(.42,.27,.09,0xfff0b5,-.78,.93,2.03); lamp(.42,.27,.09,0xfff0b5,.78,.93,2.03);
    lamp(.16,.46,.08,0xff2222,-1.0,.9,-2.12,true); lamp(.16,.46,.08,0xff2222,1.0,.9,-2.12,true);
    part(2.3,.2,.3,dark,0,.48,2.02); part(2.35,.18,.28,dark,0,.49,-2.08);
    for(const x of [-1.13,1.13]){ part(.18,.35,1.2,dark,x,.78,.55); part(.12,.25,.55,paint,x,.82,.55); }
    const spare = new THREE.Mesh(new THREE.TorusGeometry(.43*scale,.14*scale,10,20), mat3(dark,.1,.9));
    spare.position.set(0,1.22*scale,-2.12*scale); group.add(spare);
    const spareHub = new THREE.Mesh(new THREE.CylinderGeometry(.22*scale,.22*scale,.24*scale,12), mat3(chrome,.8,.2));
    spareHub.rotation.z = Math.PI/2; spareHub.position.set(0,1.22*scale,-2.13*scale); group.add(spareHub);
    wheelZ=1.38; wheelX=1.12; wheelR=.48;
  } else if(bodyId==='super'){
    hull([[-2.35,1.95,.34,.55,.62,1.65],[-1.9,2.12,.34,.73,1.02,1.75],[-.95,2.14,.34,.76,1.13,1.76],[.55,2.12,.34,.72,1.05,1.7],[1.72,2.04,.34,.66,.8,1.63],[2.22,1.9,.34,.56,.6,1.55]], paint);
    glassCabin([[-1.15,1.7,.76,.91,1.24,1.42],[-.55,1.7,.76,1.22,1.45,1.45],[.35,1.7,.76,1.18,1.4,1.42],[1.05,1.66,.72,.83,.95,1.35]]);
    part(1.65,.08,.12,dark,0,.44,2.22); lamp(.5,.14,.09,0xfff1c0,-.68,.62,2.18); lamp(.5,.14,.09,0xfff1c0,.68,.62,2.18);
    lamp(.48,.15,.09,0xff2020,-.68,.61,-2.24,true); lamp(.48,.15,.09,0xff2020,.68,.61,-2.24,true); part(1.5,.09,.16,chrome,0,.47,-2.2);
    wheelZ=1.5; wheelX=1.07; wheelR=.41;
  } else {
    hull([[-2.35,1.92,.31,.46,.48,1.45],[-1.9,2.18,.31,.58,.66,1.62],[-.95,2.3,.31,.62,.78,1.65],[.15,2.28,.31,.59,.7,1.55],[1.45,2.22,.31,.56,.61,1.5],[2.12,1.98,.31,.48,.5,1.4]], paint);
    glassCabin([[-.88,1.48,.69,.76,.92,1.22],[-.4,1.5,.69,1.0,1.12,1.22],[.28,1.5,.67,.96,1.08,1.2],[.92,1.56,.63,.65,.72,1.3]]);
    part(2.28,.09,.48,dark,0,.35,2.05); lamp(.62,.09,.08,0xfff6d0,-.72,.49,2.1); lamp(.62,.09,.08,0xfff6d0,.72,.49,2.1);
    part(.38,.12,.62,dark,-1.02,.48,.48); part(.38,.12,.62,dark,1.02,.48,.48);
    part(1.8,.1,.35,dark,0,.35,-2.12); lamp(.42,.13,.09,0xff1b1b,-.7,.49,-2.1,true); lamp(.42,.13,.09,0xff1b1b,.7,.49,-2.1,true);
    if(id==='legend'){
      part(2.3,.13,.34,0x101010,0,1.18,-1.8); part(.13,.55,.14,paint,-.82,.88,-1.65); part(.13,.55,.14,paint,.82,.88,-1.65);
      part(2.25,.12,.22,0x101010,0,1.36,-1.8); part(1.8,.12,.34,0x111111,0,.35,-2.18);
      for(const x of [-.55,-.18,.18,.55]) part(.07,.14,.3,chrome,x,.28,-2.2);
    }
    wheelZ=1.48; wheelX=1.12; wheelR=.42;
  }

  for(const x of [-1,1]) for(const z of [-wheelZ, wheelZ]){
    const tire = new THREE.Mesh(new THREE.CylinderGeometry(wheelR*scale, wheelR*scale, .34*scale, 20), mat3(0x171717,.05,.95));
    tire.rotation.z = Math.PI/2; tire.position.set(x*wheelX*scale, .42*scale, z*scale); tire.userData.wheel = true; tire.castShadow = true; group.add(tire);
    const rim = new THREE.Mesh(new THREE.CylinderGeometry(wheelR*.58*scale, wheelR*.58*scale, .36*scale, 12), mat3(id==='starter'?0x888888:0xd8d8d8,.85,.2));
    rim.rotation.z = Math.PI/2; rim.position.set(x*(wheelX+.015)*scale, .42*scale, z*scale); rim.userData.wheel = true; group.add(rim);
    const hub = new THREE.Mesh(new THREE.CylinderGeometry(.07*scale,.07*scale,.38*scale,10), mat3(0x333333,.6,.3));
    hub.rotation.z = Math.PI/2; hub.position.set(x*(wheelX+.02)*scale, .42*scale, z*scale); hub.userData.wheel = true; group.add(hub);
    UD.wheels.push(tire, rim, hub);
  }

  if(c.blower){
    const bl = new THREE.Mesh(new THREE.BoxGeometry(.5,.5,.42), mat3(0x8a8f94,.8,.3)); bl.position.set(0,1.05,.55); group.add(bl);
    const sc = new THREE.Mesh(new THREE.CylinderGeometry(.2,.24,.1,14), mat3(0x2a2a2a,.6,.4)); sc.position.set(0,1.32,.55); group.add(sc);
    const belt = new THREE.Mesh(new THREE.BoxGeometry(.06,.06,1.1), mat3(0x111111,.2,.8)); belt.position.set(.28,.72,.3); group.add(belt);
  }
  if(c.camber){
    group.position.y = -0.14; UD.noSpin = true;
    group.children.forEach(m => {
      if(m.userData && m.userData.wheel && m.geometry && m.geometry.type==='CylinderGeometry')
        m.rotation.z = Math.PI/2 + (m.position.x>0 ? -0.3 : 0.3);
    });
    part(1.7,.06,.06,0x6622cc,0,.28,1.9);
  }
  if(c.antenna){
    const mast = new THREE.Mesh(new THREE.CylinderGeometry(.025,.025,1.5,6), mat3(0x202020,.4,.5));
    mast.position.set(-.55,2.6,-.4); group.add(mast);
    const dish = new THREE.Mesh(new THREE.SphereGeometry(.28,10,6,0,Math.PI*2,0,Math.PI/2), mat3(0xd9d9d9,.3,.5));
    dish.rotation.x = -Math.PI/2; dish.position.set(-.55,3.3,-.4); group.add(dish);
    const beacon = new THREE.Mesh(new THREE.SphereGeometry(.09,8,6), new THREE.MeshBasicMaterial({ color: 0xff5500 }));
    beacon.position.set(-.55,3.45,-.4); group.add(beacon); group.userData.beacon = beacon;
    for(const dx of [-.15,0,.15]){
      const an = new THREE.Mesh(new THREE.CylinderGeometry(.015,.015,.7,4), mat3(0x111111,.3,.4));
      an.position.set(dx,2.5,.3); group.add(an);
    }
  }
}
buildCarModel(cg, { id:'starter', color:0x2d7dd2 });

/* =====================================================================
   ÁUDIO
   ===================================================================== */
let AC, MG, eo, eg, sg2, muted = false;
const bgMusic = new Audio('theme_1.mp3'); bgMusic.loop = true; bgMusic.volume = .5; bgMusic.preload = 'auto';
function startMusic(){ bgMusic.volume = muted ? 0 : .5; bgMusic.play().catch(()=>{}); }
const tone = (f,g,d,ty,v,dl=0) => {
  if(!AC) return;
  const q = AC.createOscillator(), a = AC.createGain(), t = AC.currentTime + dl;
  q.type = ty; q.frequency.setValueAtTime(f,t); q.frequency.exponentialRampToValueAtTime(g,t+d);
  a.gain.setValueAtTime(v,t); a.gain.exponentialRampToValueAtTime(.001,t+d);
  q.connect(a).connect(MG); q.start(t); q.stop(t+d);
};
const sfx = {
  quack(){ tone(520,240,.16,'sawtooth',.2); tone(560,300,.12,'square',.08,.1); },
  boing(){ tone(160,600,.3,'sine',.3); },
  horn(){ tone(440,440,.14,'square',.14); tone(350,350,.25,'square',.14,.16); },
  ding(){ tone(1318,1318,.6,'sine',.2); tone(988,988,.8,'sine',.15,.18); }
};
const NT = [261.6,329.6,392,493.9,440,392,329.6,293.7]; let ni=0, T=0;
function music(){
  const sp = Math.hypot(car.vx, car.vz);
  if(AC){
    const q = AC.createOscillator(), a = AC.createGain(), t = AC.currentTime;
    q.type = 'triangle'; q.frequency.value = NT[ni++%8]*(1+sp/120); q.detune.value = -30 + Math.sin(T)*25;
    a.gain.setValueAtTime(.06,t); a.gain.exponentialRampToValueAtTime(.001,t+.5);
    q.connect(a).connect(MG); q.start(t); q.stop(t+.5);
  }
  setTimeout(music, Math.max(170, 480 - sp*7));
}
function initAudio(){
  if(AC) return;
  AC = new (window.AudioContext || window.webkitAudioContext)();
  MG = AC.createGain(); MG.gain.value = muted ? 0 : .5; MG.connect(AC.destination);
  eo = AC.createOscillator(); eo.type = 'sawtooth';
  const lp = AC.createBiquadFilter(); lp.frequency.value = 500;
  eg = AC.createGain(); eg.gain.value = 0; eo.connect(lp).connect(eg).connect(MG); eo.start();
  const h = AC.createOscillator(); h.type='sawtooth'; h.frequency.value=60;
  const hg = AC.createGain(); hg.gain.value=.035;
  const hf = AC.createBiquadFilter(); hf.frequency.value=300;
  h.connect(hf).connect(hg).connect(MG); h.start();
  const buf = AC.createBuffer(1, AC.sampleRate, AC.sampleRate), d = buf.getChannelData(0);
  for(let i=0;i<d.length;i++) d[i] = Math.random()*2-1;
  const ns = AC.createBufferSource(); ns.buffer=buf; ns.loop=true;
  const bp = AC.createBiquadFilter(); bp.type='bandpass'; bp.frequency.value=900;
  sg2 = AC.createGain(); sg2.gain.value=0; ns.connect(bp).connect(sg2).connect(MG); ns.start();
  music();
}

/* =====================================================================
   ESTADO / GARAGEM / CARROS
   ===================================================================== */
const CAMS = [
  {id:'chase', name:'Perseguição'}, {id:'hood', name:'Capô'}, {id:'cockpit', name:'Interior'},
  {id:'top', name:'Aérea'}, {id:'cinematic', name:'Cinemática'}, {id:'side', name:'Lateral'}
];
let currentCam = 0;
const BOT_TYPES = [
  {id:'rookie', name:'Estagiário', color:0x888888, skill:0.45, desc:'Dirige devagar e bate bastante'},
  {id:'normal', name:'Funcionário', color:0x2d7dd2, skill:0.7, desc:'Nível médio, tenta acompanhar'},
  {id:'pro', name:'Supervisor', color:0xc41e3a, skill:0.9, desc:'Agressivo e rápido'},
  {id:'legend', name:'O Chefe', color:0xffd700, skill:1.05, desc:'Quase imbatível'}
];
let activeBots = [], selectedBots = new Set(['normal']);
let last=0, run=false, paused=false, busy=false, keys={}, score=0, pts=0, dtm=0, since=0, lap=1, lapT=0, cpI=0, zone='', zT=0, paT=8, paS=0, pop='', popT=0, ca=car.a;
let wheelSpin = 0, pitch = 0, prevBrake = false, mmT = 0;

const CARS = [
  {id:'starter', name:'Funcionário 98', price:0, mult:1, power:1, accel:22, maxSpeed:48, grip:1.05, driftGrip:0.72, steerResponse:9, color:0x2d7dd2, desc:'Compacto hatch inspirado num Uno: pequeno, quadradinho e econômico.'},
  {id:'sport', name:'Esportivo de Firma', price:6000, mult:1.5, power:1.08, accel:26, maxSpeed:56, grip:1.0, driftGrip:0.68, steerResponse:9.5, color:0x32a852, desc:'Hatch compacto tunado, com visual esportivo e bônus de 50% nos drifts.'},
  {id:'driftpro', name:'Drift Pro', price:15000, mult:2.5, power:1.18, accel:28, maxSpeed:58, grip:0.92, driftGrip:0.58, steerResponse:10, color:0xe94a36, desc:'SUV quadrado inspirado num Jeep, mais alto e robusto.'},
  {id:'super', name:'Supercarro Executivo', price:35000, mult:4, power:1.3, accel:32, maxSpeed:68, grip:0.95, driftGrip:0.62, steerResponse:10.5, color:0x8e44ad, desc:'Sedã esportivo baixo, comprido e com pagamento 4×.'},
  {id:'hyper', name:'Hypercarro', price:60000, mult:7, power:1.45, accel:36, maxSpeed:76, grip:0.88, driftGrip:0.55, steerResponse:11, color:0xe2a72e, desc:'Supercarro baixo e largo, inspirado numa Lamborghini.'},
  {id:'legend', name:'Lendário do Drift', price:120000, mult:10, power:1.6, accel:38, maxSpeed:82, grip:0.85, driftGrip:0.52, steerResponse:11.5, color:0x19bfc1, desc:'Supercarro de corrida com aerofólio e até 10× dinheiro por drift.'},
  {id:'b34', name:'B34 do Rian', price:95000, mult:3.5, power:1.25, accel:30, maxSpeed:64, grip:0.9, driftGrip:0.6, steerResponse:10.2, color:0x2b6fd4, desc:'Sedã azul de rua do Rian. Meio irmão de um skyline, mas ele não gosta que comentem isso.'},
  {id:'coyota', name:'COYOTA Laranja', price:140000, mult:4, power:1.32, accel:33, maxSpeed:70, grip:0.87, driftGrip:0.57, steerResponse:10.8, color:0xff7a1a, desc:'Coupé laranja clássico. O piloto dorme na largada e mesmo assim ganha.'},
  {id:'nitsubish', name:'NITSUBISH Verde', price:210000, mult:4, power:1.35, accel:34, maxSpeed:72, grip:0.93, driftGrip:0.59, steerResponse:10.5, color:0x27c93f, desc:'Tração integral, turbo verde e um amor incompreendido por pizza.'},
  {id:'ximpala', name:'XIMPALA Supercharger', price:320000, mult:5, power:1.4, accel:35, maxSpeed:74, grip:0.82, driftGrip:0.5, steerResponse:9.8, color:0x1a1a1a, blower:true, desc:'Muscle car preto com supercharger ENTRANDO PRA FORA do capô. Ruge feio e derrapa pior.'},
  {id:'golfe', name:'GOLFE Sapão', price:180000, mult:1.5, power:0.95, accel:24, maxSpeed:52, grip:0.78, driftGrip:0.48, steerResponse:8.5, color:0x9aa0a6, camber:true, desc:'Golf TSI rebaixado até o chão, rodas tortas, neon roxo. Vira mal nas curvas mas é estiloso demais.'},
  {id:'sabournaitor', name:'SABOURNAITOR III', price:500000, mult:6, power:1.5, accel:37, maxSpeed:78, grip:0.9, driftGrip:0.54, steerResponse:11, color:0xd7d7d7, antenna:true, desc:'Caçador de furacões oficial. Antena, radar e coragem. Onde tem tempestade, ele dá drift.'}
];

let money=0, owned=['starter'], selectedCar='starter', shopOpen=false;
try{
  const save = JSON.parse(localStorage.getItem('backroomsDriftGarage') || 'null');
  if(save){
    money = Math.max(0, Number(save.money)||0);
    owned = Array.isArray(save.owned) ? Array.from(new Set(['starter', ...save.owned.filter(id => CARS.some(c => c.id===id))])) : ['starter'];
    selectedCar = owned.includes(save.selectedCar) ? save.selectedCar : 'starter';
    if(Number.isInteger(save.q) && QUALS[save.q]) qIdx = save.q;
    if(Number.isInteger(save.map) && MAPS[save.map]){
      currentMap = save.map;
      currentTrack = (Number.isInteger(save.track) && MAPS[currentMap].tracks[save.track]) ? save.track : 0;
    }
    if(Number.isInteger(save.cam) && CAMS[save.cam]) currentCam = save.cam;
  }
}catch(e){}
const currentCar = () => CARS.find(c => c.id === selectedCar) || CARS[0];
function saveGarage(){
  try{ localStorage.setItem('backroomsDriftGarage', JSON.stringify({ money, owned, selectedCar, q:qIdx, map:currentMap, track:currentTrack, cam:currentCam })); }catch(e){}
}
const cashFmt = n => '$' + Math.floor(n).toLocaleString('pt-BR');
const say = (t, d=2.2) => { pop=t; popT=d; };

/* =====================================================================
   LOJA (preview 3D)
   ===================================================================== */
let previewIndex=0, previewScene, previewCamera, previewRenderer, previewGroup;
function setupPreview(){
  if(previewRenderer) return;
  const host = $('previewwrap');
  previewScene = new THREE.Scene(); previewScene.background = new THREE.Color(0x292719);
  previewCamera = new THREE.PerspectiveCamera(38,1,.1,100);
  previewCamera.position.set(6,4.2,7); previewCamera.lookAt(0,.5,0);
  previewRenderer = new THREE.WebGLRenderer({ antialias:true, alpha:false });
  previewRenderer.setPixelRatio(Math.min(devicePixelRatio, 1.4));
  host.appendChild(previewRenderer.domElement);
  previewScene.add(new THREE.HemisphereLight(0xffffff, 0x51462a, 2));
  const light = new THREE.DirectionalLight(0xffffff, 2.2); light.position.set(4,7,5); previewScene.add(light);
  const floor = new THREE.Mesh(new THREE.CircleGeometry(5,48), new THREE.MeshStandardMaterial({ color:0x45412d, roughness:.9 }));
  floor.rotation.x = -Math.PI/2; floor.position.y = -0.05; previewScene.add(floor);
  previewGroup = new THREE.Group(); previewScene.add(previewGroup); resizePreview();
}
function resizePreview(){
  if(!previewRenderer) return;
  const h = $('previewwrap');
  const w = Math.max(1, h.clientWidth), ht = Math.max(1, h.clientHeight);
  previewRenderer.setSize(w, ht, false);
  previewCamera.aspect = w/ht; previewCamera.updateProjectionMatrix();
}
function buildPreview(c){ buildCarModel(previewGroup, c, 1.12); previewGroup.rotation.y = -0.18; }
function renderShop(){
  $('shop-cash').textContent = 'Saldo: ' + cashFmt(money);
  $('h-money').textContent = 'Dinheiro: ' + cashFmt(money);
  previewIndex = Math.max(0, Math.min(CARS.length-1, previewIndex));
  const c = CARS[previewIndex], has = owned.includes(c.id), active = selectedCar === c.id;
  setupPreview(); buildPreview(c);
  $('car-index').textContent = (previewIndex+1) + ' / ' + CARS.length;
  $('car-info').innerHTML = `
    <h3>${c.name}</h3>
    <p><b>Preço:</b> ${c.price ? cashFmt(c.price) : 'GRÁTIS'}</p>
    <p><b>Pagamento de drift:</b> ×${c.mult}</p>
    <p><b>Aceleração:</b> ${c.accel} • <b>Vel. máx:</b> ${c.maxSpeed}</p>
    <p><b>Aderência:</b> ${c.grip.toFixed(2)} • <b>Drift:</b> ${c.driftGrip.toFixed(2)}</p>
    <p>${c.desc}</p>
    <button id="car-action" ${active?'disabled':''}>${active?'EM USO':has?'USAR CARRO':money>=c.price?'COMPRAR CARRO':'COMPRAR — FALTAM '+cashFmt(c.price-money)}</button>`;
  $('car-prev').disabled = previewIndex===0;
  $('car-next').disabled = previewIndex===CARS.length-1;
  $('car-action').onclick = () => {
    if(owned.includes(c.id)){ selectedCar=c.id; buildCarModel(cg,c); say('Carro selecionado: '+c.name); saveGarage(); renderShop(); return; }
    if(money < c.price){ say('Dinheiro insuficiente!'); return; }
    money -= c.price; owned.push(c.id); selectedCar = c.id; buildCarModel(cg,c); saveGarage(); renderShop(); say('Comprou: '+c.name+'!');
  };
  resizePreview();
}
$('car-prev').onclick = () => { previewIndex = Math.max(0, previewIndex-1); renderShop(); };
$('car-next').onclick = () => { previewIndex = Math.min(CARS.length-1, previewIndex+1); renderShop(); };
function openShop(){ shopOpen=true; $('shop').style.display='flex'; renderShop(); }
function closeShop(){ shopOpen=false; $('shop').style.display='none'; }
$('shop-open').onclick = openShop; $('shop-close').onclick = closeShop;

/* =====================================================================
   BOTS
   ===================================================================== */
function updateBotHUD(){ $('h-bots').textContent = activeBots.length ? ('Bots: ' + activeBots.map(b=>b.name).join(', ')) : ''; }
function spawnBots(){
  clearBots(); let i = 0;
  const fx = Math.sin(car.a), fz = Math.cos(car.a), sx = Math.cos(car.a), sz = -Math.sin(car.a);
  for(const id of selectedBots){
    const bt = BOT_TYPES.find(b => b.id===id); if(!bt) continue;
    const group = new THREE.Group();
    buildCarModel(group, {id:'sport', color:bt.color});
    const back = (Math.floor(i/2)+1)*5.5, side = (i%2 ? 1 : -1)*3.2;
    const bx = car.x - fx*back + sx*side, bz = car.z - fz*back + sz*side;
    group.position.set(bx,0,bz); group.rotation.y = car.a; world.add(group);
    activeBots.push({ group, x:bx, z:bz, a:car.a, vx:0, vz:0, r:1.5, skill:bt.skill, name:bt.name, cpI:0, st:0 });
    i++;
  }
  updateBotHUD();
}
function clearBots(){ activeBots.forEach(b => { world.remove(b.group); disposeObj(b.group); }); activeBots=[]; updateBotHUD(); }
function updateBots(dt){
  for(const b of activeBots){
    const target = CP[b.cpI % CP.length];
    const dx = target[0]-b.x, dz = target[1]-b.z;
    const da = angDiff(Math.atan2(dx, dz), b.a);
    b.st = Math.max(-1, Math.min(1, da*3)) * b.skill;
    b.a += b.st * 2.2 * dt;
    const fx = Math.sin(b.a), fz = Math.cos(b.a);
    let vf = b.vx*fx + b.vz*fz;
    const maxV = 50 + b.skill*30;
    vf += (maxV - vf) * 0.4 * dt * b.skill; vf -= vf * 0.3 * dt;
    let vl = (Math.sin(T*2 + b.x)*8) * (1 - b.skill*0.5);
    b.vx = fx*vf + Math.cos(b.a)*vl; b.vz = fz*vf - Math.sin(b.a)*vl;
    b.x += b.vx*dt; b.z += b.vz*dt;
    wallCollide(b, b.r, .4); staticCollide(b, b.r, .3);
    if(Math.hypot(b.x-target[0], b.z-target[1]) < 14) b.cpI++;
    b.group.position.set(b.x,0,b.z); b.group.rotation.y = b.a;
  }
}

/* =====================================================================
   CÂMERA
   ===================================================================== */
const camPos = new THREE.Vector3(), camLook = new THREE.Vector3(), tp = new THREE.Vector3(), tl = new THREE.Vector3();
const camQ = {x:0, z:0, vx:0, vz:0};
let camSnap = true, camFov = 68, shake = 0, camRoll = 0, hy = 0, shotT = 0, shotI = 0, cockpitOn = false;
const orbit = { yaw:0, pitch:0, zoom:1, drag:false, idle:0, lx:0, ly:0 };

function clipRay(cx,cz,tx,tz,m){
  const dx = tx-cx, dz = tz-cz, len = Math.hypot(dx,dz) || 1, n = Math.ceil(len/.5);
  for(let i=1;i<=n;i++){
    const t = i/n;
    if(solid(Math.floor((cx+dx*t)/S), Math.floor((cz+dz*t)/S))){
      const tt = Math.max(.05, (i-1)/n - m/len);
      return [cx+dx*tt, cz+dz*tt];
    }
  }
  return [tx,tz];
}
function camUpd(dt, sp, vl){
  const k = a => 1 - Math.exp(-a*dt);
  const mode = run ? CAMS[currentCam].id : 'menu';
  const fx = Math.sin(car.a), fz = Math.cos(car.a);
  if(!orbit.drag){ orbit.idle += dt; if(orbit.idle > 1.2){ const r = 1 - k(2.4); orbit.yaw *= r; orbit.pitch *= r; } }
  const back = keys.b ? Math.PI : 0;
  const slipA = sp > 5 ? clamp(angDiff(Math.atan2(car.vx, car.vz), car.a), -1, 1) : 0;
  const slipK = clamp((sp-6)/10, 0, 1);
  let fovT = 68, pr = 9, lr = 10, clip = true, cm = .9, hideCar = false, ceilClamp = true;

  if(mode === 'chase'){
    ca += angDiff(car.a + slipA*.4*slipK, ca) * k(4.2);
    const yaw = ca + orbit.yaw + back, dist = (8.6 + sp*.045) * orbit.zoom;
    tp.set(car.x - Math.sin(yaw)*dist, 2.3 + dist*(.14 + orbit.pitch), car.z - Math.cos(yaw)*dist);
    const la = back ? 0 : 5 + sp*.05;
    tl.set(car.x + fx*la, 1.2, car.z + fz*la);
    fovT = 66 + sp*.4 + (Math.abs(vl) > 3 ? 4 : 0);
  } else if(mode === 'hood'){
    hy += angDiff(car.a + slipA*.25*slipK, hy) * k(12);
    tp.set(car.x + fx*1.7, 1.15 + Math.sin(T*28)*sp*.0008, car.z + fz*1.7);
    tl.set(tp.x + Math.sin(hy)*14, 1.0, tp.z + Math.cos(hy)*14);
    fovT = 74 + sp*.5; pr = 40; lr = 40; cm = .15; ceilClamp = false;
  } else if(mode === 'cockpit'){
    hy += angDiff(car.a + slipA*.3*slipK, hy) * k(10);
    tp.set(car.x + Math.cos(car.a)*.38 + fx*.1, 1.2, car.z - Math.sin(car.a)*.38 + fz*.1);
    const ly = hy + car.st*.12;
    tl.set(tp.x + Math.sin(ly)*14, 1.1, tp.z + Math.cos(ly)*14);
    fovT = 78 + sp*.35; pr = 60; lr = 40; cm = .1; hideCar = true; ceilClamp = false;
  } else if(mode === 'top'){
    ca += angDiff(car.a, ca) * k(2.2);
    tp.set(car.x - Math.sin(ca)*8, 30 + sp*.18, car.z - Math.cos(ca)*8);
    tl.set(car.x + Math.sin(ca)*4, 0, car.z + Math.cos(ca)*4);
    fovT = 52; pr = 5; lr = 8; clip = false; ceilClamp = false;
  } else if(mode === 'cinematic'){
    shotT -= dt; if(shotT <= 0){ shotT = 4.5 + Math.random()*2.5; shotI = (shotI+1)%4; }
    ca += angDiff(car.a, ca) * k(2);
    const cfx = Math.sin(ca), cfz = Math.cos(ca), csx = Math.cos(ca), csz = -Math.sin(ca);
    if(shotI === 0) tp.set(car.x - cfx*13, 5.5, car.z - cfz*13);
    else if(shotI === 1) tp.set(car.x + cfx*10 + csx*3, 1.5, car.z + cfz*10 + csz*3);
    else if(shotI === 2) tp.set(car.x + csx*12 - cfx*2, 3.2, car.z + csz*12 - cfz*2);
    else { tp.set(car.x - cfx*6 - csx*8, 10.5, car.z - cfz*6 - csz*8); ceilClamp = false; clip = false; }
    tl.set(car.x + fx*2, 1.3, car.z + fz*2);
    fovT = 52; pr = 2.4; lr = 6;
  } else if(mode === 'side'){
    ca += angDiff(car.a, ca) * k(3.5);
    tp.set(car.x + Math.cos(ca)*11, 3.4, car.z - Math.sin(ca)*11);
    tl.set(car.x + fx*1.5, 1.3, car.z + fz*1.5);
    fovT = 58; pr = 6; lr = 9;
  } else {
    const yaw = T*.17 + 2.4;
    tp.set(car.x - Math.sin(yaw)*11, 3.6, car.z - Math.cos(yaw)*11);
    tl.set(car.x, 1.1, car.z);
    fovT = 58; pr = 3; lr = 8;
  }
  if(ceilClamp && ENV.ceil) tp.y = Math.min(tp.y, ENV.ceil - .35);
  tp.y = Math.max(tp.y, .9);
  if(clip){ const c = clipRay(car.x, car.z, tp.x, tp.z, cm); tp.x = c[0]; tp.z = c[1]; }

  if(camSnap){ camPos.copy(tp); camLook.copy(tl); camFov = fovT; camSnap = false; }
  else {
    const rp = k(pr), rl = k(lr);
    camPos.x += (tp.x-camPos.x)*rp; camPos.z += (tp.z-camPos.z)*rp; camPos.y += (tp.y-camPos.y)*k(pr*.8);
    camLook.x += (tl.x-camLook.x)*rl; camLook.y += (tl.y-camLook.y)*rl; camLook.z += (tl.z-camLook.z)*rl;
    camFov += (fovT-camFov)*k(4);
  }
  if(clip){ camQ.x = camPos.x; camQ.z = camPos.z; wallCollide(camQ, .7, 0); camPos.x = camQ.x; camPos.z = camQ.z; }

  shake *= Math.exp(-dt*5);
  const sh = shake + sp*((mode==='hood' || mode==='cockpit') ? .0022 : .0008);
  cam.position.set(camPos.x + (Math.random()-.5)*sh, camPos.y + (Math.random()-.5)*sh, camPos.z + (Math.random()-.5)*sh);
  cam.lookAt(camLook);
  camRoll += (-clamp(vl*.0035, -.08, .08) - camRoll) * k(5);
  if(mode !== 'top') cam.rotateZ(camRoll);
  cam.fov = camFov; cam.updateProjectionMatrix();

  cg.visible = !hideCar;
  const cpv = hideCar && run;
  if(cpv !== cockpitOn){ cockpitOn = cpv; $('cockpit').style.display = cpv ? 'block' : 'none'; }
  if(cockpitOn) $('wheel').style.transform = 'translateX(-50%) rotate(' + (-car.st*110).toFixed(1) + 'deg)';
}
function cycleCam(){
  currentCam = (currentCam+1)%CAMS.length; orbit.zoom = 1; saveGarage();
  say('Câmera: '+CAMS[currentCam].name, 1.8); $('h-cam').textContent = 'Câm: '+CAMS[currentCam].name;
}

/* =====================================================================
   MINIMAPA / MARCADOR DE CHECKPOINT
   ===================================================================== */
const mmc = $('minimap'), mmg = mmc.getContext('2d'); let mmBase = null;
function drawMinimapBase(){
  const k = 4;
  mmBase = document.createElement('canvas'); mmBase.width = W*k; mmBase.height = H*k;
  const g = mmBase.getContext('2d');
  g.fillStyle = '#0b0a06'; g.fillRect(0,0,W*k,H*k);
  for(let y=0;y<H;y++) for(let x=0;x<W;x++){ g.fillStyle = solid(x,y) ? ENV.mm[0] : (ENV.road ? ENV.mm[0] : ENV.mm[1]); g.fillRect(x*k,y*k,k,k); }
  if(ENV.road){
    g.strokeStyle = ENV.mm[1]; g.lineWidth = ROADHALF*2*k/S; g.lineJoin = 'round'; g.lineCap = 'round';
    g.beginPath(); CP.forEach(([x,z],i) => { if(i) g.lineTo(x*k/S, z*k/S); else g.moveTo(x*k/S, z*k/S); }); g.closePath(); g.stroke();
  }
  mmc.width = W*k; mmc.height = H*k;
}
function drawMinimap(){
  if(!mmBase) return;
  mmg.drawImage(mmBase,0,0);
  const k = 4/S, c = CP[cpI % CP.length];
  mmg.strokeStyle = '#4fe'; mmg.lineWidth = 2; mmg.beginPath(); mmg.arc(c[0]*k, c[1]*k, 5, 0, 6.283); mmg.stroke();
  mmg.fillStyle = '#f55'; activeBots.forEach(b => { mmg.beginPath(); mmg.arc(b.x*k, b.z*k, 2.5, 0, 6.283); mmg.fill(); });
  mmg.save(); mmg.translate(car.x*k, car.z*k); mmg.rotate(-car.a);
  mmg.fillStyle = '#ffe45e'; mmg.strokeStyle = '#000'; mmg.lineWidth = 1;
  mmg.beginPath(); mmg.moveTo(0,6); mmg.lineTo(4,-4); mmg.lineTo(-4,-4); mmg.closePath(); mmg.fill(); mmg.stroke(); mmg.restore();
}
function buildMisc(){
  const chk = cv(64,64,g => { for(let i=0;i<4;i++) for(let j=0;j<4;j++){ g.fillStyle = (i+j)%2 ? '#111' : '#fff'; g.fillRect(i*16,j*16,16,16); } });
  chk.repeat.set(1,6);
  const sl = new THREE.Mesh(new THREE.PlaneGeometry(2.5,15).rotateX(-Math.PI/2), new THREE.MeshBasicMaterial({ map:chk }));
  sl.rotation.y = ST.a - Math.PI/2; sl.position.set(ST.x,.07,ST.z); world.add(sl);
  bkH = ENV.ceil ? ENV.ceil : 70;
  bk = new THREE.Mesh(new THREE.CylinderGeometry(2.4,2.4,1,24,1,true),
    new THREE.MeshBasicMaterial({ color:0x44ffe0, transparent:true, opacity:.22, side:THREE.DoubleSide, depthWrite:false, blending:THREE.AdditiveBlending, fog:false }));
  bk.scale.y = bkH; bk.position.y = bkH/2;
  bkRing = new THREE.Mesh(new THREE.RingGeometry(3.2,4.4,32).rotateX(-Math.PI/2),
    new THREE.MeshBasicMaterial({ color:0x44ffe0, transparent:true, opacity:.5, side:THREE.DoubleSide, depthWrite:false, blending:THREE.AdditiveBlending }));
  bkRing.position.y = .09; world.add(bk, bkRing);
}

/* =====================================================================
   CARREGAR MAPA
   ===================================================================== */
function placeCar(){
  car.x = ST.x; car.z = ST.z; car.a = ST.a; car.vx = car.vz = 0; car.st = 0;
  cpI = 0; lapT = 0; ca = car.a; hy = car.a; zone = ''; zT = 0; camSnap = true; orbit.yaw = orbit.pitch = 0;
}
function rebuildWorld(mi, ti, keep){
  const sv = keep ? { x:car.x, z:car.z, a:car.a, vx:car.vx, vz:car.vz, st:car.st, cpI, lap, lapT } : null;
  const hadBots = activeBots.length > 0;
  clearBots(); clearWorld();
  currentMap = mi; currentTrack = ti;
  const m = MAPS[mi], tr = m.tracks[ti];
  envKey = tr.night ? 'nokio' : m.env;
  CP = getCP(); ST = startOf(tr); setRoad();
  ENV = Object.assign({slide:1,offSlide:1,offDrag:1,offAcc:1,road:false}, ENVS[envKey]);
  ROADHALF = ENV.road ? 9 : 0;
  applyEnv(ENV); applyQuality();
  m.build(tr);
  buildSkid(); buildSmoke(); buildWeather(ENV.weather); buildMisc();
  placeCar();
  if(sv){ Object.assign(car, {x:sv.x, z:sv.z, a:sv.a, vx:sv.vx, vz:sv.vz, st:sv.st}); cpI = sv.cpI; lap = sv.lap; lapT = sv.lapT; ca = car.a; hy = car.a; }
  drawMinimapBase();
  if(hadBots) spawnBots();
  saveGarage();
}
function loadMap(mi, ti, cb, keep){
  busy = true; $('loading-t').textContent = 'Carregando ' + MAPS[mi].name + '…'; $('loading').style.display = 'flex';
  setTimeout(() => {
    try{ rebuildWorld(mi, ti, keep); }catch(err){ console.error(err); say('Erro ao carregar o mapa'); }
    busy = false; $('loading').style.display = 'none';
    if(cb) cb();
  }, 60);
}
function selectMap(i){
  if(busy || i === currentMap) return;
  loadMap(i, 0, () => { renderMapMenu(); if(run) say(MAPS[i].icon + ' Mapa: ' + MAPS[i].name, 2.6); });
}
function selectTrack(i){
  if(busy || i === currentTrack) return;
  const m = MAPS[currentMap];
  if(m.id === 'backrooms'){
    currentTrack = i; CP = getCP(); setRoad(); envKey = m.tracks[i].night ? 'nokio' : m.env;
    ENV = Object.assign({slide:1,offSlide:1,offDrag:1,offAcc:1,road:false}, ENVS[envKey]);
    applyEnv(ENV); applyQuality(); setLampTint(); buildWeather(ENV.weather);
    cpI = 0; lapT = 0; lap = 1; saveGarage(); drawMinimapBase(); renderMapMenu();
    if(run) say('Pista: ' + m.tracks[i].name, 2.5);
  } else {
    loadMap(currentMap, i, () => { renderMapMenu(); if(run) say('Pista: ' + curTrack().name, 2.5); });
  }
}

/* =====================================================================
   FÍSICA / LOOP DO JOGO
   ===================================================================== */
function shadowFollow(){
  if(ENV.sun){
    sun.position.set(car.x + sunDir.x*120, sunDir.y*120, car.z + sunDir.z*120);
    sun.target.position.set(car.x, 0, car.z);
  }
}
function step(dt){
  const cc = currentCar();
  const up = keys.arrowup || keys.w, dn = keys.arrowdown || keys.s;
  const lf = keys.arrowleft || keys.a, rt = keys.arrowright || keys.d;
  const hb = keys[' '];

  let fx = Math.sin(car.a), fz = Math.cos(car.a);
  let vf = car.vx*fx + car.vz*fz;

  const steerTarget = ((lf?1:0) - (rt?1:0));
  car.st += (steerTarget - car.st) * Math.min(1, dt * cc.steerResponse);
  const steerFactor = Math.max(-1, Math.min(1, vf / 9)) / (1 + Math.abs(vf)/45);
  car.a += car.st * 2.55 * steerFactor * (hb ? 1.45 : 1) * dt;

  fx = Math.sin(car.a); fz = Math.cos(car.a);
  const sx = Math.cos(car.a), sz = -Math.sin(car.a);
  vf = car.vx*fx + car.vz*fz;
  let vl = car.vx*sx + car.vz*sz;
  const prevVf = vf;

  const isWet = wet(car.x, car.z);
  const off = ENV.road && roadDist(car.x, car.z) > ROADHALF + 1.5;
  const driftG = cc.driftGrip * (isWet ? 0.75 : 1.0);

  if(up) vf += cc.accel * cc.power * dt * (off ? ENV.offAcc : 1);
  if(dn) vf += (vf > 0.5 ? -42 : -16) * dt;

  const maxV = cc.maxSpeed * (isWet ? 0.82 : 1) * (off ? .93 : 1);
  if(vf > maxV) vf = maxV + (vf - maxV) * 0.92;

  vf -= vf * (up ? 0.55 : 0.82) * dt * (off ? ENV.offDrag : 1);
  if(hb) vf -= vf * 0.48 * dt;

  const slip = Math.abs(vl);
  const lateralFriction = driftG * (1.15 - Math.min(0.7, slip / 18));
  const decay = hb ? 0.55 : (5.8 * lateralFriction);
  vl *= Math.exp(-decay * (isWet ? 0.35 : 1) * ENV.slide * (off ? ENV.offSlide : 1) * dt);

  if(hb && Math.abs(car.st) > 0.3 && Math.abs(vf) > 8) vl += car.st * vf * 0.12 * dt;

  car.vx = fx*vf + sx*vl;
  car.vz = fz*vf + sz*vl;
  car.x += car.vx * dt;
  car.z += car.vz * dt;

  let hit = wallCollide(car, car.r, 0.35);
  hit = Math.max(hit, staticCollide(car, car.r, 0.3));
  const sp = Math.hypot(car.vx, car.vz);
  if(hit > 5){ sfx.boing(); shake = Math.max(shake, Math.min(.6, hit*.04)); }
  if(hit > 7 && pts > 0){ say('Combo perdido! A parede não perdoa.'); pts=0; dtm=0; }

  /* pontuação de drift */
  const dr = Math.abs(vl) > 2.8 && sp > 7.5;
  if(dr){
    dtm += dt; since = 0;
    pts += Math.abs(vl) * sp * 0.42 * (1 + dtm * 0.38) * dt;
  } else {
    since += dt;
    if(since > 0.65 && pts > 0){
      const p = Math.round(pts);
      score += p;
      const earned = Math.max(1, Math.round(p * cc.mult));
      money += earned; saveGarage();
      $('h-money').textContent = 'Dinheiro: ' + cashFmt(money);
      say('+' + p + ' pontos  |  +' + cashFmt(earned) + ' (×' + cc.mult + ')');
      pts=0; dtm=0;
    }
  }

  /* fumaça + marcas de pneu */
  const sliding = dr || (hb && sp > 6);
  if(sliding){
    puff(car.x - fx*1.6 + sx*(Math.random()<.5 ? .9 : -.9), car.z - fz*1.6 + sz*(Math.random()<.5 ? .9 : -.9), car.vx, car.vz);
  }
  if(skid && (sliding || (dn && vf > 12))){
    skidAcc += sp*dt;
    if(skidAcc > .55){
      skidAcc = 0;
      const yaw = sp > 2 ? Math.atan2(car.vx, car.vz) : car.a;
      for(const sgn of [-1,1]) addSkid(car.x - fx*1.35 + sx*sgn*.95, car.z - fz*1.35 + sz*sgn*.95, yaw);
    }
  }

  /* props */
  for(const p of props){
    p.x += p.vx*dt; p.z += p.vz*dt;
    const k = Math.exp(-1.6*dt); p.vx*=k; p.vz*=k; p.sp *= Math.exp(-2*dt);
    p.m.rotation.y += p.sp*dt; wallCollide(p, p.r, .5); staticCollide(p, p.r, .4);
    const dx=p.x-car.x, dz=p.z-car.z, d=Math.hypot(dx,dz), m=car.r+p.r;
    if(d < m && d > 1e-3){
      const nx=dx/d, nz=dz/d, rel=(car.vx-p.vx)*nx + (car.vz-p.vz)*nz;
      if(rel > 0){
        p.vx += nx*rel*1.5; p.vz += nz*rel*1.5;
        car.vx -= nx*rel*.25*p.k; car.vz -= nz*rel*.25*p.k;
        p.sp += (Math.random()-.5)*rel*.8;
        if(rel > 5) sfx.boing();
      }
      p.x = car.x + nx*m; p.z = car.z + nz*m;
    }
    p.m.position.x = p.x; p.m.position.z = p.z;
  }

  for(const d of ducks){
    d.cd -= dt; d.h -= dt*2;
    if(d.cd <= 0 && Math.hypot(d.x-car.x, d.z-car.z) < 2.6){ sfx.quack(); d.h=1; d.cd=1.2; }
    d.g.position.y = Math.max(0, d.h)*1.4 + 0.03*Math.sin(T*2 + d.x);
  }

  if(ENV.bulbs){
    spawnFall(dt);
    for(let i=fall.length-1; i>=0; i--){
      const f = fall[i]; f.t += dt;
      if(f.t < 1.3) f.w.visible = (f.t*8|0)%2===0;
      else {
        f.tb.position.y = Math.max(.12, 3.9 - (f.t-1.3)*15);
        if(!f.hit && f.tb.position.y <= .13){
          f.hit=1; f.w.visible=false;
          if(Math.hypot(f.x-car.x, f.z-car.z) < 2.8){ car.vx*=.55; car.vz*=.55; sfx.horn(); say('Lâmpada em queda! (garantia vencida)'); shake = Math.max(shake,.3); }
        }
      }
      if(f.t > 7){ world.remove(f.tb, f.w); f.tb.geometry.dispose(); f.w.geometry.dispose(); fall.splice(i,1); }
    }
  }

  if(cg.userData.beacon) cg.userData.beacon.material.color.setHex((T*6|0)%2 ? 0xff5500 : 0x552200);
  updateBots(dt);

  /* zona e checkpoints */
  const mp = MAPS[currentMap];
  const zk = mp.zone ? mp.zone(Math.floor(car.x/S), Math.floor(car.z/S)) : mp.id;
  if(zk !== zone){ zone = zk; zT = 3.2; }
  zT -= dt; lapT += dt;

  if(Math.hypot(car.x - CP[cpI][0], car.z - CP[cpI][1]) < 13){
    cpI++;
    if(cpI >= CP.length){
      cpI = 0; sfx.ding();
      const bonus = Math.max(5, Math.round(30 - lapT*0.4));
      money += bonus; saveGarage();
      $('h-money').textContent = 'Dinheiro: ' + cashFmt(money);
      say('Volta '+lap+' completa: '+lapT.toFixed(1)+' s  |  +'+cashFmt(bonus), 3.5);
      lap++; lapT=0;
    }
  }

  paT -= dt;
  if(paT <= 0){
    const lines = PAS[ENV.pa || mp.id] || PAS.backrooms;
    const l = lines[Math.floor(Math.random()*lines.length)];
    paT = 30 + Math.random()*15; paS = 5;
    $('h-pa').textContent = l;
    if(!muted) try{ const u=new SpeechSynthesisUtterance(l); u.lang='pt-BR'; u.pitch=.5; u.rate=.9; speechSynthesis.speak(u); }catch(e){}
  }
  paS -= dt; if(paS <= 0) $('h-pa').textContent = '';
  popT -= dt;

  /* visual do carro */
  const ax = (vf - prevVf) / Math.max(dt, 1e-3);
  pitch += (clamp(-ax*.0022, -.06, .06) - pitch) * Math.min(1, dt*6);
  wheelSpin += vf*dt/.42;
  cn.position.set(car.x, 0, car.z); cn.rotation.y = car.a;
  cg.rotation.z = -vl * 0.012; cg.rotation.x = pitch;
  if(!cg.userData.noSpin) for(const w of cg.userData.wheels) w.rotation.x = wheelSpin;
  const braking = !!dn && vf > .5;
  if(braking !== prevBrake){ prevBrake = braking; cg.userData.tails.forEach(m => m.material.color.setHex(braking ? 0xff4a3a : 0x8a1c18)); }
  hl.position.set(car.x + fx*4, 2.6, car.z + fz*4);
  head.position.set(car.x + fx*1.8, 1.1, car.z + fz*1.8); head.target.position.set(car.x + fx*28, 0, car.z + fz*28);
  shadowFollow();

  if(AC){
    eo.frequency.value = 40 + sp*3.4;
    eg.gain.value = .04 + (up ? .06 : 0);
    sg2.gain.value = Math.min(.22, Math.abs(vl)*.02 + (isWet && sp>5 ? .04 : 0));
  }

  camUpd(dt, sp, vl);
  updWeather(dt); updSmoke(dt);

  if(bk){
    const c = CP[cpI % CP.length], pulse = .2 + Math.sin(T*4)*.05;
    bk.position.x = bkRing.position.x = c[0]; bk.position.z = bkRing.position.z = c[1];
    bk.material.opacity = pulse; bkRing.rotation.y = T;
  }
  $('fx').style.setProperty('--v', (.16 + Math.min(.5, sp/130) + (dr ? .1 : 0)).toFixed(3));

  $('h-spd').textContent = Math.round(sp*3.6) + ' km/h';
  $('h-lap').textContent = 'Volta '+lap+'   '+lapT.toFixed(1)+' s   ponto '+cpI+'/'+CP.length;
  $('h-score').textContent = 'Pontos '+score;
  $('h-zone').textContent = zT>0 ? ZN[zone] : '';
  $('h-dr').textContent = pts>1 ? ('Drift '+Math.round(pts) + (dtm>2 ? '  ×'+(1+dtm*.4).toFixed(1) : '')) : (popT>0 ? pop : '');
  $('h-mode').textContent = mp.name + ' • ' + curTrack().name;
  $('h-ar').style.transform = 'translateX(-50%) rotate(' + (-(Math.atan2(CP[cpI][0]-car.x, CP[cpI][1]-car.z) - car.a)) + 'rad)';
  if((mmT++ & 1) === 0) drawMinimap();
}
function idle(dt){
  if(!run) camUpd(dt, 0, 0);
  updWeather(dt); updSmoke(dt); shadowFollow();
}
function loop(n){
  requestAnimationFrame(loop);
  const dt = Math.min(.05, (n-last)/1000 || .016); last=n; T+=dt;
  if(!busy){
    if(run && !shopOpen && !paused) step(dt); else idle(dt);
    lights(T);
  }
  if(skyG) skyG.position.copy(cam.position);
  R.render(scn, cam);
  if(previewRenderer && shopOpen){
    previewGroup.rotation.y += dt * .35;
    previewRenderer.render(previewScene, previewCamera);
  }
}
function resize(){
  R.setSize(innerWidth, innerHeight);
  cam.aspect = innerWidth / innerHeight;
  cam.updateProjectionMatrix();
}
addEventListener('resize', () => { resize(); resizePreview(); });

/* =====================================================================
   MENUS / ENTRADA
   ===================================================================== */
function dumpStorage(){
  const o = {}; try{ for(let i=0;i<localStorage.length;i++){ const k = localStorage.key(i); o[k] = localStorage.getItem(k); } }catch(e){}
  return JSON.stringify(o);
}
function quitGame(){
  saveGarage();
  const api = window.pywebview && window.pywebview.api;
  if(api && api.quit_game){ api.quit_game(dumpStorage()); return; }
  try{ window.close(); }catch(e){}
  $('mm-cash').textContent = 'Feche a janela/aba manualmente. 👋';
}
function toggleFull(){
  const api = window.pywebview && window.pywebview.api;
  if(api && api.toggle_fullscreen) api.toggle_fullscreen();
  else if(document.fullscreenElement) document.exitFullscreen(); else document.documentElement.requestFullscreen().catch(()=>{});
}
function setGfxLabels(){ const t = '⚙ GRÁFICOS: ' + Q().name; $('mm-gfx').textContent = t; $('pz-gfx').textContent = t; }
function cycleGfx(){
  if(busy) return;
  qIdx = (qIdx+1) % QUALS.length; setGfxLabels(); saveGarage();
  loadMap(currentMap, currentTrack, () => { if(run) say('Gráficos: ' + Q().name, 1.8); }, true);
}
function subOpen(){ return $('ov').style.display === 'flex'; }
function openSub(id){
  $('mm').style.display = 'none'; $('pause').style.display = 'none'; $('ov').style.display = 'flex';
  ['tracks-memo','bots-memo'].forEach(x => { $(x).style.display = x === id ? 'block' : 'none'; });
}
function closeSub(){
  $('ov').style.display = 'none';
  if(run) openPause(); else { $('mm-cash').textContent = 'Dinheiro: ' + cashFmt(money); $('mm').style.display = 'flex'; }
}
function openPause(){ paused = true; $('pause').style.display = 'flex'; }
function resumeGame(){ paused = false; $('pause').style.display = 'none'; }
function showMainMenu(){
  run = false; paused = false; saveGarage();
  $('hud').style.display = 'none';
  $('shop').style.display = 'none'; shopOpen = false;
  $('ov').style.display = 'none'; $('pause').style.display = 'none';
  $('mm-cash').textContent = 'Dinheiro: ' + cashFmt(money);
  $('mm').style.display = 'flex';
  clearBots(); camSnap = true;
}
function startGame(withBots){
  initAudio(); startMusic();
  $('mm').style.display = 'none'; $('ov').style.display = 'none'; $('pause').style.display = 'none'; $('hud').style.display = '';
  score=0; pts=0; dtm=0; since=0; lap=1;
  placeCar();
  if(withBots === true) spawnBots();
  paused = false; run = true;
}
function renderMapMenu(){
  const g = $('map-list-menu'); g.innerHTML = '';
  MAPS.forEach((m,i) => {
    const b = document.createElement('button');
    b.className = i === currentMap ? 'sel' : '';
    b.innerHTML = `<b>${m.icon} ${m.name}</b> <span class="key">[${i+1}]</span><br><span class="desc">${m.desc}</span>`;
    b.onclick = () => selectMap(i);
    g.appendChild(b);
  });
  const t = $('track-list-menu'); t.innerHTML = '';
  MAPS[currentMap].tracks.forEach((tr,i) => {
    const b = document.createElement('button');
    b.className = 'track-btn' + (i === currentTrack ? ' sel' : '');
    b.innerHTML = `<b>${tr.name}</b><br><span class="desc">${tr.desc}</span>`;
    b.onclick = () => selectTrack(i);
    t.appendChild(b);
  });
}
function renderBotListMenu(){
  const t = $('bot-list-menu'); t.innerHTML = '';
  BOT_TYPES.forEach(bt => {
    const b = document.createElement('button');
    b.className = 'bot-btn' + (selectedBots.has(bt.id) ? ' sel' : '');
    b.innerHTML = `<b>${bt.name}</b> ${selectedBots.has(bt.id)?'✓':''}<br><span class="desc">${bt.desc}</span>`;
    b.onclick = () => { if(selectedBots.has(bt.id)) selectedBots.delete(bt.id); else selectedBots.add(bt.id); renderBotListMenu(); };
    t.appendChild(b);
  });
}

addEventListener('keydown', e => {
  const k = e.key.toLowerCase(); keys[k] = 1;
  if(k.startsWith('arrow') || k === ' ') e.preventDefault();
  if(e.ctrlKey && k === 'q'){ quitGame(); return; }
  if(k === 'escape'){
    if(shopOpen) closeShop();
    else if(subOpen()) closeSub();
    else if(run) { if(paused) resumeGame(); else openPause(); }
    return;
  }
  if(k === 'm'){ muted = !muted; if(MG) MG.gain.value = muted ? 0 : .5; bgMusic.muted = muted; if(muted) try{ speechSynthesis.cancel(); }catch(x){} }
  if(k === 'f' && !e.ctrlKey) toggleFull();
  if(!run || paused || shopOpen || busy) return;
  if(k === 'r'){ car.x = ST.x; car.z = ST.z; car.a = ST.a; car.vx = car.vz = 0; car.st = 0; cpI = 0; lapT = 0; ca = car.a; hy = car.a; camSnap = true; }
  if(k === 'c') cycleCam();
  if(k === 't') selectTrack((currentTrack + 1) % MAPS[currentMap].tracks.length);
  if(k === 'g') openShop();
  if(k >= '1' && k <= '9' && MAPS[+k - 1]) selectMap(+k - 1);
});
addEventListener('keyup', e => { keys[e.key.toLowerCase()] = 0; });
addEventListener('blur', () => { keys = {}; if(run && !paused && !shopOpen) openPause(); });
document.addEventListener('click', e => { if(e.target && e.target.blur) e.target.blur(); });
R.domElement.addEventListener('mousedown', e => { orbit.drag = true; orbit.idle = 0; orbit.lx = e.clientX; orbit.ly = e.clientY; });
R.domElement.addEventListener('contextmenu', e => e.preventDefault());
addEventListener('mouseup', () => { orbit.drag = false; orbit.idle = 0; });
addEventListener('mousemove', e => {
  if(!orbit.drag) return;
  orbit.yaw -= (e.clientX - orbit.lx) * .006;
  orbit.pitch = clamp(orbit.pitch + (e.clientY - orbit.ly) * .0025, -.1, .45);
  orbit.lx = e.clientX; orbit.ly = e.clientY; orbit.idle = 0;
});
addEventListener('wheel', e => {
  if(run && !paused && !shopOpen) orbit.zoom = clamp(orbit.zoom * (1 + Math.sign(e.deltaY)*.08), .6, 2.2);
}, { passive:true });

$('mm-play').onclick = () => startGame();
$('mm-tracks').onclick = () => { renderMapMenu(); openSub('tracks-memo'); };
$('mm-bots').onclick = () => { renderBotListMenu(); openSub('bots-memo'); };
$('mm-garage').onclick = openShop;
$('mm-gfx').onclick = cycleGfx;
$('mm-quit').onclick = quitGame;
$('pz-resume').onclick = resumeGame;
$('pz-maps').onclick = () => { renderMapMenu(); openSub('tracks-memo'); };
$('pz-garage').onclick = openShop;
$('pz-gfx').onclick = cycleGfx;
$('pz-full').onclick = toggleFull;
$('pz-menu').onclick = showMainMenu;
$('pz-quit').onclick = quitGame;
$('menu-open').onclick = () => { if(run && !paused) openPause(); };
$('btn-close-tracks').onclick = closeSub;
$('btn-close-bots').onclick = closeSub;
$('btn-play-track').onclick = () => startGame();
$('btn-spawn-bots').onclick = () => startGame(true);

/* =====================================================================
   INÍCIO
   ===================================================================== */
$('h-money').textContent = 'Dinheiro: ' + cashFmt(money);
$('h-cam').textContent = 'Câm: ' + CAMS[currentCam].name;
buildCarModel(cg, currentCar());
setGfxLabels();
resize();
rebuildWorld(currentMap, currentTrack);
showMainMenu();
requestAnimationFrame(loop);
</script>
</body>
</html>
'''

# ======================================================================
# Save system (AppData)
# ======================================================================
APP_NAME = "BackroomsDrift"
SAVE_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), APP_NAME)
SAVE_FILE = os.path.join(SAVE_DIR, "save.json")
os.makedirs(SAVE_DIR, exist_ok=True)

_load_lock = threading.Lock()
_quitting = False
window = None


def load_save():
    try:
        with _load_lock:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        return data.get("localStorage", {})
    except Exception:
        return {}


def write_save(localStorage_dict):
    tmp = SAVE_FILE + ".tmp"
    try:
        with _load_lock:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump({"localStorage": localStorage_dict}, f, ensure_ascii=False)
            os.replace(tmp, SAVE_FILE)
    except Exception as e:
        print("Erro ao salvar:", e)


def make_restore_script(saved):
    payload = json.dumps(saved, ensure_ascii=False)
    return (
        "<script>"
        "try{(function(){var s=" + payload + ";"
        "for(var k in s){try{localStorage.setItem(k,s[k]);}catch(e){}}"
        "})();}catch(e){console.warn('restore falhou',e);}"
        "</script>"
    )


class Api:
    def push_state(self, localStorage_json):
        try:
            data = json.loads(localStorage_json)
            write_save(data)
            return True
        except Exception as e:
            print("push_state erro:", e)
            return False

    def quit_game(self, localStorage_json=None):
        """Chamado pelo botão SAIR: salva e fecha a janela."""
        global _quitting
        _quitting = True
        try:
            if localStorage_json:
                write_save(json.loads(localStorage_json))
        except Exception as e:
            print("quit_game erro ao salvar:", e)

        def _close():
            try:
                window.destroy()
            except Exception:
                os._exit(0)

        threading.Timer(0.1, _close).start()
        return True

    def toggle_fullscreen(self):
        try:
            window.toggle_fullscreen()
        except Exception as e:
            print("fullscreen erro:", e)
        return True


HOOK_SCRIPT = r"""
(function(){
  if (window.__bd_hooked) return; window.__bd_hooked = true;
  var push = function(){
    try {
      if (window.pywebview && window.pywebview.api) {
        var obj = {};
        for (var i = 0; i < localStorage.length; i++) {
          var k = localStorage.key(i);
          obj[k] = localStorage.getItem(k);
        }
        window.pywebview.api.push_state(JSON.stringify(obj));
      }
    } catch(e){}
  };
  var oldSet = localStorage.setItem.bind(localStorage);
  localStorage.setItem = function(k, v){ oldSet(k, v); push(); };
  setInterval(push, 3000);
  window.addEventListener('beforeunload', push);
})();
"""

DUMP_JS = (
    "(function(){var o={};for(var i=0;i<localStorage.length;i++){"
    "var k=localStorage.key(i);o[k]=localStorage.getItem(k);}return JSON.stringify(o);})()"
)


def build_final_html():
    saved = load_save()
    html = HTML
    inject_at = html.find("<head")
    if inject_at == -1:
        inject_at = html.find("<html")
    if inject_at != -1:
        gt = html.find(">", inject_at)
        html = html[:gt + 1] + make_restore_script(saved) + html[gt + 1:]
    else:
        html = make_restore_script(saved) + html
    return html


def on_loaded(win):
    win.evaluate_js(HOOK_SCRIPT)


def on_closing(win):
    if _quitting:  # já salvou em quit_game
        return True
    try:
        dump = win.evaluate_js(DUMP_JS)
        if dump:
            write_save(json.loads(dump))
    except Exception:
        pass
    return True


def periodic_save(win):
    import time
    while True:
        time.sleep(5)
        if _quitting:
            return
        try:
            dump = win.evaluate_js(DUMP_JS)
            if dump:
                write_save(json.loads(dump))
        except Exception:
            pass


if __name__ == '__main__':
    api = Api()
    window = webview.create_window(
        'WEDRIFTED - V7.0',
        html=build_final_html(),
        js_api=api,
        width=1280,
        height=720,
        resizable=True,
        confirm_close=False
    )
    window.events.loaded += on_loaded
    window.events.closing += on_closing
    threading.Thread(target=periodic_save, args=(window,), daemon=True).start()
    webview.start()
