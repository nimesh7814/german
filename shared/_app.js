/* ── German A1 — shared app script ─────────────────────────────── */

const subheadings = {
  communication: [
    { label: "Introductions", id: "sub-introductions" },
    { label: "Greetings & Farewells", id: "sub-greetings" },
    { label: "Feelings & Wellbeing", id: "sub-feelings" },
  ],
  countries: [
    { label: "Countries (Länder)", id: "sub-countries-list" },
    { label: "Languages (Sprachen)", id: "sub-languages" },
  ],
  personal: [
    { label: "Names & Forms of Address", id: "sub-names" },
    { label: "Age, Address & Contact", id: "sub-contact" },
    { label: "Marital Status & Children", id: "sub-marital" },
  ],
  numbers: [
    { label: "0 – 19", id: "sub-num0" },
    { label: "20 – 99", id: "sub-num20" },
    { label: "Hundreds (100–900)", id: "sub-hundreds" },
    { label: "Thousands (1,000–10,000)", id: "sub-thousands" },
    { label: "Number Converter", id: "sub-converter" },
  ],
  alphabet: [
    { label: "The German Alphabet", id: "sub-alpha" },
    { label: "Special Characters (Umlauts)", id: "sub-umlauts" },
  ],
  colors: [
    { label: "Color Swatches", id: "sub-colorswatches" },
    { label: "Talking About Colors", id: "sub-colortalk" },
  ],
  grammar: [
    { label: "sein & haben", id: "sub-seinhabn" },
    { label: "Regular Verb Conjugation", id: "sub-regverbs" },
    { label: "Articles & Nouns", id: "sub-articles" },
    { label: "Plural Forms", id: "sub-plurals" },
    { label: "Possessive Pronouns", id: "sub-poss" },
    { label: "Personal Pronouns", id: "sub-persp" },
  ],
  family: [
    { label: "Family Members", id: "sub-familymembers" },
    { label: "Possessive Sentences", id: "sub-familysent" },
    { label: "Possessives with Nouns (Class)", id: "sub-possnouns" },
  ],
  school: [
    { label: "School Vocabulary", id: "sub-schoolvocab" },
    { label: "School Subjects", id: "sub-subjects" },
    { label: "Timetable Phrases", id: "sub-timetable" },
    { label: "Classroom Objects", id: "sub-classobj" },
    { label: "Classroom Language", id: "sub-classlang" },
    { label: "Class Exercises (Notebook)", id: "sub-classexercise" },
  ],
  time: [
    { label: "Days of the Week", id: "sub-days" },
    { label: "Months", id: "sub-months" },
    { label: "Seasons", id: "sub-seasons" },
    { label: "Time Expressions", id: "sub-timeexpr" },
    { label: "Telling the Time", id: "sub-telling" },
    { label: "von/bis/ab (Ranges)", id: "sub-vonbis" },
    { label: "Time Prepositions: um/im/am", id: "sub-timeprep" },
    { label: "Example Sentences", id: "sub-timesentences" },
  ],
  komposita: [
    { label: "Nomen + Nomen", id: "sub-komp-nn" },
    { label: "Verb + Nomen",  id: "sub-komp-vn" },
    { label: "Adjektiv + Nomen", id: "sub-komp-adj" },
    { label: "Adverb + Nomen",  id: "sub-komp-adv" },
    { label: "Kettenkomposita", id: "sub-komp-chain" },
  ],
  hobbies: [
    { label: "Hobby-Verben", id: "sub-hob-verbs" },
    { label: "Wie oft? (Frequency)", id: "sub-hob-freq" },
    { label: "Wortstellung (Word Order)", id: "sub-hob-order" },
    { label: "Fragen über Hobbys", id: "sub-hob-questions" },
  ],
};

function getCurrentSection() {
  const active = document.querySelector('.nav-tab.active');
  if (!active) return null;
  const href = active.getAttribute('href') || '';
  const match = href.match(/([^/]+)\.html$/);
  return match ? match[1] : null;
}

