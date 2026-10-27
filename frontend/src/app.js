/**
 * CLARA Web Application Engine
 * Integrates Normalization, Multi-Candidate Recommendation,
 * Explainable Configuration Diffing, and Terraform Code Generation.
 */

// Hardware Catalog Snapshot
const CATALOG = {
  version: "pricing-snapshot-2026-10-18",
  currency: "USD",
  providers: {
    aws: {
      storage_rate: 0.08,
      instances: [
        { type: "t3.nano", vcpu: 2, memory_gb: 0.5, monthly_rate: 3.80, family: "burstable" },
        { type: "t3.micro", vcpu: 2, memory_gb: 1.0, monthly_rate: 7.60, family: "burstable" },
        { type: "t3.small", vcpu: 2, memory_gb: 2.0, monthly_rate: 15.20, family: "burstable" },
        { type: "t3.medium", vcpu: 2, memory_gb: 4.0, monthly_rate: 30.40, family: "burstable" },
        { type: "t3.large", vcpu: 2, memory_gb: 8.0, monthly_rate: 60.80, family: "burstable" },
        { type: "t3.xlarge", vcpu: 4, memory_gb: 16.0, monthly_rate: 121.60, family: "burstable" },
        { type: "t3.2xlarge", vcpu: 8, memory_gb: 32.0, monthly_rate: 243.20, family: "burstable" },
        { type: "c6i.large", vcpu: 2, memory_gb: 4.0, monthly_rate: 62.00, family: "compute_optimized" },
        { type: "c6i.xlarge", vcpu: 4, memory_gb: 8.0, monthly_rate: 124.00, family: "compute_optimized" },
        { type: "m6i.large", vcpu: 2, memory_gb: 8.0, monthly_rate: 70.00, family: "general_purpose" },
        { type: "m6i.xlarge", vcpu: 4, memory_gb: 16.0, monthly_rate: 140.00, family: "general_purpose" },
        { type: "m6i.2xlarge", vcpu: 8, memory_gb: 32.0, monthly_rate: 280.00, family: "general_purpose" },
        { type: "c6i.2xlarge", vcpu: 8, memory_gb: 16.0, monthly_rate: 248.00, family: "compute_optimized" },
        { type: "c6i.4xlarge", vcpu: 16, memory_gb: 32.0, monthly_rate: 496.00, family: "compute_optimized" },
        { type: "m6i.4xlarge", vcpu: 16, memory_gb: 64.0, monthly_rate: 560.00, family: "general_purpose" },
        { type: "c6i.8xlarge", vcpu: 32, memory_gb: 64.0, monthly_rate: 992.00, family: "compute_optimized" },
        { type: "m6i.8xlarge", vcpu: 32, memory_gb: 128.0, monthly_rate: 1120.00, family: "general_purpose" }
      ]
    },
    azure: {
      storage_rate: 0.075,
      instances: [
        { type: "Standard_B1s", vcpu: 1, memory_gb: 1.0, monthly_rate: 7.59, family: "burstable" },
        { type: "Standard_B2s", vcpu: 2, memory_gb: 4.0, monthly_rate: 30.36, family: "burstable" },
        { type: "Standard_B2ms", vcpu: 2, memory_gb: 8.0, monthly_rate: 60.72, family: "burstable" },
        { type: "Standard_B4ms", vcpu: 4, memory_gb: 16.0, monthly_rate: 121.44, family: "burstable" },
        { type: "Standard_B8ms", vcpu: 8, memory_gb: 32.0, monthly_rate: 242.88, family: "burstable" },
        { type: "Standard_D2s_v5", vcpu: 2, memory_gb: 8.0, monthly_rate: 70.08, family: "general_purpose" },
        { type: "Standard_D4s_v5", vcpu: 4, memory_gb: 16.0, monthly_rate: 140.16, family: "general_purpose" },
        { type: "Standard_D8s_v5", vcpu: 8, memory_gb: 32.0, monthly_rate: 280.32, family: "general_purpose" },
        { type: "Standard_D16s_v5", vcpu: 16, memory_gb: 64.0, monthly_rate: 560.64, family: "general_purpose" },
        { type: "Standard_F16s_v2", vcpu: 16, memory_gb: 32.0, monthly_rate: 493.48, family: "compute_optimized" },
        { type: "Standard_D32s_v5", vcpu: 32, memory_gb: 128.0, monthly_rate: 1121.28, family: "general_purpose" }
      ]
    },
    gcp: {
      storage_rate: 0.10,
      instances: [
        { type: "e2-micro", vcpu: 2, memory_gb: 1.0, monthly_rate: 6.11, family: "general_purpose" },
        { type: "e2-small", vcpu: 2, memory_gb: 2.0, monthly_rate: 12.23, family: "general_purpose" },
        { type: "e2-medium", vcpu: 2, memory_gb: 4.0, monthly_rate: 24.46, family: "general_purpose" },
        { type: "e2-standard-2", vcpu: 2, memory_gb: 8.0, monthly_rate: 48.92, family: "general_purpose" },
        { type: "e2-standard-4", vcpu: 4, memory_gb: 16.0, monthly_rate: 97.84, family: "general_purpose" },
        { type: "e2-standard-8", vcpu: 8, memory_gb: 32.0, monthly_rate: 195.68, family: "general_purpose" },
        { type: "e2-standard-16", vcpu: 16, memory_gb: 64.0, monthly_rate: 391.36, family: "general_purpose" },
        { type: "c2-standard-16", vcpu: 16, memory_gb: 64.0, monthly_rate: 490.56, family: "compute_optimized" },
        { type: "e2-standard-32", vcpu: 32, memory_gb: 128.0, monthly_rate: 782.72, family: "general_purpose" }
      ]
    }
  }
};

