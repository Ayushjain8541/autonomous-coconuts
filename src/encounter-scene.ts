import {sphereFraming,sceneVisibility} from '../web/client/scene-framing.ts';
import * as THREE from 'three';
import type {AnalysisResult,Encounter} from '../web/client/contract.ts';
import canonicalFixture from '../contracts/fixtures/analysis-demo.json';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { clampTime, phaseLabel, encounterMotion, relativeMotionSample, sliderSample, playbackStep, pointerEncounterTime } from '../web/client/encounter-model.ts';

export function createEncounterScene(host: HTMLElement, missDistanceM: number | null, model:ReturnType<typeof encounterMotion>) {
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
  controls.enablePan = true;
  const framingBounds=new THREE.Box3(),framingSphere=new THREE.Sphere();
  let fittedDistance=1;
  function fitCamera(preserveView=false) {
    const next=sphereFraming(framingSphere.radius,Math.max(1,host.clientWidth)/Math.max(1,host.clientHeight),camera.fov);
    const direction=preserveView?camera.position.clone().sub(controls.target).normalize():new THREE.Vector3(12,10,27).normalize();
    const ratio=preserveView?camera.position.distanceTo(controls.target)/fittedDistance:1;
    controls.minDistance=next.minDistance;controls.maxDistance=next.maxDistance;
    camera.near=next.near;camera.far=next.far;camera.updateProjectionMatrix();
    if(!preserveView)controls.target.copy(framingSphere.center);
    camera.position.copy(controls.target).addScaledVector(direction,Math.min(next.maxDistance,Math.max(next.minDistance,next.distance*ratio)));
    fittedDistance=next.distance;controls.update();
  }
  function reset(){fitCamera();render();}
  scene.background=new THREE.Color(0x070d17);scene.add(new THREE.HemisphereLight(0xb9d5ff,0x19120c,1.5));
  const light = new THREE.DirectionalLight(0xffffff,3); light.position.set(-10,18,20); scene.add(light);
  const metal = new THREE.MeshStandardMaterial({color:0xd5dce4,metalness:.65,roughness:.4});
  const blue = new THREE.MeshStandardMaterial({color:0x154e99,metalness:.4,roughness:.4});
  const amber = new THREE.MeshStandardMaterial({color:0xba9973,metalness:.7,roughness:.6});
  const primary = new THREE.Group();
  const body = new THREE.Mesh(new THREE.BoxGeometry(.85,1.15,.8),metal); primary.add(body);
  for (const side of [-1,1]) {
    const panel = new THREE.Mesh(new THREE.BoxGeometry(1.3,.75,.07),blue); panel.position.x=side*1.1; primary.add(panel);
    for(let i=0;i<4;i++){const bar = new THREE.Mesh(new THREE.BoxGeometry(.025,.76,.08),metal);bar.position.x=side*1.1-.48+i*.32;primary.add(bar);}
  }
  const dish = new THREE.Mesh(new THREE.ConeGeometry(.35,.28,16,1,true),metal); dish.position.y=.65; primary.add(dish);
  primary.scale.setScalar(2.2);scene.add(primary);
  const debris = new THREE.Mesh(new THREE.IcosahedronGeometry(.45,4),amber); debris.rotation.set(.3,.5,.7);debris.scale.setScalar(2.6); scene.add(debris);
  const pathMaterial = new THREE.LineBasicMaterial({color:0x51657b,transparent:true,opacity:.7});
  const primaryPath = new THREE.Line(new THREE.BufferGeometry(),pathMaterial),debrisPath = new THREE.Line(new THREE.BufferGeometry(),pathMaterial);
  const lineMaterial = new THREE.LineBasicMaterial({color:0xa8d5ff});
  const distanceLine = new THREE.Line(new THREE.BufferGeometry(),lineMaterial); scene.add(primaryPath,debrisPath,distanceLine);
  const tcaMarker = new THREE.Mesh(new THREE.TorusGeometry(.8,.025,6,40),new THREE.MeshBasicMaterial({color:0x9bcbff}));scene.add(tcaMarker);
  const fill=new THREE.DirectionalLight(0x4c9aff,2);fill.position.set(10,-5,-12);scene.add(fill);
  const foil=new THREE.Mesh(new THREE.BoxGeometry(.87,.7,.82),new THREE.MeshStandardMaterial({color:0xc1a55d,metalness:.8,roughness:.45}));foil.position.y=-.1;primary.add(foil);
  const antenna=new THREE.Mesh(new THREE.CylinderGeometry(.018,.018,.9,8),metal);antenna.position.set(.3,1,0);primary.add(antenna);
  const debrisPositions=debris.geometry.getAttribute('position');for(let i=0;i<debrisPositions.count;i++){const x=debrisPositions.getX(i),y=debrisPositions.getY(i),z=debrisPositions.getZ(i);const factor=.87+.12*Math.sin(x*13+y*9)*Math.cos(z*12)+.08*Math.sin(y*22-z*8);debrisPositions.setXYZ(i,x*factor*1.3,y*factor*.72,z*factor);}debris.geometry.computeVertexNormals();
  const grid=new THREE.GridHelper(28,14,0x34485c,0x203040);grid.position.y=-2.1;const gridMaterials=Array.isArray(grid.material)?grid.material:[grid.material];gridMaterials.forEach(m=>{m.transparent=true;m.opacity=.3});scene.add(grid);
  const axisColors=[0x8ba2b7,0x90b3a3,0xb09bbd];
  for(let i=0;i<3;i++){const direction=new THREE.Vector3();direction.setComponent(i,1);scene.add(new THREE.ArrowHelper(direction,new THREE.Vector3(),6,axisColors[i],.35,.18));const labelCanvas=document.createElement('canvas');labelCanvas.width=128;labelCanvas.height=64;const context=labelCanvas.getContext('2d')!;context.fillStyle='#c3d2e3';context.font='24px sans-serif';context.textAlign='center';context.fillText(['X · R','Y · T','Z · N'][i],64,38);const texture=new THREE.CanvasTexture(labelCanvas);const sprite=new THREE.Sprite(new THREE.SpriteMaterial({map:texture,transparent:true,depthTest:false}));sprite.position.copy(direction.clone().multiplyScalar(6.8));sprite.scale.set(2.3,1.15,1);scene.add(sprite);}
  const velocityArrow=new THREE.ArrowHelper(new THREE.Vector3(0,1,0),new THREE.Vector3(),4,0xe7b768,.45,.2);velocityArrow.visible=false;scene.add(velocityArrow);
  const positionArrow=new THREE.ArrowHelper(new THREE.Vector3(0,1,0),new THREE.Vector3(),4,0x65d5ef,.45,.2);scene.add(positionArrow);
  const distanceLabel=document.createElement('div');distanceLabel.className='tca-distance-label';distanceLabel.hidden=true;host.append(distanceLabel);
  let currentTime = 0, disposed = false;
  function render() {
    if(disposed)return;
    const width = Math.max(1,host.clientWidth),height = Math.max(1,host.clientHeight);
    renderer.setSize(width,height,false); camera.aspect=width/height; camera.updateProjectionMatrix();renderer.render(scene,camera);
    distanceLabel.hidden=!distanceLine.visible;
    if(distanceLine.visible){const projected=primary.position.clone().add(debris.position).multiplyScalar(.5).project(camera);distanceLabel.style.left=`${Math.max(65,Math.min(width-65,(projected.x*.5+.5)*width))}px`;distanceLabel.style.top=`${Math.max(130,Math.min(height-40,(-projected.y*.5+.5)*height-22))}px`;distanceLabel.textContent=`TCA · ${missDistanceM?.toLocaleString()} m`;}
  }
  controls.addEventListener('change',render);
  const resize = new ResizeObserver(()=>{fitCamera(true);render()}); resize.observe(host);
  function setTime(time:number) {
    currentTime=clampTime(time); const sample=model?relativeMotionSample(model,currentTime):null;
    const visibility=sceneVisibility(sample!==null);primary.visible=visibility.primary;primary.position.set(0,0,0);
    debris.visible=visibility.debris;
    velocityArrow.visible=positionArrow.visible=distanceLine.visible=primaryPath.visible=debrisPath.visible=tcaMarker.visible=visibility.vectors;
    if(!sample){render();return;}
    velocityArrow.position.fromArray(sample.debris);if(model){velocityArrow.setDirection(new THREE.Vector3(...model.velocity).normalize());velocityArrow.setLength(4,.45,.2);}
    primary.position.fromArray(sample.primary);debris.position.fromArray(sample.debris);const relative=debris.position.clone().sub(primary.position);positionArrow.position.copy(primary.position);positionArrow.visible=relative.length()>1e-8;if(positionArrow.visible){positionArrow.setDirection(relative.clone().normalize());positionArrow.setLength(relative.length(),Math.min(.45,relative.length()*.2),Math.min(.2,relative.length()*.1));}debris.rotation.set(.3+currentTime,.5+currentTime*.7,.7);
    distanceLine.geometry.dispose();distanceLine.geometry=new THREE.BufferGeometry().setFromPoints([primary.position.clone(),debris.position.clone()]);
    distanceLine.visible=Math.abs(currentTime-.5)<1e-8;
    tcaMarker.position.copy(primary.position);tcaMarker.visible=distanceLine.visible;tcaMarker.lookAt(camera.position);
    for(const [line,key]of [[primaryPath,'primary'],[debrisPath,'debris']]as const){line.geometry.dispose();line.geometry=new THREE.BufferGeometry().setFromPoints([0,.5,1].map(t=>new THREE.Vector3(...relativeMotionSample(model!,t)[key])));}
    render();
  }
  canvas.addEventListener('keydown',event=>{
    if(!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(event.key))return;
    event.preventDefault();const relative=camera.position.clone().sub(controls.target),spherical=new THREE.Spherical().setFromVector3(relative);
    spherical.theta+=(event.key==='ArrowLeft'?.12:event.key==='ArrowRight'?-.12:0);spherical.phi=Math.min(Math.PI-.15,Math.max(.15,spherical.phi+(event.key==='ArrowUp'?-.12:event.key==='ArrowDown'?.12:0)));camera.position.copy(controls.target).add(new THREE.Vector3().setFromSpherical(spherical));controls.update();render();
  });
  // Frame reference-model bounds even with no relative geometry. Include all supported
  // playback endpoints; linear motion stays inside their union. Never change telemetry.
  primary.updateMatrixWorld(true);framingBounds.setFromObject(primary);
  if(model){for(const time of [0,.5,1]){debris.position.fromArray(relativeMotionSample(model,time).debris);debris.updateMatrixWorld(true);const bounds=new THREE.Box3().setFromObject(debris);const sphere=bounds.getBoundingSphere(new THREE.Sphere());sphere.radius*=1.4;framingBounds.union(new THREE.Box3().setFromCenterAndSize(sphere.center,new THREE.Vector3().setScalar(sphere.radius*2)));}}
  framingBounds.getBoundingSphere(framingSphere);
  reset();setTime(0);
  return {setTime,reset,zoom(factor:number){const offset=camera.position.clone().sub(controls.target);offset.setLength(Math.min(controls.maxDistance,Math.max(controls.minDistance,offset.length()*factor)));camera.position.copy(controls.target).add(offset);controls.update();render();},dispose(){disposed=true;resize.disconnect();controls.dispose();scene.traverse(object=>{if(object instanceof THREE.Sprite){object.material.map?.dispose();object.material.dispose();}if(object instanceof THREE.Mesh||object instanceof THREE.Line){object.geometry.dispose();const materials=Array.isArray(object.material)?object.material:[object.material];for(const material of materials)material.dispose();}});renderer.dispose();canvas.remove();distanceLabel.remove();}};
}

