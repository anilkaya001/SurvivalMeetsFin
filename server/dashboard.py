
"""Self-contained HTML/CSS/JS dashboard template."""

DASHBOARD = r"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SurvivalMeetsFin — Drawdown Risk Monitor</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&family=DM+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root{--bg:#080c14;--card:#0e1525;--border:#1a2338;--text:#c8d6e5;--muted:#4a5568;--accent:#06d6a0;--accent2:#118ab2;--danger:#ef476f;--warn:#ffd166;--cyan:#22d3ee;--purple:#a78bfa}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--text);font-family:'DM Sans',system-ui,sans-serif;min-height:100vh;overflow-x:hidden}
code,pre,.mono{font-family:'JetBrains Mono',monospace}
.hdr{display:flex;align-items:center;gap:14px;padding:14px 24px;border-bottom:1px solid var(--border);background:linear-gradient(90deg,#080c14,#0e1525);flex-wrap:wrap}
.hdr h1{font-size:16px;font-weight:700;color:var(--cyan);letter-spacing:-.3px}
.dot{width:9px;height:9px;border-radius:50%;background:var(--muted);flex-shrink:0;transition:background .4s}
.dot.live{background:var(--accent);box-shadow:0 0 8px var(--accent);animation:blink 1.5s infinite}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.25}}
.status-txt{font-size:12px;color:var(--muted)}
.ts{font-size:11px;color:var(--muted);margin-left:auto;font-family:'JetBrains Mono',monospace}
.disclaimer{font-size:10px;color:#f97316;background:#1a0f05;border:1px solid #7c3512;
  padding:6px 24px;text-align:center;letter-spacing:.2px}