const REGIONS = {
  aws: { mumbai: "ap-south-1", virginia: "us-east-1", frankfurt: "eu-central-1" },
  azure: { mumbai: "centralindia", virginia: "eastus", europe: "westeurope" },
  gcp: { mumbai: "asia-south1", us: "us-central1", frankfurt: "europe-west3" }
};

// Application State
const state = {
  currentMode: "natural_language",
  canonicalRequest: null,
  recommendations: null,
  selectedCandidate: null,
  showUnchangedDiff: true,
  currentOutputTab: "dsl"
};

let isBackendConnected = false;
const API_BASE = "https://clara-backend-z0ll.onrender.com";

async function checkBackendHealth() {
  const badge = document.getElementById("backend-status-badge");
  const badgeText = document.getElementById("backend-status-text");
  try {
    const res = await fetch(`${API_BASE}/api/health`);
    if (res.ok) {
      const data = await res.json();
      isBackendConnected = true;
      if (badge && badgeText) {
        badge.classList.add("online");
        badgeText.textContent = `Backend Live (${data.version})`;
        badge.title = `Compiler: ${data.compiler_available ? "Ready" : "Unavailable"}`;
      }
      return true;
    }
  } catch (e) {
    isBackendConnected = false;
    if (badge && badgeText) {
      badge.classList.remove("online");
      badgeText.textContent = "Backend Offline (Client-Side Active)";
      badge.title = "Local client-side simulation active";
    }
  }
  return false;
}

// UI Initialization
document.addEventListener("DOMContentLoaded", async () => {
  setupTabs();
  setupSuggestions();
  setupEventListeners();

  await checkBackendHealth();

  // Run initial demo configuration
  await processNaturalLanguage("I need a small AWS web server in Mumbai with 2 vCPUs, 4 GB RAM, and 50 GB storage. Keep the monthly cost low.");
});

