import os
from pathlib import Path
import sqlite3

import json
# unique id -> unique db -> unique decisions
from typing import Dict, Optional, Tuple, List

from paxos.node_lock import NodeLock
# -----------------
# Persistent storage
# -----------------


class AcceptorStorage:
    """SQLite-based storage for acceptor state, supporting single and multi-slot Paxos."""
    SQL_DIR = Path(__file__).parent / "sql"

    def __init__(self, path: str, node_id: Optional[int] = None):

        # --- enforce OS-level lock ---
        lock_path = f"{path}.lock"
        self.lock = NodeLock(lock_path)
        self.lock.acquire()

        init_needed = not os.path.exists(path)
        self.path = path
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.conn.execute("PRAGMA synchronous=FULL;")
        self.meta_sql = self._load_queries("meta.sql")
        self.global_sql = self._load_queries("global_state.sql")
        self.slots_sql = self._load_queries("slots.sql")
        self.decisions_sql = self._load_queries("decisions.sql")

        if init_needed:
            self._init_db()
        if node_id is not None:
            self._check_or_set_node_id(node_id)

    def _load_sql(self, filename: str) -> str:
       with open(self.SQL_DIR / filename, "r", encoding="utf-8") as f:
           return f.read()

    def _load_queries(self, filename: str) -> dict[str, str]:
        queries = {}
        path = self.SQL_DIR / filename
        current_name = None
        buffer = []

        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("--"):
                    if current_name:
                        queries[current_name] = "".join(buffer).strip()
                        buffer = []
                    current_name = line[2:].strip()
                else:
                    buffer.append(line)

        if current_name:
            queries[current_name] = "".join(buffer).strip()

        return queries

    def _init_db(self):
        cur = self.conn.cursor()
        # Meta table for node identity and misc info
        
        cur.execute(self._load_sql("init_meta.sql"))
        cur.execute(self._load_sql("init_global_state.sql"))
        cur.execute(self._load_sql("seed_global_state.sql"))
        cur.execute(self._load_sql("init_slots.sql"))
        cur.execute(self._load_sql("init_decisions.sql"))

        self.conn.commit()

    """
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
    """

    def _check_or_set_node_id(self, node_id: int):
        cur = self.conn.cursor()
        cur.execute(self.meta_sql["get_node_id"])
        row = cur.fetchone()

        if not row:
            cur.execute(
                self.meta_sql["insert_node_id"],
                (json.dumps(node_id),)
            )
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
    """
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
    """
    def _get_global_promised(self) -> Optional[int]:
        cur = self.conn.cursor()
        cur.execute(self.global_sql["get_global_promised"])
        row = cur.fetchone()
        if not row or row[0] is None:
            return None
        return json.loads(row[0])


    def _set_global_promised(self, v: Optional[int]):
        cur = self.conn.cursor()
        cur.execute(
            self.global_sql["set_global_promised"],
            (None if v is None else json.dumps(v),)
        )
        self.conn.commit()
    # -----------------
    # Unified API
    # -----------------
    def next_slot(self) -> int:
        slots = self.all_slots()
        return max(slots, default=0) + 1

    def get_promised(self, slot: Optional[int] = None) -> Optional[int]:
        if slot is None:
            return self._get_global_promised()

        cur = self.conn.cursor()
        cur.execute(self.slots_sql["get_promised"], (slot,))
        row = cur.fetchone()
        if not row or row[0] is None:
            return None
        return json.loads(row[0])

    def set_promised(self, slot: Optional[int], proposal_id: int):
        if slot is None:
            return self._set_global_promised(proposal_id)

        cur = self.conn.cursor()
        cur.execute(
            self.slots_sql["upsert_promised"],
            (slot, json.dumps(proposal_id))
        )
        self.conn.commit()

    def set_accepted(self, slot: int, accepted_id: int, accepted_value):
        cur = self.conn.cursor()

        cur.execute(
            self.slots_sql["upsert_accepted"],
            (slot, json.dumps(accepted_id), json.dumps(accepted_value))
        )

        # atomically update meta.latest_proposal_id if this accepted_id is higher
        self._update_meta_latest_if_higher(cur, accepted_id)

        self.conn.commit()

    def get_accepted(self, slot: int):
        cur = self.conn.cursor()
        cur.execute(self.slots_sql["get_accepted"], (slot,))
        row = cur.fetchone()
        if not row:
            return None

        aid, val = row
        return (
            json.loads(aid) if aid else None,
            json.loads(val) if val else None
        )

    def accepted(self, slot: int) -> Tuple[Optional[int], Optional[any]]:
        result = self.get_accepted(slot)
        if result is None:
            return (None, None)
        return result

    def all_slots(self) -> List[int]:
        cur = self.conn.cursor()
        cur.execute(self.slots_sql["all_slots"])
        return [row[0] for row in cur.fetchall()]

    def all_accepted(self):
        cur = self.conn.cursor()
        cur.execute(self.slots_sql["all_accepted"])

        result = {}
        for slot, aid, val in cur.fetchall():
            if aid:
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

        cur.execute(
            self.decisions_sql["upsert_decision"],
            (slot, json.dumps(value), proposal_id)
        )

        # Inline to preserve atomicity (do NOT call set_accepted/set_promised)
        cur.execute(
            self.slots_sql["upsert_accepted"],
            (slot, json.dumps(proposal_id), json.dumps(value))
        )

        cur.execute(
            self.slots_sql["upsert_promised"],
            (slot, json.dumps(proposal_id))
        )

        self._update_meta_latest_if_higher(cur, proposal_id)
        self.conn.commit()

    def get_decision(self, slot: int):
        cur = self.conn.cursor()
        cur.execute(self.decisions_sql["get_decision"], (slot,))
        row = cur.fetchone()

        if not row or row[0] is None:
            return None

        return json.loads(row[0]), row[1]

    def all_decisions(self):
        cur = self.conn.cursor()
        cur.execute(self.decisions_sql["all_decisions"])
        return {slot: json.loads(val) for slot, val in cur.fetchall()}


    def get_latest_decision(self):
        cur = self.conn.cursor()
        cur.execute(self.decisions_sql["get_latest_decision"])
        row = cur.fetchone()
        if not row:
            return None
        return json.loads(row[1]) if row[1] else None

    def get_last_decision(self):
        cur = self.conn.cursor()
        cur.execute("""
            SELECT slot, value, proposal_id
            FROM decisions
            ORDER BY slot DESC
            LIMIT 1
        """)
        row = cur.fetchone()

        if row is None or row[1] is None:
            return None

        slot = row[0]
        value = json.loads(row[1])
        proposal_id = row[2]

        return slot, value, proposal_id
    def accepted_with_slot(self, slot: int) -> Tuple[int, any, any]:
        """
        Return a tuple (slot, accepted_id, accepted_value)
        """
        accepted_id, accepted_value = self.accepted(slot)
        return slot, accepted_id, accepted_value
    def set_latest_proposal_id(self, proposal_id: int):
        """Persist the latest known proposal ID (used for sync tracking)."""
        cur = self.conn.cursor()
        cur.execute("""
        INSERT INTO meta (key, val) VALUES ('latest_proposal_id', ?)
        ON CONFLICT(key) DO UPDATE SET val=excluded.val
        """, (json.dumps(proposal_id),))
        self.conn.commit()
    def get_latest_proposal_id(self) -> Optional[int]:
        cur = self.conn.cursor()
        cur.execute("SELECT val FROM meta WHERE key='latest_proposal_id'")
        row = cur.fetchone()
        if row and row[0] is not None:
            try:
                return json.loads(row[0])
            except Exception:
                return int(row[0])
        return row[0] if row and row[0] is not None else None


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

    def get_highest_less_than_n(self, slot: int, n: int):
        """
        Return (accepted_value, slot, accepted_id) if accepted_id < n,
        else return None.
        """

        cur = self.conn.cursor()
        cur.execute("""
            SELECT accepted_id, accepted_value
            FROM slots
            WHERE slot = ?
        """, (slot,))

        row = cur.fetchone()
        if not row:
            return None

        aid, aval = row
        if aid is None:
            return None

        accepted_id = json.loads(aid)
        accepted_value = json.loads(aval)

        if accepted_id < n:
            return (accepted_value, slot, accepted_id)
        return None

    # -----------------
    # Meta helpers
    # -----------------
    def get_meta(self, key: str):
        cur = self.conn.cursor()
        cur.execute(self.meta_sql["get_meta"], (key,))
        row = cur.fetchone()
        return None if not row else json.loads(row[0])

    def set_meta(self, key: str, val):
        cur = self.conn.cursor()
        cur.execute(
            self.meta_sql["upsert_meta"],
            (key, json.dumps(val))
        )
        self.conn.commit()

    def _update_meta_latest_if_higher(self, cur, new_pid: int):
        cur.execute(self.meta_sql["get_latest_proposal_id"])
        row = cur.fetchone()

        current = None
        if row and row[0] is not None:
            try:
                current = int(json.loads(row[0]))
            except Exception:
                try:
                    current = int(row[0])
                except Exception:
                    current = None

        if current is None or new_pid > current:
            cur.execute(
                self.meta_sql["upsert_latest_proposal_id"],
                (json.dumps(new_pid),)
            )

def test_latest():
    # Example DB path for testing
    test_db = "test_paxos_node.db"

    # Create storage (will init if not exists)
    storage = AcceptorStorage(test_db, node_id=99)


    # --- Insert some decisions for testing ---
    storage.set_decision(1, {"value": "first"}, 1)
    storage.set_decision(2, {"value": "second"},2)
    storage.set_decision(3, {"value": "third"}, 25)

    print("Get Promised1:", storage.get_promised(1))
    print("Get Promised2:", storage.get_promised(2))
    print("Get Promised3:", storage.get_promised(3))


    print("Get Accepted1:", storage.get_accepted(1))
    print("Get Accepted2:", storage.get_accepted(2))
    print("Get Accepted3:", storage.get_accepted(3))

    print("Get Decisions1: ", storage.get_decision(1))
    print("Get Decisions2: ", storage.get_decision(2))
    print("Get Decisions3: ", storage.get_decision(3))

    print("GetLastDecision:", storage.get_latest_decision())
    
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
                
