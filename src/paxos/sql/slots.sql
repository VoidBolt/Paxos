-- get_promised
SELECT promised_id FROM slots WHERE slot=?;

-- upsert_promised
INSERT INTO slots(slot, promised_id) VALUES (?, ?)
ON CONFLICT(slot) DO UPDATE SET promised_id=excluded.promised_id;

-- get_accepted
SELECT accepted_id, accepted_value FROM slots WHERE slot=?;

-- upsert_accepted
INSERT INTO slots (slot, accepted_id, accepted_value)
VALUES (?, ?, ?)
ON CONFLICT(slot) DO UPDATE SET
    accepted_id=excluded.accepted_id,
    accepted_value=excluded.accepted_value;

-- all_slots
SELECT slot FROM slots;

-- all_accepted
SELECT slot, accepted_id, accepted_value FROM slots;

-- get_highest_less_than
SELECT accepted_id, accepted_value
FROM slots
WHERE slot=?;
