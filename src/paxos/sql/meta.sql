-- get_node_id
SELECT val FROM meta WHERE key='node_id';

-- insert_node_id
INSERT INTO meta (key, val) VALUES ('node_id', ?);

-- get_latest_proposal_id
SELECT val FROM meta WHERE key='latest_proposal_id';

-- upsert_latest_proposal_id
INSERT INTO meta (key, val) VALUES ('latest_proposal_id', ?)
ON CONFLICT(key) DO UPDATE SET val=excluded.val;

-- get_meta
SELECT val FROM meta WHERE key=?;

-- upsert_meta
INSERT INTO meta (key, val) VALUES (?, ?)
ON CONFLICT(key) DO UPDATE SET val=excluded.val;
