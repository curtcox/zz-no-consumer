'use strict';
const $ = id => document.getElementById(id);
let catalog, component, selected, savedSource = '', dirty = false, category = 'all', epoch = 0, busy = false, comparisonEpoch = 0, loading = false;
const sourceCache = new Map(), blobs = new Map();
function node(tag, text, cls) { const n=document.createElement(tag); if(text!==undefined)n.textContent=text; if(cls)n.className=cls; return n; }
function notice(text,error=false) { $('notice').textContent=text; $('notice').classList.toggle('error',error); }
async function request(url,body) {
  const response=await fetch(url,body ? {method:'POST',headers:{'Content-Type':'application/json','X-Component-Token':catalog.token},body:JSON.stringify({...body,revision:catalog.revision})} : {});
  const value=await response.json(); if(!response.ok)throw new Error(value.error || 'The request failed.'); return value;
}
async function source(version) {
  if(!sourceCache.has(version.url)){const r=await fetch(version.url);if(!r.ok)throw new Error('Could not load '+version.id);sourceCache.set(version.url,await r.text());}
  return sourceCache.get(version.url);
}
function paint(svg) {
  const doc=new DOMParser().parseFromString(svg,'image/svg+xml');
  if(doc.querySelector('parsererror') || doc.documentElement.localName!=='svg')throw new Error('The SVG is not well-formed.');
  if(doc.doctype || /<!ENTITY/i.test(svg))throw new Error('SVG entities are not supported.');
  const allowed=new Set(['svg','g','path','rect','circle','ellipse','line','polyline','polygon','defs','symbol','use','clipPath','mask','linearGradient','radialGradient','stop','pattern','title','desc','image']);
  for(const element of doc.querySelectorAll('*')) {
    if(!allowed.has(element.localName))throw new Error('Unsupported SVG element: '+element.localName);
    for(const attr of element.attributes){
      if(/^on/i.test(attr.name)||['style','class'].includes(attr.name))throw new Error('Use presentation attributes without scripts or CSS.');
      if(attr.localName==='href' && !attr.value.startsWith('#') && !(element.localName==='image' && /^data:image\/(png|jpeg|webp);base64,/.test(attr.value)))throw new Error('Use embedded images or local SVG references.');
      if(/\burl\s*\(/i.test(attr.value) && !/^url\(#[A-Za-z_][A-Za-z0-9_.-]*\)$/.test(attr.value))throw new Error('Only local SVG paint references are supported.');
    }
  }
  if(doc.documentElement.getAttribute('viewBox')?.trim().replace(/,/g,' ').split(/\s+/).map(Number).join(' ')!=='0 0 100 100')throw new Error('Use viewBox="0 0 100 100".');
  doc.documentElement.setAttribute('color',$('ink').value);
  return new XMLSerializer().serializeToString(doc);
}
function image(id,svg) {
  const rendered=paint(svg), old=blobs.get(id), url=URL.createObjectURL(new Blob([rendered],{type:'image/svg+xml'}));
  $(id).src=url;blobs.set(id,url);if(old)URL.revokeObjectURL(old);
}
function controls() {
  $('save').disabled=busy || loading || !dirty || !!$('svg-error').textContent;
  $('choose').disabled=busy || loading || dirty || selected===component?.default;
  $('rebuild').disabled=busy;
  $('reset').disabled=!dirty || busy;
  $('new').disabled=busy;
  $('source').disabled=busy || loading;
  $('draft-badge').hidden=!dirty;
}
function changeDraft() {
  dirty=$('source').value!==savedSource;
  try {image('preview',$('source').value);$('svg-error').textContent='';}
  catch(error){$('svg-error').textContent=error.message;}
  controls();
}
function canLeave(){return !dirty || window.confirm('Discard this unsaved component draft?');}
function cardList() {
  const query=$('search').value.toLowerCase().trim();
  const values=catalog.components.filter(c=>(category==='all'||c.category===category) && `${c.id} ${c.name} ${c.description}`.toLowerCase().includes(query));
  $('count').textContent=`${values.length} of ${catalog.components.length} components`;
  $('components').replaceChildren();
  for(const c of values){
    const button=node('button',undefined,'component-card');button.type='button';button.setAttribute('aria-pressed',String(component?.id===c.id));button.setAttribute('aria-label',c.name);
    const img=node('img');img.src=c.versions.find(v=>v.id===c.default).url;img.alt='';img.loading='lazy';button.append(img,node('strong',c.name),node('small',`${c.versions.length} version${c.versions.length===1?'':'s'}`));
    button.onclick=()=>{if(!busy && canLeave())select(c.id);};$('components').append(button);
  }
  $('empty').hidden=values.length>0 || !!component;
}
function categoryList() {
  $('categories').replaceChildren();
  for(const value of ['all',...catalog.categories]){
    const count=catalog.components.filter(c=>value==='all'||c.category===value).length;
    const button=node('button',`${value[0].toUpperCase()+value.slice(1)} ${count}`);button.setAttribute('aria-pressed',String(category===value));button.onclick=()=>{category=value;categoryList();cardList();};$('categories').append(button);
  }
}
function versionList(){
  $('versions').replaceChildren();$('version-count').textContent=component.versions.length+' retained';
  for(const v of [...component.versions].reverse()){
    const button=node('button',undefined,'version-row');button.setAttribute('aria-pressed',String(v.id===selected));
    const text=node('span',v.id);text.append(node('small',v.note));if(v.parent)text.append(node('small','Based on '+v.parent));
    text.append(node('small',new Date(v.created).toLocaleDateString(undefined,{year:'numeric',month:'short',day:'numeric'})));button.append(text);
    if(v.id===component.default)button.append(node('span','Default','badge'));
    button.onclick=()=>{if(!busy && canLeave())select(component.id,v.id);};$('versions').append(button);
  }
  const usage=component.usage, pinned=Object.values(usage.pinned).flat();
  $('usage').textContent=`${usage.default.length} storyboards follow the default. ${new Set(pinned).size} pin a specific version. Choosing a default is reversible; saved versions stay intact.`;
  $('references').replaceChildren(node('p',usage.default.length?'Default: '+usage.default.join(', '):'No storyboards follow this default yet.'));
  for(const [v,keys] of Object.entries(usage.pinned))$('references').append(node('p',v+': '+keys.join(', ')));
}
async function comparison(){
  const serial=epoch, comparisonSerial=++comparisonEpoch, v=component.versions.find(v=>v.id===$('compare').value);if(!v)return;
  try{const svg=await source(v);if(serial!==epoch || comparisonSerial!==comparisonEpoch)return;image('comparison',svg);$('compare-label').textContent=v.id+(v.id===component.default?' · Library default':' · Saved version');$('comparison-note').textContent=v.note;}
  catch(error){notice(error.message,true);}
}
async function select(id,version){
  const serial=++epoch;component=catalog.components.find(c=>c.id===id);if(!component)return;
  selected=version||component.default;dirty=false;loading=true;$('source').value='';$('note').value='';$('svg-error').textContent='';
  $('detail').hidden=false;$('empty').hidden=true;
  $('name').textContent=component.name;$('category').textContent=component.category;$('description').textContent=component.description;$('identity').textContent=component.id;
  const v=component.versions.find(v=>v.id===selected);$('current-label').textContent=selected+(selected===component.default?' · Library default':' · Saved version');$('current-note').textContent=v.note;
  $('compare').replaceChildren(...component.versions.map(v=>{const opt=node('option',v.id+(v.id===component.default?' · Default':''));opt.value=v.id;return opt;}));
  $('compare').value=component.default===selected && component.versions.length>1 ? component.versions.find(v=>v.id!==selected).id : component.default;
  versionList();cardList();controls();history.replaceState(null,'','#'+encodeURIComponent(id)+'/'+selected);
  try{const svg=await source(v);if(serial!==epoch)return;savedSource=svg;$('source').value=svg;loading=false;changeDraft();await comparison();}
  catch(error){notice(error.message,true);}finally{if(serial===epoch){loading=false;controls();}}
}
function adopt(value){catalog=value;categoryList();$('mode').textContent=catalog.editable?'Local · Editing enabled':'Published · Preview & download';for(const id of ['new','save','choose','rebuild'])$(id).hidden=!catalog.editable;$('readonly').hidden=catalog.editable;}
$('search').oninput=cardList;
$('source').oninput=changeDraft;
$('compare').onchange=comparison;
$('ink').oninput=()=>{changeDraft();comparison();};
$('surface').onchange=()=>document.querySelectorAll('.canvas').forEach(n=>n.className='canvas '+$('surface').value);
$('guides').onchange=()=>document.body.classList.toggle('show-guides',$('guides').checked);
function fitGuides(){
  for(const canvas of document.querySelectorAll('.canvas')){
    const size=Math.min(canvas.clientWidth,canvas.clientHeight)*Number($('zoom').value)/100;
    for(const item of [canvas.querySelector('img'),canvas.querySelector('.guides')]){
      item.style.width=size+'px';item.style.height=size+'px';
    }
  }
}
const previewObserver=new ResizeObserver(fitGuides);
for(const canvas of document.querySelectorAll('.canvas'))previewObserver.observe(canvas);
$('zoom').oninput=fitGuides;
$('reset').onclick=()=>{if(canLeave()){$('source').value=savedSource;$('note').value='';changeDraft();}};
$('import').onchange=async()=>{const file=$('import').files[0];if(!file)return;if(file.size>2000000){notice('Choose an SVG smaller than 2 MB.',true);return;}if(canLeave()){$('source').value=await file.text();changeDraft();}$('import').value='';};
$('download').onclick=()=>{try{paint($('source').value);const url=URL.createObjectURL(new Blob([$('source').value],{type:'image/svg+xml'}));const a=node('a');a.href=url;a.download=component.id+'-'+(dirty?'draft':selected)+'.svg';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}catch(error){notice(error.message,true);}};
$('save').onclick=async()=>{
  if(!$('note').value.trim()){notice('Describe what changed before saving.',true);$('note').focus();return;}
  busy=true;controls();try{const result=await request('api/version',{id:component.id,svg:$('source').value,note:$('note').value,parent:selected});const id=component.id;adopt(result.catalog);await select(id,result.version);notice(`Saved ${result.version}. The library default is unchanged until you choose it.`);}catch(error){notice(error.message,true);}finally{busy=false;controls();}
};
$('choose').onclick=async()=>{
  busy=true;controls();try{const id=component.id,version=selected,result=await request('api/default',{id,version});adopt(result.catalog);await select(id,version);notice(`Default updated to ${version}. Apply to storyboards when you’re ready; pinned versions stay fixed.`);}catch(error){notice(error.message,true);}finally{busy=false;controls();}
};
$('new').onclick=()=>$('create-dialog').showModal();
$('cancel-create').onclick=()=>$('create-dialog').close();
$('create-form').onsubmit=async event=>{
  event.preventDefault();const form=new FormData(event.target),submit=event.target.querySelector('[type=submit]');submit.disabled=true;$('create-error').textContent='';
  try{if(!canLeave())return;const id=form.get('id'),result=await request('api/version',{id,svg:form.get('svg'),note:'Initial component',create:{name:form.get('name'),category:form.get('category'),description:form.get('description')}});adopt(result.catalog);$('create-dialog').close();event.target.reset();await select(id,result.version);notice('Component created. Its first version is ready to use.');}catch(error){$('create-error').textContent=error.message;}finally{submit.disabled=false;}
};
async function watchBuild(){
  try{const result=await request('api/build');busy=result.running;controls();notice(result.message,result.ok===false);if(result.running)setTimeout(watchBuild,1500);}
  catch(error){busy=false;controls();notice(error.message,true);}
}
$('rebuild').onclick=async()=>{
  if(dirty){notice('Save or discard the component draft before rebuilding.',true);return;}
  busy=true;controls();try{await request('api/rebuild',{});watchBuild();}catch(error){busy=false;controls();notice(error.message,true);}
};
window.addEventListener('beforeunload',event=>{if(dirty){event.preventDefault();event.returnValue='';}});
(async()=>{try{adopt(await request('catalog.json'));const parts=decodeURIComponent(location.hash.slice(1)).split('/'),c=catalog.components.find(c=>c.id===parts[0])||catalog.components[0];if(c)await select(c.id,c.versions.some(v=>v.id===parts[1])?parts[1]:undefined);else cardList();if(catalog.editable){const job=await request('api/build');if(job.running)watchBuild();}}catch(error){notice(error.message,true);}})();
