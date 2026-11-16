// Frontend behavior checks using the actual HTML ids and DOM-compatible stubs.
const {readFileSync}=require('node:fs');
const vm=require('node:vm');
const assert=require('node:assert/strict');
const html=readFileSync(__dirname+'/index.html','utf8');
const ids=[...html.matchAll(/\bid="([^"]+)"/g)].map(x=>x[1]);
assert.equal(new Set(ids).size,ids.length,'HTML ids must be unique');
function element(tag='div') {
 return {tag,children:[],textContent:'',value:'',hidden:false,disabled:false,style:{},listeners:{},
 append(...nodes){this.children.push(...nodes);},replaceChildren(...nodes){this.children=nodes;},
 setAttribute(){},focus(){},addEventListener(name,fn){this.listeners[name]=fn;}};
}
const els=Object.fromEntries(ids.map(id=>[id,element()]));
els['demo-time'].value='11:55'; els.edition.value='2025';
let scheduled;
const context={Intl,Date,URLSearchParams,AbortController,AbortSignal,console,
 setTimeout(fn){scheduled=fn;return 1;},clearTimeout(){scheduled=null;},
 document:{getElementById(id){assert.ok(els[id],`Unknown HTML id ${id}`);return els[id];},createElement:element,createElementNS:(_,tag)=>element(tag)},
 fetch:async path=>({ok:true,status:200,json:async()=>path.includes('/giornata')?{visitatori:0,ingressi:0,piccoPresenti:0}:[]})};
vm.createContext(context);vm.runInContext(readFileSync(__dirname+'/app.js','utf8'),context);
const run=s=>vm.runInContext(s,context);
(async()=>{
 run('drawComparison([{edizione:2024,codiceStand:"<script>",padiglione:"P1",mq:10,imponibile:100,visite:null,contatti:0,ingressiPadiglione:20}])');
 assert.equal(els.comparison.children[0].children[5].textContent,'\u2014');
 assert.equal(els.comparison.children[0].children[6].textContent,'0');
 assert.equal(els.comparison.children[0].children[1].textContent,'<script>');
 run('drawComparison([])');assert.equal(els['comparison-empty'].hidden,false);
 run('tableRows("contacts",[["TEST","date","<img src=x>",null]])');
 assert.equal(els.contacts.children[0].children[2].textContent,'<img src=x>');
 assert.equal(els.contacts.children[0].children[3].textContent,'\u2014');
 els['demo-time'].value='25:00';assert.throws(()=>run('selectedDemoTime()'));
 els['demo-time'].value='18:55';
 run('session={ruolo:"STAFF",accessToken:"test"}; demoTime="18:55";demoRunning=true');
 await run('refresh()');assert.equal(typeof scheduled,'function');
 await scheduled(); // advances to 19:00, then stops
 assert.equal(run('demoTime'),'19:00');assert.equal(run('demoRunning'),false);
 run('logout()');assert.equal(els.contacts.children.length,0);assert.equal(els.renewal.children.length,0);
 // Multiple summaries keep missing measurements distinct from a measured zero.
 context.fetch=async path=>({ok:true,status:200,json:async()=>{
   if(path.includes('/riepiloghi')) return [
    {codiceStand:'TEST1',imponibile:100,visite:null,contatti:0,contattiConConsenso:0,costoPerContatto:null},
    {codiceStand:'TEST2',imponibile:200,visite:0,contatti:2,contattiConConsenso:1,costoPerContatto:100}];
   if(path.includes('/contatti')) return {content:[],page:0,totalPages:0,totalElements:0};
   return [];
 }});
 run('session={accessToken:"test",ruolo:"ESPOSITORE"}'); await run('refresh()');
 assert.equal(els['stand-summaries'].children.length,2);
 assert.equal(els['stand-summaries'].children[0].children[2].textContent,'\u2014');
 assert.equal(els['stand-summaries'].children[1].children[2].textContent,'0');
 // A failed sibling request must not leave previous private results visible.
 context.fetch=async()=>({ok:false,status:503,json:async()=>({message:'Unavailable'})});
 await run('refresh()');
 assert.equal(els['stand-summaries'].children.length,0);
 assert.equal(els.contacts.children.length,0);
 assert.equal(els.message.textContent,'Unavailable');
 assert.equal(els.refresh.disabled,false);
 // An expired response belonging to a previous login must not log out the new one.
 context.fetch=async()=>{run('session={accessToken:"new",ruolo:"ESPOSITORE"}');return {ok:false,status:401,json:async()=>({message:'expired'})};};
 run('session={accessToken:"old",ruolo:"ESPOSITORE"}');
 await assert.rejects(run('api("/test")'));
 assert.equal(run('session.accessToken'),'new');
 console.log('OK: HTML ids, missing/zero values, safe text, empty states, demo stop, logout and stale login response.');
})().catch(err=>{console.error(err);process.exitCode=1;});
