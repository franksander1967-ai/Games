var OBJ=(()=>{
// Vector objects in the style of the club crest: flat fills, heavy black outline.
const K='#0C0D0A', P='#F1EEE4', G='#22A23C', B='#C65B3C', G2='#1B8030', P2='#CFCABC';
function STK(id,col,r){return `<defs><filter id="${id}" x="-30%" y="-30%" width="160%" height="160%"><feMorphology in="SourceAlpha" operator="dilate" radius="${r}" result="d"/><feFlood flood-color="${col}"/><feComposite in2="d" operator="in" result="o"/><feMerge><feMergeNode in="o"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>`;}
const OBJ0={
rifle(st='#F1EEE4'){ // match air rifle, muzzle left. viewBox 0 0 900 230
 return `<svg viewBox="-20 -10 940 250" width="100%" height="100%" style="overflow:visible">${STK('stR',st,7)}
 <g filter="url(#stR)"><g stroke="${K}" stroke-width="7" stroke-linejoin="round" stroke-linecap="round">
  <rect x="40" y="62" width="470" height="18" rx="4" fill="${P2}"/>
  <rect x="130" y="84" width="330" height="30" rx="14" fill="${P2}"/>
  <rect x="10" y="44" width="76" height="54" rx="8" fill="${P}"/>
  <rect x="460" y="50" width="210" height="58" rx="8" fill="${P}"/>
  <path d="M556 50 L556 16 L626 16 L626 50 Z" fill="${P}"/>
  <path d="M420 108 L668 108 L706 96 L862 84 L884 84 L884 200 L864 208 L806 180 L764 172 L748 172 L736 220 L690 224 L684 172 Q676 150 640 144 L430 140 Z" fill="${B}"/>
  <path d="M742 96 L742 66 L860 60 L860 84" fill="${B}"/>
  <rect x="876" y="78" width="26" height="134" rx="6" fill="${K}"/>
  <path d="M700 172 Q712 196 724 172" fill="none"/>
 </g>
 <circle cx="591" cy="33" r="10" fill="${K}"/>
 <path d="M52 68 L500 68" stroke="${P}" stroke-width="4" opacity=".9"/>
 <path d="M680 118 C760 108 820 100 870 96" stroke="#E07D5E" stroke-width="6" fill="none" stroke-linecap="round"/>
 <path d="M140 92 L450 92" stroke="#fff" stroke-width="4" opacity=".7"/>
 </g></svg>`;},
hat(st='#F1EEE4'){ // Schützenhut. viewBox 0 0 400 270
 return `<svg viewBox="-20 -20 440 310" width="100%" height="100%" style="overflow:visible">${STK('stH'+st.slice(1),st,6)}<g filter="url(#stH${st.slice(1)})">
 <g stroke="${K}" stroke-width="8" stroke-linejoin="round">
  <ellipse cx="200" cy="214" rx="192" ry="44" fill="${G2}"/>
  <path d="M86 206 C80 140 96 66 140 44 C170 28 230 28 260 44 C304 66 320 140 314 206 C260 226 140 226 86 206 Z" fill="${G}"/>
  <path d="M174 34 C190 60 210 60 226 34" fill="none"/>
  <path d="M88 168 C150 186 250 186 312 168 L314 206 C250 226 150 226 86 206 Z" fill="${K}"/>
  <path d="M286 176 C300 120 330 70 372 28 C352 86 330 140 304 182 Z" fill="${P}"/>
  <circle cx="276" cy="186" r="20" fill="${B}"/>
 </g>
 <path d="M300 166 C318 120 340 84 362 50" stroke="${K}" stroke-width="4" fill="none"/>
 <path d="M112 150 C110 110 122 76 146 60" stroke="#5BC46F" stroke-width="7" fill="none" stroke-linecap="round"/>
 </g></svg>`;},
chain(st='#F1EEE4'){ // Königskette. viewBox 0 0 500 620, medallion centre (250,470) r 92
 let links='';
 const strand=(sx,ex,cx)=>{ const N=11; for(let i=0;i<N;i++){ const u=i/(N-1);
   const x=(1-u)*(1-u)*sx+2*(1-u)*u*cx+u*u*ex, y=(1-u)*(1-u)*0+2*(1-u)*u*300+u*u*362;
   const dx=2*(1-u)*(cx-sx)+2*u*(ex-cx), dy=2*(1-u)*300+2*u*(362-300);
   const a=Math.atan2(dy,dx)*180/Math.PI;
   if(i===3||i===7) links+=`<g transform="translate(${x.toFixed(1)} ${y.toFixed(1)})"><path d="M-24 -20 L24 -20 L24 4 Q0 32 -24 4 Z" fill="${P}" stroke="${K}" stroke-width="6" stroke-linejoin="round"/><circle cx="0" cy="-4" r="7" fill="${G}" stroke="${K}" stroke-width="4"/></g>`;
   else links+=`<g transform="translate(${x.toFixed(1)} ${y.toFixed(1)}) rotate(${(a+(i%2?90:0)).toFixed(1)})"><ellipse rx="18" ry="10" fill="none" stroke="${K}" stroke-width="12"/><ellipse rx="18" ry="10" fill="none" stroke="${P2}" stroke-width="5"/></g>`; } };
 strand(40,236,60); strand(460,264,440);
 return `<svg viewBox="-30 -30 560 690" width="100%" height="100%" style="overflow:visible">${STK('stC',st,6)}<g filter="url(#stC)">
 ${links}
 <g stroke="${K}" stroke-width="8">
  <circle cx="250" cy="470" r="92" fill="${P}"/>
  <circle cx="250" cy="470" r="70" fill="${G}"/>
  <circle cx="250" cy="470" r="46" fill="${P}"/>
  <circle cx="250" cy="470" r="24" fill="${K}"/>
  <path d="M206 372 L250 352 L294 372 L276 390 L224 390 Z" fill="${B}" stroke-linejoin="round"/>
 </g></g></svg>`;},
cup(st='#F1EEE4'){ // Pokal. viewBox 0 0 360 470
 return `<svg viewBox="-20 -20 400 510" width="100%" height="100%" style="overflow:visible">${STK('stP',st,6)}<g filter="url(#stP)">
 <g stroke="${K}" stroke-width="8" stroke-linejoin="round">
  <path d="M70 70 C10 70 10 170 96 190" fill="none" stroke-width="22"/><path d="M70 70 C10 70 10 170 96 190" fill="none" stroke="${P2}" stroke-width="8"/>
  <path d="M290 70 C350 70 350 170 264 190" fill="none" stroke-width="22"/><path d="M290 70 C350 70 350 170 264 190" fill="none" stroke="${P2}" stroke-width="8"/>
  <path d="M60 30 L300 30 C300 150 260 230 180 244 C100 230 60 150 60 30 Z" fill="${P}"/>
  <path d="M66 92 L294 92 C290 120 284 140 276 156 L84 156 C76 140 70 120 66 92 Z" fill="${G}"/>
  <rect x="150" y="244" width="60" height="70" fill="${P2}"/>
  <path d="M120 314 L240 314 L262 352 L98 352 Z" fill="${B}"/>
  <rect x="70" y="352" width="220" height="70" rx="8" fill="${K}"/>
  <ellipse cx="180" cy="30" rx="120" ry="16" fill="${P2}"/>
 </g>
 <text x="180" y="140" text-anchor="middle" font-family="Archivo" font-weight="900" font-stretch="62%" font-size="54" fill="${P}">10</text>
 <path d="M96 52 C100 120 120 180 160 214" stroke="#fff" stroke-width="10" fill="none" stroke-linecap="round" opacity=".8"/>
 <rect x="96" y="378" width="168" height="18" rx="3" fill="${B}" opacity=".9"/>
 </g></svg>`;}
};

return OBJ0;})();