function setupTabs() {
  const nlTab = document.getElementById("tab-nl");
  const formTab = document.getElementById("tab-form");
  const nlForm = document.getElementById("nl-form-container");
  const structForm = document.getElementById("struct-form-container");

  nlTab.addEventListener("click", () => {
    nlTab.classList.add("active");
    formTab.classList.remove("active");
    nlForm.style.display = "flex";
    structForm.style.display = "none";
    state.currentMode = "natural_language";
  });

  formTab.addEventListener("click", () => {
    formTab.classList.add("active");
    nlTab.classList.remove("active");
    structForm.style.display = "block";
    nlForm.style.display = "none";
    state.currentMode = "form";
  });

  // Output Code tabs
  document.querySelectorAll(".out-tab").forEach(tab => {
    tab.addEventListener("click", (e) => {
      document.querySelectorAll(".out-tab").forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      state.currentOutputTab = tab.dataset.target;
      renderOutputCode();
    });
  });
}

function setupSuggestions() {
  document.querySelectorAll(".suggestion-pill").forEach(pill => {
    pill.addEventListener("click", async () => {
      const text = pill.dataset.prompt;
      document.getElementById("nl-input").value = text;
      await processNaturalLanguage(text);
    });
  });
}

function setupEventListeners() {
  document.getElementById("btn-submit-nl").addEventListener("click", async () => {
    const text = document.getElementById("nl-input").value.trim();
    await processNaturalLanguage(text);
  });

  document.getElementById("btn-submit-form").addEventListener("click", async (e) => {
    e.preventDefault();
    await processStructuredForm();
  });

  document.getElementById("toggle-unchanged").addEventListener("change", async (e) => {
    state.showUnchangedDiff = e.target.checked;
    await renderDiff();
  });

  document.getElementById("btn-copy-code").addEventListener("click", copyCurrentCode);
}

// Phase 4: Normalization
async function processNaturalLanguage(text) {
  if (!text) return;

  // Attempt to normalize via Backend API
  try {
    const res = await fetch(`${API_BASE}/api/normalize`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mode: "natural_language", input: { text } })
    });
    if (res.ok) {
      const data = await res.json();
      if (data && data.normalized_request) {
        await applyCanonicalRequest(data.normalized_request);
        return;
      }
    }
  } catch (err) {
    console.debug("Backend normalize not reachable, using client-side fallback:", err);
  }

  // Client-side fallback
  const textLower = text.toLowerCase();

  // Provider
  let provider = "aws";
  if (textLower.includes("azure")) provider = "azure";
  else if (textLower.includes("gcp") || textLower.includes("google")) provider = "gcp";

  // Workload
  let workload = "web_server";
  if (textLower.includes("database") || textLower.includes("db") || textLower.includes("sql") || textLower.includes("postgres")) workload = "database";
  else if (textLower.includes("api")) workload = "api_server";

  // Region
  let region = REGIONS[provider].mumbai;
  if (textLower.includes("virginia") || textLower.includes("us-east")) region = REGIONS[provider].virginia || "us-east-1";
  else if (textLower.includes("frankfurt")) region = REGIONS[provider].frankfurt || "eu-central-1";

  // CPU
  let vcpu = 2;
  const cpuMatch = textLower.match(/(\d+)\s*(?:vcpu|core|cpu)/);
  if (cpuMatch) vcpu = parseInt(cpuMatch[1], 10);

  // Memory
  let memory_gb = 4.0;
  const memMatch = textLower.match(/(\d+(?:\.\d+)?)\s*(gb|mb)\s*(?:ram|memory)?/);
  if (memMatch) {
    const val = parseFloat(memMatch[1]);
    memory_gb = memMatch[2] === "mb" ? val / 1024 : val;
  }

  // Storage
  let storage_gb = 50.0;
  const storageMatch = textLower.match(/(\d+(?:\.\d+)?)\s*(gb|tb)\s*(?:storage|disk|ssd)/);
  if (storageMatch) {
    const val = parseFloat(storageMatch[1]);
    storage_gb = storageMatch[2] === "tb" ? val * 1024 : val;
  }

  // Priority
  let priority = "cost";
  if (textLower.includes("performance") || textLower.includes("fast")) priority = "performance";
  else if (textLower.includes("balanced")) priority = "balanced";

  const canonical = {
    schema_version: "1.0",
    provider,
    workload,
    region,
    requirements: {
      vcpu_min: vcpu,
      memory_gb_min: memory_gb,
      storage_gb_min: storage_gb
    },
    optimization: {
      priority,
      monthly_budget: null
    },
    constraints: {
      must_satisfy_all: true
    }
  };

  await applyCanonicalRequest(canonical);
}

