# CareerPivots — Admin Setup Guide

This guide walks you through setting up and running CareerPivots from scratch. No prior experience with Python, web servers, or cloud databases is assumed. Follow each section in order.

---

## What You'll Need

Before starting, make sure you have accounts and access to the following services. All of them have free tiers that are sufficient to run this app.

| Service | What it's for | Sign up at |
|---------|--------------|------------|
| **Supabase** | Database that stores job data and embeddings | supabase.com |
| **Groq** | AI service that parses resumes and explains job matches | console.groq.com |
| **O\*NET Web Services** | Career interest questionnaire API | services.onetcenter.org/developer/signup |
| **OpenAI** (optional) | Alternative AI embedding provider | platform.openai.com |

---

## Part 1 — Install Prerequisites

### 1.1 Install Python

The app requires Python 3.11 or newer.

1. Go to [python.org/downloads](https://www.python.org/downloads/)
2. Download the installer for your operating system
3. Run the installer — on Windows, check **"Add Python to PATH"** before clicking Install
4. Verify the installation by opening a terminal and running:
   ```
   python --version
   ```
   You should see something like `Python 3.11.x` or higher.

### 1.2 Install Git

Git is used to download the code.

1. Go to [git-scm.com](https://git-scm.com/downloads)
2. Download and install for your operating system
3. Verify: open a terminal and run `git --version`

### 1.3 Install Make (Windows only)

On Mac and Linux, `make` is already installed. On Windows:

1. Install [Chocolatey](https://chocolatey.org/install) (a Windows package manager) by following the instructions on their site
2. Then run in an Administrator terminal:
   ```
   choco install make
   ```

---

## Part 2 — Get the Code

Open a terminal, navigate to where you want to store the project, and run:

```bash
git clone <repository-url>
cd <repository-folder>
```

Replace `<repository-url>` with the URL of the repository and `<repository-folder>` with the folder name it creates.

---

## Part 3 — Set Up a Python Virtual Environment

A virtual environment keeps the app's dependencies isolated from the rest of your system.

```bash
python -m venv .venv
```

Then activate it:

- **Mac / Linux:**
  ```bash
  source .venv/bin/activate
  ```
- **Windows (Command Prompt):**
  ```
  .venv\Scripts\activate
  ```
- **Windows (PowerShell):**
  ```
  .venv\Scripts\Activate.ps1
  ```

Your terminal prompt should now show `(.venv)` at the start. You'll need to activate the virtual environment every time you open a new terminal.

### Install dependencies

```bash
pip install -r requirements.txt
```

This will take a few minutes the first time.

---

## Part 4 — Collect Your API Keys

You need to gather credentials from each service before the app can run.

### 4.1 Supabase

1. Log in to [supabase.com](https://supabase.com) and open your project
2. Go to **Project Settings → API**
3. Copy:
   - **Project URL** (looks like `https://xxxx.supabase.co`)
   - **anon / public key** (the long string under "Project API keys")

### 4.2 Groq

1. Log in to [console.groq.com](https://console.groq.com)
2. Go to **API Keys** and create a new key
3. Copy the key (it starts with `gsk_`)

### 4.3 O\*NET

1. Sign up at [services.onetcenter.org/developer/signup](https://services.onetcenter.org/developer/signup)
2. After approval, log in and go to **My Account → API Keys**
3. Generate a key and copy it

### 4.4 OpenAI (optional)

Only needed if you want to use OpenAI as the embedding provider instead of the default local model.

1. Log in to [platform.openai.com](https://platform.openai.com)
2. Go to **API Keys** and create a new key

---

## Part 5 — Create Your Environment Files

The app uses two separate configuration files for secrets — one for development/testing and one for production. These files are never committed to git (they're in `.gitignore`).

### 5.1 Create the development environment file

In the root of the project, create a file called `.env.dev` with the following content. Replace each placeholder with your actual keys:

```
APP_ENV=dev

SUPABASE_URL=https://your-project.supabase.co
SUPABASE_PUBLISHABLE_KEY=your-anon-key-here

GROQ_API_KEY=your-groq-key-here
OPENAI_API_KEY=your-openai-key-here
ONET_API_KEY=your-onet-key-here
```

### 5.2 Create the production environment file

Create a second file called `.env.prod` with the same structure. You can point this at a different Supabase project if you want a separate production database, or use the same one:

```
APP_ENV=prod

SUPABASE_URL=https://your-project.supabase.co
SUPABASE_PUBLISHABLE_KEY=your-anon-key-here

GROQ_API_KEY=your-groq-key-here
OPENAI_API_KEY=your-openai-key-here
ONET_API_KEY=your-onet-key-here
```

> **Security note:** Never share these files or commit them to git. They contain your private API keys.

---

## Part 6 — Run the Prep Pipeline

Before the app can show job matches, it needs to load job data into the database and compute embeddings. This is a one-time setup step (and should be re-run whenever the job data is updated).

```bash
make prep
```

This will take several minutes depending on the size of your job dataset. You'll see progress output in the terminal. When it finishes without errors, the database is ready.

---

## Part 7 — Starting the App

### Development / Test mode

Development mode is for testing changes. It runs on port **8300**, shows verbose logging, and has relaxed input limits.

```bash
make dev
```

Once started, open your browser and go to:
```
http://localhost:8300
```

You should see the CareerPivots interface. The terminal will show the URL once the app is ready.

To stop the app, press `Ctrl+C` in the terminal.

### Production mode

Production mode is for live use. It runs on port **8501**, shows only errors in the terminal, and enforces stricter input limits.

```bash
make prod
```

Once started, the app is available at:
```
http://localhost:8501
```

> **To make the app accessible from other computers on your network**, you'll need to configure your firewall to allow traffic on the relevant port (8300 for dev, 8501 for prod). Consult your IT team or hosting provider for this step.

---

## Part 8 — Customizing the App Appearance

Visual settings are controlled in `version2/infra/settings.toml`. You can edit this file with any text editor. Changes take effect the next time the app starts.

```toml
[ui]
app_name = "CareerPivots"       # Name shown in the header
logo_size_px = 56               # Logo size in pixels (16–256)
header_font_size_rem = 2.0      # Header text size (0.5–5.0)
body_font_size_rem = 1.0        # Body text size (0.5–5.0)
background_color = "#f4f6f9"    # Page background (hex color)
card_background_color = "#ffffff"
accent_color = "#14b8a6"        # Teal highlight color
header_text_color = "#111111"
body_text_color = "#333333"
muted_text_color = "#666666"
```

Colors must be in hex format (e.g. `#ffffff` for white, `#000000` for black). Font sizes must be between 0.5 and 5.0. The app will refuse to start if invalid values are provided.

### Adjusting input limits

```toml
[limits]
max_resume_chars = 50000    # Max characters for pasted resume text
max_upload_mb = 5           # Max file size in megabytes
```

---

## Part 9 — Viewing Error Logs

All application errors are written to:

```
version2/logs/app.log
```

You can open this file with any text editor. Each line includes a timestamp, the error level, the file and line number where the error occurred, and the error message.

If the app is behaving unexpectedly, this is the first place to look.

---

## Part 10 — Running Tests

To verify the app is working correctly after making changes:

```bash
make test
```

This runs the automated test suite and reports any failures. Run this before deploying to production.

---

## Part 11 — Other Useful Commands

```bash
make help    # List all available commands
make lint    # Check the code for style issues
```

---

## Part 12 — Running with Docker (Recommended for Production)

Docker packages the entire app and all its dependencies into a self-contained unit called a **container**. This is the recommended way to run CareerPivots in production because it works the same way on any machine and is easier to manage long-term.

### 12.1 Install Docker

1. Go to [docs.docker.com/get-docker](https://docs.docker.com/get-docker/)
2. Download and install **Docker Desktop** for your operating system (Mac, Windows, or Linux)
3. Open Docker Desktop and wait for it to finish starting — you'll see a green indicator when it's ready
4. Verify the installation by opening a terminal and running:
   ```
   docker --version
   ```
   You should see something like `Docker version 24.x.x`

> Docker Desktop must be running in the background whenever you use Docker commands.

### 12.2 Make sure your `.env.prod` file is ready

Docker uses your `.env.prod` file to pass secrets into the container. If you haven't created it yet, go back to **Part 5.2** and do that first.

The file must be in the **root of the project** (the same folder as the `Makefile`), not inside `version2/`.

### 12.3 Build the Docker image

From the root of the project, run:

```bash
docker build -t careerpivots -f version2/docker/Dockerfile.app .
```

What this does:
- `docker build` — creates a Docker image (a snapshot of the app and all its dependencies)
- `-t careerpivots` — names the image "careerpivots"
- `-f version2/docker/Dockerfile.app` — tells Docker which build instructions to use
- `.` — uses the current folder as the source

This will take 5–15 minutes the first time. Subsequent builds are much faster because Docker caches layers.

### 12.4 Run with Docker Compose (easiest method)

Docker Compose manages the container for you, including starting it automatically if the server reboots.

From the root of the project, run:

```bash
docker compose -f version2/docker/docker-compose.yml up --build -d
```

What each part means:
- `docker compose` — the tool that manages multi-container apps
- `-f version2/docker/docker-compose.yml` — the configuration file
- `up` — start the container
- `--build` — rebuild the image if anything has changed
- `-d` — run in the background (detached mode) so your terminal stays free

Once running, the app is available at:
```
http://localhost:8501
```

### 12.5 Check that it's running

```bash
docker ps
```

You should see a row with `careerpivots` in the `NAMES` column and `Up` in the `STATUS` column.

### 12.6 View logs from the container

```bash
docker logs careerpivots
```

Add `-f` to follow the log in real time:

```bash
docker logs -f careerpivots
```

Application errors are also written to `version2/logs/app.log` on your host machine (the logs folder is shared between the container and your computer).

### 12.7 Stop the container

```bash
docker compose -f version2/docker/docker-compose.yml down
```

### 12.8 Restart after making changes

If you update the code or configuration, rebuild and restart:

```bash
docker compose -f version2/docker/docker-compose.yml up --build -d
```

### 12.9 Run without Docker Compose (alternative)

If you prefer to run the container directly without Compose:

```bash
docker run -d \
  --name careerpivots \
  --env-file .env.prod \
  -e APP_ENV=prod \
  -p 8501:8501 \
  -v "$(pwd)/version2/logs:/app/version2/logs" \
  --restart unless-stopped \
  careerpivots
```

What each flag means:
- `-d` — run in the background
- `--name careerpivots` — give the container a name
- `--env-file .env.prod` — load your secrets from the env file
- `-e APP_ENV=prod` — set the environment to production
- `-p 8501:8501` — map port 8501 on your machine to port 8501 in the container
- `-v ...` — share the logs folder so you can read logs from outside the container
- `--restart unless-stopped` — automatically restart if the container crashes or the server reboots

### 12.10 Making the app accessible from the internet

By default, the app is only accessible on the machine running Docker (`localhost`). To make it accessible from other computers or the internet, you have two options:

**Option A — Direct port access (simple)**
Configure your server's firewall to allow inbound traffic on port 8501. The exact steps depend on your hosting provider (AWS, Azure, DigitalOcean, etc.) — look for "security groups" or "firewall rules" in their documentation.

Users would then access the app at `http://your-server-ip:8501`.

**Option B — Reverse proxy with a domain name (recommended for public use)**
Set up a reverse proxy (such as [Nginx](https://nginx.org/) or [Caddy](https://caddyserver.com/)) in front of the app. This lets you:
- Use a proper domain name (e.g. `careerpivots.yourdomain.com`)
- Enable HTTPS (encrypted connections)
- Hide the port number from users

Caddy is the easiest option for beginners — it handles HTTPS certificates automatically. If you need help with this step, consult your IT team or a hosting provider's documentation.

---

## Troubleshooting

**The app won't start and shows "SUPABASE_URL must be set"**
Your `.env.dev` or `.env.prod` file is missing or has incorrect values. Double-check that the file exists in the project root and that the keys are correct.

**The app starts but shows "Could not connect to the database"**
Your Supabase URL or key is wrong, or the Supabase project is paused (free tier projects pause after inactivity). Log in to supabase.com and check your project status.

**Job matches aren't appearing**
The prep pipeline may not have run, or it may have failed. Run `make prep` and check the terminal output for errors.

**The O\*NET questionnaire shows an error**
Your `ONET_API_KEY` is missing or incorrect. Check your `.env.dev` / `.env.prod` file and verify the key at services.onetcenter.org.

**"Why this matches" explanations aren't loading**
The Groq API key may be missing or the service may be temporarily rate-limited. Check `version2/logs/app.log` for details.

**Port already in use**
Another process is using port 8300 or 8501. Either stop that process, or change the port in `version2/infra/settings.dev.toml` or `settings.prod.toml` under `[server] port = ...`.

**Docker container exits immediately after starting**
Run `docker logs careerpivots` to see the error. The most common cause is a missing or incorrect `.env.prod` file. Make sure it exists in the project root and contains all required keys.

**Docker build fails with "requirements.txt not found"**
Make sure you're running the build command from the project root (the folder containing `Makefile`), not from inside `version2/`.

**Changes to the code aren't showing up in Docker**
You need to rebuild the image after any code change: `docker compose -f version2/docker/docker-compose.yml up --build -d`

---

## Summary of Key Files

| File | Purpose |
|------|---------|
| `.env.dev` | Development secrets (API keys) — never commit |
| `.env.prod` | Production secrets (API keys) — never commit |
| `version2/infra/settings.toml` | Base app configuration (safe to edit) |
| `version2/infra/settings.dev.toml` | Dev-specific overrides |
| `version2/infra/settings.prod.toml` | Prod-specific overrides |
| `version2/logs/app.log` | Error log — check here when things go wrong |
| `Makefile` | All runnable commands |
| `version2/docker/Dockerfile.app` | Docker image build instructions |
| `version2/docker/docker-compose.yml` | Docker Compose configuration for production |
| `version2/docker/entrypoint.sh` | Container startup script (runs prep, then Streamlit) |
