# OpenIRM Frontend Dashboard

React + TypeScript dashboard for OpenIRM built with Vite, Tailwind CSS, and Recharts.

## Subdirectories

- `src/pages/`: Main application view pages (`Overview`, `UserDrilldown`, `FeedbackPanel`, `PolicyFeed`).
- `src/components/`: Reusable UI components (`RiskBadge`, `ShapExplanationPanel`, `ActivityTimeline`, `ScoreSlider`).
- `src/api/`: Typed API client modules communicating with the FastAPI backend.
- `src/types/`: Shared TypeScript interface definitions mirroring backend Pydantic models.
- `src/hooks/`: Custom React hooks for data fetching and state management.

## Setup & Running

Full Vite + React scaffolding occurs in Week 11.
```bash
npm install
npm run dev
```
