# OpenIRM Dashboard Manual QA Checklist & Verification Guide

**Phase**: Week 11 & Week 11B Deliverable Verification  
**Author**: OpenIRM Core Team  
**Date**: 2026-08-31  
**Scope**: Full end-to-end user experience and interactive pipeline verification (`frontend/` React app against `backend/` FastAPI REST API).

---

## 1. Prerequisites & Environment Setup

Before starting the manual walkthrough, ensure both the backend service and the frontend development server are running locally.

### Step 1.1: Start FastAPI Backend Service
Open Terminal 1:
```bash
# Windows
backend\venv\Scripts\activate
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```
- [ ] Verify terminal displays: `Application startup complete.` and `Uvicorn running on http://127.0.0.1:8000`.
- [ ] Open `http://127.0.0.1:8000/docs` in your browser to verify Swagger UI loads.

### Step 1.2: Start React Vite Frontend
Open Terminal 2:
```bash
cd frontend
npm run dev
```
- [ ] Verify terminal displays: `VITE v5.4.21 ready in ... ms` on `http://localhost:3000` (or `5173`).
- [ ] Open `http://localhost:3000` in Google Chrome or Edge.

---

## 2. Navigation & Global Shell QA

| # | Test Action | Expected Result | Pass / Fail |
|---|-------------|-----------------|:-----------:|
| 2.1 | View Top Navbar | OpenIRM logo badge displayed with "v0.1-MVP" pill. FastApi 8000 live status indicator is visible with a green pulsing dot. | [ ] |
| 2.2 | Click Navigation Links | Clicking `Overview`, `User Drilldown`, `Policy Feed`, and `Analyst Feedback` switches routes cleanly with active tab highlight and no full page reload. | [ ] |
| 2.3 | GitHub External Link | Clicking the GitHub icon in the top right opens the repository in a new browser tab. | [ ] |
| 2.4 | Footer | Displays copyright citation (`Koli et al., arXiv:2505.03796`) and `MIT License • Free Tier Architecture`. | [ ] |

---

## 3. Page 1: Overview SOC Dashboard (`/`)

| # | Test Action | Expected Result | Pass / Fail |
|---|-------------|-----------------|:-----------:|
| 3.1 | Initial Load | Displays brief spinner: *"Aggregating real-time telemetry from PRISM & AIRS engines..."* before rendering. | [ ] |
| 3.2 | KPI Stat Cards | 4 cards render: **Monitored Entities** (total count), **Elevated Threats** (High + Critical count), **Mean Fleet Risk** (floating decimal), and **Active Policy Alerts** (rule trigger count). | [ ] |
| 3.3 | Risk Tier Distribution Chart | Recharts Bar Chart renders 4 risk columns (`LOW` green, `MODERATE` amber, `HIGH` orange, `CRITICAL` rose). Hovering over bars displays accurate tooltip counts. | [ ] |
| 3.4 | Policy Violations Donut Chart | Recharts Pie/Donut Chart displays severity breakdown with color-coded legend at bottom. | [ ] |
| 3.5 | Top 10 High-Risk Entities Table | Table lists up to 10 employees sorted descending by `latest_score`. Displays employee ID, role/department, score progress bar, color-coded `RiskBadge`, and alert counter. | [ ] |
| 3.6 | Drilldown Button | Clicking the blue `Drilldown →` button on any row navigates directly to `/users/{userId}` with that employee pre-selected. | [ ] |
| 3.7 | Refresh Feed Button | Clicking `Refresh Feed` triggers `refetch()` and refreshes metrics without errors. | [ ] |

---

## 4. Page 2: Entity Risk Drilldown (`/users/:userId`)

| # | Test Action | Expected Result | Pass / Fail |
|---|-------------|-----------------|:-----------:|
| 4.1 | Route Loading | Loading `/users/ACM2278` loads profile card with user name, role, department, violation count, and total telemetry days. | [ ] |
| 4.2 | User Selector Dropdown | Selecting a different user from the dropdown switches the profile, updates the URL, and refreshes the timeline. | [ ] |
| 4.3 | Search Input | Typing in `Search employee...` filters the dropdown list in real time by name, user ID, or job title. | [ ] |
| 4.4 | Longitudinal Activity Timeline | Multi-line Recharts graph plots `Ensemble (blue)`, `AIRS Anomaly (orange dashed)`, and `PRISM Rules (grey)`. Reference lines mark Critical (0.8) and High (0.6) risk boundaries. | [ ] |
| 4.5 | Timeline Tooltips | Hovering over data points on the line chart displays date, Ensemble score, AIRS score, and PRISM score. | [ ] |
| 4.6 | Date Selector Pills | Clicking any date pill underneath the chart updates the active event analysis section to that specific activity record. | [ ] |
| 4.7 | Multi-Model Score Banner | Event Analysis banner displays Activity ID, date tag, RiskBadge, and numerical scores for Ensemble, AIRS, and PRISM. | [ ] |

---

## 5. Tab 1: SHAP Explainability (XAI) Panel

| # | Test Action | Expected Result | Pass / Fail |
|---|-------------|-----------------|:-----------:|
| 5.1 | Base Metrics Header | Displays `Base Value` (reference error), `SAI` (normalized score), and `MSE` (reconstruction error). | [ ] |
| 5.2 | Key Attribution Insight | Displays plain-English incident attribution summary card (e.g. *"High volume USB file transfers drive 42.5% of positive anomaly lift"*). | [ ] |
| 5.3 | SHAP Horizontal Bar Chart | Renders horizontal bars for top feature contributions. Positive risk elevators are rendered in **red/rose**, negative baseline suppressors in **green/emerald**. | [ ] |
| 5.4 | SHAP Tooltips | Hovering over any feature bar reveals full feature name, exact SHAP attribution value ($\phi_i$), observed feature value, and percentage contribution. | [ ] |
| 5.5 | Top Flagged Risk Drivers | Grid cards at bottom highlight the top 3 dominant risk drivers with impact ratings. | [ ] |

