// YouTube Trend & Content Founder - Frontend Application

let appState = {
  currentTab: 'explore',
  niches: [],
  selectedNiche: null,
  currentQuery: '',
  currentContentType: 'all',
  currentDateFilter: 'relevant',
  currentTrendSubtab: 'yt_trending',
  dailyGoogleTrends: [],
  youtubeTrending: [],
  referenceVideos: [],
  autocompleteKeywords: [],
  currentAiAnalysis: null,
  currentPackage: null,
  currentScript: '',
  tasks: [],
  savedScripts: []
};

// Initialize App
document.addEventListener('DOMContentLoaded', async () => {
  await loadNiches();
  await refreshAllTrends();
  await loadWeeklyTasks();
  lucide.createIcons();
});

// Toast notification helper
function showToast(message, isError = false) {
  const toast = document.getElementById('toast');
  const msgEl = document.getElementById('toast-message');
  const iconEl = document.getElementById('toast-icon');
  
  msgEl.textContent = message;
  iconEl.innerHTML = isError 
    ? '<i data-lucide="alert-circle" class="w-5 h-5 text-red-400"></i>'
    : '<i data-lucide="check-circle" class="w-5 h-5 text-emerald-400"></i>';
    
  toast.classList.remove('translate-y-8', 'opacity-0');
  toast.classList.add('translate-y-0', 'opacity-100');
  lucide.createIcons();
  
  setTimeout(() => {
    toast.classList.add('translate-y-8', 'opacity-0');
    toast.classList.remove('translate-y-0', 'opacity-100');
  }, 3200);
}

// Copy Helper
async function copyText(text, successMsg = 'Copiado para a área de transferência!') {
  try {
    await navigator.clipboard.writeText(text);
    showToast(successMsg);
  } catch (e) {
    const ta = document.createElement('textarea');
    ta.value = text;
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
    showToast(successMsg);
  }
}

// Tab Switching
function switchTab(tabId) {
  appState.currentTab = tabId;
  
  document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
  document.querySelectorAll('.nav-tab').forEach(el => {
    el.classList.remove('bg-red-600', 'text-white', 'shadow-sm');
    el.classList.add('text-slate-300');
  });
  
  const targetTab = document.getElementById(`tab-${tabId}`);
  const targetBtn = document.getElementById(`tab-btn-${tabId}`);
  
  if (targetTab) targetTab.classList.remove('hidden');
  if (targetBtn) {
    targetBtn.classList.add('bg-red-600', 'text-white', 'shadow-sm');
    targetBtn.classList.remove('text-slate-300');
  }

  if (tabId === 'saved') {
    loadSavedContents();
  } else if (tabId === 'schedule') {
    loadWeeklyTasks();
  }
  
  lucide.createIcons();
}

// Sub-tabs for Trends: YouTube Em Alta vs Google Trends
function switchTrendSubtab(subtabId) {
  appState.currentTrendSubtab = subtabId;
  
  const btnYt = document.getElementById('subtab-btn-yt');
  const btnGoogle = document.getElementById('subtab-btn-google');
  const containerYt = document.getElementById('subtab-yt_trending');
  const containerGoogle = document.getElementById('subtab-google_trends');
  
  if (subtabId === 'yt_trending') {
    btnYt.className = 'pb-2 text-xs font-semibold text-red-400 border-b-2 border-red-500 flex items-center gap-1';
    btnGoogle.className = 'pb-2 text-xs font-semibold text-slate-400 hover:text-slate-200 border-b-2 border-transparent flex items-center gap-1';
    containerYt.classList.remove('hidden');
    containerGoogle.classList.add('hidden');
  } else {
    btnGoogle.className = 'pb-2 text-xs font-semibold text-blue-400 border-b-2 border-blue-500 flex items-center gap-1';
    btnYt.className = 'pb-2 text-xs font-semibold text-slate-400 hover:text-slate-200 border-b-2 border-transparent flex items-center gap-1';
    containerGoogle.classList.remove('hidden');
    containerYt.classList.add('hidden');
  }
  lucide.createIcons();
}

// Set Content Type (All, Videos, Shorts, Lives)
function setContentType(type) {
  appState.currentContentType = type;
  
  document.querySelectorAll('.ctype-btn').forEach(btn => {
    btn.className = 'ctype-btn px-3 py-1.5 text-xs font-medium rounded-lg text-slate-300 hover:text-white hover:bg-dark-800 transition flex items-center gap-1.5';
  });
  
  const activeBtn = document.getElementById(`ctype-${type}`);
  if (activeBtn) {
    activeBtn.className = 'ctype-btn px-3 py-1.5 text-xs font-medium rounded-lg bg-red-600 text-white transition flex items-center gap-1.5 shadow-md shadow-red-600/20';
  }
  
  searchCurrentNiche();
}

// Load Pre-configured Niches
async function loadNiches() {
  try {
    const res = await fetch('/api/niches');
    const data = await res.json();
    appState.niches = data.niches || [];
    renderNichePills();
    
    if (appState.niches.length > 0 && !appState.selectedNiche) {
      selectNiche(appState.niches[0]);
    }
  } catch (err) {
    console.error('Error loading niches:', err);
  }
}

