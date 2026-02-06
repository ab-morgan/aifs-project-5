-- table.sql
-- Minimal schema for version2 job matching

create table if not exists jobs (
    id bigint generated always as identity primary key,
    title text not null,
    company text,
    location text,
    description text
);

create table if not exists job_embeddings (
    id bigint generated always as identity primary key,
    job_id bigint not null references jobs(id) on delete cascade,
    embedding double precision[] not null
);

create table if not exists job_stats (
    id bigint generated always as identity primary key,
    job_id bigint references jobs(id) on delete cascade,
    vector_norm double precision,
    frequency_rank integer,
    mean double precision,
    std double precision,
    min double precision,
    max double precision
);
create table if not exists events (
    id bigint generated always as identity primary key,
    session_id text not null,
    event_type text not null,
    timestamp timestamptz not null default now(),
    payload jsonb,

    -- Optional indexing for analytics
    constraint events_session_id_check check (length(session_id) > 0)
);

-- Helpful indexes
create index if not exists idx_events_session_id
    on events (session_id);

create index if not exists idx_events_event_type
    on events (event_type);

create index if not exists idx_events_timestamp
    on events (timestamp desc);
