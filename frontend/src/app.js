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
        { type: "m6i.2xlarge", vcpu: 8, memory_gb: 32.0, monthly_rate: 280.00, family: "general_purpose" }
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
        { type: "Standard_D4s_v5", vcpu: 4, memory_gb: 16.0, monthly_rate: 140.16, family: "general_purpose" }
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
        { type: "e2-standard-8", vcpu: 8, memory_gb: 32.0, monthly_rate: 195.68, family: "general_purpose" }
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

// UI Initialization
document.addEventListener("DOMContentLoaded", () => {
  setupTabs();
  setupSuggestions();
  setupEventListeners();

  // Run initial demo configuration
  processNaturalLanguage("I need a small AWS web server in Mumbai with 2 vCPUs, 4 GB RAM, and 50 GB storage. Keep the monthly cost low.");
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
    pill.addEventListener("click", () => {
      const text = pill.dataset.prompt;
      document.getElementById("nl-input").value = text;
      processNaturalLanguage(text);
    });
  });
}

function setupEventListeners() {
  document.getElementById("btn-submit-nl").addEventListener("click", () => {
    const text = document.getElementById("nl-input").value.trim();
    processNaturalLanguage(text);
  });

  document.getElementById("btn-submit-form").addEventListener("click", (e) => {
    e.preventDefault();
    processStructuredForm();
  });

  document.getElementById("toggle-unchanged").addEventListener("change", (e) => {
    state.showUnchangedDiff = e.target.checked;
    renderDiff();
  });

  document.getElementById("btn-copy-code").addEventListener("click", copyCurrentCode);
}

// Phase 4: Normalization
function processNaturalLanguage(text) {
  if (!text) return;
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

  applyCanonicalRequest(canonical);
}

function processStructuredForm() {
  const provider = document.getElementById("form-provider").value;
  const region = document.getElementById("form-region").value;
  const workload = document.getElementById("form-workload").value;
  const vcpu = parseInt(document.getElementById("form-vcpu").value, 10);
  const memory_gb = parseFloat(document.getElementById("form-memory").value);
  const storage_gb = parseFloat(document.getElementById("form-storage").value);
  const priority = document.getElementById("form-priority").value;
  const rawBudget = document.getElementById("form-budget").value;
  const monthly_budget = rawBudget ? parseFloat(rawBudget) : null;

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

  applyCanonicalRequest(canonical);
}

function applyCanonicalRequest(canonical) {
  state.canonicalRequest = canonical;
  document.getElementById("canonical-json-preview").textContent = JSON.stringify(canonical, null, 2);

  // Phase 5: Alternatives Generation
  generateAlternatives(canonical);
}

// Phase 5: Alternative Generation Engine
function generateAlternatives(req) {
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
    alertContainer.innerHTML = `<strong>Infeasible Request:</strong> Declared budget of $${budget}/mo cannot satisfy minimum specifications (${vcpuMin} vCPU, ${memMin} GB RAM). Please increase budget.`;
    document.getElementById("candidates-cards-container").innerHTML = "";
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
    card.onclick = () => {
      state.selectedCandidate = c;
      renderCandidateCards();
      renderDiff();
      renderOutputCode();
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
function renderDiff() {
  const req = state.canonicalRequest;
  const cand = state.selectedCandidate;
  if (!req || !cand) return;

  const tbody = document.getElementById("diff-table-body");
  tbody.innerHTML = "";

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
function renderOutputCode() {
  const req = state.canonicalRequest;
  const cand = state.selectedCandidate;
  if (!req || !cand) return;

  const codeBlock = document.getElementById("generated-code-block");
  const codeTitle = document.getElementById("code-title-text");

  if (state.currentOutputTab === "dsl") {
    codeTitle.textContent = "clara_specification.clara";
    codeBlock.textContent = `CLOUD ${req.provider.toUpperCase()} {
    REGION ${req.region}

    SERVER ${req.workload} {
        CPU ${cand.resources.vcpu}
        MEMORY ${cand.resources.memory_gb}GB
        STORAGE ${cand.resources.storage_gb}GB
    }
}`;
  } else if (state.currentOutputTab === "ir") {
    codeTitle.textContent = "intermediate_representation.json";
    const irObj = {
      schema_version: "1.0",
      provider: req.provider,
      region: req.region,
      resources: {
        servers: [
          {
            name: req.workload,
            cpu: cand.resources.vcpu,
            memory_gb: cand.resources.memory_gb,
            storage_gb: cand.resources.storage_gb,
            instance_type: cand.instance_type
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
  instance_type = "${cand.instance_type}" # ${cand.resources.vcpu} vCPU, ${cand.resources.memory_gb} GB RAM

  root_block_device {
    volume_size = ${cand.resources.storage_gb} # GB
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