function renderNichePills() {
  const container = document.getElementById('niche-pills-container');
  if (!container) return;
  
  container.innerHTML = appState.niches.map(n => {
    const isSelected = appState.selectedNiche && appState.selectedNiche.id === n.id;
    const activeClasses = isSelected 
      ? 'bg-red-600 text-white border-red-500 shadow-md shadow-red-600/20' 
      : 'bg-dark-800 text-slate-300 border-dark-700 hover:border-slate-500 hover:text-white';
      
    return `
      <button onclick="selectNicheById('${n.id}')" class="px-3 py-1.5 rounded-xl border text-xs font-medium transition flex items-center gap-1.5 ${activeClasses}">
        <span>${n.name}</span>
      </button>
    `;
  }).join('');
}

function selectNicheById(nicheId) {
  const n = appState.niches.find(item => item.id === nicheId);
  if (n) selectNiche(n);
}

function selectNiche(niche) {
  appState.selectedNiche = niche;
  document.getElementById('niche-search-input').value = niche.query || niche.name;
  document.getElementById('gen-niche-input').value = niche.name;
  renderNichePills();
  searchCurrentNiche();
}

// Refresh ALL Trends & Search
async function refreshAllTrends() {
  const refreshIcon = document.getElementById('refresh-icon');
  const btnText = document.getElementById('refresh-btn-text');
  if (refreshIcon) refreshIcon.classList.add('animate-spin');
  if (btnText) btnText.textContent = 'Atualizando...';
  
  try {
    const res = await fetch('/api/trends/daily?geo=BR');
    const data = await res.json();
    appState.dailyGoogleTrends = data.google_trends || [];
    appState.youtubeTrending = data.youtube_trends || [];
    
    renderYouTubeTrendingList();
    renderGoogleTrendsList();
    
    // Also refresh current niche search
    await searchCurrentNiche();
    
    const now = new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    showToast(`Tendências atualizadas com sucesso às ${now}!`);
  } catch (err) {
    console.error('Error fetching daily trends:', err);
    showToast('Erro ao atualizar tendências.', true);
  } finally {
    if (refreshIcon) refreshIcon.classList.remove('animate-spin');
    if (btnText) btnText.textContent = 'Atualizar Tendências';
  }
}

// Render YouTube Em Alta Brasil (Trending Videos with Thumbnails & Views)
function renderYouTubeTrendingList() {
  const listEl = document.getElementById('subtab-yt_trending');
  if (!listEl) return;
  
  if (appState.youtubeTrending.length === 0) {
    listEl.innerHTML = '<p class="text-xs text-slate-500 italic p-3">Nenhum vídeo em alta retornado no momento.</p>';
    return;
  }
  
  listEl.innerHTML = appState.youtubeTrending.slice(0, 15).map((v, idx) => `
    <div class="p-2.5 bg-dark-850 hover:bg-dark-800 rounded-xl border border-dark-750 transition flex items-center justify-between gap-2.5 group">
      <div class="flex items-center space-x-2.5 min-w-0 flex-1">
        <span class="text-xs font-mono font-bold text-red-500 w-4 flex-shrink-0">${idx + 1}.</span>
        <div class="w-12 h-8 rounded-lg overflow-hidden bg-dark-950 flex-shrink-0 relative">
          <img src="${v.thumbnail}" alt="" class="w-full h-full object-cover">
        </div>
        <div class="min-w-0 flex-1">
          <h4 class="text-xs font-semibold text-slate-200 truncate group-hover:text-white" title="${v.title}">${v.title}</h4>
          <div class="flex items-center gap-1.5 text-[10px] text-slate-400 mt-0.5">
            <span class="truncate max-w-[90px] text-slate-300">${v.channel}</span>
            <span>•</span>
            <span class="text-red-400 font-medium">${v.views}</span>
          </div>
        </div>
      </div>
      <div class="flex items-center space-x-1 flex-shrink-0">
        <button onclick="useVideoAsReference('${v.title.replace(/'/g, "\\'")}', '${v.url}')" class="p-1.5 bg-dark-800 hover:bg-red-600 text-slate-300 hover:text-white rounded-lg transition" title="Criar Roteiro">
          <i data-lucide="sparkles" class="w-3.5 h-3.5"></i>
        </button>
        <a href="${v.url}" target="_blank" class="p-1.5 text-slate-400 hover:text-white" title="Ver no YouTube">
          <i data-lucide="external-link" class="w-3.5 h-3.5"></i>
        </a>
      </div>
    </div>
  `).join('');
  
  lucide.createIcons();
}

// Render Google Trends with News Headlines (Explains why it is trending!)
function renderGoogleTrendsList() {
  const listEl = document.getElementById('subtab-google_trends');
  if (!listEl) return;
  
  if (appState.dailyGoogleTrends.length === 0) {
    listEl.innerHTML = '<p class="text-xs text-slate-500 italic p-3">Nenhum termo do Google Trends disponível.</p>';
    return;
  }
  
  listEl.innerHTML = appState.dailyGoogleTrends.map((t, idx) => `
    <div class="p-3 bg-dark-850 hover:bg-dark-800 rounded-xl border border-dark-750 transition space-y-1.5 group">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-2 min-w-0 pr-2">
          <span class="text-xs font-mono font-bold text-blue-400 w-4">${idx + 1}.</span>
          <span class="text-xs font-bold text-white capitalize group-hover:text-blue-300">${t.title}</span>
        </div>
        <div class="flex items-center space-x-1.5 flex-shrink-0">
          <span class="text-[10px] px-1.5 py-0.5 rounded bg-blue-500/15 text-blue-400 font-mono font-semibold">${t.traffic}</span>
          <button onclick="useTopicAsIdea('${t.title.replace(/'/g, "\\'")}')" class="p-1 text-slate-400 hover:text-amber-400" title="Usar como tema">
            <i data-lucide="sparkles" class="w-3.5 h-3.5"></i>
          </button>
        </div>
      </div>

      ${t.headline ? `
        <div class="text-[11px] text-slate-400 bg-dark-950 p-2 rounded-lg border border-dark-800 flex items-start gap-1.5">
          <i data-lucide="newspaper" class="w-3.5 h-3.5 text-slate-500 mt-0.5 flex-shrink-0"></i>
          <span class="leading-snug line-clamp-2">${t.headline} <strong class="text-slate-500">(${t.source || 'Notícia'})</strong></span>
        </div>
      ` : ''}
    </div>
  `).join('');
  
  lucide.createIcons();
}

