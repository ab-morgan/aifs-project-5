-- table.sql
-- Full schema for CareerPivots version2
-- Run this once against your Supabase project to set up all tables and views.
-- Safe to re-run (uses IF NOT EXISTS / CREATE OR REPLACE).

-- ─────────────────────────────────────────────────────────────────────────────
-- Raw job data (source of truth — populated externally from JobHop / O*NET)
-- ─────────────────────────────────────────────────────────────────────────────
create table if not exists jobhop_raw (
    id          bigint generated always as identity primary key,
    title       text not null,
    company     text,
    location    text,
    description text,
    industry    text,
    created_at  timestamptz not null default now()
);

-- ─────────────────────────────────────────────────────────────────────────────
-- Precomputed embeddings (one row per job)
-- ─────────────────────────────────────────────────────────────────────────────
create table if not exists jobhop_embeddings (
    id          bigint generated always as identity primary key,
    job_id      bigint not null references jobhop_raw(id) on delete cascade,
    title       text,                          -- denormalized for fast reads
    description text,                          -- denormalized for fast reads
    embedding   double precision[] not null,
    created_at  timestamptz not null default now(),
    unique (job_id)                            -- one embedding per job
);

create index if not exists idx_jobhop_embeddings_job_id on jobhop_embeddings (job_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- Job-level statistics (one row per unique job title)
-- Populated by the prep pipeline's compute_stats step.
-- ─────────────────────────────────────────────────────────────────────────────
create table if not exists jobhop_stats (
    id                  bigint generated always as identity primary key,
    job_title           text not null unique,
    count               integer,
    percent             double precision,       -- fraction of total database
    frequency_rank      integer,
    avg_tenure_days     double precision,
    median_tenure_days  double precision,
    top_transitions     jsonb,                  -- [{next_job_title, count, percent}]
    industry            text,
    growth_rate         double precision,
    updated_at          timestamptz not null default now()
);

create index if not exists idx_jobhop_stats_job_title on jobhop_stats (job_title);

-- ─────────────────────────────────────────────────────────────────────────────
-- jobhop_stats_mv — view used by the app at runtime
-- This is a plain view (not a materialized view) so it always reflects
-- the current state of jobhop_stats without a manual refresh step.
-- ─────────────────────────────────────────────────────────────────────────────
create or replace view jobhop_stats_mv as
    select
        job_title,
        count,
        percent,
        frequency_rank,
        avg_tenure_days,
        median_tenure_days,
        top_transitions,
        industry,
        growth_rate,
        updated_at
    from jobhop_stats;

-- ─────────────────────────────────────────────────────────────────────────────
-- Session tracking events
-- ─────────────────────────────────────────────────────────────────────────────
create table if not exists events (
    id          bigint generated always as identity primary key,
    session_id  text not null,
    event_type  text not null,
    timestamp   timestamptz not null default now(),
    payload     jsonb,
    constraint events_session_id_check check (length(session_id) > 0)
);

create index if not exists idx_events_session_id on events (session_id);
create index if not exists idx_events_event_type  on events (event_type);
create index if not exists idx_events_timestamp   on events (timestamp desc);
