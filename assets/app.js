(()=>{'use strict';
function languageFromUrl(){
 const lang=new URLSearchParams(location.search).get('lang');
 return ['en','ru'].includes(lang)?lang:'en';
}
function setLanguage(lang,historyMode='replace'){
 if(!['en','ru'].includes(lang))lang='en';
 const currentUrl=new URL(location.href);
 currentUrl.searchParams.set('lang',lang);
 if(currentUrl.href!==location.href){
  try{window.history[historyMode+'State'](null,'',currentUrl.href)}catch(e){
   // Some file:// viewers restrict History API updates; navigation still preserves the choice.
   if(historyMode==='push'){location.href=currentUrl.href;return;}
  }
 }
 document.documentElement.lang=lang;
 document.querySelectorAll('[data-lang]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.lang===lang)));
 document.title=document.documentElement.dataset[lang+'Title']||document.title;
 // Keep local page links shareable, including links opened in a new tab.
 document.querySelectorAll('a[href]').forEach(a=>{
  const raw=a.getAttribute('href');
  if(!raw||raw.startsWith('#')||a.hasAttribute('download'))return;
  let url;try{url=new URL(raw,location.href)}catch(e){return;}
  if(url.origin!==location.origin||url.protocol!==location.protocol||!/(?:\.html|\/)$/i.test(url.pathname))return;
  url.searchParams.set('lang',lang);
  a.setAttribute('href',url.href);
 });
}
setLanguage(languageFromUrl());
document.querySelectorAll('[data-lang]').forEach(b=>b.addEventListener('click',()=>setLanguage(b.dataset.lang,'push')));
window.addEventListener('popstate',()=>{setLanguage(languageFromUrl());openHash();});
document.querySelectorAll('[data-print]').forEach(b=>b.addEventListener('click',()=>window.print()));
const search=document.getElementById('nav-search');if(search)search.addEventListener('input',()=>{const q=search.value.toLowerCase().trim();document.querySelectorAll('.month-links a').forEach(a=>a.hidden=!a.textContent.toLowerCase().includes(q))});
function openHash(){let id;try{id=decodeURIComponent(location.hash.slice(1))}catch(e){return}const target=document.getElementById(id);if(target?.tagName==='DETAILS')target.open=true;}
openHash();window.addEventListener('hashchange',openHash);
})();
