// HTTP checks for Docker/Supabase or the Render URL. No SQL writes or secret output.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
const base=new URL(process.argv.find(arg=>/^https?:\/\//.test(arg)) || 'http://127.0.0.1:8081');
const loginOnly=process.argv.includes('--solo-login');
assert.ok(['localhost','127.0.0.1'].includes(base.hostname) || (base.protocol==='https:' && base.hostname.endsWith('.onrender.com')),'Usare localhost oppure un URL HTTPS onrender.com');
assert.ok(!base.username && !base.password && !base.search && !base.hash);
const file=fileURLToPath(new URL('./demo-accounts.local',import.meta.url));
const credentials=Object.fromEntries(readFileSync(file,'utf8').split(/\r?\n/).filter(line=>line && !line.startsWith('#')).map(line=>{const i=line.indexOf('=');return [line.slice(0,i),line.slice(i+1)];}));
async function request(path,token,options={}) {
  const response=await fetch(new URL(path,base),{...options,headers:{'Content-Type':'application/json',...(token?{Authorization:`Bearer ${token}`}:{})},redirect:'error',signal:AbortSignal.timeout(90000)});
  return {status:response.status,body:await response.json()};
}
async function login(username,expectedRole) {
  const result=await request('/auth/login',null,{method:'POST',body:JSON.stringify({username,password:credentials[username]})});
  assert.equal(result.status,200,`Login ${username}: atteso 200, ricevuto ${result.status}`);
  assert.equal(result.body.ruolo,expectedRole); assert.ok(result.body.accessToken);
  return result.body;
}
const page=await fetch(base,{signal:AbortSignal.timeout(90000)});
assert.equal(page.status,200);assert.ok((await page.text()).includes('id="login-form"'));
for(const path of ['/app.js','/style.css']) assert.equal((await fetch(new URL(path,base))).status,200);
assert.equal((await request('/affluenza/padiglioni')).status,401);
assert.equal((await request('/affluenza/padiglioni','invalid')).status,401);
const staff=await login('staff.demo','STAFF');
const first=await login('espositore.demo1','ESPOSITORE');
const second=await login('espositore.demo2','ESPOSITORE');
assert.notEqual(first.idEspositore,second.idEspositore);
assert.equal((await request('/espositore/me/visite?edizione=2025',staff.accessToken)).status,403);
for(const account of [first,second]) {
  assert.equal((await request('/affluenza/padiglioni',account.accessToken)).status,403);
  assert.equal((await request('/espositore/me/visite?edizione=2030',account.accessToken)).status,400);
}
assert.equal((await request('/auth/login',null,{method:'POST',body:JSON.stringify({username:'staff.demo',password:'incorrect'})})).status,401);
console.log('OK: container/pagina e asset, 3 login Supabase, ruoli e rifiuto di token/password non validi.');
if(loginOnly) {
  console.log('Verifica dati omessa: completare prima la pubblicazione delle viste API su Supabase.');
} else {
  for(const path of ['padiglioni','giornata','andamento','ingressi']) {
    const result=await request(`/affluenza/${path}`,staff.accessToken);
    assert.equal(result.status,200,`${path}: atteso 200, ricevuto ${result.status}; verificare db/pubblica_api_supabase.sql`);
    if(path==='padiglioni') assert.equal(result.body.length,3);
  }
  const sets=[];
  for(const account of [first,second]) {
    const visits=await request('/espositore/me/visite?edizione=2025',account.accessToken);
    assert.equal(visits.status,200); assert.ok(visits.body.length>0);
    assert.ok(visits.body.every(row=>!Object.hasOwn(row,'idEspositore')));
    const spoof=await request(`/espositore/me/visite?edizione=2025&idEspositore=${account===first?second.idEspositore:first.idEspositore}`,account.accessToken);
    assert.equal(spoof.status,200);assert.deepEqual(spoof.body,visits.body);
    assert.deepEqual((await request('/espositore/me/visite?edizione=2024',account.accessToken)).body,[]);
    assert.equal((await request('/espositore/me/riepilogo?edizione=2025',account.accessToken)).status,200);
    sets.push(new Set(visits.body.map(row=>row.codiceStand)));
  }
  assert.ok([...sets[0]].every(stand=>!sets[1].has(stand)),'Gli espositori devono avere stand distinti');
  console.log('OK: 4 endpoint staff, visite/riepilogo espositori e isolamento dei due account.');
}
