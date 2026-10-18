# CLARA Frontend — Configuration Studio & Landing Page

The CLARA web frontend provides an interactive, glassmorphic Configuration Studio and product landing page adhering to the design specifications defined in `CLARA_Project_Progress_and_Design_Requirements.md`.

---

## 🎨 Visual Aesthetics & Design System

- **Color Palette**: Warm dark-brown to amber gradient (`#120702` → `#3b1a08` → `#8a4a12` → `#d98a2b`).
- **Glassmorphism**: Translucent panels (`rgba(28, 14, 6, 0.68)`), thin light borders, soft multi-layer shadows, and `backdrop-filter: blur(24px)`.
- **Atmospheric Glow**: Ambient floating radial gradient orbs simulating soft clouds.
- **Typography**: Clean modern sans-serif using Google Fonts **Poppins**.
- **Accessibility**: Keyboard navigable, visible focus states, high contrast text ratios, and `prefers-reduced-motion` compliance.

---

## 🚀 Key Features

1. **Dual-Mode Input Normalization (Novelty 1)**:
   - Toggle between **Natural Language** (unstructured text prompts) and **Structured Form** input.
   - Real-time normalization to canonical JSON (`schema_version = "1.0"`).
2. **Constraint-Aware Alternatives (Novelty 2)**:
   - Evaluates multi-cloud hardware catalogue (AWS, Azure, GCP).
   - Produces three distinct feasible candidates: **Cost-Optimized (A)**, **Balanced (B)**, and **Performance-Focused (C)**.
   - Shows itemized monthly cost ($/mo), resource specs, and trade-offs.
3. **Explainable Configuration Diff (Novelty 3)**:
   - Compares user input against the selected candidate.
   - Renders grounded rule justifications (`WORKLOAD_MEMORY_HEADROOM`, `WORKLOAD_CPU_HEADROOM`, `INSTANCE_MAPPING`, etc.).
   - Interactive toggle to show or hide unchanged dimensions.
4. **Compiler Artifacts & Code Export**:
   - Synthesizes live **CLARA DSL (`.clara`)**, **Intermediate Representation (`IR JSON`)**, and **Terraform HCL (`main.tf`)**.
   - One-click copy to clipboard.

---

## 💻 Running the Web UI

You can serve the frontend locally using any static web server:

### Option 1: Python HTTP Server (Zero Dependencies)
```powershell
# From the project root:
python -m http.server 8000 --directory frontend
```
Then open: [http://localhost:8000](http://localhost:8000)

### Option 2: Node.js (npx serve)
```powershell
npx serve frontend
```

Or simply open `frontend/index.html` directly in any modern web browser!