// Search YouTube Niche Trends & Autocomplete
async function searchCurrentNiche() {
  const query = document.getElementById('niche-search-input').value.trim();
  const filter = document.getElementById('filter-select').value;
  const ctype = appState.currentContentType || 'all';
  if (!query) return;

  appState.currentQuery = query;
  appState.currentDateFilter = filter;
  const container = document.getElementById('reference-videos-container');
  const countEl = document.getElementById('video-results-count');
  
  // Show loading spinner
  container.innerHTML = `
    <div class="col-span-2 space-y-3 py-12 text-center">
      <div class="w-8 h-8 border-2 border-red-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
      <p class="text-xs text-slate-400">Varrendo o YouTube para "${query}" (${ctype.toUpperCase()} • ${filter})...</p>
    </div>
  `;

  try {
    const res = await fetch(`/api/trends/niche?query=${encodeURIComponent(query)}&filter=${filter}&content_type=${ctype}`);
    const data = await res.json();
    
    appState.referenceVideos = data.videos || [];
    appState.autocompleteKeywords = data.autocomplete_keywords || [];
    
    countEl.textContent = `${appState.referenceVideos.length} referências`;
    
    renderReferenceVideos();
    renderAutocompleteKeywords();
  } catch (err) {
    console.error('Error searching niche:', err);
    container.innerHTML = `
      <div class="col-span-2 text-center py-8 text-red-400">
        <p class="text-xs">Erro ao conectar com a pesquisa do YouTube. Tente novamente.</p>
      </div>
    `;
  }
}

function renderAutocompleteKeywords() {
  const container = document.getElementById('autocomplete-keywords-list');
  if (!container) return;
  
  if (appState.autocompleteKeywords.length === 0) {
    container.innerHTML = '<span class="text-xs text-slate-500 italic">Nenhuma sugestão encontrada.</span>';
    return;
  }
  
  container.innerHTML = appState.autocompleteKeywords.map(kw => `
    <button onclick="searchKeywordDirectly('${kw.replace(/'/g, "\\'")}')" class="badge-keyword px-2.5 py-1 bg-dark-800 hover:bg-red-600/20 text-slate-300 hover:text-red-300 border border-dark-700 hover:border-red-500/40 rounded-lg text-xs transition flex items-center gap-1">
      <i data-lucide="search" class="w-2.5 h-2.5 opacity-60"></i>
      <span>${kw}</span>
    </button>
  `).join('');
  
  lucide.createIcons();
}

function searchKeywordDirectly(keyword) {
  document.getElementById('niche-search-input').value = keyword;
  searchCurrentNiche();
}

function copyAllAutocompleteKeywords() {
  if (appState.autocompleteKeywords.length === 0) return;
  copyText(appState.autocompleteKeywords.join(', '), 'Palavras-chave copiadas com sucesso!');
}

