-- upsert_decision
INSERT INTO decisions (slot, value, proposal_id, logical_time)
VALUES (?, ?, ?, ?)
ON CONFLICT(slot) DO UPDATE SET
    value = excluded.value,
    proposal_id = excluded.proposal_id,
    logical_time = excluded.logical_time;

-- get_decision
SELECT value, proposal_id, logical_time
FROM decisions
WHERE slot = ?;

-- get_last_decision
SELECT slot, value, proposal_id, logical_time
FROM decisions
ORDER BY slot DESC
LIMIT 1;

-- all_decisions
SELECT slot, value, logical_time
FROM decisions
ORDER BY slot;

-- get_known_slots
SELECT slot
FROM decisions
ORDER BY slot ASC;

-- get_known_slots_with_pid
SELECT slot, proposal_id, logical_time
FROM decisions
ORDER BY slot ASC;

-- get_latest_decision
SELECT slot, value, proposal_id, logical_time
FROM decisions
ORDER BY proposal_id DESC, logical_time DESC
LIMIT 1;
