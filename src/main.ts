import { Viewer, ArcGisMapServerImageryProvider, EllipsoidTerrainProvider, Cartesian3, Math as CesiumMath, Color, SceneMode, ScreenSpaceEventType, PerspectiveFrustum, DirectionalLight } from 'cesium';
import 'cesium/Build/Cesium/Widgets/widgets.css';
import './style.css';
import {createDecorativeOrbit} from './decorative-orbit';
import { setupWorkspace } from './workspace';
import { globeFitHeight } from '../web/client/globe-fit.ts';

(window as unknown as { CESIUM_BASE_URL: string }).CESIUM_BASE_URL = '/cesium/';
const icon = (path: string) => `<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">${path}</svg>`;
document.querySelector<HTMLDivElement>('#app')!.innerHTML = `
<main aria-label="Interactive Earth explorer">
  <section class="earth-stage" aria-label="Earth view">
  <div id="globe" tabindex="0" role="region" aria-label="Interactive globe. Drag to rotate, scroll to zoom. Arrow keys rotate; plus and minus zoom. Press H for help." aria-describedby="globe-instructions"></div>
  <header class="identity"><span class="earth-mark" aria-hidden="true"></span><h1>Earth</h1><span class="identity-divider" aria-hidden="true"></span><span class="identity-description">Satellite explorer</span></header>
  <p id="globe-instructions" class="sr-only">Drag to explore. Scroll or pinch to zoom. Focus this globe to use arrow keys and plus or minus. Use the controls to reset the view or open help.</p>
  <div class="toolbar" role="group" aria-label="Globe controls">
    <button id="north" aria-label="Point north up" title="Point north up">${icon('<path d="m12 3 6 17-6-4-6 4Z"/><path d="M12 3v13"/>')}</button>
    <div class="zoom-group"><button id="zoom-in" aria-label="Zoom in" title="Zoom in (+)">${icon('<path d="M12 5v14M5 12h14"/>')}</button><button id="zoom-out" aria-label="Zoom out" title="Zoom out (−)">${icon('<path d="M5 12h14"/>')}</button></div>
    <button id="reset" aria-label="Reset to full Earth view" title="Reset view">${icon('<circle cx="12" cy="12" r="8"/><path d="M4 12h16M12 4a15 15 0 0 1 0 16 15 15 0 0 1 0-16Z"/>')}</button>
    <button id="help-toggle" aria-label="Show navigation help" aria-expanded="false" aria-controls="help" title="Navigation help (H)">${icon('<circle cx="12" cy="12" r="8"/><path d="M9.7 9a2.4 2.4 0 0 1 4.6 1c0 1.5-2.3 1.7-2.3 3M12 16h.01"/>')}</button>
  </div>
  <section id="help" class="help-panel" aria-labelledby="help-title" hidden><div class="help-heading"><h2 id="help-title">Explore Earth</h2><button id="help-close" aria-label="Close navigation help">${icon('<path d="m6 6 12 12M6 18 18 6"/>')}</button></div><dl><div><dt>Rotate</dt><dd>Drag or arrow keys</dd></div><div><dt>Zoom</dt><dd>Scroll, pinch or + / −</dd></div><div><dt>Reset view</dt><dd>Home</dd></div></dl><p>For keyboard navigation, focus the globe first. Satellite detail varies by location.</p></section>
  <div id="status" class="status" role="status"><span class="loading-dot" aria-hidden="true"></span>Loading satellite imagery…</div>
  <section id="error" class="error-panel" role="alert" hidden><h2 id="error-title">Earth couldn’t load</h2><p id="error-message"></p><button id="retry">Try again</button></section>
  <span class="orbital-label">Illustrative orbital animation</span><button id="orbit-motion" class="orbit-motion">Pause illustrative orbits</button><footer><span class="gesture-hint">Drag to explore <span aria-hidden="true">·</span> Scroll to zoom</span><output id="altitude" aria-label="Camera altitude"></output></footer>
</section></main>`;
const globe = document.querySelector<HTMLDivElement>('#globe')!;
const status = document.querySelector<HTMLDivElement>('#status')!;
const error = document.querySelector<HTMLElement>('#error')!;
let viewer: Viewer | undefined;
let decoration:ReturnType<typeof createDecorativeOrbit>|undefined;
let orbitsPaused=false;
function syncDecoration(){const button=document.querySelector<HTMLButtonElement>('#orbit-motion')!;const reduced=window.matchMedia('(prefers-reduced-motion: reduce)').matches;button.disabled=reduced;button.textContent=reduced?'Illustrative orbits · reduced motion':orbitsPaused?'Resume illustrative orbits':'Pause illustrative orbits';button.setAttribute('aria-pressed',String(orbitsPaused));decoration?.setPaused(orbitsPaused);decoration?.setActive(document.querySelector('main')!.classList.contains('dashboard')&&!document.querySelector('main')!.classList.contains('encounter-route')&&!document.hidden);}
document.querySelector('#orbit-motion')!.addEventListener('click',()=>{orbitsPaused=!orbitsPaused;syncDecoration();});
const orbitMotionPreference=window.matchMedia('(prefers-reduced-motion: reduce)');orbitMotionPreference.addEventListener('change',syncDecoration);
const routeObserver=new MutationObserver(syncDecoration);routeObserver.observe(document.querySelector('main')!,{attributes:true,attributeFilter:['class']});document.addEventListener('visibilitychange',syncDecoration);window.addEventListener('pagehide',event=>{if(!event.persisted){decoration?.dispose();routeObserver.disconnect();document.removeEventListener('visibilitychange',syncDecoration);orbitMotionPreference.removeEventListener('change',syncDecoration);}});
let loadingTimer: ReturnType<typeof setTimeout>;
let successfulTiles = false;
let initialization = 0;
let overviewHeight = 21_500_000;
function fittedHeight() {
  return globeFitHeight(globe.clientWidth, globe.clientHeight) ?? overviewHeight;
}
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
function showError(message: string) { status.hidden = true; error.hidden = false; document.querySelector('#error-message')!.textContent = message; }
function reset() { overviewHeight = fittedHeight(); viewer?.camera.flyTo({ destination: Cartesian3.fromDegrees(-45.47, 26.15, overviewHeight), orientation: { heading: 0, pitch: -CesiumMath.PI_OVER_TWO, roll: 0 }, duration: reducedMotion.matches ? 0 : 1.1 }); }
function zoom(inward: boolean) { if (!viewer) return; const height = viewer.camera.positionCartographic.height; const target = Math.min(Math.max(40_000_000, fittedHeight()), Math.max(1000, height * (inward ? .64 : 1.36))); inward ? viewer.camera.zoomIn(Math.max(0, height - target)) : viewer.camera.zoomOut(Math.max(0, target - height)); viewer.scene.requestRender(); }
async function initialize() {
  const generation = ++initialization;
  decoration?.dispose();decoration=undefined;
  if (viewer && !viewer.isDestroyed()) viewer.destroy();
  viewer = undefined;
  clearTimeout(loadingTimer); error.hidden = true; status.hidden = false; status.textContent = 'Loading satellite imagery…'; successfulTiles = false;
  loadingTimer = setTimeout(() => { if (!successfulTiles) showError('Satellite imagery is taking too long to arrive. Check your connection and try again.'); }, 25_000);
  try {
    viewer = new Viewer(globe, { baseLayer: false, terrainProvider: new EllipsoidTerrainProvider(), animation: false, timeline: false, baseLayerPicker: false, geocoder: false, homeButton: false, sceneModePicker: false, navigationHelpButton: false, fullscreenButton: false, infoBox: false, selectionIndicator: false, skyBox: false, skyAtmosphere: undefined, sceneMode: SceneMode.SCENE3D, requestRenderMode: true, maximumRenderTimeChange: Infinity, contextOptions: { webgl: { alpha: false, antialias: true, powerPreference: 'high-performance' } } });
    const current = viewer;decoration=createDecorativeOrbit(current,reducedMotion);syncDecoration();
    const provider = await ArcGisMapServerImageryProvider.fromUrl('https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer', { maximumLevel: 19 });
    if (generation !== initialization) return;
    const requestImage = provider.requestImage.bind(provider);
    let pendingImages = 0;
    const failedImages = new Set<string>();
    let progressTimer: ReturnType<typeof setTimeout>;
    const updateProgress = () => {
      if (current !== viewer) return;
      if (!navigator.onLine) { status.hidden = false; status.textContent = 'You’re offline. Reconnect to load more imagery.'; return; }
      if (failedImages.size > 0 && pendingImages === 0 && successfulTiles) {
        status.hidden = false; status.textContent = 'Some imagery could not load. ';
        const retry = document.createElement('button'); retry.className = 'inline-retry'; retry.textContent = 'Retry';
        retry.addEventListener('click', () => { failedImages.clear(); const position = current.camera.position.clone(); const orientation = { heading: current.camera.heading, pitch: current.camera.pitch, roll: current.camera.roll }; void initialize().then(() => { viewer?.camera.setView({ destination: position, orientation }); viewer?.scene.requestRender(); }); });
        status.append(retry);
      } else if (pendingImages > 0 && successfulTiles) { status.hidden = false; status.textContent = 'Refining satellite imagery…'; }
      else if (successfulTiles) status.hidden = true;
    };
    provider.requestImage = (x, y, level, request) => {
      const tileKey = `${level}/${x}/${y}`;
      const result = requestImage(x, y, level, request);
      if (result) {
        pendingImages++;
        clearTimeout(progressTimer); progressTimer = setTimeout(updateProgress, 650);
        void Promise.resolve(result).then(image => {
          pendingImages--;
          if (image && current === viewer) { failedImages.delete(tileKey); successfulTiles = true; clearTimeout(loadingTimer); error.hidden = true; updateProgress(); }
        }, () => { pendingImages--; failedImages.add(tileKey); clearTimeout(progressTimer); progressTimer = setTimeout(updateProgress, 1800); });
      }
      return result;
    };
    current.imageryLayers.addImageryProvider(provider);
    current.scene.backgroundColor = Color.fromCssColorString('#070b10');
    current.scene.globe.baseColor = Color.fromCssColorString('#142532');
    // Presentation light, relative to the camera: imagery remains readable while
    // the lower-right limb recedes. This is deliberately not live solar time.
    current.scene.globe.enableLighting = true;
    current.scene.globe.dynamicAtmosphereLighting = false;
    current.scene.globe.lightingFadeOutDistance = 6_500_000;
    current.scene.globe.lightingFadeInDistance = 60_000_000;
    const presentationLight = new DirectionalLight({ direction: new Cartesian3(1, 0, 0) });
    current.scene.light = presentationLight;
    const lightRight = new Cartesian3();
    const lightUp = new Cartesian3();
    current.scene.preRender.addEventListener(() => {
      Cartesian3.multiplyByScalar(current.camera.directionWC, .7, presentationLight.direction);
      Cartesian3.multiplyByScalar(current.camera.rightWC, .65, lightRight);
      Cartesian3.multiplyByScalar(current.camera.upWC, -.5, lightUp);
      Cartesian3.add(presentationLight.direction, lightRight, presentationLight.direction);
      Cartesian3.add(presentationLight.direction, lightUp, presentationLight.direction);
      Cartesian3.normalize(presentationLight.direction, presentationLight.direction);
    });
    current.scene.globe.showGroundAtmosphere = true;
    current.scene.globe.maximumScreenSpaceError = 1.2;
    current.scene.screenSpaceCameraController.minimumZoomDistance = 1000;
    current.scene.screenSpaceCameraController.maximumZoomDistance = Math.max(40_000_000, fittedHeight());
    current.scene.screenSpaceCameraController.enableTilt = false;
    current.scene.screenSpaceCameraController.enableLook = false;
    current.cesiumWidget.screenSpaceEventHandler.removeInputAction(ScreenSpaceEventType.LEFT_DOUBLE_CLICK);
    current.resolutionScale = Math.min(window.devicePixelRatio || 1, 2);
    if (current.camera.frustum instanceof PerspectiveFrustum) current.camera.frustum.fov = CesiumMath.toRadians(50);
    overviewHeight = fittedHeight();
    current.camera.setView({ destination: Cartesian3.fromDegrees(-45.47, 26.15, overviewHeight) });

    current.scene.renderError.addEventListener(() => showError('The graphics renderer stopped. Try again, or use a browser with hardware acceleration enabled.'));
    current.camera.changed.addEventListener(() => { const km = current.camera.positionCartographic.height / 1000; document.querySelector('#altitude')!.textContent = `Altitude ${km >= 10 ? Math.round(km).toLocaleString() : km.toFixed(1)} km`; });
    current.camera.percentageChanged = .02;
    current.scene.requestRender();
  } catch { if (generation !== initialization) return; clearTimeout(loadingTimer); showError(viewer ? 'The satellite imagery service could not be reached. Check your connection and try again.' : 'This globe needs WebGL. Enable hardware acceleration in your browser, then try again.'); }
}
const help = document.querySelector<HTMLElement>('#help')!;
const helpToggle = document.querySelector<HTMLButtonElement>('#help-toggle')!;
function toggleHelp(open = help.hidden) { help.hidden = !open; helpToggle.setAttribute('aria-expanded', String(open)); }
helpToggle.addEventListener('click', () => toggleHelp());
document.querySelector('#help-close')!.addEventListener('click', () => { toggleHelp(false); helpToggle.focus(); });
document.querySelector('#zoom-in')!.addEventListener('click', () => zoom(true));
document.querySelector('#zoom-out')!.addEventListener('click', () => zoom(false));
document.querySelector('#reset')!.addEventListener('click', reset);
document.querySelector('#north')!.addEventListener('click', () => { if (viewer) { viewer.camera.setView({ orientation: { heading: 0, pitch: -CesiumMath.PI_OVER_TWO, roll: 0 } }); viewer.scene.requestRender(); } });
document.querySelector('#retry')!.addEventListener('click', initialize);
globe.addEventListener('pointerdown', () => globe.focus({ preventScroll: true }));
globe.addEventListener('keydown', (event) => {
  if (!viewer) return;
  const step = Math.min(.12, Math.max(.00002, viewer.camera.positionCartographic.height / 150_000_000));
  const actions: Record<string, () => void> = { ArrowLeft: () => viewer!.camera.rotateRight(step), ArrowRight: () => viewer!.camera.rotateLeft(step), ArrowUp: () => viewer!.camera.rotateDown(step), ArrowDown: () => viewer!.camera.rotateUp(step), '+': () => zoom(true), '=': () => zoom(true), '-': () => zoom(false), Home: reset, h: () => toggleHelp(), H: () => toggleHelp(), Escape: () => toggleHelp(false) };
  if (actions[event.key]) { event.preventDefault(); actions[event.key](); viewer.scene.requestRender(); }
});
document.addEventListener('keydown', event => { if (event.key === 'Escape' && !help.hidden) { toggleHelp(false); helpToggle.focus(); } });
window.addEventListener('offline', () => { status.hidden = false; status.textContent = 'You’re offline. Reconnect to load more imagery.'; });
window.addEventListener('online', () => { status.hidden = true; viewer?.scene.requestRender(); });
initialize();

window.addEventListener('resize', () => { if (!viewer || globeFitHeight(globe.clientWidth,globe.clientHeight) === null) return; const wasOverview = Math.abs(viewer.camera.positionCartographic.height - overviewHeight) < overviewHeight * .03; viewer.resize(); viewer.scene.screenSpaceCameraController.maximumZoomDistance = Math.max(40_000_000, fittedHeight()); if (wasOverview) { const position = viewer.camera.positionCartographic; overviewHeight = fittedHeight(); viewer.camera.setView({ destination: Cartesian3.fromRadians(position.longitude, position.latitude, overviewHeight) }); } viewer.scene.requestRender(); });

setupWorkspace(() => {
  if (!viewer || globeFitHeight(globe.clientWidth,globe.clientHeight) === null) return;
  viewer.resize();
  overviewHeight=fittedHeight();
  viewer.scene.screenSpaceCameraController.maximumZoomDistance=Math.max(40_000_000,overviewHeight);
  const position=viewer.camera.positionCartographic;
  viewer.camera.cancelFlight();
  viewer.camera.setView({destination:Cartesian3.fromRadians(position.longitude,position.latitude,overviewHeight)});
  viewer.scene.requestRender();
}, () => toggleHelp(false));
