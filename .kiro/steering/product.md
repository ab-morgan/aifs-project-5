# Product: CareerPivots (Federal Worker Skill Transition Assistant)

An intelligent platform that helps recently unemployed federal workers translate their government experience into qualifications for the broader private-sector job market.

## Core Functionality
- Accepts resume text or file upload (PDF, DOCX, TXT) with configurable size limits
- Parses resume into structured work experiences using an LLM (Groq/Llama)
- Generates embeddings for resume experiences and computes similarity against a precomputed job database
- Displays top job matches with match score, description, LLM explanation, job insights, and career transitions
- O*NET Mini-IP Interest Profiler (30-question wizard) generates RIASEC scores displayed in the sidebar
- Users can select matches for export as a formatted HTML report
- Job market statistics and analytics dashboards (Sankey diagrams, transition explorer)
- Admin-configurable UI (colors, font sizes, logo size) via `settings.toml`

## Key User Flows
1. User uploads/pastes resume → system extracts experiences → generates embedding → returns top-k job matches with LLM explanations
2. User optionally completes O*NET Interest Questionnaire → RIASEC scores stored in session and shown in sidebar
3. User selects matches → downloads formatted HTML export
4. Users explore job market statistics and analytics dashboards
5. A prep pipeline runs offline to precompute and store job embeddings in Supabase

## Target Users
Recently unemployed federal workers seeking private-sector career transitions.

## Attribution
This product incorporates O*NET Web Services by USDOL/ETA. O*NET® is a trademark of USDOL/ETA. The O*NET attribution badge and legal notice must appear in the app footer at all times.