function renderReferenceVideos() {
  const container = document.getElementById('reference-videos-container');
  if (!container) return;
  
  if (appState.referenceVideos.length === 0) {
    container.innerHTML = `
      <div class="col-span-2 text-center py-12 text-slate-500 space-y-2">
        <i data-lucide="search-x" class="w-10 h-10 mx-auto opacity-30"></i>
        <p class="text-xs">Nenhum resultado para este filtro específico. Tente mudar o filtro de data ou formato acima.</p>
      </div>
    `;
    lucide.createIcons();
    return;
  }
  
  container.innerHTML = appState.referenceVideos.map(v => {
    const isLive = v.is_live;
    const isShort = v.is_short;
    
    return `
      <div class="video-card bg-dark-850 border ${isLive ? 'border-red-500/40' : 'border-dark-750'} rounded-2xl overflow-hidden flex flex-col justify-between">
        <div>
          <!-- Thumbnail & Badges -->
          <div class="relative ${isShort ? 'aspect-[9/14] max-h-72 mx-auto' : 'aspect-video'} bg-dark-950 overflow-hidden group">
            <img src="${v.thumbnail}" alt="${v.title}" class="w-full h-full object-cover group-hover:scale-105 transition duration-300" onerror="this.src='https://i.ytimg.com/vi/${v.id}/hqdefault.jpg'">
            
            <!-- Type Badges -->
            <div class="absolute top-2 left-2 flex gap-1">
              ${isLive ? `<span class="bg-red-600 text-white text-[10px] font-bold px-2 py-0.5 rounded-full flex items-center gap-1 shadow-lg animate-pulse"><i data-lucide="radio" class="w-3 h-3"></i> AO VIVO</span>` : ''}
              ${isShort ? `<span class="bg-amber-500 text-slate-950 text-[10px] font-bold px-2 py-0.5 rounded-full flex items-center gap-1 shadow-lg"><i data-lucide="smartphone" class="w-3 h-3"></i> SHORTS</span>` : ''}
            </div>

            ${v.duration ? `<span class="absolute bottom-2 right-2 bg-black/80 text-white text-[10px] font-mono px-1.5 py-0.5 rounded font-semibold">${v.duration}</span>` : ''}
            
            <a href="${v.url}" target="_blank" class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition flex items-center justify-center text-white">
              <div class="w-10 h-10 rounded-full bg-red-600 flex items-center justify-center shadow-lg">
                <i data-lucide="play" class="w-5 h-5 fill-white ml-0.5"></i>
              </div>
            </a>
          </div>

          <!-- Video Info -->
          <div class="p-4 space-y-2">
            <h3 class="text-xs font-bold text-white line-clamp-2 hover:text-red-400 transition" title="${v.title}">
              ${v.title}
            </h3>
            
            <div class="flex items-center justify-between text-[11px] text-slate-400">
              <span class="font-medium text-slate-300 truncate max-w-[130px]">${v.channel}</span>
              <div class="flex items-center gap-1.5">
                <span class="text-red-400 font-semibold">${v.views}</span>
                <span>•</span>
                <span>${v.published}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="p-3 bg-dark-900/60 border-t border-dark-750 flex items-center gap-2">
          <button onclick="useVideoAsReference('${v.title.replace(/'/g, "\\'")}', '${v.url}')" class="flex-1 py-1.5 px-3 bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 text-white text-xs font-semibold rounded-lg shadow-sm flex items-center justify-center gap-1.5 transition">
            <i data-lucide="sparkles" class="w-3.5 h-3.5"></i>
            <span>Gerar Roteiro / Ideia</span>
          </button>
          <a href="${v.url}" target="_blank" class="p-1.5 rounded-lg bg-dark-800 hover:bg-dark-700 text-slate-300 hover:text-white border border-dark-700" title="Ver no YouTube">
            <i data-lucide="external-link" class="w-4 h-4"></i>
          </a>
        </div>
      </div>
    `;
  }).join('');
  
  lucide.createIcons();
}

// Deep AI Niche Analysis (SEO & Topics)
async function runAiNicheAnalysis() {
  const niche = appState.selectedNiche ? appState.selectedNiche.name : (appState.currentQuery || 'Geral');
  const btn = document.getElementById('btn-run-ai-analysis');
  const panel = document.getElementById('ai-niche-panel');
  
  const originalBtnContent = btn.innerHTML;
  btn.innerHTML = `<div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div><span>Analisando com IA...</span>`;
  btn.disabled = true;

  try {
    const titles = appState.referenceVideos.map(v => v.title);
    const res = await fetch('/api/ai/analyze-niche', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        niche: niche,
        subniche: appState.currentQuery,
        trending_titles: titles
      })
    });
    
    const json = await res.json();
    if (json.status === 'success') {
      appState.currentAiAnalysis = json.data;
      renderAiNichePanel();
      panel.classList.remove('hidden');
      panel.scrollIntoView({ behavior: 'smooth' });
      showToast('Análise de SEO e temas concluída pela IA!');
    }
  } catch (err) {
    console.error('Error analyzing niche:', err);
    showToast('Erro ao gerar análise da IA.', true);
  } finally {
    btn.innerHTML = originalBtnContent;
    btn.disabled = false;
    lucide.createIcons();
  }
}

function renderAiNichePanel() {
  const data = appState.currentAiAnalysis;
  if (!data) return;
  
  document.getElementById('ai-report-niche-label').textContent = data.niche_summary || 'Análise de tendências e estratégia de crescimento.';
  
  // Core keywords
  const coreEl = document.getElementById('ai-core-keywords');
  const coreList = data.core_keywords || [];
  coreEl.innerHTML = coreList.map(k => `
    <button onclick="copyText('${k}', 'Palavra-chave copiada!')" class="px-2.5 py-1 bg-blue-500/10 hover:bg-blue-500/20 text-blue-300 border border-blue-500/30 rounded-lg text-xs font-medium transition flex items-center gap-1">
      <i data-lucide="copy" class="w-2.5 h-2.5 opacity-60"></i>
      <span>${k}</span>
    </button>
  `).join('');

  // Longtail keywords
  const longEl = document.getElementById('ai-longtail-keywords');
  const longList = data.long_tail_keywords || [];
  longEl.innerHTML = longList.map(k => `
    <div class="p-1.5 bg-dark-950 rounded-lg border border-dark-800 text-xs text-slate-300 flex items-center justify-between">
      <span class="truncate pr-2">• ${k}</span>
      <button onclick="copyText('${k.replace(/'/g, "\\'")}', 'Copiado!')" class="text-slate-400 hover:text-white p-1">
        <i data-lucide="copy" class="w-3 h-3"></i>
      </button>
    </div>
  `).join('');

  // YouTube tags
  const tagsEl = document.getElementById('ai-youtube-tags');
  tagsEl.textContent = data.youtube_tags || 'Nenhuma tag gerada.';

  // Hot topics
  const topicsContainer = document.getElementById('ai-hot-topics-container');
  const topics = data.hot_topics || [];
  topicsContainer.innerHTML = topics.map(t => `
    <div class="bg-dark-850 p-4 rounded-xl border border-dark-750 flex flex-col justify-between space-y-3">
      <div class="space-y-2">
        <div class="flex items-center gap-1.5 text-xs font-bold text-amber-400">
          <i data-lucide="sparkles" class="w-3.5 h-3.5"></i>
          <span>${t.topic}</span>
        </div>
        <p class="text-xs text-slate-300"><strong class="text-slate-400">Ângulo:</strong> ${t.angle}</p>
        <p class="text-xs text-slate-400"><strong class="text-slate-500">Por que viraliza:</strong> ${t.why_viral}</p>
        ${t.hook_idea ? `<p class="text-[11px] p-2 bg-dark-950 rounded border border-dark-800 text-amber-200/90 font-mono italic">"${t.hook_idea}"</p>` : ''}
      </div>

      <div class="pt-2 border-t border-dark-800 flex gap-2">
        <button onclick="useTopicAsIdea('${t.topic.replace(/'/g, "\\'")}')" class="flex-1 py-1.5 bg-red-600 hover:bg-red-500 text-white text-xs font-semibold rounded-lg transition flex items-center justify-center gap-1">
          <i data-lucide="play" class="w-3 h-3 fill-white"></i> Criar Roteiro
        </button>
        <button onclick="addTopicToWeeklySchedule('${t.topic.replace(/'/g, "\\'")}', '${(t.hook_idea || '').replace(/'/g, "\\'")}')" class="p-1.5 bg-dark-800 hover:bg-dark-700 text-blue-400 rounded-lg border border-dark-700" title="Salvar na Segunda-feira">
          <i data-lucide="calendar-plus" class="w-4 h-4"></i>
        </button>
      </div>
    </div>
  `).join('');

  lucide.createIcons();
}

