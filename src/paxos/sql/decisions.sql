-- upsert_decision
INSERT INTO decisions (slot, value, proposal_id)
VALUES (?, ?, ?)
ON CONFLICT(slot) DO UPDATE SET value=excluded.value;

-- get_decision
SELECT value, proposal_id FROM decisions WHERE slot=?;

-- get_last_decision
SELECT slot, value, proposal_id
FROM decisions
ORDER BY slot DESC
LIMIT 1;

-- all_decisions
SELECT slot, value FROM decisions ORDER BY slot;

-- get_known_slots
SELECT slot FROM decisions ORDER BY slot ASC;

-- get_known_slots_with_pid
SELECT slot, proposal_id FROM decisions ORDER BY slot ASC;

-- get_latest_decision
SELECT slot, value
FROM decisions
ORDER BY slot DESC
LIMIT 1;
