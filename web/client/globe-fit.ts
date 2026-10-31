/** Hidden or zero-size viewports must never produce an infinite camera height. */
export function globeFitHeight(width: number, height: number): number | null {
  if (!Number.isFinite(width) || !Number.isFinite(height) || width <= 0 || height <= 0) return null;
  const aspect=width/height;
  const halfAngle=Math.atan(Math.tan(25*Math.PI/180)*Math.min(aspect,1/aspect)*.86);
  const result=6_378_137/Math.sin(halfAngle)-6_378_137;
  return Number.isFinite(result)&&result>0?result:null;
}
