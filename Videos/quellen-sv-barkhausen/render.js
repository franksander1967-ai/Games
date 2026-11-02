const {chromium}=require('playwright');const path=require('path');const {spawn}=require('child_process');
(async()=>{const fps=+process.argv[2]||30;const out=process.argv[3]||'video_noaudio.mp4';const T0=+(process.argv[4]||0),T1=+(process.argv[5]||30);
const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
p.on('pageerror',e=>console.log('ERR',e.message));
await p.goto('file://'+path.resolve('video.html'));await p.waitForFunction(()=>window.READY,null,{timeout:30000});
const ff=spawn('ffmpeg',['-y','-loglevel','error','-f','image2pipe','-framerate',String(fps),'-c:v','mjpeg','-i','-','-c:v','libx264','-preset','medium','-crf','16','-pix_fmt','yuv420p','-r',String(fps),out]);
ff.stderr.on('data',d=>process.stderr.write(d));
const n=Math.round((T1-T0)*fps);const st=Date.now();
for(let i=0;i<n;i++){const t=T0+i/fps;await p.evaluate(t=>render(t),t);
 const buf=await p.screenshot({type:'jpeg',quality:95});if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));
 if(i%150===0)console.log('frame',i,'/',n,((Date.now()-st)/1000).toFixed(1)+'s');}
ff.stdin.end();await new Promise(r=>ff.on('close',r));await b.close();console.log('done',((Date.now()-st)/1000).toFixed(1)+'s');})();
