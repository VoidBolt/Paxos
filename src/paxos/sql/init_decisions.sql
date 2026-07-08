CREATE TABLE IF NOT EXISTS decisions (
    slot INTEGER PRIMARY KEY,
    value TEXT NOT NULL,
    proposal_id INTEGER NOT NULL,
    logical_time INTEGER NOT NULL
);
