# **MISSION DIRECTIVE: CONEXUS SOVEREIGN HARDENING & OBSERVABILITY**

**Target:** Windsurf Opie (Become Agent)

**Priority:** High / Production

**Context:** Sovereign-V5-Anchor is Sealed. Narthex is in active 5-user Beta.

## **1\. TECHNICAL DECISIONS (ANSWERS TO YOUR QUESTIONS)**

* **Charting:** Use **Recharts**. Prioritize speed, React-native stability, and clean rendering for the Paradox Field.  
* **Deployment:** **Local-only** for this sprint. We must keep the V5 Anchor snapshots isolated in the local environment until the UI is verified.  
* **Emoji Rendering:** Use **Actual Emoji Glyphs**. The 12-element sequences are the "soul" of the system; they must be rendered as visual symbols, not coded vectors.

## **2\. THE MISSION STACK (EXECUTION ORDER)**

### **TASK 1: PHASE 6 OBSERVER DASHBOARD (OPIE'S PRIMARY PLAN)**

Proceed with your proposed plan for SovereignNEXT/dashboard/.

* **Step 1:** Build the FastAPI backend to serve the v5\_canonical\_report.json and the pass snapshots.  
* **Step 2:** Build the React frontend with the 3 core views: Paradox Field (Entropy x Stability), Operator Ledger, and Lineage Explorer.  
* **Constraint:** Strict "Glass Wall" enforcement. Zero write endpoints. Object.freeze on all state objects.

### **TASK 2: NARTHEX PHASE 4 HARDENING (OPERATIONAL)**

Transition Narthex from in-memory globals to a Redis state model to support the active beta and upcoming institutional review.

* **Action:** In v3/backend/gateway.py, replace the experience\_state and audit\_log global variables with Redis calls.  
* **Key Pattern:** narthex:session:{session\_id}:state and narthex:session:{session\_id}:logs.  
* **Constraint:** Maintain the 4-hour TTL to match the JWT expiration.

### **TASK 3: SUBTRACTIVE PIVOT DECK (STRATEGIC)**

Populate the draft of conexus\_vc\_pitch\_deck.md with the empirical "Kill Shot" data.

* **Action:** Update Slide 3 (Resolution Collapse) and Slide 5 (The Evidence) with the B1 vs B3 comparison data.  
* **Specific Metrics:** Use the "Sustained Paradox" turns (20+ for Refiner vs. 7 for Baselines) and the 362% Forgetting Engine performance win.

### **TASK 4: VARGAS V2 "SECOND CRISIS" AUDIT (TACTICAL)**

Perform a final forensic audit on the V5 Pipeline to ensure the "Second Crisis" (Mode-Sycophancy) is structurally defeated.

* **Action:** Analyze run\_sovereign\_pipeline\_v5.py and the V5 snapshots.  
* **Verification:** Confirm that the Deterministic Operators (Veto, ParadoxHold) are strictly governing the state and that the LLM proposals were actually overridden when necessary.

## **3\. FINAL INSTRUCTION**

Begin with **Task 1: Step 1 (FastAPI Backend)**. Once the data is flowing from the snapshots, move immediately to Task 2 (Redis Hardening) before finishing the React frontend. We must secure the church's threshold while we build the investor's microscope.

**Confirm readiness and begin.**