function copyYoutubeTags() {
  const tags = document.getElementById('ai-youtube-tags').textContent;
  copyText(tags, 'Tags para o YouTube copiadas com sucesso!');
}

function copyFullAiReport() {
  if (!appState.currentAiAnalysis) return;
  const d = appState.currentAiAnalysis;
  const text = `=== RELATÓRIO DE INTELIGÊNCIA YOUTUBE ===\n\nNicho: ${appState.selectedNiche?.name || appState.currentQuery}\n${d.niche_summary}\n\nPALAVRAS-CHAVE PRINCIPAIS:\n${(d.core_keywords || []).join(', ')}\n\nCAUDA LONGA:\n${(d.long_tail_keywords || []).join('\n')}\n\nTAGS PRONTAS:\n${d.youtube_tags}\n`;
  copyText(text, 'Relatório completo copiado!');
}

// Transfer Video Reference to Generator
function useVideoAsReference(videoTitle, videoUrl) {
  const nicheName = appState.selectedNiche ? appState.selectedNiche.name : (appState.currentQuery || 'Geral');
  document.getElementById('gen-niche-input').value = nicheName;
  document.getElementById('gen-topic-input').value = `Versão aprofundada baseada em: ${videoTitle}`;
  document.getElementById('gen-reference-input').value = videoUrl;
  
  switchTab('generator');
  showToast('Dados transferidos para o Gerador IA!');
}

function useTopicAsIdea(topicTitle) {
  const nicheName = appState.selectedNiche ? appState.selectedNiche.name : (appState.currentQuery || 'Geral');
  document.getElementById('gen-niche-input').value = nicheName;
  document.getElementById('gen-topic-input').value = topicTitle;
  
  switchTab('generator');
  showToast('Tema carregado no Gerador IA!');
}

// Generate Viral Package (Titles, Thumbs, Hook, Outline)
async function generateViralPackage() {
  const niche = document.getElementById('gen-niche-input').value.trim();
  const topic = document.getElementById('gen-topic-input').value.trim();
  const refUrl = document.getElementById('gen-reference-input').value.trim();
  
  if (!topic) {
    showToast('Digite um tema para o vídeo.', true);
    return;
  }

  const btn = document.getElementById('btn-gen-package');
  const emptyState = document.getElementById('generator-empty-state');
  const packageCard = document.getElementById('package-output-card');
  
  const originalHtml = btn.innerHTML;
  btn.innerHTML = `<div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div><span>Gerando Pacote Viral...</span>`;
  btn.disabled = true;

  try {
    const res = await fetch('/api/ai/video-package', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        niche: niche || 'Geral',
        topic_or_title: topic,
        reference_urls: refUrl
      })
    });
    
    const json = await res.json();
    if (json.status === 'success') {
      appState.currentPackage = json.data;
      renderViralPackage();
      emptyState.classList.add('hidden');
      packageCard.classList.remove('hidden');
      packageCard.scrollIntoView({ behavior: 'smooth' });
      showToast('Títulos, Thumbs e Hook gerados com sucesso!');
    }
  } catch (err) {
    console.error('Error generating package:', err);
    showToast('Erro ao gerar pacote viral com a IA.', true);
  } finally {
    btn.innerHTML = originalHtml;
    btn.disabled = false;
    lucide.createIcons();
  }
}

