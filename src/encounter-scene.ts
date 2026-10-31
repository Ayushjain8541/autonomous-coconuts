import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { clampTime, phaseLabel, schematicSample, sliderSample, advancePlayback } from '../web/client/encounter-model.ts';

export function createEncounterScene(host: HTMLElement, missDistanceM: number | null) {
  const canvas = document.createElement('canvas');
  canvas.setAttribute('aria-label','Conceptual local encounter. Drag to orbit; scroll to zoom. Arrow keys orbit.');
  canvas.tabIndex = 0;
  host.append(canvas);
  let renderer: THREE.WebGLRenderer;
  try { renderer = new THREE.WebGLRenderer({ canvas, antialias:true, alpha:true }); }
  catch { canvas.remove(); host.append(document.createTextNode('3D rendering unavailable. Numeric encounter facts remain available.')); return { setTime(_time:number){},reset(){},zoom(_factor:number){},dispose(){} }; }
  renderer.setPixelRatio(Math.min(devicePixelRatio,2));
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(42,1,.1,500);
  const controls = new OrbitControls(camera,canvas);
  controls.enablePan = false; controls.minDistance = 10; controls.maxDistance = 65;
  controls.target.set(0,2,0);
  function reset() { camera.position.set(12,10,27); controls.target.set(0,2,0); controls.update(); render(); }
  scene.add(new THREE.AmbientLight(0xd9e7ff,2));
  const light = new THREE.DirectionalLight(0xffffff,3); light.position.set(-10,18,20); scene.add(light);
  const metal = new THREE.MeshStandardMaterial({color:0xd5dce4,metalness:.65,roughness:.4});
  const blue = new THREE.MeshStandardMaterial({color:0x326fa9,metalness:.4,roughness:.4});
  const amber = new THREE.MeshStandardMaterial({color:0xba9973,metalness:.7,roughness:.6});
  const primary = new THREE.Group();
  const body = new THREE.Mesh(new THREE.CylinderGeometry(.42,.42,1,16),metal); primary.add(body);
  for (const side of [-1,1]) {
    const panel = new THREE.Mesh(new THREE.BoxGeometry(1.3,.75,.07),blue); panel.position.x=side*1.1; primary.add(panel);
    for(let i=0;i<4;i++){const bar = new THREE.Mesh(new THREE.BoxGeometry(.025,.76,.08),metal);bar.position.x=side*1.1-.48+i*.32;primary.add(bar);}
  }
  const dish = new THREE.Mesh(new THREE.ConeGeometry(.35,.28,16,1,true),metal); dish.position.y=.65; primary.add(dish);
  scene.add(primary);
  const debris = new THREE.Mesh(new THREE.IcosahedronGeometry(.45,0),amber); debris.rotation.set(.3,.5,.7); scene.add(debris);
  const pathMaterial = new THREE.LineBasicMaterial({color:0x51657b,transparent:true,opacity:.7});
  const primaryPath = new THREE.Line(new THREE.BufferGeometry(),pathMaterial),debrisPath = new THREE.Line(new THREE.BufferGeometry(),pathMaterial);
  const lineMaterial = new THREE.LineBasicMaterial({color:0xa8d5ff});
  const distanceLine = new THREE.Line(new THREE.BufferGeometry(),lineMaterial); scene.add(primaryPath,debrisPath,distanceLine);
  const tcaMarker = new THREE.Mesh(new THREE.TorusGeometry(.8,.025,6,40),new THREE.MeshBasicMaterial({color:0x9bcbff}));scene.add(tcaMarker);
  const grid = new THREE.GridHelper(32,16,0x344454,0x1d2a38);grid.position.y=-1.5;scene.add(grid);
  let currentTime = 0, disposed = false;
  function render() {
    if(disposed)return;
    const width = Math.max(1,host.clientWidth),height = Math.max(1,host.clientHeight);
    renderer.setSize(width,height,false); camera.aspect=width/height; camera.updateProjectionMatrix();renderer.render(scene,camera);
  }
  controls.addEventListener('change',render);
  const resize = new ResizeObserver(render); resize.observe(host);
  function setTime(time:number) {
    currentTime=clampTime(time); const sample=schematicSample(missDistanceM,currentTime);
    primary.visible=debris.visible=distanceLine.visible=primaryPath.visible=debrisPath.visible=tcaMarker.visible=sample!==null;
    if(!sample){render();return;}
    primary.position.fromArray(sample.primary);debris.position.fromArray(sample.debris);
    distanceLine.geometry.dispose();distanceLine.geometry=new THREE.BufferGeometry().setFromPoints([primary.position.clone(),debris.position.clone()]);
    distanceLine.visible=Math.abs(currentTime-.5)<.025;
    tcaMarker.position.copy(primary.position);tcaMarker.visible=distanceLine.visible;tcaMarker.lookAt(camera.position);
    for(const [line,key]of [[primaryPath,'primary'],[debrisPath,'debris']]as const){line.geometry.dispose();line.geometry=new THREE.BufferGeometry().setFromPoints([0,.5,1].map(t=>new THREE.Vector3(...schematicSample(missDistanceM,t)![key])));}
    render();
  }
  canvas.addEventListener('keydown',event=>{
    if(!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(event.key))return;
    event.preventDefault();const relative=camera.position.clone().sub(controls.target),spherical=new THREE.Spherical().setFromVector3(relative);
    spherical.theta+=(event.key==='ArrowLeft'?.12:event.key==='ArrowRight'?-.12:0);spherical.phi=Math.min(Math.PI-.15,Math.max(.15,spherical.phi+(event.key==='ArrowUp'?-.12:event.key==='ArrowDown'?.12:0)));camera.position.copy(controls.target).add(new THREE.Vector3().setFromSpherical(spherical));controls.update();render();
  });
  reset();setTime(0);
  return {setTime,reset,zoom(factor:number){const offset=camera.position.clone().sub(controls.target);offset.setLength(Math.min(65,Math.max(10,offset.length()*factor)));camera.position.copy(controls.target).add(offset);controls.update();render();},dispose(){disposed=true;resize.disconnect();controls.dispose();scene.traverse(object=>{if(object instanceof THREE.Mesh||object instanceof THREE.Line){object.geometry.dispose();const materials=Array.isArray(object.material)?object.material:[object.material];for(const material of materials)material.dispose();}});renderer.dispose();canvas.remove();}};
}