async function processStructuredForm() {
  const provider = document.getElementById("form-provider").value;
  const region = document.getElementById("form-region").value;
  const workload = document.getElementById("form-workload").value;
  const vcpu = parseInt(document.getElementById("form-vcpu").value, 10);
  const memory_gb = parseFloat(document.getElementById("form-memory").value);
  const storage_gb = parseFloat(document.getElementById("form-storage").value);
  const priority = document.getElementById("form-priority").value;
  const rawBudget = document.getElementById("form-budget").value;
  const monthly_budget = rawBudget ? parseFloat(rawBudget) : null;

  const rawForm = {
    provider,
    region,
    workload,
    vcpu_min: vcpu,
    memory_gb_min: memory_gb,
    storage_gb_min: storage_gb,
    priority,
    monthly_budget
  };

  // Attempt Backend API form normalization
  try {
    const res = await fetch(`${API_BASE}/api/normalize`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mode: "form", input: rawForm })
    });
    if (res.ok) {
      const data = await res.json();
      if (data && data.normalized_request) {
        await applyCanonicalRequest(data.normalized_request);
        return;
      }
    }
  } catch (err) {
    console.debug("Backend form normalize not reachable, using fallback:", err);
  }

  const canonical = {
    schema_version: "1.0",
    provider,
    workload,
    region,
    requirements: {
      vcpu_min: vcpu,
      memory_gb_min: memory_gb,
      storage_gb_min: storage_gb
    },
    optimization: {
      priority,
      monthly_budget
    },
    constraints: {
      must_satisfy_all: true
    }
  };

  await applyCanonicalRequest(canonical);
}

async function applyCanonicalRequest(canonical) {
  state.canonicalRequest = canonical;
  document.getElementById("canonical-json-preview").textContent = JSON.stringify(canonical, null, 2);

  // Phase 5: Alternatives Generation
  await generateAlternatives(canonical);
}

