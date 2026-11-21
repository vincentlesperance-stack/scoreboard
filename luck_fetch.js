// Run in the built-in browser on any https://hockey.fantasysports.yahoo.com/hockey/60964/... page.
// Set WEEKS to the completed week numbers to fetch. Returns JSON entries in raw.json format.
const WEEKS=[/*e.g. 8*/];
const data=[];
for(const w of WEEKS){
  const seen=new Set();
  for(let t=1;t<=10;t++){
    if(seen.has(t)) continue;
    const html=await fetch(`/hockey/60964/matchup?week=${w}&mid1=${t}`).then(r=>r.text());
    const d=new DOMParser().parseFromString(html,'text/html');
    const tb=[...d.querySelectorAll('table')].find(x=>/SV%/.test(x.textContent)&&/Team/.test(x.textContent));
    if(!tb) throw new Error(`no matchup table for week ${w} team ${t} (signed out?)`);
    const hrefs=[...d.querySelectorAll('a')].filter(a=>a.textContent.trim()&&/hockey\/60964\/\d+$/.test(a.getAttribute('href')||'')&&a.textContent.trim()!=='My Team').map(a=>+a.getAttribute('href').match(/(\d+)$/)[1]);
    [...new Set(hrefs)].slice(0,2).forEach(p=>seen.add(p));
    const rows=[...tb.querySelectorAll('tr')].slice(1).map(r=>[...r.children].map(c=>c.textContent.trim()));
    data.push({w,rows});
  }
}
JSON.stringify(data)
