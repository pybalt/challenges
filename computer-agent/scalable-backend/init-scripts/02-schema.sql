-- Create tables required by the Computer Use Agent backend
-- NOTE: This script is idempotent (uses IF NOT EXISTS) so it can run safely multiple times

-- Sessions -----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sessions (
    id            UUID PRIMARY KEY,
    user_id       VARCHAR NOT NULL,
    status        VARCHAR,
    model         VARCHAR,
    screen_width  INTEGER,
    screen_height INTEGER,
    vnc_port      INTEGER,
    container_id  VARCHAR,
    system_prompt TEXT,
    created_at    TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ended_at      TIMESTAMP WITHOUT TIME ZONE,
    last_activity TIMESTAMP WITHOUT TIME ZONE
);

-- Chat history -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS chat_history (
    id               UUID PRIMARY KEY,
    session_id       UUID REFERENCES sessions(id) ON DELETE CASCADE,
    message          TEXT NOT NULL,
    message_type     VARCHAR NOT NULL,
    timestamp        TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    message_metadata TEXT
);

-- Indexes ------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions (user_id);
CREATE INDEX IF NOT EXISTS idx_chat_history_session_id ON chat_history (session_id);