export function mountPlayback(host: HTMLElement, analysis:AnalysisResult,row:Encounter) {
  const missDistanceM=row.miss_distance_m,model=encounterMotion(analysis,row,canonicalFixture as AnalysisResult);
  host.innerHTML=`<div class="scene-camera"><button data-camera="in" aria-label="Zoom encounter in">+</button><button data-camera="out" aria-label="Zoom encounter out">−</button><button data-camera="reset">Focus / reset camera</button></div><div class="local-scene"></div><div class="scene-disclosure"><strong>Illustrative encounter${model?' · sizes exaggerated':' · relative geometry unavailable'}</strong></div><div class="playback"><div class="minimum-readout"></div><div class="playback-readout" aria-live="off"></div><div class="rubber-slider" tabindex="0" role="slider" aria-label="Normalized encounter phase" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"><div class="slider-track"><div class="slider-progress"></div><span class="tca-tick"></span><span class="slider-thumb"></span></div></div><div class="phase-labels"><span>Approach</span><span>TCA</span><span>Departure</span></div><div class="playback-buttons"><button data-play="toggle">Play</button><button data-play="restart">Restart</button><button data-play="tca">Jump to TCA</button><label>Speed <select aria-label="Playback speed"><option value=".5">0.5×</option><option value="1" selected>1×</option><option value="2">2×</option></select></label></div></div>`;
  const motion=matchMedia('(prefers-reduced-motion: reduce)'),scene=createEncounterScene(host.querySelector<HTMLElement>('.local-scene')!,missDistanceM,model);
  const slider=host.querySelector<HTMLElement>('.rubber-slider')!,thumb=host.querySelector<HTMLElement>('.slider-thumb')!,progress=host.querySelector<HTMLElement>('.slider-progress')!,readout=host.querySelector<HTMLElement>('.playback-readout')!,toggle=host.querySelector<HTMLButtonElement>('[data-play="toggle"]')!,speed=host.querySelector<HTMLSelectElement>('select')!;
  host.querySelector('.minimum-readout')!.textContent=`Predicted closest-approach distance: ${missDistanceM===null?'Unavailable':`${missDistanceM.toLocaleString()} m`}`;
  let time=0,playing=false,frame=0,last=0,holdMs=0,held=false;
  function update(value:number){time=clampTime(value);scene.setTime(time);slider.setAttribute('aria-valuenow',String(Math.round(time*100)));slider.setAttribute('aria-valuetext',`${phaseLabel(time)}, ${Math.round(time*100)} percent of illustrative interval`);thumb.style.left=progress.style.width=`${time*100}%`;const sample=model?relativeMotionSample(model,time):null;readout.textContent=sample?`${phaseLabel(time)} · ${Math.abs(time-.5)<1e-8?'TCA miss distance':'Illustrative center separation'} ${sample.separationM.toLocaleString(undefined,{maximumFractionDigits:1})} m · synthetic local interval`:'Relative-motion data unavailable.';}
  function pause(){playing=false;cancelAnimationFrame(frame);toggle.textContent='Play';}
  function tick(now:number){if(!playing)return;const delta=Math.min(100,now-last);last=now;const step=playbackStep(time,delta,Number(speed.value),holdMs,held);holdMs=step.holdMs;held=step.held;update(step.time);if(time>=1)pause();else frame=requestAnimationFrame(tick);}
  toggle.addEventListener('click',()=>{if(playing){pause();return;}if(!model)return;if(time>=1){update(0);held=false;}holdMs=0;playing=true;last=performance.now();toggle.textContent='Pause';frame=requestAnimationFrame(tick);});
  host.querySelector('[data-play="restart"]')!.addEventListener('click',()=>{pause();holdMs=0;held=false;update(0)});
  host.querySelector('[data-play="tca"]')!.addEventListener('click',()=>{pause();holdMs=0;held=true;update(.5)});
  for(const button of host.querySelectorAll<HTMLButtonElement>('[data-camera]'))button.addEventListener('click',()=>button.dataset.camera==='reset'?scene.reset():scene.zoom(button.dataset.camera==='in'?.8:1.25));
  function seek(event:PointerEvent){if(!model)return;holdMs=0;held=true;const rect=slider.getBoundingClientRect(),sample=sliderSample((event.clientX-rect.left)/rect.width,motion.matches);update(pointerEncounterTime(sample.time));thumb.style.transform=`translateX(calc(-50% + ${sample.visualOffset*rect.width/100}px))`;}
  slider.addEventListener('pointerdown',event=>{pause();slider.focus();slider.setPointerCapture(event.pointerId);seek(event)});
  slider.addEventListener('pointermove',event=>{if(slider.hasPointerCapture(event.pointerId))seek(event)});
  function release(event:PointerEvent){if(slider.hasPointerCapture(event.pointerId))slider.releasePointerCapture(event.pointerId);thumb.style.transform='translateX(-50%)';}
  slider.addEventListener('pointerup',release);slider.addEventListener('pointercancel',release);slider.addEventListener('lostpointercapture',()=>{thumb.style.transform='translateX(-50%)'});
  slider.addEventListener('keydown',event=>{if(!model)return;const actions:Record<string,number>={ArrowLeft:time-.01,ArrowDown:time-.01,ArrowRight:time+.01,ArrowUp:time+.01,PageDown:time-.1,PageUp:time+.1,Home:0,End:1};if(event.key in actions){event.preventDefault();pause();holdMs=0;held=true;update(actions[event.key])}});
  if(!model){for(const button of host.querySelectorAll<HTMLButtonElement>('[data-play]'))button.disabled=true;slider.setAttribute('aria-disabled','true');slider.tabIndex=-1;}
  const onVisibility=()=>{if(document.hidden)pause()};document.addEventListener('visibilitychange',onVisibility);
  update(0);
  return {dispose(){pause();document.removeEventListener('visibilitychange',onVisibility);scene.dispose();host.replaceChildren();}};
}
