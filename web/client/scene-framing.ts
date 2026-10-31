/** Fit a bounding sphere to both viewport axes without altering source units. */
export function sphereFraming(radius:number,aspect:number,verticalFovDegrees=42) {
 const r=Math.max(Number.isFinite(radius)?radius:1,.01);
 const a=Math.max(Number.isFinite(aspect)?aspect:1,.01);
 const half=verticalFovDegrees*Math.PI/360;
 const limiting=Math.min(half,Math.atan(Math.tan(half)*a));
 const distance=r/Math.sin(limiting)*1.2;
 const minDistance=Math.max(r*.25,.01),maxDistance=distance*5;
 return {distance,minDistance,maxDistance,near:Math.max(r*.001,.0001),far:maxDistance+r*4};
}

/** Reference visibility never depends on optional event geometry. */
export function sceneVisibility(hasRelativeSample:boolean){return {primary:true,debris:hasRelativeSample,vectors:hasRelativeSample};}
