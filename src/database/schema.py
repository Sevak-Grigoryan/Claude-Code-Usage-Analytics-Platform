SCHEMA_SQL = """
-- Employees table
CREATE TABLE IF NOT EXISTS employees (
    email TEXT PRIMARY KEY,
    full_name TEXT NOT NULL,
    practice TEXT NOT NULL,
    level TEXT NOT NULL,
    location TEXT NOT NULL
);

-- API requests (token usage, cost, model performance)
CREATE TABLE IF NOT EXISTS api_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_timestamp TEXT NOT NULL,
    session_id TEXT NOT NULL,
    user_email TEXT NOT NULL,
    user_id TEXT NOT NULL,
    organization_id TEXT NOT NULL,
    model TEXT NOT NULL,
    input_tokens INTEGER NOT NULL,
    output_tokens INTEGER NOT NULL,
    cache_read_tokens INTEGER DEFAULT 0,
    cache_creation_tokens INTEGER DEFAULT 0,
    cost_usd REAL NOT NULL,
    duration_ms INTEGER NOT NULL,
    terminal_type TEXT,
    host_arch TEXT,
    os_type TEXT,
    os_version TEXT,
    service_version TEXT,
    FOREIGN KEY (user_email) REFERENCES employees(email)
);

-- Tool decisions (accept/reject)
CREATE TABLE IF NOT EXISTS tool_decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_timestamp TEXT NOT NULL,
    session_id TEXT NOT NULL,
    user_email TEXT NOT NULL,
    user_id TEXT NOT NULL,
    tool_name TEXT NOT NULL,
    decision TEXT NOT NULL,
    source TEXT NOT NULL,
    terminal_type TEXT,
    FOREIGN KEY (user_email) REFERENCES employees(email)
);

-- Tool execution results
CREATE TABLE IF NOT EXISTS tool_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_timestamp TEXT NOT NULL,
    session_id TEXT NOT NULL,
    user_email TEXT NOT NULL,
    user_id TEXT NOT NULL,
    tool_name TEXT NOT NULL,
    success TEXT NOT NULL,
    duration_ms INTEGER NOT NULL,
    decision_type TEXT,
    decision_source TEXT,
    result_size_bytes INTEGER,
    terminal_type TEXT,
    FOREIGN KEY (user_email) REFERENCES employees(email)
);

-- User prompts
CREATE TABLE IF NOT EXISTS user_prompts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_timestamp TEXT NOT NULL,
    session_id TEXT NOT NULL,
    user_email TEXT NOT NULL,
    user_id TEXT NOT NULL,
    prompt_length INTEGER NOT NULL,
    terminal_type TEXT,
    FOREIGN KEY (user_email) REFERENCES employees(email)
);

-- API errors
CREATE TABLE IF NOT EXISTS api_errors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_timestamp TEXT NOT NULL,
    session_id TEXT NOT NULL,
    user_email TEXT NOT NULL,
    user_id TEXT NOT NULL,
    model TEXT NOT NULL,
    error TEXT NOT NULL,
    status_code TEXT,
    duration_ms INTEGER NOT NULL,
    attempt INTEGER DEFAULT 1,
    terminal_type TEXT,
    FOREIGN KEY (user_email) REFERENCES employees(email)
);

-- Indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_api_requests_timestamp ON api_requests(event_timestamp);
CREATE INDEX IF NOT EXISTS idx_api_requests_user ON api_requests(user_email);
CREATE INDEX IF NOT EXISTS idx_api_requests_model ON api_requests(model);
CREATE INDEX IF NOT EXISTS idx_api_requests_session ON api_requests(session_id);

CREATE INDEX IF NOT EXISTS idx_tool_decisions_timestamp ON tool_decisions(event_timestamp);
CREATE INDEX IF NOT EXISTS idx_tool_decisions_tool ON tool_decisions(tool_name);
CREATE INDEX IF NOT EXISTS idx_tool_decisions_user ON tool_decisions(user_email);

CREATE INDEX IF NOT EXISTS idx_tool_results_timestamp ON tool_results(event_timestamp);
CREATE INDEX IF NOT EXISTS idx_tool_results_tool ON tool_results(tool_name);
CREATE INDEX IF NOT EXISTS idx_tool_results_user ON tool_results(user_email);

CREATE INDEX IF NOT EXISTS idx_user_prompts_timestamp ON user_prompts(event_timestamp);
CREATE INDEX IF NOT EXISTS idx_user_prompts_user ON user_prompts(user_email);
CREATE INDEX IF NOT EXISTS idx_user_prompts_session ON user_prompts(session_id);

CREATE INDEX IF NOT EXISTS idx_api_errors_timestamp ON api_errors(event_timestamp);
CREATE INDEX IF NOT EXISTS idx_api_errors_user ON api_errors(user_email);
"""
