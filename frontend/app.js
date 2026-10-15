// PulseYT — YouTube SEO Strategy & Prediction Studio Client Engine

let currentPlanData = null;
let currentRawMarkdown = '';
let isAnalyzing = false;
let executionTimer = null;
let executionStartTime = 0;
let currentUser = null;
let pendingAuthEmail = '';

// DOM Selectors
const topicInput = document.getElementById('topicInput');
const clearTopicBtn = document.getElementById('clearTopicBtn');
const topSearchForm = document.getElementById('topSearchForm');
const quickPredictBtn = document.getElementById('quickPredictBtn');
const launchCrewBtn = document.getElementById('launchCrewBtn');
const modelSelect = document.getElementById('modelSelect');
const headerEngineBadge = document.getElementById('headerEngineBadge');
const currentTopicTitle = document.getElementById('currentTopicTitle');
const topicSubtitle = document.getElementById('topicSubtitle');
const refreshLiveYtBtn = document.getElementById('refreshLiveYtBtn');

// Modal Elements
const executionModal = document.getElementById('executionModal');
const modalElapsed = document.getElementById('modalElapsed');
const modalStatusText = document.getElementById('modalStatusText');

// Notification Toast
function showToast(message, type = 'success') {
  const container = document.getElementById('toastContainer');
  const toast = document.createElement('div');
  toast.className = `toast px-4 py-3 rounded-xl border text-xs font-medium flex items-center gap-2 shadow-2xl backdrop-blur-xl ${
    type === 'success' 
      ? 'bg-surface-card/95 border-emerald-500/50 text-emerald-300' 
      : 'bg-surface-card/95 border-rose-500/50 text-rose-300'
  }`;
  toast.innerHTML = `
    <span class="material-symbols-outlined text-[16px]">${type === 'success' ? 'check_circle' : 'error'}</span>
    <span>${escapeHTML(message)}</span>
  `;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(8px)';
    toast.style.transition = 'all 0.25s ease';
    setTimeout(() => toast.remove(), 250);
  }, 2500);
}

