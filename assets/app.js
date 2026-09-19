(()=>{'use strict';
function setLanguage(lang){
 if(!['ru','en'].includes(lang))lang='ru';
 document.documentElement.lang=lang;
 try{localStorage.setItem('robotics-plan-language',lang)}catch(e){}
 document.querySelectorAll('[data-lang]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.lang===lang)));
 document.title=document.documentElement.dataset[lang+'Title']||document.title;
 // Pass the language through local HTML links; file:// storage policies vary by browser.
 document.querySelectorAll('a[href]').forEach(a=>{const raw=a.getAttribute('href');if(!raw||/^(?:[a-z]+:|\/\/|#)/i.test(raw))return;const [before,fragment]=raw.split('#');const [pathname,query]=before.split('?');if(!pathname.endsWith('.html'))return;const params=new URLSearchParams(query||'');params.set('lang',lang);a.setAttribute('href',pathname+'?'+params.toString()+(fragment!==undefined?'#'+fragment:''));});
}
let saved;try{saved=localStorage.getItem('robotics-plan-language')}catch(e){}
setLanguage(new URLSearchParams(location.search).get('lang')||saved||'ru');
document.querySelectorAll('[data-lang]').forEach(b=>b.addEventListener('click',()=>setLanguage(b.dataset.lang)));
document.querySelectorAll('[data-print]').forEach(b=>b.addEventListener('click',()=>window.print()));
const search=document.getElementById('nav-search');if(search)search.addEventListener('input',()=>{const q=search.value.toLowerCase().trim();document.querySelectorAll('.month-links a').forEach(a=>a.hidden=!a.textContent.toLowerCase().includes(q))});
function openHash(){let id;try{id=decodeURIComponent(location.hash.slice(1))}catch(e){return}const target=document.getElementById(id);if(target?.tagName==='DETAILS')target.open=true;}
openHash();window.addEventListener('hashchange',openHash);
})();