function renderViralPackage() {
  const pkg = appState.currentPackage;
  if (!pkg) return;

  // 5 Titles
  const titlesList = document.getElementById('package-titles-list');
  const titles = pkg.titles || [];
  titlesList.innerHTML = titles.map((t, idx) => `
    <div class="p-3 bg-dark-950 hover:bg-dark-900 rounded-xl border border-dark-800 transition flex items-center justify-between group">
      <div class="flex items-center space-x-2.5 min-w-0 pr-2">
        <span class="text-xs font-mono font-bold text-red-500">${idx + 1}.</span>
        <span class="text-xs font-semibold text-white truncate group-hover:text-red-300">${t}</span>
      </div>
      <div class="flex items-center gap-1.5 flex-shrink-0">
        <button onclick="copyText('${t.replace(/'/g, "\\'")}', 'Título copiado!')" class="p-1.5 text-slate-400 hover:text-white" title="Copiar Título">
          <i data-lucide="copy" class="w-3.5 h-3.5"></i>
        </button>
        <button onclick="setScriptTitle('${t.replace(/'/g, "\\'")}')" class="px-2 py-1 bg-red-600/20 hover:bg-red-600 text-red-300 hover:text-white text-[10px] font-semibold rounded-md border border-red-500/30 transition" title="Usar para gerar roteiro">
          Usar Título
        </button>
      </div>
    </div>
  `).join('');

  // Thumbnails
  const thumbsList = document.getElementById('package-thumbs-list');
  const thumbs = pkg.thumbnail_concepts || [];
  thumbsList.innerHTML = thumbs.map(th => `
    <div class="p-4 bg-dark-950 rounded-xl border border-dark-800 flex flex-col justify-between space-y-3">
      <div class="space-y-2">
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold text-amber-400">${th.concept_title || 'Conceito de Thumb'}</span>
          <span class="text-[10px] px-2 py-0.5 bg-red-600/20 text-red-400 rounded-full font-bold uppercase tracking-wider">${th.text_overlay || 'TEXTO'}</span>
        </div>
        <p class="text-xs text-slate-300 leading-relaxed">${th.visual_description}</p>
        ${th.ai_prompt ? `
          <div class="p-2 bg-dark-900 rounded border border-dark-750 text-[11px] font-mono text-slate-400">
            <strong class="text-slate-500">Prompt IA:</strong> ${th.ai_prompt}
          </div>
        ` : ''}
      </div>
      <button onclick="copyText('${(th.visual_description + ' | Texto da Thumb: ' + th.text_overlay).replace(/'/g, "\\'")}', 'Conceito da Thumbnail copiado!')" class="text-xs text-slate-400 hover:text-white flex items-center justify-end gap-1">
        <i data-lucide="copy" class="w-3 h-3"></i> Copiar Conceito
      </button>
    </div>
  `).join('');

  // 15s Hook
  document.getElementById('package-hook-text').textContent = `"${pkg.hook_script_15s || 'Gancho de alto impacto para os primeiros 15 segundos.'}"`;

  // Outline
  const outlineList = document.getElementById('package-outline-list');
  const outline = pkg.structure_outline || [];
  outlineList.innerHTML = outline.map(item => `<div>• ${item}</div>`).join('');

  lucide.createIcons();
}

function copyHookText() {
  const hook = document.getElementById('package-hook-text').textContent;
  copyText(hook, 'Gancho copiado!');
}

function setScriptTitle(title) {
  document.getElementById('gen-topic-input').value = title;
  generateCompleteScript();
}

// Generate Complete Script
async function generateCompleteScript() {
  const niche = document.getElementById('gen-niche-input').value.trim();
  const title = document.getElementById('gen-topic-input').value.trim();
  const tone = document.getElementById('gen-tone-select').value;
  
  if (!title) {
    showToast('Defina um título ou tema para o roteiro.', true);
    return;
  }

  const btn = document.getElementById('btn-gen-script');
  const emptyState = document.getElementById('generator-empty-state');
  const scriptCard = document.getElementById('script-output-card');
  
  const originalHtml = btn.innerHTML;
  btn.innerHTML = `<div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div><span>Escrevendo Roteiro...</span>`;
  btn.disabled = true;

  try {
    const res = await fetch('/api/ai/script', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        niche: niche || 'Geral',
        title: title,
        notes_or_outline: appState.currentPackage ? JSON.stringify(appState.currentPackage.structure_outline) : '',
        tone: tone
      })
    });
    
    const json = await res.json();
    if (json.status === 'success') {
      appState.currentScript = json.script;
      document.getElementById('script-title-preview').textContent = `Título: ${title} (${niche})`;
      document.getElementById('full-script-text').textContent = json.script;
      
      emptyState.classList.add('hidden');
      scriptCard.classList.remove('hidden');
      scriptCard.scrollIntoView({ behavior: 'smooth' });
      showToast('Roteiro completo gerado!');
    }
  } catch (err) {
    console.error('Error generating script:', err);
    showToast('Erro ao gerar roteiro.', true);
  } finally {
    btn.innerHTML = originalHtml;
    btn.disabled = false;
    lucide.createIcons();
  }
}

function copyFullScript() {
  if (!appState.currentScript) return;
  copyText(appState.currentScript, 'Roteiro copiado na íntegra!');
}

