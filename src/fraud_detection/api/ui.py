"""Self-contained HTML demo UI served at the API root."""

INDEX_HTML = """<!doctype html>
<html lang='en'><head><meta charset='utf-8'>
<meta name='viewport' content='width=device-width,initial-scale=1'>
<link rel='icon' href='data:,'>
<title>Card Fraud Detection - Live Demo</title>
<style>
:root{--card:#1e293b;--muted:#94a3b8;--line:#334155;--accent:#38bdf8}
*{box-sizing:border-box}body{margin:0;font-family:system-ui,Segoe UI,Roboto,sans-serif;background:linear-gradient(160deg,#0b1220,#0f172a);color:#e2e8f0;min-height:100vh}
.wrap{max-width:840px;margin:0 auto;padding:22px 20px 64px}
.top{display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;font-size:.85rem;color:var(--muted);border-bottom:1px solid var(--line);padding-bottom:12px;margin-bottom:22px}
.top b{color:#e2e8f0}.top a{color:var(--accent);text-decoration:none;margin-left:10px}
h1{font-size:1.6rem;margin:0 0 6px}.sub{color:var(--muted);margin:0 0 12px;font-size:.95rem}
.chips{margin:0 0 22px;display:flex;gap:8px;flex-wrap:wrap}
.chip{font-size:.72rem;padding:4px 10px;border-radius:999px;background:#0b1220;border:1px solid var(--line);color:#cbd5e1}
.chip.warn{border-color:#854d0e;color:#fde68a}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:22px;margin-bottom:20px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:14px}
label{display:block;font-size:.78rem;color:var(--muted);margin-bottom:5px}
input,select{width:100%;padding:9px 10px;border-radius:8px;border:1px solid var(--line);background:#0b1220;color:#e2e8f0;font-size:.92rem}
.row{display:flex;gap:10px;align-items:center;margin-top:18px;flex-wrap:wrap}
button{cursor:pointer;border:none;border-radius:9px;padding:11px 18px;font-weight:600;font-size:.92rem}
button:disabled{opacity:.6;cursor:wait}
.primary{background:var(--accent);color:#04263a}.ghost{background:transparent;border:1px solid var(--line);color:#cbd5e1}
.check{display:flex;align-items:center;gap:8px}.check input{width:auto}
.result{display:none}.score{font-size:3rem;font-weight:800;line-height:1}
.badge{display:inline-block;padding:6px 14px;border-radius:999px;font-weight:700;font-size:.85rem}
.meter{position:relative;height:14px;border-radius:999px;background:#0b1220;border:1px solid var(--line);overflow:visible;margin:14px 0}
.fill{height:100%;width:0;border-radius:999px;transition:width .6s ease}
.thr{position:absolute;top:-4px;width:2px;height:22px;background:#e2e8f0;opacity:.7}
.muted{color:var(--muted);font-size:.85rem}
.why{margin-top:14px;border-top:1px solid var(--line);padding-top:12px}
.why h4{margin:0 0 8px;font-size:.8rem;color:var(--muted);font-weight:600;text-transform:uppercase;letter-spacing:.04em}
.factor{display:flex;align-items:center;gap:9px;padding:4px 0;font-size:.9rem}
.dot{width:9px;height:9px;border-radius:50%;flex:none}
.err{color:#fca5a5}.foot{color:var(--muted);font-size:.8rem;text-align:center;margin-top:26px}a{color:var(--accent)}
</style></head>
<body><div class='wrap'>
<div class='top'><div><b>MD Minhazur Rahman</b> - Data Scientist / ML Engineer</div>
<div><a href='https://github.com/minhazda'>Portfolio</a><a href='https://www.linkedin.com/in/mohammadminhaz/'>LinkedIn</a><a href='https://retail-forecasting-api-ude5vos6lq-uc.a.run.app/'>Forecast demo</a></div></div>
<h1>Card Fraud Detection</h1>
<p class='sub'>A LightGBM model scores a card transaction for fraud risk in real time. Try the presets, then read the risk drivers it surfaces.</p>
<div class='chips'><span class='chip'>LightGBM</span><span class='chip'>ROC-AUC 0.90</span><span class='chip'>PR-AUC 0.49 (~8x base)</span><span class='chip'>GCP Cloud Run</span><span class='chip warn'>synthetic demo data</span></div>
<div class='card'><div class='grid'>
<div><label>Amount ($)</label><input id='amount' type='number' value='920'></div>
<div><label>Hour (0-23)</label><input id='hour' type='number' value='2'></div>
<div><label>Day</label><select id='day_of_week'><option value='0'>Monday</option><option value='1'>Tuesday</option><option value='2'>Wednesday</option><option value='3'>Thursday</option><option value='4'>Friday</option><option value='5'>Saturday</option><option value='6' selected>Sunday</option></select></div>
<div><label>Merchant category</label><select id='merchant_category'><option>online</option><option>gambling</option><option>grocery</option><option>restaurant</option><option>travel</option><option>electronics</option><option>fuel</option></select></div>
<div><label>Customer age</label><input id='customer_age' type='number' value='31'></div>
<div><label>Account age (days)</label><input id='account_age_days' type='number' value='12'></div>
<div><label>Txns in last 24h</label><input id='n_tx_24h' type='number' value='9'></div>
<div><label>Avg amount (30d)</label><input id='avg_amount_30d' type='number' value='40'></div>
<div><label>Distance from home (km)</label><input id='distance_from_home' type='number' value='480'></div>
<div class='check'><input id='is_foreign' type='checkbox' checked><label style='margin:0'>Foreign transaction</label></div>
</div>
<div class='row'><button class='primary' id='go' onclick='score()'>Score transaction</button>
<button class='ghost' onclick=\"preset('risky')\">Risky example</button>
<button class='ghost' onclick=\"preset('safe')\">Typical example</button></div></div>
<div class='card result' id='result'>
<div style='display:flex;justify-content:space-between;align-items:flex-end;flex-wrap:wrap;gap:10px'>
<div><div class='muted'>Fraud probability</div><div class='score' id='pct'>-</div></div><div id='badge' class='badge'>-</div></div>
<div class='meter'><div class='fill' id='fill'></div><div class='thr' id='thr'></div></div>
<div class='muted' id='explain'></div>
<div class='why' id='why' style='display:none'><h4>Key risk signals in this transaction</h4><div id='factors'></div>
<div class='muted' style='margin-top:8px'>Indicative drivers - the model weighs these jointly, not as a checklist.</div></div></div>
<p class='foot'>LightGBM - imbalanced classification - threshold tuned on a validation split - <a href='/docs'>API docs</a> - <a href='https://github.com/minhazda/fraud-detection-mlops'>source</a></p>
</div>
<script>
function preset(k){var r={amount:920,hour:2,day_of_week:'6',merchant_category:'online',customer_age:31,account_age_days:12,n_tx_24h:9,avg_amount_30d:40,distance_from_home:480,is_foreign:true};
var s={amount:18,hour:13,day_of_week:'2',merchant_category:'grocery',customer_age:45,account_age_days:1500,n_tx_24h:2,avg_amount_30d:22,distance_from_home:3,is_foreign:false};
var v=k==='risky'?r:s;for(var key in v){var el=document.getElementById(key);if(el.type==='checkbox')el.checked=v[key];else el.value=v[key];}}
function drivers(row){var f=[];var hi='#ef4444',md='#f59e0b';
if(row.is_foreign)f.push(['Foreign transaction',hi]);
if(row.hour<5||row.hour>=23)f.push(['Late-night transaction ('+row.hour+':00)',hi]);
var ratio=row.amount/Math.max(row.avg_amount_30d,1);
if(ratio>=3)f.push(['Amount '+ratio.toFixed(1)+'x the 30-day average',hi]);else if(ratio>=1.5)f.push(['Amount above usual ('+ratio.toFixed(1)+'x)',md]);
if(row.distance_from_home>100)f.push(['Far from home ('+row.distance_from_home+' km)',hi]);
if(row.account_age_days<60)f.push(['New account ('+row.account_age_days+' days old)',md]);
if(row.merchant_category==='gambling'||row.merchant_category==='online')f.push(['High-risk merchant: '+row.merchant_category,md]);
if(row.n_tx_24h>6)f.push(['High velocity ('+row.n_tx_24h+' txns/24h)',md]);
return f;}
async function score(){var ids=['amount','hour','customer_age','account_age_days','n_tx_24h','avg_amount_30d','distance_from_home'];var row={};ids.forEach(function(i){row[i]=parseFloat(document.getElementById(i).value);});
row.day_of_week=parseInt(document.getElementById('day_of_week').value);row.merchant_category=document.getElementById('merchant_category').value;row.is_foreign=document.getElementById('is_foreign').checked?1:0;
var go=document.getElementById('go');go.disabled=true;var old=go.textContent;go.textContent='Scoring...';
var result=document.getElementById('result'),explain=document.getElementById('explain'),why=document.getElementById('why');
result.style.display='block';explain.className='muted';explain.textContent='Waking the model... the first request after idle can take ~10s.';why.style.display='none';
document.getElementById('pct').textContent='-';document.getElementById('fill').style.width='0';document.getElementById('badge').textContent='';
try{var res=await fetch('/predict',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({rows:[row]})});
if(!res.ok)throw new Error('HTTP '+res.status);var d=await res.json();var p=d.fraud_probability[0],fraud=d.is_fraud[0],thr=d.threshold;
var pctEl=document.getElementById('pct'),fill=document.getElementById('fill'),badge=document.getElementById('badge');
pctEl.textContent=(p*100).toFixed(1)+'%';var color=p>=thr?'#ef4444':(p>=thr*0.5?'#f59e0b':'#22c55e');
fill.style.width=Math.min(p*100,100)+'%';fill.style.background=color;pctEl.style.color=color;
document.getElementById('thr').style.left=(thr*100)+'%';
badge.textContent=fraud?'FLAGGED AS FRAUD':'LEGITIMATE';badge.style.background=fraud?'#7f1d1d':'#14532d';badge.style.color=fraud?'#fecaca':'#bbf7d0';
explain.textContent='Decision threshold '+(thr*100).toFixed(1)+'% (white marker) - at or above it the transaction is flagged for review.';
var f=drivers(row),box=document.getElementById('factors');box.innerHTML='';
if(f.length===0){box.innerHTML='<div class=\"factor\"><span class=\"dot\" style=\"background:#22c55e\"></span>No notable risk signals.</div>';}
else{f.forEach(function(x){box.innerHTML+='<div class=\"factor\"><span class=\"dot\" style=\"background:'+x[1]+'\"></span>'+x[0]+'</div>';});}
why.style.display='block';
}catch(e){explain.className='err';explain.textContent='Could not reach the model ('+e.message+'). It may be waking from idle - please try again in a few seconds.';}
finally{go.disabled=false;go.textContent=old;}}
</script></body></html>"""
