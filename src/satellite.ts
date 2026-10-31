import * as THREE from 'three';

/** Procedural 3D model. Its canvas is active only during the demo preparation. */
export function createSatellite(host: HTMLElement, reducedMotion: MediaQueryList) {
  const canvas = document.createElement('canvas'); canvas.className = 'satellite-canvas'; canvas.setAttribute('aria-hidden', 'true'); host.append(canvas);
  let renderer: THREE.WebGLRenderer;
  try { renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true }); } catch { canvas.remove(); return { start() {}, stop() {}, dispose() {} }; }
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  const scene = new THREE.Scene();
  const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, .1, 2000); camera.position.z = 1000;
  scene.add(new THREE.AmbientLight(0xc9dcf4, 2));
  const light = new THREE.DirectionalLight(0xffffff, 3); light.position.set(-150, 200, 400); scene.add(light);
  const satellite = new THREE.Group(); scene.add(satellite);
  const cream = new THREE.MeshStandardMaterial({ color: 0xe6dec8, roughness: .52, metalness: .22 });
  const red = new THREE.MeshStandardMaterial({ color: 0xc6403b, roughness: .42, metalness: .25 });
  const metal = new THREE.MeshStandardMaterial({ color: 0xaeb8c5, roughness: .32, metalness: .75 });
  const blue = new THREE.MeshStandardMaterial({ color: 0x164a9c, roughness: .3, metalness: .45 });
  const dark = new THREE.MeshStandardMaterial({ color: 0x172d4d, roughness: .4, metalness: .6 });
  const add = (geometry: THREE.BufferGeometry, material: THREE.Material, x=0, y=0, z=0) => { const mesh = new THREE.Mesh(geometry, material); mesh.position.set(x,y,z); satellite.add(mesh); return mesh; };
  add(new THREE.CylinderGeometry(11, 11, 29, 32), cream);
  add(new THREE.CylinderGeometry(11.5, 11.5, 2, 32), metal, 0, -14);
  add(new THREE.CylinderGeometry(3, 4, 9, 16), metal, 0, 19);
  const dish = new THREE.LatheGeometry([new THREE.Vector2(0,0),new THREE.Vector2(4,1),new THREE.Vector2(9,4),new THREE.Vector2(15,10)], 40);
  const dishMaterial = cream.clone(); dishMaterial.side = THREE.DoubleSide;
  add(dish, dishMaterial, 0, 22);
  const rim = add(new THREE.TorusGeometry(15, 1.5, 10, 48), red, 0, 32); rim.rotation.x = Math.PI/2;
  add(new THREE.CylinderGeometry(.9, .9, 22, 8), metal, 0, 35);
  add(new THREE.SphereGeometry(2.4, 12, 12), red, 0, 47);
  for (const sign of [-1,1]) {
    add(new THREE.BoxGeometry(22, 3, 3), metal, sign*21, 0);
    add(new THREE.BoxGeometry(54, 29, 3), metal, sign*57, 0);
    add(new THREE.BoxGeometry(51, 26, 3.4), dark, sign*57, 0);
    for (let col=0; col<6; col++) for (let row=0; row<3; row++) add(new THREE.BoxGeometry(7.7, 7.6, .5), blue, sign*57-21+col*8.4, -8.5+row*8.5, 2);
  }
  satellite.rotation.set(.4, -.35, -.28);
  // Bound every part around the orbit origin. Scale to the margin outside the
  // Earth, rather than moving the requested circumference orbit into the disc.
  let modelRadius = 0;
  satellite.traverse(item => {
    if (item instanceof THREE.Mesh) {
      item.geometry.computeBoundingSphere();
      modelRadius = Math.max(modelRadius, item.position.length() + item.geometry.boundingSphere!.radius);
    }
  });
  let frame = 0;
  let began = 0;
  const draw = (time: number) => {
    const width = host.clientWidth, height = host.clientHeight;
    renderer.setSize(width, height, false); camera.left=-width/2; camera.right=width/2; camera.top=height/2; camera.bottom=-height/2; camera.updateProjectionMatrix();
    const angle = reducedMotion.matches ? -Math.PI/4 : (time-began)/1000*Math.PI*2-Math.PI/4;
    const diameter = Math.min(width,height);
    const radius = diameter * .43;
    const margin = Math.max(1, diameter * .07 - 6);
    satellite.scale.setScalar(Math.min(.82, margin / modelRadius));
    satellite.position.set(Math.cos(angle)*radius, Math.sin(angle)*radius, 0);
    if (!reducedMotion.matches) satellite.rotation.y = -.35 + (time-began)/1000*.6;
    renderer.render(scene,camera);
  };
  const tick = (time: number) => { draw(time); frame=requestAnimationFrame(tick); };
  // Compile the real geometry before selection, rather than spending the loader on setup.
  draw(0); canvas.hidden = true;
  return {
    start() { cancelAnimationFrame(frame); canvas.hidden=false; began=performance.now(); if (reducedMotion.matches) draw(began); else frame=requestAnimationFrame(tick); },
    stop() { cancelAnimationFrame(frame); canvas.hidden=true; },
    dispose() { cancelAnimationFrame(frame); scene.traverse(item => { if (item instanceof THREE.Mesh) item.geometry.dispose(); }); for (const material of [cream, red, metal, blue, dark, dishMaterial]) material.dispose(); renderer.dispose(); canvas.remove(); }
  };
}