// Phase 5: Alternative Generation Engine
async function generateAlternatives(req) {
  // Attempt to fetch from Backend API
  try {
    const res = await fetch(`${API_BASE}/api/recommend`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(req)
    });
    if (res.ok) {
      const data = await res.json();
      if (data && data.status === "INFEASIBLE") {
        const alertContainer = document.getElementById("diagnostics-alert");
        if (alertContainer) {
          alertContainer.style.display = "block";
          alertContainer.className = "alert-box alert-error";
          alertContainer.innerHTML = `<strong>Infeasible Request:</strong> ${data.message || "Declared constraints cannot be satisfied by catalogue."}`;
        }
        document.getElementById("candidates-cards-container").innerHTML = "";
        document.getElementById("diff-table-body").innerHTML = "";
        return;
      }
      if (data && data.candidates && data.candidates.length > 0) {
        state.recommendations = data.candidates;
        const recId = data.recommended_candidate_id || "A";
        state.selectedCandidate = data.candidates.find(c => c.candidate_id === recId) || data.candidates[0];

        const alertContainer = document.getElementById("diagnostics-alert");
        if (alertContainer) alertContainer.style.display = "none";

        renderCandidateCards();
        await renderDiff();
        await renderOutputCode();
        return;
      }
    }
  } catch (err) {
    console.debug("Backend API recommend not available, using client-side fallback:", err);
  }
  const providerData = CATALOG.providers[req.provider] || CATALOG.providers.aws;
  const storageRate = providerData.storage_rate;
  const instances = providerData.instances;
  const storageGb = req.requirements.storage_gb_min;
  const vcpuMin = req.requirements.vcpu_min;
  const memMin = req.requirements.memory_gb_min;
  const budget = req.optimization.monthly_budget;

  const feasible = [];

  for (const inst of instances) {
    const vcpuPass = inst.vcpu >= vcpuMin;
    const memPass = inst.memory_gb >= memMin;
    const computeCost = inst.monthly_rate;
    const storageCost = storageGb * storageRate;
    const totalCost = Number((computeCost + storageCost).toFixed(2));
    const budgetPass = budget ? totalCost <= budget : true;

    if (vcpuPass && memPass && budgetPass) {
      feasible.push({
        instance: inst,
        vcpu: inst.vcpu,
        memory_gb: inst.memory_gb,
        storage_gb: storageGb,
        compute_cost: computeCost,
        storage_cost: storageCost,
        total_monthly_cost: totalCost
      });
    }
  }

  const alertContainer = document.getElementById("diagnostics-alert");
  if (feasible.length === 0) {
    alertContainer.style.display = "block";
    alertContainer.className = "alert-box alert-error";
    if (budget !== null && budget !== undefined && budget > 0) {
      alertContainer.innerHTML = `<strong>Infeasible Request:</strong> Declared monthly budget of $${budget.toFixed(2)} cannot satisfy minimum specifications (${vcpuMin} vCPU, ${memMin} GB RAM). Please increase budget.`;
    } else {
      const maxVcpu = Math.max(...instances.map(i => i.vcpu));
      const maxMem = Math.max(...instances.map(i => i.memory_gb));
      alertContainer.innerHTML = `<strong>Infeasible Request:</strong> No single instance in the ${req.provider.toUpperCase()} catalogue satisfies minimum requirements (${vcpuMin} vCPU, ${memMin} GB RAM). Maximum available size is ${maxVcpu} vCPU, ${maxMem} GB RAM.`;
    }
    document.getElementById("candidates-cards-container").innerHTML = "";
    document.getElementById("diff-table-body").innerHTML = "";
    return;
  } else {
    alertContainer.style.display = "none";
  }

  feasible.sort((a, b) => a.total_monthly_cost - b.total_monthly_cost);

  const candA = feasible[0];
  const candC = feasible[feasible.length - 1];
  const midIdx = Math.floor(feasible.length / 2);
  const candB = feasible[midIdx];

  const candidates = [
    {
      candidate_id: "A",
      profile: "cost_optimized",
      instance_type: candA.instance.type,
      family: candA.instance.family,
      resources: { vcpu: candA.vcpu, memory_gb: candA.memory_gb, storage_gb: candA.storage_gb },
      cost: { total_monthly: candA.total_monthly_cost, currency: "USD" },
      summary: "Lowest price point meeting hard minimum requirements.",
      tradeoff: "Baseline compute capacity. Ideal for dev, staging, or low traffic."
    },
    {
      candidate_id: "B",
      profile: "balanced",
      instance_type: candB.instance.type,
      family: candB.instance.family,
      resources: { vcpu: candB.vcpu, memory_gb: candB.memory_gb, storage_gb: candB.storage_gb },
      cost: { total_monthly: candB.total_monthly_cost, currency: "USD" },
      summary: "Balanced headroom: extra vCPU and RAM buffer for spike tolerance.",
      tradeoff: "Optimal balance between cost efficiency and operational stability."
    },
    {
      candidate_id: "C",
      profile: "performance_focused",
      instance_type: candC.instance.type,
      family: candC.instance.family,
      resources: { vcpu: candC.vcpu, memory_gb: candC.memory_gb, storage_gb: candC.storage_gb },
      cost: { total_monthly: candC.total_monthly_cost, currency: "USD" },
      summary: "Maximum throughput: highest compute cores and memory allocation.",
      tradeoff: "Highest monthly cost, delivers superior concurrency throughput."
    }
  ];

  // Priority sort
  if (req.optimization.priority === "performance") {
    candidates.sort((a, b) => b.resources.vcpu - a.resources.vcpu || b.resources.memory_gb - a.resources.memory_gb);
  } else if (req.optimization.priority === "balanced") {
    const order = { balanced: 0, cost_optimized: 1, performance_focused: 2 };
    candidates.sort((a, b) => order[a.profile] - order[b.profile]);
  } else {
    candidates.sort((a, b) => a.cost.total_monthly - b.cost.total_monthly);
  }

  state.recommendations = candidates;
  state.selectedCandidate = candidates[0]; // Default select recommended

  renderCandidateCards();
  renderDiff();
  renderOutputCode();
}

