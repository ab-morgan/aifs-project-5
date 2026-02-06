# Docker Deployment

Contains:
- Dockerfile (builds full app)
- docker-compose.yml (optional orchestration)
- entrypoint.sh (runs PREP then Streamlit)

Build:
docker build -t job-match-app -f version2/docker/Dockerfile .

Run:
docker run -p 8501:8501 job-match-app

Compose:
docker-compose -f version2/docker/docker-compose.yml up --build

Entrypoint:
Runs PREP pipeline, then launches Streamlit.