function downloadScriptFile(ext = 'md') {
  if (!appState.currentScript) return;
  const title = document.getElementById('gen-topic-input').value.trim() || 'roteiro_youtube';
  const cleanTitle = title.replace(/[^a-zA-Z0-9_-]/g, '_').toLowerCase();
  
  const blob = new Blob([appState.currentScript], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${cleanTitle}.${ext}`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  showToast(`Arquivo ${cleanTitle}.${ext} baixado com sucesso!`);
}

async function saveCurrentScriptToDb() {
  if (!appState.currentScript) return;
  const niche = document.getElementById('gen-niche-input').value.trim() || 'Geral';
  const title = document.getElementById('gen-topic-input').value.trim() || 'Vídeo YouTube';
  const hook = appState.currentPackage?.hook_script_15s || '';
  const thumbs = appState.currentPackage?.thumbnail_concepts ? JSON.stringify(appState.currentPackage.thumbnail_concepts) : '';
  const titlesSug = appState.currentPackage?.titles ? JSON.stringify(appState.currentPackage.titles) : '';

  try {
    const res = await fetch('/api/scripts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        niche: niche,
        title: title,
        hook: hook,
        script_body: appState.currentScript,
        thumbnail_concept: thumbs,
        titles_suggestions: titlesSug
      })
    });
    const json = await res.json();
    if (json.status === 'success') {
      showToast('Roteiro salvo na aba de Salvos!');
    }
  } catch (err) {
    console.error('Error saving script:', err);
  }
}

// Weekly Production Tasks (Kanban)
async function loadWeeklyTasks() {
  try {
    const res = await fetch('/api/tasks');
    const data = await res.json();
    appState.tasks = data.tasks || [];
    renderWeeklyTasks();
  } catch (err) {
    console.error('Error loading tasks:', err);
  }
}

function renderWeeklyTasks() {
  const days = ['segunda', 'terca', 'quarta'];
  
  days.forEach(day => {
    const listEl = document.getElementById(`tasks-list-${day}`);
    const countEl = document.getElementById(`count-${day}`);
    if (!listEl) return;
    
    const dayTasks = appState.tasks.filter(t => t.day_column === day);
    countEl.textContent = `${dayTasks.length} itens`;
    
    if (dayTasks.length === 0) {
      listEl.innerHTML = `
        <div class="h-28 border border-dashed border-dark-700 rounded-xl flex items-center justify-center text-xs text-slate-500">
          Nenhum item agendado
        </div>
      `;
      return;
    }
    
    listEl.innerHTML = dayTasks.map(task => {
      const isDone = task.status === 'completed';
      return `
        <div class="p-3.5 bg-dark-900 border ${isDone ? 'border-emerald-500/30 bg-emerald-950/10' : 'border-dark-750'} rounded-xl space-y-2.5 transition">
          <div class="flex items-start justify-between gap-2">
            <div class="space-y-1">
              <span class="text-[10px] px-2 py-0.5 rounded-full ${day === 'segunda' ? 'bg-blue-500/20 text-blue-300' : day === 'terca' ? 'bg-amber-500/20 text-amber-300' : 'bg-emerald-500/20 text-emerald-300'} font-semibold">
                ${task.step_name || 'Etapa'}
              </span>
              <h4 class="text-xs font-bold text-white leading-snug ${isDone ? 'line-through text-slate-400' : ''}">${task.title}</h4>
            </div>
            <button onclick="deleteWeeklyTask(${task.id})" class="text-slate-500 hover:text-red-400 p-1" title="Excluir">
              <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
            </button>
          </div>

          ${task.reference_links ? `
            <div class="text-[11px] text-slate-400 truncate">
              <a href="${task.reference_links}" target="_blank" class="text-blue-400 hover:underline flex items-center gap-1">
                <i data-lucide="link" class="w-3 h-3"></i> Referência
              </a>
            </div>
          ` : ''}

          <div class="flex items-center justify-between pt-1 border-t border-dark-800">
            <button onclick="toggleTaskStatus(${task.id}, '${task.status}')" class="text-[11px] flex items-center gap-1 font-medium ${isDone ? 'text-emerald-400' : 'text-slate-400 hover:text-white'}">
              <i data-lucide="${isDone ? 'check-circle' : 'circle'}" class="w-3.5 h-3.5"></i>
              <span>${isDone ? 'Concluído' : 'Marcar Concluído'}</span>
            </button>

            <!-- Move to next day button -->
            ${day === 'segunda' ? `
              <button onclick="moveTaskDay(${task.id}, 'terca')" class="text-[10px] text-slate-400 hover:text-amber-400 flex items-center gap-0.5">
                <span>Terça</span> <i data-lucide="arrow-right" class="w-3 h-3"></i>
              </button>
            ` : day === 'terca' ? `
              <button onclick="moveTaskDay(${task.id}, 'quarta')" class="text-[10px] text-slate-400 hover:text-emerald-400 flex items-center gap-0.5">
                <span>Quarta</span> <i data-lucide="arrow-right" class="w-3 h-3"></i>
              </button>
            ` : ''}
          </div>
        </div>
      `;
    }).join('');
  });
  
  lucide.createIcons();
}

async function toggleTaskStatus(taskId, currentStatus) {
  const newStatus = currentStatus === 'completed' ? 'pending' : 'completed';
  try {
    await fetch(`/api/tasks/${taskId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: newStatus })
    });
    await loadWeeklyTasks();
  } catch (e) {
    console.error(e);
  }
}