function renderCandidateCards() {
  const container = document.getElementById("candidates-cards-container");
  container.innerHTML = "";

  state.recommendations.forEach((c, idx) => {
    const isRec = idx === 0;
    const isSelected = state.selectedCandidate && state.selectedCandidate.candidate_id === c.candidate_id;

    const card = document.createElement("div");
    card.className = `candidate-card ${isRec ? "recommended" : ""} ${isSelected ? "selected" : ""}`;
    card.onclick = async () => {
      state.selectedCandidate = c;
      renderCandidateCards();
      await renderDiff();
      await renderOutputCode();
    };

    const profTitle = c.profile.replace("_", " ");

    card.innerHTML = `
      ${isRec ? `<div class="card-badge">RECOMMENDED</div>` : ""}
      <div>
        <div class="card-profile">${profTitle}</div>
        <div class="card-title">${c.instance_type}</div>
        <div class="card-cost">
          <span class="cost-amount">$${c.cost.total_monthly.toFixed(2)}</span>
          <span class="cost-period">/ month (${c.cost.currency})</span>
        </div>
        <div class="spec-list">
          <div class="spec-item"><span>vCPU Cores</span><strong>${c.resources.vcpu} Cores</strong></div>
          <div class="spec-item"><span>Memory / RAM</span><strong>${c.resources.memory_gb} GB</strong></div>
          <div class="spec-item"><span>Storage Volume</span><strong>${c.resources.storage_gb} GB</strong></div>
          <div class="spec-item"><span>Hardware Family</span><strong>${c.family}</strong></div>
        </div>
        <div class="card-tradeoff">${c.summary}</div>
      </div>
      <button class="btn-select-cand" type="button">
        ${isSelected ? "✓ Selected for Diff" : "Inspect Configuration"}
      </button>
    `;

    container.appendChild(card);
  });
}

