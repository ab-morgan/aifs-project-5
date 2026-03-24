# Product: CareerPivots (Federal Worker Skill Transition Assistant)

An intelligent platform that helps recently unemployed federal workers translate their government experience into qualifications for the broader private-sector job market.

## Core Functionality
- Accepts resume text or file upload (PDF, DOCX)
- Parses resume into structured work experiences using an LLM (Groq/Llama)
- Generates embeddings for resume experiences
- Computes similarity against a precomputed database of job embeddings
- Displays top job matches with market statistics and analytics

## Key User Flows
1. User uploads/pastes resume → system extracts experiences → generates embedding → returns top-k job matches
2. Users can explore job market statistics and analytics dashboards
3. A prep pipeline runs offline to precompute and store job embeddings in Supabase

## Target Users
Recently unemployed federal workers seeking private-sector career transitions.
