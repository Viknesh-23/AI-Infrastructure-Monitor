(() => {
  if (typeof Chart === 'undefined') return;
  const colors = { blue:'#5b6dfb', cyan:'#27a9e8', green:'#25ae76', amber:'#efaa25', red:'#e8495f', purple:'#9869e8' };
  const grid = { color: 'rgba(130,145,170,.15)' };
  const common = { responsive:true, maintainAspectRatio:false, plugins:{ legend:{ labels:{ boxWidth:10, usePointStyle:true } } }, scales:{ x:{ grid:{ display:false } }, y:{ beginAtZero:true, grid } } };
  const canvas = (id) => document.getElementById(id);
  const overview = canvas('overviewChart');
  if (overview && window.dashboardChartData) {
    const d = window.dashboardChartData;
    new Chart(overview, { type:'bar', data:{ labels:d.map(x=>x.name), datasets:[{ label:'CPU usage %', data:d.map(x=>x.cpu), backgroundColor:colors.blue, borderRadius:5 },{ label:'Memory usage %', data:d.map(x=>x.memory), backgroundColor:colors.cyan, borderRadius:5 }] }, options:{...common, scales:{...common.scales, y:{...common.scales.y, max:100}} });
  }
  const fetchHistory = async (element) => { const r = await fetch(element.dataset.historyUrl); return r.ok ? r.json() : null; };
  const performance = canvas('serverPerformanceChart');
  const capacity = canvas('capacityChart');
  const risk = canvas('riskChart');
  if (performance) fetchHistory(performance).then(d => { if (!d) return; new Chart(performance, { type:'line', data:{labels:d.labels,datasets:[{label:'CPU %',data:d.cpu,borderColor:colors.blue,tension:.35,pointRadius:1.5},{label:'Memory %',data:d.memory,borderColor:colors.cyan,tension:.35,pointRadius:1.5}]},options:{...common,scales:{...common.scales,y:{...common.scales.y,max:100}}})); });
  if (capacity) fetchHistory(capacity).then(d => { if (!d) return; new Chart(capacity, { type:'line', data:{labels:d.labels,datasets:[{label:'Disk usage %',data:d.disk,borderColor:colors.purple,tension:.35,pointRadius:1.5,yAxisID:'y'},{label:'Latency ms',data:d.latency,borderColor:colors.amber,tension:.35,pointRadius:1.5,yAxisID:'y1'}]},options:{...common,scales:{x:common.scales.x,y:{beginAtZero:true,position:'left',grid},y1:{beginAtZero:true,position:'right',grid:{drawOnChartArea:false}}}}})); });
  if (risk) fetchHistory(risk).then(d => { if (!d) return; new Chart(risk, { type:'line', data:{labels:d.labels,datasets:[{label:'Failure risk %',data:d.risk,borderColor:colors.red,backgroundColor:'rgba(232,73,95,.13)',fill:true,tension:.35,pointRadius:1.5}]},options:{...common,scales:{...common.scales,y:{...common.scales.y,max:100}}})); });
  if (window.analyticsData) {
    const d = window.analyticsData;
    const severity = canvas('severityChart'); if (severity) new Chart(severity,{type:'doughnut',data:{labels:['Low','Medium','High','Critical'],datasets:[{data:['Low','Medium','High','Critical'].map(x=>d.severity[x]||0),backgroundColor:[colors.green,colors.amber,'#f18140',colors.red],borderWidth:0}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'bottom'}}}});
    const server = canvas('serverIncidentChart'); if (server) new Chart(server,{type:'bar',data:{labels:d.servers.map(x=>x[0]),datasets:[{label:'Incidents',data:d.servers.map(x=>x[1]),backgroundColor:colors.blue,borderRadius:5}]},options:common});
    const status = canvas('statusChart'); if (status) new Chart(status,{type:'pie',data:{labels:['Open','Investigating','Resolved'],datasets:[{data:['Open','Investigating','Resolved'].map(x=>d.status[x]||0),backgroundColor:[colors.red,colors.amber,colors.green],borderWidth:0}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'bottom'}}}});
  }
})();