export function mountPlayback(host: HTMLElement, missDistanceM: number | null) {
  host.innerHTML=`<div class="local-scene"></div><div class="scene-object-labels"><span>Primary satellite · representative model</span><span>Debris · generic shape, class unavailable</span></div><div class="scene-camera"><button data-camera="in" aria-label="Zoom encounter in">+</button><button data-camera="out" aria-label="Zoom encounter out">−</button><button data-camera="reset">Focus / reset camera</button></div><div class="scene-disclosure"><strong>Illustrative encounter geometry — not a reconstructed orbital trajectory.</strong><span>Mode B · normalized conceptual motion · object sizes exaggerated</span></div><div class="playback"><div class="playback-readout" aria-live="off"></div><div class="rubber-slider" tabindex="0" role="slider" aria-label="Normalized encounter phase" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"><div class="slider-track"><div class="slider-progress"></div><span class="tca-tick"></span><span class="slider-thumb"></span></div></div><div class="phase-labels"><span>Approach</span><span>TCA</span><span>Departure</span></div><div class="playback-buttons"><button data-play="toggle">Play</button><button data-play="restart">Restart</button><button data-play="tca">Jump to TCA</button><label>Speed <select aria-label="Playback speed"><option value=".5">0.5×</option><option value="1" selected>1×</option><option value="2">2×</option></select></label></div></div>`;
  const motion=matchMedia('(prefers-reduced-motion: reduce)'),scene=createEncounterScene(host.querySelector<HTMLElement>('.local-scene')!,missDistanceM);
  const slider=host.querySelector<HTMLElement>('.rubber-slider')!,thumb=host.querySelector<HTMLElement>('.slider-thumb')!,progress=host.querySelector<HTMLElement>('.slider-progress')!,readout=host.querySelector<HTMLElement>('.playback-readout')!,toggle=host.querySelector<HTMLButtonElement>('[data-play="toggle"]')!,speed=host.querySelector<HTMLSelectElement>('select')!;
  let time=0,playing=false,frame=0,last=0;
  function update(value:number){time=clampTime(value);scene.setTime(time);slider.setAttribute('aria-valuenow',String(Math.round(time*100)));slider.setAttribute('aria-valuetext',`${phaseLabel(time)}, ${Math.round(time*100)} percent of illustrative interval`);thumb.style.left=progress.style.width=`${time*100}%`;const sample=schematicSample(missDistanceM,time);readout.textContent=sample?`${phaseLabel(time)} · ${Math.abs(time-.5)<1e-8?'TCA miss distance':'Illustrative center separation'} ${sample.separationM.toLocaleString(undefined,{maximumFractionDigits:1})} m · scale 1 scene unit = ${sample.metresPerUnit.toLocaleString()} m`:'Encounter geometry unavailable: predicted miss distance not supplied.';}
  function pause(){playing=false;cancelAnimationFrame(frame);toggle.textContent='Play';}
  function tick(now:number){if(!playing)return;const delta=Math.min(100,now-last);last=now;update(advancePlayback(time,delta,Number(speed.value)));if(time>=1)pause();else frame=requestAnimationFrame(tick);}
  toggle.addEventListener('click',()=>{if(playing){pause();return;}if(missDistanceM===null)return;if(time>=1)update(0);playing=true;last=performance.now();toggle.textContent='Pause';frame=requestAnimationFrame(tick);});
  host.querySelector('[data-play="restart"]')!.addEventListener('click',()=>{pause();update(0)});
  host.querySelector('[data-play="tca"]')!.addEventListener('click',()=>{pause();update(.5)});
  for(const button of host.querySelectorAll<HTMLButtonElement>('[data-camera]'))button.addEventListener('click',()=>button.dataset.camera==='reset'?scene.reset():scene.zoom(button.dataset.camera==='in'?.8:1.25));
  function seek(event:PointerEvent){if(missDistanceM===null)return;const rect=slider.getBoundingClientRect(),sample=sliderSample((event.clientX-rect.left)/rect.width,motion.matches);update(sample.time);thumb.style.transform=`translateX(calc(-50% + ${sample.visualOffset}px))`;}
  slider.addEventListener('pointerdown',event=>{pause();slider.focus();slider.setPointerCapture(event.pointerId);seek(event)});
  slider.addEventListener('pointermove',event=>{if(slider.hasPointerCapture(event.pointerId))seek(event)});
  function release(event:PointerEvent){if(slider.hasPointerCapture(event.pointerId))slider.releasePointerCapture(event.pointerId);thumb.style.transform='translateX(-50%)';}
  slider.addEventListener('pointerup',release);slider.addEventListener('pointercancel',release);slider.addEventListener('lostpointercapture',()=>{thumb.style.transform='translateX(-50%)'});
  slider.addEventListener('keydown',event=>{if(missDistanceM===null)return;const actions:Record<string,number>={ArrowLeft:time-.01,ArrowDown:time-.01,ArrowRight:time+.01,ArrowUp:time+.01,PageDown:time-.1,PageUp:time+.1,Home:0,End:1};if(event.key in actions){event.preventDefault();pause();update(actions[event.key])}});
  if(missDistanceM===null){for(const button of host.querySelectorAll<HTMLButtonElement>('[data-play]'))button.disabled=true;slider.setAttribute('aria-disabled','true');slider.tabIndex=-1;}
  const onVisibility=()=>{if(document.hidden)pause()};document.addEventListener('visibilitychange',onVisibility);
  update(0);
  return {dispose(){pause();document.removeEventListener('visibilitychange',onVisibility);scene.dispose();host.replaceChildren();}};
}
