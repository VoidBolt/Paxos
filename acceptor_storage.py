import os
import sqlite3

import json
# unique id -> unique db -> unique decisions
from node_lock import NodeLock
from typing import Dict, Optional, Tuple, List
# -----------------
# Persistent storage
# -----------------


class AcceptorStorage:
    """SQLite-based storage for acceptor state, supporting single and multi-slot Paxos."""

    def __init__(self, path: str, node_id: Optional[int] = None):

        # --- enforce OS-level lock ---
        lock_path = f"{path}.lock"
        self.lock = NodeLock(lock_path)
        self.lock.acquire()

        init_needed = not os.path.exists(path)
        self.path = path
        self.conn = sqlite3.connect(path, check_same_thread=False)
        if init_needed:
            self._init_db()
        if node_id is not None:
            self._check_or_set_node_id(node_id)

    def _init_db(self):
        cur = self.conn.cursor()
        # Meta table for node identity and misc info
        cur.execute("""
        CREATE TABLE IF NOT EXISTS meta (
            key TEXT PRIMARY KEY,
            val TEXT
        )
        """)
        # Global promised_id (for single-decree)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS global_state (
            key TEXT PRIMARY KEY,
            val TEXT
        )
        """)
        cur.execute("INSERT OR IGNORE INTO global_state (key, val) VALUES ('promised_id', NULL)")

        # Multi-slot table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS slots (
            slot INTEGER PRIMARY KEY,
            promised_id TEXT,
            accepted_id TEXT,
            accepted_value TEXT
        )
        """)
        self.conn.commit()
        # Decisions table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS decisions (
            slot INTEGER PRIMARY KEY,
            value TEXT,
            proposal_id INTEGER
        )
        """)
        self.conn.commit()

    def _check_or_set_node_id(self, node_id: int):
        cur = self.conn.cursor()
        cur.execute("SELECT val FROM meta WHERE key='node_id'")
        row = cur.fetchone()
        if not row:
            # Not set yet, bind this DB to the node_id
            cur.execute("INSERT INTO meta (key, val) VALUES ('node_id', ?)", (json.dumps(node_id),))
            self.conn.commit()
        else:
            stored = json.loads(row[0])
            if stored != node_id:
                raise RuntimeError(
                    f"Database {self.path} already bound to node_id={stored}, "
                    f"but tried to start with node_id={node_id}"
                )
    # -----------------
    # Shutdown helpers
    # -----------------
    def close(self):
        """Cleanly close SQLite and release lock."""
        try:
            self.conn.commit()
            self.conn.close()
        except Exception:
            pass
        self.lock.release()

    def __del__(self):
        # Fallback if close() wasn’t called explicitly
        self.close()
    # -----------------
    # Global promised_id (single-decree) – internal use
    # -----------------
    def _get_global_promised(self) -> Optional[int]:
        cur = self.conn.cursor()
        cur.execute("SELECT val FROM global_state WHERE key='promised_id'")
        row = cur.fetchone()
        if not row or row[0] is None:
            return None
        return json.loads(row[0])

    def _set_global_promised(self, v: Optional[int]):
        cur = self.conn.cursor()
        cur.execute("UPDATE global_state SET val=? WHERE key='promised_id'",
                    (None if v is None else json.dumps(v),))
        self.conn.commit()

    # -----------------
    # Unified API
    # -----------------
    def get_promised(self, slot: Optional[int] = None) -> Optional[int]:
        """Return promised_id for given slot, or global if slot=None."""
        if slot is None:
            return self._get_global_promised()
        cur = self.conn.cursor()
        cur.execute("SELECT promised_id FROM slots WHERE slot=?", (slot,))
        row = cur.fetchone()
        if not row or row[0] is None:
            return None
        return json.loads(row[0])

    def set_promised(self, slot: Optional[int], proposal_id: int):
        """Set promised_id for given slot, or global if slot=None."""
        if slot is None:
            return self._set_global_promised(proposal_id)
        cur = self.conn.cursor()
        cur.execute("""
        INSERT INTO slots(slot, promised_id) VALUES (?, ?)
        ON CONFLICT(slot) DO UPDATE SET promised_id=excluded.promised_id
        """, (slot, json.dumps(proposal_id)))
        self.conn.commit()

    def set_accepted(self, slot: int, accepted_id: int, accepted_value):
        cur = self.conn.cursor()
        cur.execute("""
        INSERT INTO slots (slot, accepted_id, accepted_value) 
        VALUES (?, ?, ?)
        ON CONFLICT(slot) DO UPDATE SET
            accepted_id=excluded.accepted_id,
            accepted_value=excluded.accepted_value
        """, (slot, json.dumps(accepted_id), json.dumps(accepted_value)))
        self.conn.commit()

    def get_accepted(self, slot: int) -> Optional[Tuple[Optional[int], Optional[any]]]:
        cur = self.conn.cursor()
        cur.execute("SELECT accepted_id, accepted_value FROM slots WHERE slot=?", (slot,))
        row = cur.fetchone()
        if not row:
            return None
        aid, val = row
        accepted_id = json.loads(aid) if aid is not None else None
        accepted_value = json.loads(val) if val is not None else None
        return (accepted_id, accepted_value)

    def accepted(self, slot: int) -> Tuple[Optional[int], Optional[any]]:
        result = self.get_accepted(slot)
        if result is None:
            return (None, None)
        return result

    def all_slots(self) -> List[int]:
        cur = self.conn.cursor()
        cur.execute("SELECT slot FROM slots")
        return [row[0] for row in cur.fetchall()]

    def all_accepted(self) -> Dict[int, Tuple[int, any]]:
        cur = self.conn.cursor()
        cur.execute("SELECT slot, accepted_id, accepted_value FROM slots")
        result = {}
        for slot, aid, val in cur.fetchall():
            result[slot] = (json.loads(aid), json.loads(val))
        return result

    def next_slot(self) -> int:
        slots = self.all_slots()
        return max(slots, default=0) + 1
    # -----------------
    # Decisions (chosen values for slots)
    # -----------------
    def set_decision(self, slot: int, value, proposal_id):
        cur = self.conn.cursor()
        cur.execute("""
        INSERT INTO decisions (slot, value) VALUES (?, ?)
        ON CONFLICT(slot) DO UPDATE SET value=excluded.value
        """, (slot, json.dumps(value)))
        self.conn.commit()

    def get_decision(self, slot: int):
        cur = self.conn.cursor()
        cur.execute("SELECT value FROM decisions WHERE slot=?", (slot,))
        row = cur.fetchone()
        if row is None or row[0] is None:
            return None
        return json.loads(row[0])

    def get_latest_proposal_id(self) -> Optional[int]:
        """Return the highest slot number (used as a proposal index)."""
        cur = self.conn.cursor()
        cur.execute("SELECT MAX(slot) FROM decisions")
        row = cur.fetchone()
        return row[0] if row and row[0] is not None else None

    def all_decisions(self) -> Dict[int, any]:
        cur = self.conn.cursor()
        cur.execute("SELECT slot, value FROM decisions ORDER BY slot")
        return {slot: json.loads(val) for slot, val in cur.fetchall()}

    def get_known_slots(self) -> list[int]:
        """
        Return a sorted list of slots for which this node has a decided value.
        """
        cur = self.conn.cursor()
        cur.execute("SELECT slot FROM decisions ORDER BY slot ASC")
        rows = cur.fetchall()
        return [row[0] for row in rows]

    def get_known_slots_with_pid(self) -> list[tuple[int, int]]:
        """
        Return list of (slot, proposal_id) tuples for decided slots.
        """
        cur = self.conn.cursor()
        cur.execute("SELECT slot, proposal_id FROM decisions ORDER BY slot ASC")
        return cur.fetchall()

    def get_latest_decision(self) -> Optional[any]:
        """
        Return the most recently decided value (highest slot),
        or None if no decisions have been made yet.
        """
        cur = self.conn.cursor()
        cur.execute("SELECT slot, value FROM decisions ORDER BY slot DESC LIMIT 1")
        row = cur.fetchone()
        if not row:
            return None
        slot, val = row
        try:
            return json.loads(val) if val else None
        except Exception:
            return val
    # -----------------
    # Meta helpers
    # -----------------
    def get_meta(self, key: str) -> Optional[str]:
        cur = self.conn.cursor()
        cur.execute("SELECT val FROM meta WHERE key=?", (key,))
        row = cur.fetchone()
        return None if not row else json.loads(row[0])

    def set_meta(self, key: str, val):
        cur = self.conn.cursor()
        cur.execute("""
        INSERT INTO meta (key, val) VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET val=excluded.val
        """, (key, json.dumps(val)))
        self.conn.commit()

def test_latest():
    # Example DB path for testing
    test_db = "test_paxos_node.db"

    # Create storage (will init if not exists)
    storage = AcceptorStorage(test_db, node_id=99)

    # --- Insert some decisions for testing ---
    storage.set_decision(1, {"value": "first"}, 1)
    storage.set_decision(2, {"value": "second"},2)
    storage.set_decision(3, {"value": "third"}, 25)
    
    # --- Test get_latest_proposal_id ---
    get_latest_proposal_id = storage.get_latest_proposal_id()
    print("Latest proposal_id:", get_latest_proposal_id)
    # --- Test get_latest_decision ---
    latest = storage.get_latest_decision()
    print("Latest decision:", latest)

    # --- Test get_known_slots ---
    slots = storage.get_known_slots()
    print("Known slots:", slots)

    # Cleanup test DB if desired
    storage.close()
    # os.remove(test_db)  # Uncomment to remove test DB after test

if __name__ == "__main__":
    import glob
    test_latest()
    input("Wait...")
    # iterate over all node databases
    for db_path in sorted(glob.glob("paxos_manager_workspace/paxos_node_*.db")):
        store = AcceptorStorage(db_path)

        print(f"\n=== DATABASE: {db_path} ===")

        # --- META ---
        print("=== META ===")
        cur = store.conn.cursor()
        cur.execute("SELECT key, val FROM meta")
        rows = cur.fetchall()
        if not rows:
            print("(empty)")
        else:
            for k, v in rows:
                print(f"{k}: {json.loads(v) if v is not None else None}")

        # --- GLOBAL STATE ---
        print("\n=== GLOBAL STATE ===")
        cur.execute("SELECT key, val FROM global_state")
        for key, val in cur.fetchall():
            print(f"{key}: {json.loads(val) if val is not None else None}")

        # --- SLOTS ---
        print("\n=== SLOTS ===")
        cur.execute("SELECT slot, promised_id, accepted_id, accepted_value FROM slots")
        rows = cur.fetchall()
        if not rows:
            print("(empty)")
        else:
            print(rows)
            for slot, promised, aid, val in rows:
                print(f"slot {slot}: promised={json.loads(promised) if promised else None}, "
                      f"accepted=({json.loads(aid) if aid else None}, {json.loads(val) if val else None})")

        # --- DECISIONS ---
        print("\n=== DECISIONS ===")
        cur.execute("SELECT slot, value FROM decisions")
        rows = cur.fetchall()
        if not rows:
            print("(empty)")
        else:
            for slot, v in rows:
                print(f"slot {slot}: value={json.loads(v) if v else None}")


        print("\n=== LATEST DECISION ===")
        try:
            cur.execute("SELECT slot, value FROM decisions ORDER BY slot DESC LIMIT 1")
            row = cur.fetchone()
            print(row)
            if not row:
                print("(empty)")
            slot, val = row
            print("Latest_Decision:", val)
        except Exception as e:
            print(f"Error on {db_path}")
            continue
                
