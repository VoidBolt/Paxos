-- get_global_promised
SELECT val FROM global_state WHERE key='promised_id';

-- set_global_promised
INSERT INTO global_state (key, val) VALUES ('promised_id', ?)
ON CONFLICT(key) DO UPDATE SET val=excluded.val;
