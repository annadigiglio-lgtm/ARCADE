'use strict';
const $ = id => document.getElementById(id);
const number = new Intl.NumberFormat('it-IT');
const date = value => new Date(value).toLocaleString('it-IT', {timeZone:'Europe/Rome'});
let session = null;
let timer = null;
let pending = null;
function message(text='') { $('message').textContent=text; }
async function api(path, options={}, signal) {
  const response=await fetch(path, { ...options, signal, headers:{'Content-Type':'application/json', ...(session ? {Authorization:`Bearer ${session.accessToken}`} : {})}, cache:'no-store' });
  const body=await response.json().catch(()=>({message:'Risposta del server non valida'}));
  if (!response.ok) {
    if(response.status===401 && session) logout();
    throw new Error(body.message || 'Impossibile recuperare i dati');
  }
  return body;
}
function card(label,value,code) {
  const el=document.createElement('article'); el.className='card';
  if(code) { const tag=document.createElement('span'); tag.className='code'; tag.textContent=code; el.append(tag); }
  const title=document.createElement('h3'); title.textContent=label;
  const amount=document.createElement('strong'); amount.textContent=value==null ? '—' : number.format(value);
  el.append(title,amount); return el;
}
function drawTrend(rows) {
  const container=$('trend'); container.replaceChildren();
  if(!rows.length) { container.textContent='Nessun dato di andamento disponibile.'; return; }
  const ns='http://www.w3.org/2000/svg';
  const svg=document.createElementNS(ns,'svg');
  svg.setAttribute('viewBox','0 0 800 280'); svg.setAttribute('role','img');
  svg.setAttribute('aria-label','Andamento delle presenze stimate per padiglione');
  const start=Math.min(...rows.map(r=>Date.parse(r.istante)));
  const end=Math.max(...rows.map(r=>Date.parse(r.istante)));
  const max=Math.max(1,...rows.map(r=>r.presenti));
  const x=value=>65+(Date.parse(value)-start)/Math.max(1,end-start)*710;
  const y=value=>225-value/max*200;
  const element=(name,attrs,text)=>{const el=document.createElementNS(ns,name);for(const [key,value] of Object.entries(attrs)) el.setAttribute(key,value);if(text!=null) el.textContent=text;svg.append(el);return el;};
  for(const fraction of [0,.5,1]) {
    element('line',{x1:65,x2:775,y1:y(max*fraction),y2:y(max*fraction),stroke:'#363c38'});
    element('text',{x:55,y:y(max*fraction)+5,'text-anchor':'end',fill:'#b0b8ae','font-size':12},number.format(Math.round(max*fraction)));
  }
  const legend=document.createElement('div');legend.className='chart-legend';
  const colors=['#d2ff5a','#86cfff','#ffb38a'];
  [...new Set(rows.map(r=>r.padiglione))].sort().forEach((pavilion,index)=>{
    const points=rows.filter(r=>r.padiglione===pavilion).sort((a,b)=>Date.parse(a.istante)-Date.parse(b.istante));
    const color=colors[index%colors.length];
    element('polyline',{points:points.map(r=>`${x(r.istante)},${y(r.presenti)}`).join(' '),fill:'none',stroke:color,'stroke-width':3,'stroke-linejoin':'round'});
    if(points.length===1) element('circle',{cx:x(points[0].istante),cy:y(points[0].presenti),r:4,fill:color});
    const label=document.createElement('span');label.style.color=color;label.textContent=pavilion;legend.append(label);
  });
  const time=value=>new Date(value).toLocaleTimeString('it-IT',{hour:'2-digit',minute:'2-digit',timeZone:'Europe/Rome'});
  element('text',{x:65,y:255,fill:'#b0b8ae','font-size':12},time(start));
  element('text',{x:775,y:255,fill:'#b0b8ae','font-size':12,'text-anchor':'end'},time(end));
  container.append(legend,svg);
  const details=document.createElement('details'); const summary=document.createElement('summary');summary.textContent='Leggi i dati del grafico';details.append(summary);
  const table=document.createElement('table');const head=document.createElement('thead');const tr=document.createElement('tr');
  for(const title of ['Ora','Padiglione','Presenze']) { const th=document.createElement('th');th.scope='col';th.textContent=title;tr.append(th); }head.append(tr);table.append(head);
  const body=document.createElement('tbody');
  rows.forEach(row=>{const tr=document.createElement('tr');[time(row.istante),row.padiglione,number.format(row.presenti)].forEach(value=>{const td=document.createElement('td');td.textContent=value;tr.append(td);});body.append(tr);});
  table.append(body);details.append(table);container.append(details);
}
function logout() {
  session=null; clearTimeout(timer); pending?.abort();
  $('workspace').hidden=true; $('login-panel').hidden=false; $('logout').hidden=true;
  $('identity').textContent='Area riservata'; $('pavilions').replaceChildren(); $('summary').replaceChildren(); $('visits').replaceChildren();
  message(''); $('username').focus();
}
async function refresh() {
  if(!session) return;
  clearTimeout(timer); pending?.abort();
  const controller=new AbortController(); pending=controller;
  const currentSession=session;
  $('refresh').disabled=true; message('');
  // Remove previous values so errors cannot leave old data looking current.
  $('pavilions').replaceChildren(); $('summary').replaceChildren(); $('visits').replaceChildren(); $('trend').replaceChildren(); $('entries').replaceChildren(); $('empty').hidden=true;
  $('timestamp').textContent='Caricamento…';
  try {
    if(session.ruolo==='STAFF') {
      const [rows,summary,trend,entries]=await Promise.all(['padiglioni','giornata','andamento','ingressi'].map(endpoint=>api(`/affluenza/${endpoint}`,{},controller.signal)));
      if(session!==currentSession) return;
      $('pavilions').replaceChildren(...rows.map(r=>card(r.nomePadiglione,r.presenti,r.padiglione)));
      $('summary').replaceChildren(card('Visitatori della giornata',summary.visitatori),card('Ingressi ai varchi',summary.ingressi),card('Picco di presenze',summary.piccoPresenti));
      drawTrend(trend);
      $('entries').replaceChildren(...entries.map(row=>{
        const tr=document.createElement('tr');
        [new Date(row.ora).toLocaleTimeString('it-IT',{hour:'2-digit',minute:'2-digit',timeZone:'Europe/Rome'}),row.padiglione,number.format(row.ingressi),number.format(row.persone)].forEach(value=>{const td=document.createElement('td');td.textContent=value;tr.append(td);});return tr;
      }));
      $('timestamp').textContent=rows.length ? `Dati riferiti al ${date(rows[0].istante)} · Aggiornamento ogni 30 secondi` : 'Nessun padiglione disponibile';
    } else {
      const edition=$('edition').value;
      const rows=await api(`/espositore/me/visite?edizione=${edition}`,{},controller.signal);
      if(session!==currentSession) return;
      $('visits').replaceChildren(...rows.map(r=>{
        const tr=document.createElement('tr');
        const values=[r.codiceStand,new Date(`${r.giorno}T12:00:00+01:00`).toLocaleDateString('it-IT',{timeZone:'Europe/Rome'}),new Date(r.ora).toLocaleTimeString('it-IT',{hour:'2-digit',minute:'2-digit',timeZone:'Europe/Rome'}),number.format(r.scansioni)];
        values.forEach(value=>{const td=document.createElement('td');td.textContent=value;tr.append(td);}); return tr;
      }));
      $('empty').hidden=rows.length>0;
      $('empty').textContent=edition==='2024' ? 'Nel 2024 le visite agli stand non erano rilevate.' : 'Nessuna visita disponibile per questa edizione.';
      $('timestamp').textContent=`Edizione ${edition} · Ultimo aggiornamento ${new Date().toLocaleTimeString('it-IT')}`;
    }
  } catch(error) {
    if(error.name!=='AbortError') { message(error.message); $('timestamp').textContent='Dati non disponibili: riprova con Aggiorna dati.'; }
  } finally {
    if(pending===controller) { pending=null; $('refresh').disabled=false; if(session?.ruolo==='STAFF') timer=setTimeout(refresh,30000); }
  }
}
$('login-form').addEventListener('submit',async event=>{
  event.preventDefault(); $('login-button').disabled=true; message('');
  try {
    const result=await api('/auth/login',{method:'POST',body:JSON.stringify({username:$('username').value,password:$('password').value})});
    $('password').value='';
    if(!['STAFF','ESPOSITORE'].includes(result.ruolo)) throw new Error('Questa area è dedicata a staff ed espositori.');
    session=result; $('login-panel').hidden=true; $('workspace').hidden=false; $('logout').hidden=false;
    const staff=session.ruolo==='STAFF';
    $('staff').hidden=!staff; $('exhibitor').hidden=staff;
    $('area-label').textContent=staff?'OPERAZIONI FIERA':'AREA ESPOSITORE';
    $('page-title').textContent=staff?'Il festival, adesso.':'Il tuo stand, in numeri.';
    $('identity').textContent=staff?'Staff ARCADE':`Espositore ${session.idEspositore}`;
    await refresh();
  } catch(error) { message(error.message); }
  finally { $('login-button').disabled=false; }
});
$('logout').addEventListener('click',logout);
$('refresh').addEventListener('click',refresh);
$('edition').addEventListener('change',refresh);