function scrollToSub(id) {
  const el = document.getElementById(id);
  if (!el) return;
  const navbar = document.getElementById('top-navbar');
  const offset = (navbar ? navbar.offsetHeight : 0) + 12;
  window.scrollTo({ top: el.getBoundingClientRect().top + window.scrollY - offset, behavior: 'smooth' });
}

function buildDropdown() {
  const dropdown = document.getElementById('nav-dropdown');
  if (!dropdown) return;
  const sec = getCurrentSection();
  const subs = (sec && subheadings[sec]) || [];
  if (subs.length) {
    dropdown.innerHTML = subs.map(s =>
      `<div class="nav-sub" onclick="scrollToSub('${s.id}')">${s.label}</div>`
    ).join('');
    dropdown.classList.add('open');
  } else {
    dropdown.innerHTML = '';
    dropdown.classList.remove('open');
  }
}

/* Number Converter */
const ones = ['','ein','zwei','drei','vier','fünf','sechs','sieben','acht','neun',
               'zehn','elf','zwölf','dreizehn','vierzehn','fünfzehn','sechzehn',
               'siebzehn','achtzehn','neunzehn'];
const tens = ['','','zwanzig','dreißig','vierzig','fünfzig','sechzig','siebzig','achtzig','neunzig'];

function numToGerman(n) {
  if (n === 0) return 'null';
  if (n === 1) return 'eins';
  let r = '';
  if (n >= 100000) return 'hunderttausend';
  if (n >= 1000)  { const t=Math.floor(n/1000); r+=(t===1?'ein':numToGerman(t))+'tausend'; n%=1000; if(!n) return r; }
  if (n >= 100)   { const h=Math.floor(n/100);  r+=(h===1?'ein':ones[h])+'hundert'; n%=100; if(!n) return r; }
  if (n >= 20)    { const u=n%10,t=Math.floor(n/10); r+=u>0?ones[u]+'und'+tens[t]:tens[t]; }
  else if (n > 0) { r+=ones[n]; }
  return r;
}

const pronMap = {
  'null':'[nool]','eins':'[ines]','zwei':'[tsvye]','drei':'[drye]','vier':'[feer]',
  'fünf':'[fuenf]','sechs':'[zeks]','sieben':'[ZEE-ben]','acht':'[akht]','neun':'[noyn]',
  'zehn':'[tsayn]','elf':'[elf]','zwölf':'[tsvurlf]','zwanzig':'[TSVAN-tsish]',
  'dreißig':'[DRY-ssish]','vierzig':'[FEER-tsish]','fünfzig':'[FUENF-tsish]',
  'sechzig':'[ZEKH-tsish]','siebzig':'[ZEEP-tsish]','achtzig':'[AHKH-tsish]',
  'neunzig':'[NOYN-tsish]','hundert':'[HOON-dert]','tausend':'[TOW-zent]',
};

function convertNumber() {
  const input=document.getElementById('num-input'),
        resultDiv=document.getElementById('num-result'),
        errorDiv=document.getElementById('num-error');
  const val=parseInt(input.value,10);
  resultDiv.style.display='none'; errorDiv.style.display='none';
  if (isNaN(val)||val<0||val>100000) {
    errorDiv.textContent='⚠️ Please enter a number between 0 and 100,000.';
    errorDiv.style.display='block'; return;
  }
  const word=numToGerman(val);
  document.getElementById('res-number').textContent=val.toLocaleString('de-DE');
  document.getElementById('res-word').textContent=word;
  let pron='';
  for (const [k,v] of Object.entries(pronMap)) { if(word===k){pron=v;break;} }
  document.getElementById('res-pron').textContent=pron;
  resultDiv.style.display='block';
}

document.addEventListener('DOMContentLoaded', () => {
  buildDropdown();
  const inp=document.getElementById('num-input');
  if (inp) inp.addEventListener('keydown', e=>{ if(e.key==='Enter') convertNumber(); });
});