---

## 6. Tab 2: Groq LLM Threat Intelligence Assessment

| # | Test Action | Expected Result | Pass / Fail |
|---|-------------|-----------------|:-----------:|
| 6.1 | Header & Urgency Pill | Displays *"AI Threat Intelligence & Action Guidance"*, Groq Cloud LLM badge, and color-coded urgency level (`CRITICAL`, `HIGH`, etc.). | [ ] |
| 6.2 | Recommended Action Banner | Blue callout box explicitly highlights the AI's containment directive (e.g., *"Initiate immediate forensic image of endpoint and revoke USB access"*). | [ ] |
| 6.3 | Incident Narrative | Paragraph summarizing the behavioral sequence leading to the risk score elevation. | [ ] |
| 6.4 | Threat Vector Cards | Cards display each identified threat vector with risk impact rating and specific contextual description. | [ ] |

---

## 7. Tab 3 & Dedicated Page: Analyst Score Calibration (`/feedback`)

| # | Test Action | Expected Result | Pass / Fail |
|---|-------------|-----------------|:-----------:|
| 7.1 | Embedded Calibration View | Clicking `Analyst Calibration` tab inside User Drilldown renders the score adjustment form pre-populated with target user ID, Activity ID, and current score. | [ ] |
| 7.2 | Interactive ScoreSlider | Dragging the slider smoothly updates the numerical display ($0.00$ to $1.00$) and changes the tier label and color dynamically (`LOW` -> `MODERATE` -> `HIGH` -> `CRITICAL`). | [ ] |
| 7.3 | Preset Buttons | Clicking preset buttons (`Low 0.15`, `Moderate 0.45`, `High 0.70`, `Critical 0.90`) immediately jumps the slider to that exact value. | [ ] |
| 7.4 | Investigation Notes Input | Analyst can type notes explaining why the risk score was adjusted (e.g., *"Authorized red team drill"*). | [ ] |
| 7.5 | Feedback Submission | Clicking `Commit Risk Score Adjustment` submits to `POST /api/v1/feedback`. | [ ] |
| 7.6 | Mathematical Blending Result | Green confirmation panel appears displaying: Original AI Score, Analyst Adjusted Score, and Mathematically Blended Score ($S_{\text{final}} = (1-\alpha)S_{AI} + \alpha S_{\text{user}}$, $\alpha=0.70$). | [ ] |
| 7.7 | Live Score Sync | In the User Drilldown view, submitting feedback immediately updates the active activity's score in the UI. | [ ] |
| 7.8 | Standalone Page (`/feedback`) | Navigating to `/feedback` in the top navbar provides full manual inputs for User ID and Activity ID with identical calibration functionality. | [ ] |

---

## 8. Page 3: Automated Policy Containment Feed (`/policies`)

| # | Test Action | Expected Result | Pass / Fail |
|---|-------------|-----------------|:-----------:|
| 8.1 | Initial Load | Audit table lists recorded containment policy violations with timestamp, user ID, rule name, severity, action, and rationale. | [ ] |
| 8.2 | Severity Filter Tabs | Clicking `CRITICAL`, `HIGH`, `MEDIUM`, or `LOW` filters the table rows instantly to only violations of that severity. Clicking `ALL` restores all rows. | [ ] |
| 8.3 | Free-text Search | Typing into the search bar filters rows by matching User ID, Rule ID, Action, or description text. | [ ] |
| 8.4 | Click-to-Drilldown | Clicking on any User ID in the table navigates directly to that user's Drilldown page (`/users/:userId`). | [ ] |
| 8.5 | Action Pill Styling | Automated SOAR actions (e.g., `REVOKE_USB_ACCESS`, `TERMINATE_SESSION`) are styled in distinct cyan pills. | [ ] |

---

## 9. Error Resilience & Edge Cases

| # | Test Action | Expected Result | Pass / Fail |
|---|-------------|-----------------|:-----------:|
| 9.1 | Backend Offline Resilience | Stop the backend server (`Ctrl+C` in Terminal 1) and reload Overview. The page must display a clean error alert with a *"Retry Connection"* button, rather than a blank white screen or silent console failure. | [ ] |
| 9.2 | Invalid User ID | Navigate to `/users/NON_EXISTENT_USER`. The page displays an informative *"Unable to load entity history: User 'NON_EXISTENT_USER' not found"* message with a Retry button. | [ ] |
| 9.3 | React Error Boundary | If any component throws an uncaught JavaScript error, `ErrorBoundary` catches it and displays the SOC Telemetry Recovery screen with "Reload View" and "Return to Overview" buttons. | [ ] |

---

## 10. Verification Sign-Off

- [ ] Automated Vitest Suite: `16 / 16 passed`
- [ ] TypeScript Type Check: `0 errors` (`npx tsc --noEmit`)
- [ ] ESLint Check: `0 errors, 0 warnings` (`npm run lint`)
- [ ] Production Build: `0 errors` (`npm run build`)
- [ ] Backend Regression Suite: `66 / 66 passed` (`pytest backend/tests/`)
- [ ] Manual QA Walkthrough: Verified by Human Reviewer