// Phase 6: Explainable Diff Engine
async function renderDiff() {
  const req = state.canonicalRequest;
  const cand = state.selectedCandidate;
  if (!req || !cand) return;

  const tbody = document.getElementById("diff-table-body");
  tbody.innerHTML = "";

  // Attempt to fetch from Backend API
  try {
    const res = await fetch(`${API_BASE}/api/diff`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        original_request: req,
        candidate: cand,
        include_unchanged: state.showUnchangedDiff
      })
    });
    if (res.ok) {
      const data = await res.json();
      const allChanges = [...(data.changes || [])];
      if (state.showUnchangedDiff && data.unchanged) {
        data.unchanged.forEach(u => {
          allChanges.push({
            field: u.field,
            display_name: u.display_name,
            change_type: "unchanged",
            old_value: u.value,
            new_value: u.value,
            unit: u.unit,
            reason: u.reason,
            rule_id: u.rule_id
          });
        });
      }
      if (allChanges.length > 0) {
        allChanges.forEach(item => {
          const isMod = item.change_type === "modified";
          const isAdd = item.change_type === "added";
          const actionClass = isMod ? "tag-modified" : isAdd ? "tag-added" : "tag-unchanged";
          const actionText = item.change_type.toUpperCase();

          const unitStr = item.unit ? ` ${item.unit}` : "";
          const origStr = item.old_value !== null && item.old_value !== undefined ? `${item.old_value}${unitStr}` : "—";
          const recStr = item.new_value !== null && item.new_value !== undefined ? `${item.new_value}${unitStr}` : "—";

          const tr = document.createElement("tr");
          tr.innerHTML = `
            <td><strong>${item.display_name || item.field}</strong></td>
            <td>${origStr}</td>
            <td><strong>${recStr}</strong></td>
            <td><span class="tag-badge ${actionClass}">${actionText}</span></td>
            <td>${item.reason} <span class="rule-badge">${item.rule_id}</span></td>
          `;
          tbody.appendChild(tr);
        });
        return;
      }
    }
  } catch (err) {
    console.debug("Backend diff not reachable, using client-side fallback:", err);
  }

  const diffItems = [];

  // vCPU
  const origVcpu = req.requirements.vcpu_min;
  const newVcpu = cand.resources.vcpu;
  if (origVcpu !== newVcpu) {
    diffItems.push({
      field: "vCPU Cores",
      original: `${origVcpu} Cores`,
      recommended: `${newVcpu} Cores`,
      action: "MODIFIED",
      actionClass: "tag-modified",
      reason: `Increased from ${origVcpu} to ${newVcpu} cores to provide headroom for concurrent workload spikes.`,
      ruleId: "WORKLOAD_CPU_HEADROOM"
    });
  } else {
    diffItems.push({
      field: "vCPU Cores",
      original: `${origVcpu} Cores`,
      recommended: `${newVcpu} Cores`,
      action: "UNCHANGED",
      actionClass: "tag-unchanged",
      reason: "Exact match with declared requirement.",
      ruleId: "EXACT_MATCH"
    });
  }

  // Memory
  const origMem = req.requirements.memory_gb_min;
  const newMem = cand.resources.memory_gb;
  if (origMem !== newMem) {
    diffItems.push({
      field: "Memory / RAM",
      original: `${origMem} GB`,
      recommended: `${newMem} GB`,
      action: "MODIFIED",
      actionClass: "tag-modified",
      reason: `Allocated ${newMem} GB RAM (up from ${origMem} GB) to ensure operational buffer and match instance ratios.`,
      ruleId: "WORKLOAD_MEMORY_HEADROOM"
    });
  } else {
    diffItems.push({
      field: "Memory / RAM",
      original: `${origMem} GB`,
      recommended: `${newMem} GB`,
      action: "UNCHANGED",
      actionClass: "tag-unchanged",
      reason: "Exact match with declared requirement.",
      ruleId: "EXACT_MATCH"
    });
  }

  // Storage
  const origStorage = req.requirements.storage_gb_min;
  const newStorage = cand.resources.storage_gb;
  if (origStorage !== newStorage) {
    diffItems.push({
      field: "Storage Volume",
      original: `${origStorage} GB`,
      recommended: `${newStorage} GB`,
      action: "MODIFIED",
      actionClass: "tag-modified",
      reason: `Scaled storage to ${newStorage} GB.`,
      ruleId: "STORAGE_ALIGNMENT"
    });
  } else {
    diffItems.push({
      field: "Storage Volume",
      original: `${origStorage} GB`,
      recommended: `${newStorage} GB`,
      action: "UNCHANGED",
      actionClass: "tag-unchanged",
      reason: "Exact match with declared requirement.",
      ruleId: "EXACT_MATCH"
    });
  }

  // Instance Type (Added)
  diffItems.push({
    field: "Hardware Instance",
    original: "— (User Defined)",
    recommended: cand.instance_type,
    action: "ADDED",
    actionClass: "tag-added",
    reason: `Mapped to provider instance shape '${cand.instance_type}' based on capacity and pricing.`,
    ruleId: "INSTANCE_MAPPING"
  });

  // Estimated Cost (Added)
  diffItems.push({
    field: "Estimated Monthly Cost",
    original: "— (Unpriced)",
    recommended: `$${cand.cost.total_monthly.toFixed(2)} USD`,
    action: "ADDED",
    actionClass: "tag-added",
    reason: `Calculated from catalogue snapshot: compute ($${cand.instance.monthly_rate}) + storage ($${(cand.resources.storage_gb * CATALOG.providers[req.provider].storage_rate).toFixed(2)}).`,
    ruleId: "COST_ESTIMATION"
  });

  diffItems.forEach(item => {
    if (!state.showUnchangedDiff && item.action === "UNCHANGED") {
      return;
    }

    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><strong>${item.field}</strong></td>
      <td>${item.original}</td>
      <td><strong>${item.recommended}</strong></td>
      <td><span class="tag-badge ${item.actionClass}">${item.action}</span></td>
      <td>${item.reason} <span class="rule-badge">${item.ruleId}</span></td>
    `;
    tbody.appendChild(tr);
  });
}

// Phase 3 & 4: Code Generation & Exporters
async function renderOutputCode() {
  const req = state.canonicalRequest;
  const cand = state.selectedCandidate;
  if (!req || !cand) return;

  const codeBlock = document.getElementById("generated-code-block");
  const codeTitle = document.getElementById("code-title-text");

  const vcpu = cand.resources ? cand.resources.vcpu : 2;
  const mem = cand.resources ? cand.resources.memory_gb : 4;
  const stg = cand.resources ? cand.resources.storage_gb : 50;
  const instType = cand.instance_type || "t3.medium";

  const claraDsl = `CLOUD ${req.provider.toUpperCase()} {
    REGION ${req.region}

    SERVER ${req.workload} {
        CPU ${vcpu}
        MEMORY ${mem}GB
        STORAGE ${stg}GB
    }
}`;

  if (state.currentOutputTab === "dsl") {
    codeTitle.textContent = "clara_specification.clara";
    codeBlock.textContent = claraDsl;
    return;
  }

  // Live compilation via native clara.exe compiler backend
  if (isBackendConnected) {
    try {
      const res = await fetch(`${API_BASE}/api/compile`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          source: claraDsl,
          target: state.currentOutputTab
        })
      });
      if (res.ok) {
        const result = await res.json();
        if (result.status === "SUCCESS" && result.output) {
          if (state.currentOutputTab === "ir") {
            codeTitle.textContent = "intermediate_representation.json (Compiled by CLARA C Backend)";
          } else if (state.currentOutputTab === "terraform") {
            codeTitle.textContent = "main.tf (Compiled by CLARA C Backend)";
          }
          codeBlock.textContent = result.output;
          return;
        }
      }
    } catch (e) {
      console.debug("Compiler API not reachable, fallback to template:", e);
    }
  }

  if (state.currentOutputTab === "ir") {
    codeTitle.textContent = "intermediate_representation.json";
    const irObj = {
      schema_version: "1.0",
      provider: req.provider,
      region: req.region,
      resources: {
        servers: [
          {
            name: req.workload,
            cpu: vcpu,
            memory_gb: mem,
            storage_gb: stg,
            instance_type: instType
          }
        ]
      }
    };
    codeBlock.textContent = JSON.stringify(irObj, null, 2);
  } else if (state.currentOutputTab === "terraform") {
    codeTitle.textContent = "main.tf";
    codeBlock.textContent = `# Automatically generated by CLARA Compiler
# Target: ${req.provider.toUpperCase()} | Region: ${req.region}

provider "${req.provider}" {
  region = "${req.region}"
}

resource "${req.provider}_instance" "${req.workload}" {
  ami           = "ami-0c55b159cbfafe1f0" # Ubuntu 22.04 LTS
  instance_type = "${instType}" # ${vcpu} vCPU, ${mem} GB RAM

  root_block_device {
    volume_size = ${stg} # GB
    volume_type = "gp3"
  }

  tags = {
    Name = "${req.workload}"
    ManagedBy = "CLARA"
  }
}`;
  }
}

function copyCurrentCode() {
  const code = document.getElementById("generated-code-block").textContent;
  navigator.clipboard.writeText(code).then(() => {
    const btn = document.getElementById("btn-copy-code");
    const orig = btn.textContent;
    btn.textContent = "Copied!";
    setTimeout(() => { btn.textContent = orig; }, 1800);
  });
}