.cfg{display:flex;align-items:center;gap:10px;padding:10px 24px;background:#0a0f1a;border-bottom:1px solid var(--border);flex-wrap:wrap}
.cfg label{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.5px}
.cfg input{background:var(--card);border:1px solid var(--border);color:var(--text);padding:6px 10px;border-radius:6px;font-size:13px;width:110px;font-family:'JetBrains Mono',monospace;transition:border-color .2s}
.cfg input:focus{outline:none;border-color:var(--cyan)}
.cfg button{background:linear-gradient(135deg,var(--accent2),var(--cyan));color:#080c14;border:none;padding:7px 18px;border-radius:6px;font-size:12px;font-weight:700;cursor:pointer;text-transform:uppercase;letter-spacing:.5px;transition:opacity .2s}
.cfg button:hover{opacity:.85}.cfg button:disabled{opacity:.4;cursor:not-allowed}
.section-label{font-size:10px;font-weight:600;color:var(--muted);text-transform:uppercase;letter-spacing:.8px;padding:16px 24px 4px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(165px,1fr));gap:10px;padding:4px 24px 12px}
.card{background:var(--card);border-radius:10px;padding:14px 16px;border:1px solid var(--border);transition:border-color .4s,box-shadow .4s}
.card:hover{border-color:var(--accent2)44}
.lbl{font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:.4px;margin-bottom:6px}
.val{font-size:26px;font-weight:700;letter-spacing:-.6px;font-family:'JetBrains Mono',monospace;transition:color .4s}
.sub{font-size:11px;color:var(--muted);margin-top:4px}
.badge{display:inline-block;padding:3px 10px;border-radius:20px;font-size:11px;font-weight:700}
.surv-wrap{padding:0 24px 12px}
.surv-grid{display:grid;grid-template-columns:repeat(6,1fr);gap:8px;margin-top:8px}
.surv-box{background:var(--card);border-radius:8px;padding:10px 6px;text-align:center;border:1px solid var(--border)}
.st{font-size:9px;color:var(--muted);margin-bottom:4px;text-transform:uppercase;letter-spacing:.3px}
.sc{font-size:18px;font-weight:700;color:var(--cyan);font-family:'JetBrains Mono',monospace}
.sw{font-size:12px;font-weight:600;margin-top:2px;font-family:'JetBrains Mono',monospace}
.sw.wb{color:var(--purple)}.sw.ln{color:var(--warn)}.sw.ll{color:var(--accent)}
.charts{display:grid;grid-template-columns:1fr 1fr;gap:10px;padding:0 24px 12px}
.chart-card{background:var(--card);border-radius:10px;padding:14px 16px;border:1px solid var(--border)}
.chart-card h3{font-size:10px;font-weight:600;color:var(--muted);text-transform:uppercase;letter-spacing:.6px;margin-bottom:10px}
.tbl{width:100%;border-collapse:collapse;font-size:11px;margin-top:6px}
.tbl th{color:var(--muted);font-size:9px;font-weight:600;text-transform:uppercase;letter-spacing:.4px;text-align:left;padding:5px 6px;border-bottom:1px solid var(--border)}
.tbl td{padding:6px;border-bottom:1px solid #0a0f1a;color:var(--text);font-family:'JetBrains Mono',monospace;font-size:11px}
.tbl tr:last-child td{border:none}
.loading{display:flex;align-items:center;gap:10px;padding:20px 24px;color:var(--muted);font-size:13px}
.spin{width:14px;height:14px;border:2px solid var(--border);border-top-color:var(--cyan);border-radius:50%;animation:spin .7s linear infinite;flex-shrink:0}
@keyframes spin{to{transform:rotate(360deg)}}
.err-box{background:#2d0a0a;border:1px solid #5c1a1a;color:#fca5a5;padding:10px 24px;font-size:12px;margin:8px 24px;border-radius:8px;display:none;font-family:'JetBrains Mono',monospace}
.footer{padding:10px 24px 18px;font-size:9px;color:#1a2338;text-align:center}
@media(max-width:800px){.charts{grid-template-columns:1fr}.surv-grid{grid-template-columns:repeat(3,1fr)}.grid{grid-template-columns:repeat(auto-fit,minmax(140px,1fr))}}
</style></head><body>
<div class="hdr">
  <div class="dot" id="dot"></div>
  <h1 id="title">SurvivalMeetsFin — Drawdown Risk Monitor</h1>
  <div class="status-txt" id="status-txt"><div class="loading"><div class="spin"></div>Fitting models …</div></div>
  <span class="ts" id="ts"></span>
</div>
<div class="disclaimer">
  ⚠ Educational &amp; Research Use Only — Not Financial Advice. See DISCLAIMER.md.
</div>
<div class="cfg">
  <label>Asset</label><input id="inp-asset" value="QQQ" placeholder="e.g. SPY">
  <label>Risk Indicator</label><input id="inp-risk" value="^VIX" placeholder="e.g. ^VIX">
  <button id="btn-go" onclick="changeTickers()">Apply &amp; Refit</button>
</div>
<div class="err-box" id="err-box"></div>
<div id="main" style="display:none">
<div class="section-label">Live Snapshot</div>
<div class="grid">
  <div class="card"><div class="lbl" id="lbl-asset">Asset Price</div><div class="val" id="v-asset">—</div><div class="sub" id="s-asset"></div></div>
  <div class="card"><div class="lbl" id="lbl-risk">Risk Indicator</div><div class="val" id="v-risk">—</div><div class="sub" id="s-risk">—</div></div>
  <div class="card"><div class="lbl">Realised Vol (21d ann.)</div><div class="val" id="v-rvol">—</div><div class="sub"></div></div>
  <div class="card"><div class="lbl">Vol Spread (Impl-Real)</div><div class="val" id="v-vs">—</div><div class="sub">risk - rvol×100</div></div>
  <div class="card"><div class="lbl">20d Momentum</div><div class="val" id="v-mom">—</div><div class="sub">cum log return</div></div>
  <div class="card"><div class="lbl">Regime</div><div class="val" id="v-reg">—</div><div class="sub" id="s-reg">—</div></div>
  <div class="card" id="c-hr"><div class="lbl">Relative Hazard (Cox)</div><div class="val" id="v-hr">—</div><div class="sub"><span class="badge" id="b-risk">—</span></div></div>
  <div class="card"><div class="lbl">Linear Predictor</div><div class="val" id="v-lp">—</div><div class="sub">log-hazard vs mean</div></div>
</div>
<div class="section-label">Survival Probability — no 5% breach within …
  <span style="color:var(--cyan);margin-left:10px;font-weight:400">■ Cox</span>
  <span style="color:var(--purple);margin-left:6px;font-weight:400">■ Weibull</span>
  <span style="color:var(--warn);margin-left:6px;font-weight:400">■ LogNorm</span>
  <span style="color:var(--accent);margin-left:6px;font-weight:400">■ LogLogistic</span>
</div>
<div class="surv-wrap"><div class="surv-grid" id="surv-grid"></div></div>
<div class="charts">
  <div class="chart-card"><h3 id="ch-asset-title">Asset — last 60 sessions</h3><div style="position:relative;height:180px"><canvas id="assetChart"></canvas></div></div>
  <div class="chart-card"><h3 id="ch-risk-title">Risk — last 60 sessions</h3><div style="position:relative;height:180px"><canvas id="riskChart"></canvas></div></div>
</div>
<div class="charts">
  <div class="chart-card"><h3>Hazard Ratio — rolling ticks</h3><div style="position:relative;height:170px"><canvas id="hrChart"></canvas></div></div>
  <div class="chart-card"><h3>Cox Hazard Ratios (exp(b) with 95% CI)</h3><div style="position:relative;height:190px"><canvas id="hrForest"></canvas></div></div>
</div>
<div class="charts">
  <div class="chart-card"><h3>Model Diagnostics</h3><table class="tbl" id="diag-tbl"></table></div>
  <div class="chart-card"><h3>Cox Coefficient Table</h3><table class="tbl" id="coef-tbl"></table></div>
</div>
<div class="charts">
  <div class="chart-card" style="grid-column:1/-1"><h3>AIC / BIC Model Comparison</h3><table class="tbl" id="aic-tbl"></table></div>
</div>
</div>
<div class="footer">
  Refresh ~60 s · Cox PH (Efron) + Weibull / Log-Normal / Log-Logistic AFT · 5% drawdown breach · 2005-present<br>
  <span style="color:#f97316">Educational &amp; Research Use Only — Not Financial Advice</span>
</div>
<script>
let assetChart=null,riskChart=null,hrChart=null,hrForest=null,initialized=false;
const $=id=>document.getElementById(id);
const RC={Low:'#34d399',Mid:'#fbbf24',High:'#ef476f'};
const co={responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},
  scales:{x:{ticks:{color:'#4a5568',font:{size:8,family:'JetBrains Mono'},maxTicksLimit:8},grid:{color:'#1a2338'}},
          y:{ticks:{color:'#4a5568',font:{size:8,family:'JetBrains Mono'}},grid:{color:'#1a2338'}}}};
function changeTickers(){
  const a=$('inp-asset').value.trim()||'QQQ',r=$('inp-risk').value.trim()||'^VIX';
  $('btn-go').disabled=true;
  $('status-txt').innerHTML='<div class="loading"><div class="spin"></div>Refitting for '+a+' / '+r+' …</div>';
  $('dot').classList.remove('live');initialized=false;$('main').style.display='none';
  fetch('/api/config',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({asset:a,risk:r})}).then(()=>{$('btn-go').disabled=false}).catch(()=>{$('btn-go').disabled=false});}
function mkLine(ctx,labels,data,color,fill){
  return new Chart(ctx,{type:'line',data:{labels,datasets:[{data,borderColor:color,
    backgroundColor:fill||color+'11',borderWidth:1.8,pointRadius:0,fill:!!fill,tension:.35}]},options:co});}
function buildAsset(s){if(assetChart)assetChart.destroy();assetChart=mkLine($('assetChart').getContext('2d'),s.map(d=>d.t.slice(5)),s.map(d=>d.asset),'#22d3ee','rgba(34,211,238,.06)');}
function buildRisk(s){if(riskChart)riskChart.destroy();riskChart=mkLine($('riskChart').getContext('2d'),s.map(d=>d.t.slice(5)),s.map(d=>d.risk),'#a78bfa','rgba(167,139,250,.06)');}
function buildHr(h){if(h.length<2)return;if(hrChart)hrChart.destroy();hrChart=mkLine($('hrChart').getContext('2d'),h.map(d=>d.ts.slice(11,19)),h.map(d=>d.hr),'#06d6a0','rgba(6,214,160,.06)');}
function buildForest(m){if(!m||!m.hr)return;
  const names=['log(Risk)','RiskD5d','AssetRVol','VolSpread','Momentum','Reg:Mid','Reg:High'],hrs=m.hr;
  if(hrForest)hrForest.destroy();
  hrForest=new Chart($('hrForest').getContext('2d'),{type:'bar',
    data:{labels:names,datasets:[{data:hrs,
      backgroundColor:hrs.map(h=>h>1?'rgba(239,71,111,.55)':'rgba(6,214,160,.55)'),
      borderColor:hrs.map(h=>h>1?'#ef476f':'#06d6a0'),borderWidth:1,borderRadius:3}]},
    options:{...co,indexAxis:'y',scales:{
      x:{min:0,ticks:{color:'#4a5568',font:{size:8,family:'JetBrains Mono'}},grid:{color:'#1a2338'},
         title:{display:true,text:'Hazard Ratio',color:'#4a5568',font:{size:8}}},
      y:{ticks:{color:'#c8d6e5',font:{size:9,family:'DM Sans'}},grid:{display:false}}}}});}
function buildSurvGrid(sig){
  const h=sig.horizons||[7,14,30,60,90,180];let html='';
  h.forEach(t=>{const cx=sig.cox_surv['d'+t]??'—',wb=sig.aft_surv?.weibull?.['d'+t]??'—',
    ln=sig.aft_surv?.lognormal?.['d'+t]??'—',ll=sig.aft_surv?.loglogistic?.['d'+t]??'—';
    html+=`<div class="surv-box"><div class="st">${t}d</div><div class="sc">${cx}%</div>
      <div class="sw wb">${wb}%</div><div class="sw ln">${ln}%</div><div class="sw ll">${ll}%</div></div>`;});
  $('surv-grid').innerHTML=html;}
function updateUI(data){
  const sig=data.signal||{},mod=data.model||{},cfg=data.config||{};
  if(data.error&&data.error.trim()){$('err-box').style.display='block';$('err-box').textContent='Warning: '+data.error.slice(0,500);}
  else{$('err-box').style.display='none';}
  if(data.status==='refitting'){$('status-txt').innerHTML='<div class="loading"><div class="spin"></div>Refitting …</div>';$('dot').classList.remove('live');return;}
  if(!sig.asset_price)return;
  if(!initialized){$('main').style.display='block';
    $('status-txt').innerHTML='<span style="color:var(--accent);font-weight:700;font-size:13px">● LIVE</span><span style="color:var(--muted);font-size:11px;margin-left:8px">~60 s</span>';
    $('dot').classList.add('live');$('inp-asset').value=cfg.asset||'QQQ';$('inp-risk').value=cfg.risk||'^VIX';
    $('lbl-asset').textContent=(cfg.asset||'Asset')+' Price';$('lbl-risk').textContent=(cfg.risk||'Risk');
    $('ch-asset-title').textContent=(cfg.asset||'Asset')+' — last 60 sessions';
    $('ch-risk-title').textContent=(cfg.risk||'Risk')+' — last 60 sessions';
    $('title').textContent='SurvivalMeetsFin — '+(cfg.asset||'')+' × '+(cfg.risk||'');
    document.title=$('title').textContent;initialized=true;}
  $('ts').textContent=(sig.ts||'').replace('T',' ').slice(0,19)+' UTC';
  $('v-asset').textContent='$'+sig.asset_price.toFixed(2);
  $('v-risk').textContent=sig.risk_price.toFixed(2);$('v-risk').style.color=RC[sig.regime]||'var(--text)';
  $('s-risk').textContent='5d Δ: '+(sig.risk_chg5>=0?'+':'')+sig.risk_chg5.toFixed(1)+'%';
  const rvc=sig.rvol_pct>25?'var(--danger)':sig.rvol_pct>15?'var(--warn)':'var(--accent)';
  $('v-rvol').textContent=sig.rvol_pct.toFixed(1)+'%';$('v-rvol').style.color=rvc;
  const vsc=sig.vol_spread>10?'var(--danger)':sig.vol_spread>5?'var(--warn)':'var(--accent)';
  $('v-vs').textContent=sig.vol_spread.toFixed(1);$('v-vs').style.color=vsc;
  const mc=sig.momentum_pct<-3?'var(--danger)':sig.momentum_pct<0?'var(--warn)':'var(--accent)';
  $('v-mom').textContent=(sig.momentum_pct>=0?'+':'')+sig.momentum_pct.toFixed(1)+'%';$('v-mom').style.color=mc;
  $('v-reg').textContent=sig.regime;$('v-reg').style.color=RC[sig.regime]||'var(--text)';
  $('s-reg').textContent=sig.regime==='Low'?'Risk < 15':sig.regime==='Mid'?'15 ≤ Risk ≤ 25':'Risk > 25';
  $('v-hr').textContent=sig.rel_hazard.toFixed(3)+'x';$('v-hr').style.color=sig.risk_col;
  $('c-hr').style.borderColor=sig.risk_col+'44';$('c-hr').style.boxShadow='0 0 12px '+sig.risk_col+'18';
  $('b-risk').textContent=sig.risk_level;$('b-risk').style.background=sig.risk_col+'22';$('b-risk').style.color=sig.risk_col;
  const lp=sig.linear_pred;$('v-lp').textContent=(lp>=0?'+':'')+lp.toFixed(3);$('v-lp').style.color=lp>0?'var(--danger)':'var(--accent)';
  buildSurvGrid(sig);
  if(sig.spark){buildAsset(sig.spark);buildRisk(sig.spark);}
  if(data.history&&data.history.length>1)buildHr(data.history);
  if(mod&&mod.n_ep){buildForest(mod);
    $('diag-tbl').innerHTML='<tr><th>Metric</th><th>Value</th></tr>'
      +[['Episodes',mod.n_ep],['Events (breaches)',mod.n_ev+' ('+mod.breach_rate+'%)'],
        ['Cox LRT χ²',mod.lrt_stat],['Cox LRT p',mod.lrt_p],['Concordance C',mod.c_index],
        ['Log-rank χ² Low vs High (1df)',mod.pw_lr_stat],['  p-value',mod.pw_lr_p],
        ['Log-rank χ² 3-group (2df)',mod.g3_lr_stat],['  p-value',mod.g3_lr_p],
        ['Best AIC model',mod.aic_winner]]
       .map(([l,v])=>'<tr><td>'+l+'</td><td style="text-align:right;font-weight:600">'+v+'</td></tr>').join('');
    if(mod.coef_names){let ct='<tr><th>Covariate</th><th>β</th><th>SE</th><th>HR</th><th>p</th></tr>';
      mod.coef_names.forEach((n,i)=>{const p=mod.coef_pval[i];
        const pc=p<.01?'var(--accent)':p<.05?'var(--warn)':'var(--muted)';
        ct+='<tr><td>'+n+'</td><td>'+mod.coefs[i]+'</td><td>'+mod.coef_se[i]+'</td><td>'+mod.hr[i]+'</td><td style="color:'+pc+'">'+p+'</td></tr>';});
      $('coef-tbl').innerHTML=ct;}
    if(mod.aft_aic){let at='<tr><th>Model</th><th>AIC</th><th>BIC</th><th></th></tr>';
      for(const[n,a]of Object.entries(mod.aft_aic)){const b=mod.aft_bic[n];
        const win=n.charAt(0).toUpperCase()+n.slice(1)===mod.aic_winner;
        at+='<tr><td>'+n.charAt(0).toUpperCase()+n.slice(1)+'</td><td>'+a+'</td><td>'+b+'</td><td>'+(win?'<span style="color:var(--accent)">★ Best</span>':'')+'</td></tr>';}
      $('aic-tbl').innerHTML=at;}}}
const es=new EventSource('/api/stream');
es.onmessage=e=>{try{updateUI(JSON.parse(e.data))}catch(err){console.error(err)}};
es.onerror=()=>{$('status-txt').innerHTML='<span style="color:var(--danger)">Connection lost — retrying …</span>'};
fetch('/api/signal').then(r=>r.json()).then(updateUI).catch(()=>{});
</script></body></html>"""
