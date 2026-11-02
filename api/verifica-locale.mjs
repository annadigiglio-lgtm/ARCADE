// Integration check against the running local API and its existing PostgreSQL DB.
// No database writes; credentials and tokens are never printed.
import assert from 'node:assert/strict';
import {readFileSync,existsSync,readdirSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname,resolve,join} from 'node:path';
import {spawnSync} from 'node:child_process';
const here=dirname(fileURLToPath(import.meta.url));
const root=resolve(here,'..');
function settings(path) {
  return Object.fromEntries(readFileSync(path,'utf8').split(/\r?\n/).filter(line=>/^\s*[\w.]+\s*=/.test(line)).map(line=>{
    const i=line.indexOf('='); return [line.slice(0,i).trim(),line.slice(i+1).trim().replace(/^"|"$/g,'')];
  }));
}
const env=settings(join(root,'.env.local'));
assert.ok(['localhost','127.0.0.1'].includes(env.DB_HOST),'La verifica richiede il DB locale');
const credentials=settings(join(here,'demo-accounts.local'));
let psql=process.env.PSQL_PATH;
if(!psql) {
  const pgRoot='C:/Program Files/PostgreSQL';
  psql=readdirSync(pgRoot).sort((a,b)=>Number(b)-Number(a)).map(v=>join(pgRoot,v,'bin/psql.exe')).find(existsSync);
}
assert.ok(psql,'Impostare PSQL_PATH al percorso di psql');
function sql(query) {
  const result=spawnSync(psql,['-X','-A','-t','-v','ON_ERROR_STOP=1','-d',env.DB_NAME,'-c',query],{
    env:{...process.env,PGHOST:env.DB_HOST,PGPORT:env.DB_PORT,PGUSER:env.DB_USER,PGPASSWORD:env.DB_PASSWORD,PGSSLMODE:env.DB_SSLMODE,PGOPTIONS:'-c search_path=arcade'},encoding:'utf8'
  });
  assert.equal(result.status,0,'Query di verifica SQL fallita');
  return result.stdout.trim();
}
const base='http://127.0.0.1:8080';
async function request(path,token,options={}) {
  const response=await fetch(base+path,{...options,headers:{'Content-Type':'application/json',...(token?{Authorization:`Bearer ${token}`}:{})},signal:AbortSignal.timeout(30000)});
  return {status:response.status,body:await response.json()};
}
async function login(username) {
  const response=await request('/auth/login',null,{method:'POST',body:JSON.stringify({username,password:credentials[username]})});
  assert.equal(response.status,200,`Login ${username}`);return response.body;
}
assert.equal((await fetch(base)).status,200,'Pagina iniziale');
assert.equal((await fetch(base+'/app.js')).status,200,'JavaScript');
assert.equal((await fetch(base+'/style.css')).status,200,'CSS');
assert.equal((await request('/affluenza/padiglioni')).status,401);
assert.equal((await request('/affluenza/padiglioni','invalid')).status,401);
const staff=await login('staff.demo');
assert.equal(staff.ruolo,'STAFF');
const presenze=await request('/affluenza/padiglioni',staff.accessToken);
assert.equal(presenze.status,200);
const instant=process.env.ARCADE_DEMO_ISTANTE||'2025-12-20T11:55:00+01:00';
assert.match(instant,/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d[+-]\d\d:\d\d$/,'La verifica richiede un istante demo fisso');
const expected=JSON.parse(sql(`SELECT json_agg(r ORDER BY r.padiglione) FROM (SELECT padiglione,nome_padiglione AS "nomePadiglione",presenti FROM presenze_al('${instant}'::timestamptz)) r;`));
assert.deepEqual(presenze.body.map(({padiglione,nomePadiglione,presenti})=>({padiglione,nomePadiglione,presenti})),expected,'Presenze API = SQL');
for(const endpoint of ['giornata','ingressi','andamento']) assert.equal((await request(`/affluenza/${endpoint}`,staff.accessToken)).status,200,endpoint);
const first=await login('espositore.demo1');
const second=await login('espositore.demo2');
assert.notEqual(first.idEspositore,second.idEspositore);
for(const account of [first,second]) {
  assert.match(account.idEspositore,/^[A-Za-z0-9_-]+$/);
  assert.equal((await request('/affluenza/padiglioni',account.accessToken)).status,403);
  const rows=await request('/espositore/me/visite?edizione=2025',account.accessToken);
  assert.equal(rows.status,200); assert.ok(rows.body.length>0);
  const expectedRows=JSON.parse(sql(`SELECT json_agg(r ORDER BY r.giorno,r.ora,r."codiceStand") FROM (SELECT edizione,codice_stand AS "codiceStand",giorno,ora,scansioni FROM v_espositore_visite_ora WHERE id_espositore='${account.idEspositore}' AND edizione=2025) r;`));
  const normalized=rows=>rows.map(row=>({...row,ora:new Date(row.ora).toISOString()}));
  assert.deepEqual(normalized(rows.body),normalized(expectedRows),'Visite API = SQL per espositore');
  const spoof=await request(`/espositore/me/visite?edizione=2025&idEspositore=${account===first?second.idEspositore:first.idEspositore}`,account.accessToken);
  assert.deepEqual(spoof.body,rows.body,'Identità in URL non modifica i dati');
  assert.deepEqual((await request('/espositore/me/visite?edizione=2024',account.accessToken)).body,[]);
  assert.equal((await request('/espositore/me/visite?edizione=2030',account.accessToken)).status,400);
  assert.equal((await request('/espositore/me/riepilogo?edizione=2025',account.accessToken)).status,200);
}
assert.equal((await request('/espositore/me/visite?edizione=2025',staff.accessToken)).status,403);
assert.equal((await request('/auth/login',null,{method:'POST',body:JSON.stringify({username:'staff.demo',password:'incorrect'})})).status,401);
console.log('OK: pagina e asset, 3 login, 4 endpoint staff, visite confrontate con SQL, ruoli e isolamento dei 2 espositori.');
