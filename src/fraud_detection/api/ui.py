"""Self-contained HTML demo UI served at the API root."""

INDEX_HTML = """<!doctype html>
<html lang=\"en\"><head><meta charset=\"utf-8\">
<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">
<title>Card Fraud Detection — Live Demo</title>
<style>
:root{--card:#1e293b;--muted:#94a3b8;--line:#334155;--accent:#38bdf8}
*{box-sizing:border-box}body{margin:0;font-family:system-ui,Segoe UI,Roboto,sans-serif;background:linear-gradient(160deg,#0b1220,#0f172a);color:#e2e8f0;min-height:100vh}
.wrap{max-width:820px;margin:0 auto;padding:32px 20px 64px}
h1{font-size:1.6rem;margin:0 0 4px}.sub{color:var(--muted);margin:0 0 24px;font-size:.95rem}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:22px;margin-bottom:20px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:14px}
label{display:block;font-size:.78rem;color:var(--muted);margin-bottom:5px}
input,select{width:100%;padding:9px 10px;border-radius:8px;border:1px solid var(--line);background:#0b1220;color:#e2e8f0;font-size:.92rem}
.row{display:flex;gap:10px;align-items:center;margin-top:18px;flex-wrap:wrap}
button{cursor:pointer;border:none;border-radius:9px;padding:11px 18px;font-weight:600;font-size:.92rem}
.primary{background:var(--accent);color:#04263a}.ghost{background:transparent;border:1px solid var(--line);color:#cbd5e1}
.check{display:flex;align-items:center;gap:8px}.check input{width:auto}
.result{display:none}
.score{font-size:3rem;font-weight:800;line-height:1}
.badge{display:inline-block;padding:6px 14px;border-radius:999px;font-weight:700;font-size:.85rem}
.meter{height:14px;border-radius:999px;background:#0b1220;border:1px solid var(--line);overflow:hidden;margin:14px 0}
.fill{height:100%;width:0;transition:width .6s ease}
.muted{color:var(--muted);font-size:.85rem}.foot{color:var(--muted);font-size:.8rem;text-align:center;margin-top:26px}
a{color:var(--accent)}
</style></head>
<body><div class=\"wrap\">
<h1>\U0001f4b3 Card Fraud Detection</h1>
<p class=\"sub\">Enter a card transaction — a LightGBM model served on GCP Cloud Run returns its fraud-risk score in real time. Try the presets to see how the risk signals change the outcome.</p>
<div class=\"card\"><div class=\"grid\">
<div><label>Amount ($)</label><input id=\"amount\" type=\"number\" value=\"920\"></div>
<div><label>Hour (0–23)</label><input id=\"hour\" type=\"number\" value=\"2\"></div>
<div><label>Day of week (0–6)</label><input id=\"day_of_week\" type=\"number\" value=\"6\"></div>
<div><label>Merchant category</label><select id=\"merchant_category\"><option>online</option><option>gambling</option><option>grocery</option><option>restaurant</option><option>travel</option><option>electronics</option><option>fuel</option></select></div>
<div><label>Customer age</label><input id=\"customer_age\" type=\"number\" value=\"31\"></div>
<div><label>Account age (days)</label><input id=\"account_age_days\" type=\"number\" value=\"12\"></div>
<div><label>Txns in last 24h</label><input id=\"n_tx_24h\" type=\"number\" value=\"9\"></div>
<div><label>Avg amount (30d)</label><input id=\"avg_amount_30d\" type=\"number\" value=\"40\"></div>
<div><label>Distance from home (km)</label><input id=\"distance_from_home\" type=\"number\" value=\"480\"></div>
<div class=\"check\"><input id=\"is_foreign\" type=\"checkbox\" checked><label style=\"margin:0\">Foreign transaction</label></div>
</div>
<div class=\"row\"><button class=\"primary\" onclick=\"score()\">Score transaction</button>
<button class=\"ghost\" onclick=\"preset('risky')\">Risky example</button>
<button class=\"ghost\" onclick=\"preset('safe')\">Typical example</button></div></div>
<div class=\"card result\" id=\"result\">
<div style=\"display:flex;justify-content:space-between;align-items:flex-end;flex-wrap:wrap;gap:10px\">
<div><div class=\"muted\">Fraud probability</div><div class=\"score\" id=\"pct\">—</div></div>
<div id=\"badge\" class=\"badge\">—</div></div>
<div class=\"meter\"><div class=\"fill\" id=\"fill\"></div></div>
<div class=\"muted\" id=\"explain\"></div></div>
<p class=\"foot\">LightGBM · imbalanced classification · threshold tuned on a validation split · <a href=\"/docs\">API docs</a> · <a href=\"https://github.com/minhazda/fraud-detection-mlops\">source</a></p>
</div>
<script>
function preset(k){var r={amount:920,hour:2,day_of_week:6,merchant_category:'online',customer_age:31,account_age_days:12,n_tx_24h:9,avg_amount_30d:40,distance_from_home:480,is_foreign:true};
var s={amount:18,hour:13,day_of_week:2,merchant_category:'grocery',customer_age:45,account_age_days:1500,n_tx_24h:2,avg_amount_30d:22,distance_from_home:3,is_foreign:false};
var v=k==='risky'?r:s;for(var key in v){var el=document.getElementById(key);if(el.type==='checkbox')el.checked=v[key];else el.value=v[key];}}
async function score(){var ids=['amount','hour','day_of_week','customer_age','account_age_days','n_tx_24h','avg_amount_30d','distance_from_home'];var row={};ids.forEach(function(i){row[i]=parseFloat(document.getElementById(i).value);});
row.merchant_category=document.getElementById('merchant_category').value;row.is_foreign=document.getElementById('is_foreign').checked?1:0;
var res=await fetch('/predict',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({rows:[row]})});
if(!res.ok){alert('Error '+res.status);return;}var d=await res.json();var p=d.fraud_probability[0],fraud=d.is_fraud[0],thr=d.threshold;
document.getElementById('result').style.display='block';var pctEl=document.getElementById('pct'),fill=document.getElementById('fill'),badge=document.getElementById('badge');
pctEl.textContent=(p*100).toFixed(1)+'%';var color=p>=thr?'#ef4444':(p>=thr*0.5?'#f59e0b':'#22c55e');
fill.style.width=Math.min(p*100,100)+'%';fill.style.background=color;pctEl.style.color=color;
badge.textContent=fraud?'⚠ FLAGGED AS FRAUD':'✓ LEGITIMATE';badge.style.background=fraud?'#7f1d1d':'#14532d';badge.style.color=fraud?'#fecaca':'#bbf7d0';
document.getElementById('explain').textContent='Decision threshold '+(thr*100).toFixed(1)+'% — probabilities at or above it are flagged for review.';}
</script></body></html>"""
