import { Viewer, Cartesian3, Color, CallbackPositionProperty, Cartesian2 } from 'cesium';

/** Presentation-only geocentric loops, never sourced from encounters or telemetry. */
export function createDecorativeOrbit(viewer:Viewer, reduced:MediaQueryList){
 const entities:ReturnType<typeof viewer.entities.add>[]=[];let elapsed=0,last=performance.now(),frame=0,active=false,paused=false;
 const canvas=document.createElement('canvas');canvas.width=120;canvas.height=80;const ctx=canvas.getContext('2d')!;
 ctx.fillStyle='#2c6599';ctx.fillRect(5,22,40,32);ctx.fillRect(75,22,40,32);ctx.strokeStyle='#bbd3e8';ctx.lineWidth=2;for(let x=5;x<116;x+=10){ctx.beginPath();ctx.moveTo(x,22);ctx.lineTo(x,54);ctx.stroke();}ctx.fillStyle='#d4dbe2';ctx.fillRect(48,17,24,43);ctx.fillStyle='#cfad66';ctx.fillRect(51,28,18,22);ctx.beginPath();ctx.ellipse(60,13,14,6,0,0,Math.PI*2);ctx.fillStyle='#e5ecf4';ctx.fill();
 function point(angle:number,inclination:number,radius:number){return new Cartesian3(radius*Math.cos(angle),radius*Math.sin(angle)*Math.cos(inclination),radius*Math.sin(angle)*Math.sin(inclination));}
 for(let i=0;i<3;i++){const inclination=[.65,-.9,1.1][i],radius=8_000_000+i*650_000;
  entities.push(viewer.entities.add({polyline:{positions:Array.from({length:129},(_,n)=>point(n/128*Math.PI*2,inclination,radius)),width:1,material:Color.fromCssColorString(i===0?'#638fb8':'#56677c').withAlpha(.42)}}));
  const position=new CallbackPositionProperty(()=>point(elapsed*(i===0?.19:.14+i*.018)+i*2,inclination,radius),false);
  entities.push(viewer.entities.add({position,...(i===0?{billboard:{image:canvas,width:60,height:40,scale:.8,pixelOffset:new Cartesian2(0,0)}}:{point:{pixelSize:6,color:Color.fromCssColorString('#c5bfae'),outlineColor:Color.fromCssColorString('#536273'),outlineWidth:1}})}));
 }
 function tick(now:number){if(!active)return;const delta=Math.min(100,now-last);last=now;if(!reduced.matches&&!paused)elapsed+=delta/1000;viewer.scene.requestRender();if(!reduced.matches&&!paused)frame=requestAnimationFrame(tick);}
 function setActive(value:boolean){active=value;cancelAnimationFrame(frame);for(const entity of entities)entity.show=value;if(value){last=performance.now();tick(last);}viewer.scene.requestRender();}
 const onMotion=()=>setActive(active);reduced.addEventListener('change',onMotion);
 return {setActive,setPaused(value:boolean){paused=value;setActive(active);},dispose(){active=false;cancelAnimationFrame(frame);reduced.removeEventListener('change',onMotion);for(const entity of entities)viewer.entities.remove(entity);}};
}