async function moveTaskDay(taskId, nextDay) {
  try {
    await fetch(`/api/tasks/${taskId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: 'pending', day_column: nextDay })
    });
    await loadWeeklyTasks();
    showToast(`Tarefa movida para ${nextDay.toUpperCase()}!`);
  } catch (e) {
    console.error(e);
  }
}

async function deleteWeeklyTask(taskId) {
  try {
    await fetch(`/api/tasks/${taskId}`, { method: 'DELETE' });
    await loadWeeklyTasks();
    showToast('Tarefa removida.');
  } catch (e) {
    console.error(e);
  }
}

// Add Topic Directly to Weekly Schedule (Segunda)
async function addTopicToWeeklySchedule(topic, hook) {
  const niche = appState.selectedNiche?.name || appState.currentQuery || 'Geral';
  try {
    await fetch('/api/tasks', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        day_column: 'segunda',
        step_name: 'Estudar tema & Roteiro',
        title: topic,
        niche: niche,
        details: hook ? `Gancho sugerido: ${hook}` : ''
      })
    });
    showToast('Ideia adicionada à Segunda-feira no Cronograma!');
  } catch (e) {
    console.error(e);
  }
}

async function addCurrentPackageToWeeklySchedule() {
  if (!appState.currentPackage) return;
  const title = document.getElementById('gen-topic-input').value.trim();
  const niche = document.getElementById('gen-niche-input').value.trim();
  const ref = document.getElementById('gen-reference-input').value.trim();
  
  try {
    await fetch('/api/tasks', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        day_column: 'segunda',
        step_name: 'Pesquisar palavras-chave & Roteiro',
        title: title,
        niche: niche,
        reference_links: ref
      })
    });
    showToast('Vídeo adicionado ao seu Cronograma Semanal!');
  } catch (e) {
    console.error(e);
  }
}

// Modal for manual task creation
function openNewTaskModal() {
  document.getElementById('modal-task').classList.remove('hidden');
}
function closeNewTaskModal() {
  document.getElementById('modal-task').classList.add('hidden');
}
async function submitNewTask() {
  const day = document.getElementById('modal-task-day').value;
  const title = document.getElementById('modal-task-title').value.trim();
  const step = document.getElementById('modal-task-step').value.trim() || 'Produção de Conteúdo';
  const links = document.getElementById('modal-task-links').value.trim();
  
  if (!title) {
    showToast('Preencha o título do vídeo ou tarefa.', true);
    return;
  }
  
  try {
    await fetch('/api/tasks', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        day_column: day,
        step_name: step,
        title: title,
        reference_links: links
      })
    });
    closeNewTaskModal();
    document.getElementById('modal-task-title').value = '';
    document.getElementById('modal-task-links').value = '';
    await loadWeeklyTasks();
    showToast('Nova tarefa criada no cronograma!');
  } catch (e) {
    console.error(e);
  }
}

// Saved Content (Scripts & Ideas)
async function loadSavedContents() {
  const container = document.getElementById('saved-scripts-container');
  if (!container) return;
  
  try {
    const res = await fetch('/api/scripts');
    const data = await res.json();
    appState.savedScripts = data.scripts || [];
    
    if (appState.savedScripts.length === 0) {
      container.innerHTML = `
        <div class="text-center py-12 text-slate-500">
          <i data-lucide="bookmark" class="w-12 h-12 mx-auto mb-2 opacity-30"></i>
          <p class="text-xs">Nenhum roteiro salvo ainda. Gere e salve seus roteiros na aba Gerador IA.</p>
        </div>
      `;
      lucide.createIcons();
      return;
    }
    
    container.innerHTML = appState.savedScripts.map(s => `
      <div class="p-5 bg-dark-850 border border-dark-750 rounded-2xl space-y-3">
        <div class="flex items-start justify-between gap-3">
          <div>
            <span class="text-[10px] px-2 py-0.5 bg-red-500/20 text-red-400 rounded-full font-semibold uppercase">${s.niche}</span>
            <h3 class="text-sm font-bold text-white mt-1">${s.title}</h3>
            <span class="text-[10px] text-slate-500">${new Date(s.created_at).toLocaleDateString('pt-BR')}</span>
          </div>
          <div class="flex items-center gap-1.5">
            <button onclick="copyText('${s.script_body.replace(/'/g, "\\'").replace(/\n/g, "\\n")}', 'Roteiro copiado!')" class="p-2 bg-dark-800 hover:bg-dark-700 text-slate-300 rounded-lg" title="Copiar">
              <i data-lucide="copy" class="w-4 h-4"></i>
            </button>
            <button onclick="deleteSavedScript(${s.id})" class="p-2 bg-dark-800 hover:bg-red-900/30 text-red-400 rounded-lg" title="Excluir">
              <i data-lucide="trash-2" class="w-4 h-4"></i>
            </button>
          </div>
        </div>

        <div class="p-3 bg-dark-950 rounded-xl border border-dark-800 max-h-36 overflow-y-auto text-xs text-slate-300 font-mono whitespace-pre-wrap">
          ${s.script_body}
        </div>
      </div>
    `).join('');
    
    lucide.createIcons();
  } catch (e) {
    console.error(e);
  }
}

async function deleteSavedScript(id) {
  try {
    await fetch(`/api/scripts/${id}`, { method: 'DELETE' });
    await loadSavedContents();
    showToast('Roteiro excluído.');
  } catch (e) {
    console.error(e);
  }
}

// Settings
async function saveApiKeySettings() {
  const key = document.getElementById('settings-api-key-input').value.trim();
  if (!key) return;
  try {
    await fetch('/api/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ nvidia_api_key: key })
    });
    showToast('Chave da API NVIDIA salva com sucesso!');
  } catch (e) {
    console.error(e);
  }
}