// Client Markdown Formatter
function renderMarkdown(md) {
  if (!md) return '<p class="text-on-surface-muted italic">No report available yet.</p>';
  let html = escapeHTML(md)
    .replace(/^### (.*$)/gim, '<h3>$1</h3>')
    .replace(/^## (.*$)/gim, '<h2>$1</h2>')
    .replace(/^# (.*$)/gim, '<h1>$1</h1>')
    .replace(/^\> (.*$)/gim, '<blockquote>$1</blockquote>')
    .replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/gim, '<em>$1</em>')
    .replace(/```([\s\S]*?)```/gim, '<pre><code>$1</code></pre>')
    .replace(/`([^`]+)`/gim, '<code>$1</code>')
    .replace(/\[([^\]]+)\]\(([^)]+)\)/gim, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>')
    .replace(/\n\n/gim, '</p><p>')
    .replace(/^\* (.*$)/gim, '<li>$1</li>');

  // Tables
  html = html.replace(/\|(.+)\|/gim, (match) => {
    const cells = match.split('|').filter(c => c.trim().length > 0);
    if (cells[0].includes('---')) return '';
    const tds = cells.map(c => `<td>${c.trim()}</td>`).join('');
    return `<tr>${tds}</tr>`;
  });

  return `<p>${html}</p>`;
}

// Number Formatter
function formatNum(n) {
  if (n === null || n === undefined || isNaN(n)) return 'N/A';
  return Number(n).toLocaleString();
}

// Workflow Navigation (Smooth Scroll & Step Highlight)
document.querySelectorAll('.wf-step-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const targetId = btn.dataset.target;
    const targetEl = document.getElementById(targetId);
    if (targetEl) {
      document.querySelectorAll('.wf-step-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      targetEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});

// Update the Entire Dashboard
function updateDashboard(data, competitors, rawMd) {
  currentPlanData = data;
  currentRawMarkdown = rawMd || data.raw_markdown || '';

  const topic = data.topic || topicInput.value.trim() || 'No analysis yet';
  currentTopicTitle.textContent = topic;
  topicSubtitle.textContent = 'Public YouTube results and agent-generated strategy for ' + topic + '. Estimates appear only when supported by available data.';

  document.getElementById('opportunityScore').textContent = 'Unavailable';
  document.getElementById('targetCtr').textContent = 'Unavailable';
  document.getElementById('targetRetention').textContent = 'Unavailable';
  document.getElementById('tier1Seed').textContent = 'Unavailable';
  document.getElementById('tier2Mid').textContent = 'Unavailable';
  document.getElementById('tier3Authority').textContent = 'Unavailable';
  document.getElementById('statCompCount').textContent = '0 public videos';
  document.getElementById('statMedianViews').textContent = 'N/A';
  document.getElementById('statAvgViews').textContent = 'N/A';
  document.getElementById('statTopViews').textContent = 'N/A';

  // 1. WHAT THE AI PREDICTS
  // Public search data does not expose CTR, retention, or future view counts.

  // 2. HOW THE AI PREDICTS IT
  const stats = data.stats || {};
  const vids = competitors || data.competitors || [];
  document.getElementById('statCompCount').textContent = `${vids.length} public videos`;
  
  if (stats.median_views) {
    document.getElementById('statMedianViews').textContent = stats.median_views;
    document.getElementById('statAvgViews').textContent = stats.avg_views || 'N/A';
    document.getElementById('statTopViews').textContent = stats.top_views || stats.viral_ceiling || 'N/A';
  } else if (vids.length) {
    const rawViews = vids.map(v => parseInt(v.views)).filter(v => !isNaN(v)).sort((a,b)=>a-b);
    if (rawViews.length) {
      const med = rawViews[Math.floor(rawViews.length/2)];
      const avg = Math.round(rawViews.reduce((a,b)=>a+b,0)/rawViews.length);
      const top = rawViews[rawViews.length-1];
      document.getElementById('statMedianViews').textContent = formatNum(med);
      document.getElementById('statAvgViews').textContent = formatNum(avg);
      document.getElementById('statTopViews').textContent = formatNum(top);
    }
  }

  const methodology = data.prediction_methodology || [];
  const methodologyGrid = document.getElementById('predictionMethodologyGrid');
  const evidenceSteps = methodology.map(function (item) { return item.detail || item.step || ''; });
  if (data.data_limitations) evidenceSteps.push(data.data_limitations);
  if (!evidenceSteps.length && vids.length) evidenceSteps.push('Observed public search results; counts can change and are not a forecast.');
  methodologyGrid.innerHTML = evidenceSteps.slice(0, 3).map(function (detail) {
    return '<div class="p-3 rounded-xl bg-surface-low border border-surface-border/60 text-xs text-on-surface-muted">' +
      escapeHTML(detail) + '</div>';
  }).join('') || '<p class="text-xs text-on-surface-muted">Data limitations and analysis notes will appear here.</p>';


  // 3. WORKFLOW STEP 1: RESEARCH
  const research = data.research || {};
  if (research.persona_name) document.getElementById('researchPersonaTitle').textContent = research.persona_name;
  if (research.demographics) document.getElementById('researchDemographics').textContent = research.demographics;

  const drivers = research.emotional_drivers || [];
  if (drivers.length) {
    document.getElementById('researchDriversList').innerHTML = drivers.map((d, idx) => `
      <li class="p-3 rounded-xl bg-surface-low border border-surface-border/60">
        <strong class="text-xs text-white block mb-1">${idx + 1}. ${escapeHTML(d.title)}</strong>
        <p class="text-[11px] text-on-surface-muted">${escapeHTML(d.desc)}</p>
      </li>
    `).join('');
  }

  // 4. WORKFLOW STEP 2: COMPETITOR ANALYSIS
  populateCompetitorsTable(vids);
  const gaps = data.competitor_gaps || [];
  if (gaps.length) {
    document.getElementById('competitorGapsGrid').innerHTML = gaps.map(g => `
      <div class="p-3.5 rounded-xl bg-surface-low border border-surface-border/70 flex flex-col gap-1.5">
        <div class="text-xs font-bold text-accent-rose flex items-center gap-1">✕ ${escapeHTML(g.gap)}</div>
        <p class="text-xs text-on-surface-muted">${escapeHTML(g.fix)}</p>
      </div>
    `).join('');
  }

  // 5. WORKFLOW STEP 3: KEYWORDS
  const kws = data.keywords || {};
  const renderKwList = (elId, list) => {
    const el = document.getElementById(elId);
    if (!list || !list.length) {
      el.innerHTML = '<li class="text-on-surface-muted italic text-[11px]">No queries extracted</li>';
      return;
    }
    el.innerHTML = list.map(q => `
      <li class="flex items-center justify-between p-2 rounded-lg bg-surface-low border border-surface-border/60 hover:border-primary/50 transition-all group">
        <span class="truncate">${escapeHTML(q)}</span>
        <button class="copy-query-btn opacity-0 group-hover:opacity-100 text-primary-bright hover:text-white" data-copy="${escapeHTML(q)}">
          <span class="material-symbols-outlined text-[13px]">content_copy</span>
        </button>
      </li>
    `).join('');
  };
  renderKwList('kwInfoList', kws.informational || data.top_keywords?.slice(0, 4) || []);
  renderKwList('kwTutorialList', kws.tutorial || data.top_keywords?.slice(2, 6) || []);
  renderKwList('kwCompList', kws.comparison || data.top_keywords?.slice(4, 8) || []);
  renderKwList('kwTroubleList', kws.troubleshooting || data.top_keywords?.slice(6, 10) || []);

  document.querySelectorAll('.copy-query-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      navigator.clipboard.writeText(btn.dataset.copy);
      showToast('Keyword copied!');
    });
  });

  // 6. WORKFLOW STEP 5: FINAL STRATEGY PLAN
  populateConcepts(data.concepts || data.instant_concepts || []);
  populatePackaging(data.packaging || []);
  populateCalendar(data.launch_calendar || []);

  // Markdown viewer
  document.getElementById('fullReportViewer').innerHTML = renderMarkdown(currentRawMarkdown);
}

// Populate Live Competitor Table
function populateCompetitorsTable(videos) {
  const tbody = document.getElementById('competitorTableBody');
  if (!videos || !videos.length) {
    tbody.innerHTML = '<tr><td colspan="5" class="py-6 text-center text-on-surface-muted">No competitor videos found.</td></tr>';
    return;
  }
  tbody.innerHTML = videos.map(function (video) {
    const url = safeUrl(video.url);
    const title = escapeHTML(video.title || 'Untitled');
    const channel = escapeHTML(video.channel || 'Channel not provided');
    const published = escapeHTML(video.published_at ? String(video.published_at).substring(0, 10) : 'Unavailable');
    const views = escapeHTML(formatNum(video.views));
    const likes = escapeHTML(formatNum(video.likes));
    return '<tr class="hover:bg-surface-high/40 transition-colors">' +
      '<td class="py-3 px-4"><a href="' + url + '" target="_blank" rel="noopener noreferrer" class="font-medium text-white hover:text-accent-cyan">' +
      title + '</a><div class="text-[11px] text-on-surface-muted mt-1">' + channel + '</div></td>' +
      '<td class="py-3 px-4 text-right text-accent-cyan font-semibold">' + views + '</td>' +
      '<td class="py-3 px-4 text-right text-on-surface-muted">' + likes + '</td>' +
      '<td class="py-3 px-4 text-center text-on-surface-muted">' + published + '</td>' +
      '<td class="py-3 px-4 text-center"><a href="' + url + '" target="_blank" rel="noopener noreferrer" aria-label="Open YouTube video" class="p-1 rounded text-primary-bright hover:bg-surface-border inline-block">↗</a></td>' +
      '</tr>';
  }).join('');
}

// Populate Concepts
function populateConcepts(concepts) {
  const container = document.getElementById('strategyConceptsList');
  if (!concepts || !concepts.length) {
    container.innerHTML = `<div class="p-6 text-center text-on-surface-muted bg-surface-card rounded-2xl">No video concepts generated yet.</div>`;
    return;
  }

  container.innerHTML = concepts.map((c, idx) => {
    const hooks = (c.hook_timeline || []).map(h => `
      <div class="flex items-start gap-2 text-xs">
        <span class="font-mono font-bold text-accent-cyan bg-surface-low px-1.5 py-0.5 rounded text-[10px] shrink-0">${escapeHTML(h.time)}</span>
        <span class="text-white">${escapeHTML(h.description)}</span>
      </div>
    `).join('');

    return `
      <div class="p-5 rounded-2xl bg-surface-card border border-surface-border flex flex-col gap-3 shadow-md">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-surface-border/50 pb-2.5">
          <div class="flex items-center gap-2">
            <span class="w-6 h-6 rounded-lg bg-primary/20 text-primary-bright font-bold text-xs flex items-center justify-center">0${idx + 1}</span>
            <h4 class="font-headline text-base font-bold text-white">${escapeHTML(c.working_title || c.title || c.name)}</h4>
          </div>
          <span class="px-2 py-0.5 rounded-full bg-accent-cyan/15 text-accent-cyan border border-accent-cyan/30 text-[11px] font-semibold self-start sm:self-auto">
            ${escapeHTML(c.retention_potential || c.retention || 'No retention estimate')}
          </span>
        </div>

        <div class="text-xs text-on-surface-muted leading-relaxed">
          <strong class="text-white">Content Angle:</strong> ${escapeHTML(c.angle || 'Curiosity Hook Framework')}
        </div>

        ${hooks ? `
          <div class="bg-surface-low p-3.5 rounded-xl border border-surface-border/60 flex flex-col gap-2">
            <div class="text-[10px] uppercase font-bold text-primary-bright tracking-wider">30-Second Drop-Off Defense Hook</div>
            <div class="flex flex-col gap-1.5 mt-0.5">${hooks}</div>
          </div>
        ` : (c.hook ? `
          <div class="bg-surface-low p-3 rounded-xl border border-surface-border/60 text-xs">
            <strong class="text-primary-bright block text-[10px] uppercase font-bold mb-1">30-Second Hook:</strong>
            <span class="text-white">${escapeHTML(c.hook)}</span>
          </div>
        ` : '')}

        ${c.takeaway ? `
          <div class="text-xs text-on-surface-muted flex items-center gap-1.5 pt-1">
            <span class="material-symbols-outlined text-[14px] text-accent-emerald">verified</span>
            <span><strong>Viewer Takeaway:</strong> ${escapeHTML(c.takeaway)}</span>
          </div>
        ` : ''}
      </div>
    `;
  }).join('');
}

// Populate Packaging
function populatePackaging(pkgList) {
  const container = document.getElementById('strategyPackagingList');
  if (!pkgList || !pkgList.length) {
    container.innerHTML = `<div class="p-6 text-center text-on-surface-muted bg-surface-card rounded-2xl">No packaging packages generated yet.</div>`;
    return;
  }

  container.innerHTML = pkgList.map((pkg, idx) => `
    <div class="p-5 rounded-2xl bg-surface-card border border-surface-border flex flex-col gap-4 shadow-md">
      <div class="flex items-center justify-between border-b border-surface-border/50 pb-2">
        <span class="font-headline font-bold text-white text-sm">Packaging Suite 0${idx + 1}</span>
        <span class="text-xs font-mono text-on-surface-muted">No CTR forecast available</span>
      </div>

      <!-- 3 Titles -->
      <div class="flex flex-col gap-2">
        <div class="p-2.5 rounded-xl bg-surface-low border border-surface-border/60 flex items-center justify-between gap-3">
          <div>
            <span class="text-[10px] font-bold uppercase text-accent-cyan bg-accent-cyan/15 px-1.5 py-0.5 rounded">Curiosity Hook</span>
            <div class="text-xs text-white font-medium mt-1">${escapeHTML(pkg.titles?.curiosity || 'Title variant')}</div>
          </div>
          <button class="copy-title-btn text-on-surface-muted hover:text-white p-1" data-copy="${pkg.titles?.curiosity || ''}">
            <span class="material-symbols-outlined text-[15px]">content_copy</span>
          </button>
        </div>

        <div class="p-2.5 rounded-xl bg-surface-low border border-surface-border/60 flex items-center justify-between gap-3">
          <div>
            <span class="text-[10px] font-bold uppercase text-accent-emerald bg-accent-emerald/15 px-1.5 py-0.5 rounded">Direct Value</span>
            <div class="text-xs text-white font-medium mt-1">${escapeHTML(pkg.titles?.direct_value || 'Title variant')}</div>
          </div>
          <button class="copy-title-btn text-on-surface-muted hover:text-white p-1" data-copy="${pkg.titles?.direct_value || ''}">
            <span class="material-symbols-outlined text-[15px]">content_copy</span>
          </button>
        </div>

        <div class="p-2.5 rounded-xl bg-surface-low border border-surface-border/60 flex items-center justify-between gap-3">
          <div>
            <span class="text-[10px] font-bold uppercase text-primary-bright bg-primary/20 px-1.5 py-0.5 rounded">Contrarian</span>
            <div class="text-xs text-white font-medium mt-1">${escapeHTML(pkg.titles?.contrarian || 'Title variant')}</div>
          </div>
          <button class="copy-title-btn text-on-surface-muted hover:text-white p-1" data-copy="${pkg.titles?.contrarian || ''}">
            <span class="material-symbols-outlined text-[15px]">content_copy</span>
          </button>
        </div>
      </div>

      <!-- Thumbnail Overlay Spec -->
      <div class="p-3 rounded-xl bg-surface-low border border-surface-border/60 flex items-center justify-between text-xs">
        <div class="flex items-center gap-2">
          <span class="material-symbols-outlined text-accent-amber text-[18px]">palette</span>
          <span class="text-on-surface-muted">Thumbnail Visual Overlay:</span>
        </div>
        <span class="font-headline font-bold text-accent-amber bg-accent-amber/20 px-2 py-0.5 rounded text-xs border border-accent-amber/40">
          ${escapeHTML(pkg.overlay_text || '100% FREE')}
        </span>
      </div>
    </div>
  `).join('');

  document.querySelectorAll('.copy-title-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      navigator.clipboard.writeText(btn.dataset.copy);
      showToast('Title copied to clipboard!');
    });
  });
}

// Populate Calendar
function populateCalendar(days) {
  const container = document.getElementById('strategyCalendarGrid');
  if (!days || !days.length) {
    container.innerHTML = `<div class="p-4 text-center text-on-surface-muted col-span-7">Calendar unavailable</div>`;
    return;
  }

  container.innerHTML = days.map(d => `
    <div class="p-3 rounded-xl bg-surface-low border border-surface-border/70 flex flex-col justify-between">
      <div>
        <div class="text-[10px] font-bold text-accent-cyan uppercase tracking-wider">${escapeHTML(d.day)}</div>
        <div class="text-xs font-bold text-white mt-0.5">${escapeHTML(d.phase)}</div>
        <p class="text-[11px] text-on-surface-muted mt-1 leading-snug">${escapeHTML(d.task)}</p>
      </div>
    </div>
  `).join('');
}

// Health Check
async function fetchHealth() {
  try {
    const res = await fetch('/api/health');
    const data = await res.json();
    if (data.model) {
      headerEngineBadge.textContent = data.model.replace('gemini/', '').replace('google/', '');
      modelSelect.value = data.model;
      const runtime = document.getElementById('landingRuntime');
      if (runtime) runtime.textContent = 'CrewAI Multi-Agent · ' + data.model;
    }
    const serviceStatus = document.getElementById('serviceStatus');
    if (serviceStatus) {
      const services = ['Web API online'];
      services.push(data.ollama_connected ? 'Ollama online' : 'Ollama unavailable');
      services.push(data.youtube_connected ? 'YouTube API connected' : 'YouTube API not configured');
      serviceStatus.textContent = services.join(' · ');
    }
  } catch {
    headerEngineBadge.textContent = 'Server Online';
  }
}

// Load Saved Report
async function fetchSavedReport() {
  try {
    const res = await fetch('/api/report');
    if (!res.ok) return;
    const json = await res.json();
    topicInput.value = json.topic || 'AI tools for college students';
    updateDashboard(json.data || {}, json.competitors || [], json.report || '');
  } catch (err) {
    console.log('No saved report.');
  }
}

// Quick Predict Action
async function handleQuickPredict() {
  if (!currentUser) { openAuth('login'); return; }
  const topic = topicInput.value.trim();
  if (!topic) return;

  quickPredictBtn.disabled = true;
  quickPredictBtn.innerHTML = '<span class="material-symbols-outlined text-[16px] animate-spin">sync</span><span>Analyzing...</span>';

  try {
    const res = await fetch('/api/quick-predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Quick prediction failed');

    updateDashboard(data, data.competitors, '');
    showToast(`Predictions updated for "${topic}"!`);
  } catch (err) {
    showToast(err.message || 'Quick predict failed', 'error');
  } finally {
    quickPredictBtn.disabled = false;
    quickPredictBtn.innerHTML = '<span class="material-symbols-outlined text-[16px]">bolt</span><span>Instant Predict</span>';
  }
}

// 6-Agent Deep AI Run Action
function updateModalProgress(elapsedSeconds) {
  modalElapsed.textContent = elapsedSeconds + 's';
  modalStatusText.querySelector('span:last-child').textContent =
    'CrewAI is processing the request. Individual agent progress is not streamed by this backend.';
}

async function handleRunCrew() {
  if (!currentUser) { openAuth('login'); return; }
  if (isAnalyzing) return;
  const topic = topicInput.value.trim();
  if (!topic) return;

  isAnalyzing = true;
  executionStartTime = Date.now();
  executionModal.classList.remove('hidden');

  for (let i = 1; i <= 6; i++) {
    const badge = document.getElementById(`stageStep${i}`).querySelector('.stage-badge');
    badge.textContent = 'Status unavailable';
    badge.className = 'stage-badge text-[11px] text-on-surface-muted font-medium';
  }


  executionTimer = setInterval(() => {
    const sec = Math.floor((Date.now() - executionStartTime) / 1000);
    updateModalProgress(sec);
  }, 1000);

  try {
    const res = await fetch('/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        topic,
        model: modelSelect.value 
      })
    });
    const json = await res.json();
    if (!res.ok) throw new Error(json.detail || json.error || 'Execution failed');

    updateDashboard(json.data || {}, json.competitors || [], json.report || '');
    showToast('6-Agent Strategy Blueprint generated successfully!');
  } catch (err) {
    showToast(err.message || 'Workflow error', 'error');
  } finally {
    isAnalyzing = false;
    clearInterval(executionTimer);
    executionModal.classList.add('hidden');
  }
}

// Event Listeners
quickPredictBtn.addEventListener('click', handleQuickPredict);
launchCrewBtn.addEventListener('click', handleRunCrew);
refreshLiveYtBtn.addEventListener('click', handleQuickPredict);

topSearchForm.addEventListener('submit', (e) => {
  e.preventDefault();
  handleQuickPredict();
});

clearTopicBtn.addEventListener('click', () => {
  topicInput.value = '';
  topicInput.focus();
});

modelSelect.addEventListener('change', async () => {
  const selected = modelSelect.value;
  try {
    await fetch('/api/model', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model: selected })
    });
    headerEngineBadge.textContent = selected.replace('gemini/', '').replace('google/', '');
    showToast(`Switched engine to ${selected}`);
  } catch {
    showToast('Error switching engine', 'error');
  }
});

// Copy & Download Actions
document.getElementById('copyMdBtn').addEventListener('click', () => {
  if (!currentRawMarkdown) return;
  navigator.clipboard.writeText(currentRawMarkdown);
  showToast('Raw Markdown copied!');
});

document.getElementById('downloadMdBtn').addEventListener('click', () => {
  if (!currentRawMarkdown) return;
  const blob = new Blob([currentRawMarkdown], { type: 'text/markdown;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `YouTube_SEO_Plan_${Date.now()}.md`;
  a.click();
  URL.revokeObjectURL(url);
  showToast('Exported Markdown file!');
});

document.getElementById('copyTagsBtn').addEventListener('click', () => {
  const tags = (currentPlanData?.candidate_tags || []).join(', ');
  if (!tags) { showToast('No tags were returned by the analysis.', 'error'); return; }
  navigator.clipboard.writeText(tags);
  showToast('Tags copied to clipboard!');
});

// Initialization
fetchHealth();
initializeAuth();


function safeUrl(value) {
  try {
    const url = new URL(value || '', window.location.origin);
    return (url.protocol === 'http:' || url.protocol === 'https:') ? escapeHTML(url.href) : '#';
  } catch (error) { return '#'; }
}

function escapeHTML(value) {
  return String(value == null ? '' : value).replace(/[&<>"']/g, function (character) {
    return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[character];
  });
}

function openAuth(view) {
  document.getElementById('authModal').classList.remove('hidden');
  showAuthView(view || 'login');
}
function showAuthView(view) {
  ['Login', 'Signup', 'Verify', 'Forgot', 'Reset'].forEach(function (name) {
    document.getElementById('authView' + name)?.classList.toggle('hidden', name.toLowerCase() !== view);
  });
  if (view === 'verify') document.getElementById('verifyEmailDisplay').textContent = pendingAuthEmail;
}
async function authRequest(path, payload) {
  const response = await fetch(path, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload || {}), credentials: 'same-origin'
  });
  const body = await response.json().catch(function () { return {}; });
  if (!response.ok) throw new Error(body.error || body.detail || 'Request failed. Please try again.');
  return body;
}
function setSignedIn(user) {
  currentUser = user || null;
  document.body.classList.toggle('is-authenticated', Boolean(currentUser));
  document.getElementById('studioDashboardView')?.classList.toggle('hidden', !currentUser);
  document.getElementById('guestControls')?.classList.toggle('hidden', Boolean(currentUser));
  document.getElementById('userControls')?.classList.toggle('hidden', !currentUser);
  if (currentUser) {
    const name = currentUser.full_name || currentUser.email || 'Creator';
    document.getElementById('userNameLabel').textContent = name;
    document.getElementById('userDropdownName').textContent = name;
    document.getElementById('userDropdownEmail').textContent = currentUser.email || '';
    document.getElementById('userAvatar').textContent = name.trim().charAt(0).toUpperCase();
    loadHistory();
    fetchSavedReport();
  }
}
async function initializeAuth() {
  try {
    const response = await fetch('/api/auth/me', { credentials: 'same-origin' });
    const result = await response.json();
    if (result.authenticated) {
      setSignedIn(result.user);
      await fetchSavedReport();
    }
  } catch (error) { console.error('Could not restore sign-in session.', error); }
}

async function submitLandingResearch() {
  const input = document.getElementById('landingQuickInput');
  const topic = input.value.trim();
  if (!topic) { showToast('Enter a topic to research.', 'error'); input.focus(); return; }
  topicInput.value = topic;
  if (!currentUser) { openAuth('login'); return; }
  document.querySelector('.dashboard-shell')?.scrollIntoView({ behavior: 'smooth' });
  await handleQuickPredict();
}
document.getElementById('landingQuickBtn')?.addEventListener('click', submitLandingResearch);
document.getElementById('landingQuickInput')?.addEventListener('keydown', function (event) {
  if (event.key === 'Enter') { event.preventDefault(); submitLandingResearch(); }
});

document.getElementById('openLoginBtn')?.addEventListener('click', function () { openAuth('login'); });
document.getElementById('openSignupBtn')?.addEventListener('click', function () { openAuth('signup'); });
document.getElementById('closeAuthModalBtn')?.addEventListener('click', function () {
  document.getElementById('authModal').classList.add('hidden');
});
document.getElementById('switchToSignupBtn')?.addEventListener('click', function () { showAuthView('signup'); });
document.getElementById('switchToLoginBtn')?.addEventListener('click', function () { showAuthView('login'); });
document.getElementById('switchToForgotBtn')?.addEventListener('click', function () {
  document.getElementById('forgotEmail').value = document.getElementById('loginEmail').value;
  showAuthView('forgot');
});
document.getElementById('backToLoginFromForgot')?.addEventListener('click', function () { showAuthView('login'); });


document.getElementById('signupForm')?.addEventListener('submit', async function (event) {
  event.preventDefault();
  const button = document.getElementById('submitSignupBtn');
  button.disabled = true;
  try {
    const result = await authRequest('/api/auth/signup', {
      full_name: document.getElementById('signupName').value.trim(),
      email: document.getElementById('signupEmail').value.trim(),
      password: document.getElementById('signupPassword').value
    });
    pendingAuthEmail = result.email;
    showAuthView('verify');
    if (result.dev_code) {
      document.getElementById('devCodeBanner').classList.remove('hidden');
      document.getElementById('devCodeValue').textContent = result.dev_code;
    }
    showToast(result.message || 'Check your email for a verification code.');
  } catch (error) { showToast(error.message, 'error'); }
  finally { button.disabled = false; }
});
document.getElementById('verifyForm')?.addEventListener('submit', async function (event) {
  event.preventDefault();
  try {
    const result = await authRequest('/api/auth/verify-email', {
      email: pendingAuthEmail, code: document.getElementById('verifyCodeInput').value.trim()
    });
    setSignedIn(result.user);
    document.getElementById('authModal').classList.add('hidden');
    showToast('Your email is verified. Welcome!');
  } catch (error) { showToast(error.message, 'error'); }
});
document.getElementById('loginForm')?.addEventListener('submit', async function (event) {
  event.preventDefault();
  const button = document.getElementById('submitLoginBtn');
  button.disabled = true;
  try {
    const result = await authRequest('/api/auth/login', {
      email: document.getElementById('loginEmail').value.trim(),
      password: document.getElementById('loginPassword').value
    });
    setSignedIn(result.user);
    document.getElementById('authModal').classList.add('hidden');
    showToast('Signed in successfully.');
  } catch (error) {
    if (error.message.toLowerCase().includes('verify')) {
      pendingAuthEmail = document.getElementById('loginEmail').value.trim();
      showAuthView('verify');
    }
    showToast(error.message, 'error');
  }
  finally { button.disabled = false; }
});
document.getElementById('autoFillCodeBtn')?.addEventListener('click', function () {
  document.getElementById('verifyCodeInput').value = document.getElementById('devCodeValue').textContent.trim();
});
document.getElementById('resendCodeBtn')?.addEventListener('click', async function (event) {
  event.preventDefault();
  try {
    const result = await authRequest('/api/auth/resend-verification', { email: pendingAuthEmail });
    if (result.dev_code) {
      document.getElementById('devCodeBanner').classList.remove('hidden');
      document.getElementById('devCodeValue').textContent = result.dev_code;
    }
    showToast(result.message || 'A new verification code was sent.');
  } catch (error) { showToast(error.message, 'error'); }
});
document.getElementById('forgotForm')?.addEventListener('submit', async function (event) {
  event.preventDefault();
  try {
    const result = await authRequest('/api/auth/forgot-password', {
      email: document.getElementById('forgotEmail').value.trim()
    });
    if (result.dev_token) {
      document.getElementById('resetTokenInput').value = result.dev_token;
      showAuthView('reset');
    }
    showToast(result.message || 'If the account exists, reset instructions were sent.');
  } catch (error) { showToast(error.message, 'error'); }
});
document.getElementById('resetForm')?.addEventListener('submit', async function (event) {
  event.preventDefault();
  try {
    const result = await authRequest('/api/auth/reset-password', {
      token: document.getElementById('resetTokenInput').value.trim(),
      new_password: document.getElementById('resetNewPassword').value
    });
    showAuthView('login');
    showToast(result.message || 'Password updated.');
  } catch (error) { showToast(error.message, 'error'); }
});

async function loadHistory() {
  if (!currentUser) return;
  try {
    const response = await fetch('/api/history', { credentials: 'same-origin' });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'History could not be loaded.');
    const history = result.history || [];
    document.getElementById('historyCountBadge').textContent = String(history.length);
    const container = document.getElementById('historyListContainer');
    if (!history.length) {
      container.innerHTML = '<p class="text-sm text-on-surface-muted text-center py-8">Completed agent analyses will appear here.</p>';
      return;
    }
    container.innerHTML = history.map(function (item) {
      return '<button type="button" class="history-item w-full text-left p-4 rounded-xl bg-surface-low border border-surface-border hover:border-primary/60" data-history-id="' +
        Number(item.id) + '"><span class="block font-semibold text-white">' + escapeHTML(item.topic) +
        '</span><span class="block mt-1 text-xs text-on-surface-muted">' + escapeHTML(item.created_at || '') +
        ' · ' + escapeHTML(item.model || '') + '</span></button>';
    }).join('');
    container.querySelectorAll('.history-item').forEach(function (button) {
      button.addEventListener('click', function () { loadHistoryItem(button.dataset.historyId); });
    });
  } catch (error) { showToast(error.message, 'error'); }
}
async function loadHistoryItem(id) {
  try {
    const response = await fetch('/api/history/' + encodeURIComponent(id), { credentials: 'same-origin' });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'Saved report could not be opened.');
    topicInput.value = result.topic || '';
    updateDashboard(result.data || {}, result.data?.competitors || [], result.report || '');
    document.getElementById('historyModal').classList.add('hidden');
    document.querySelector('.dashboard-shell')?.scrollIntoView({ behavior: 'smooth' });
  } catch (error) { showToast(error.message, 'error'); }
}
document.getElementById('openHistoryBtn')?.addEventListener('click', async function () {
  await loadHistory();
  document.getElementById('historyModal').classList.remove('hidden');
});
document.getElementById('dropdownHistoryBtn')?.addEventListener('click', async function () {
  document.getElementById('userDropdown').classList.add('hidden');
  await loadHistory();
  document.getElementById('historyModal').classList.remove('hidden');
});
document.getElementById('closeHistoryModalBtn')?.addEventListener('click', function () {
  document.getElementById('historyModal').classList.add('hidden');
});
document.getElementById('userProfileBtn')?.addEventListener('click', function () {
  document.getElementById('userDropdown').classList.toggle('hidden');
});
document.getElementById('logoutBtn')?.addEventListener('click', async function () {
  try {
    await authRequest('/api/auth/logout');
    setSignedIn(null);
    showToast('You have been signed out.');
  } catch (error) { showToast(error.message, 'error'); }
});

['navOpenStudioBtn', 'heroDeployBtn', 'heroDeployBtnShortcut', 'ctaDeployBtn'].forEach(function (id) {
  document.getElementById(id)?.addEventListener('click', function () {
    if (!currentUser) return openAuth('login');
    document.querySelector('.dashboard-shell')?.scrollIntoView({ behavior: 'smooth' });
  });
});
document.querySelectorAll('.launch-studio-action').forEach(function (button) {
  button.addEventListener('click', function () { openAuth('signup'); });
});
