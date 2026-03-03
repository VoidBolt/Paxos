import os
import csv
import json

from dataclasses import dataclass
import time
from datetime import datetime, timezone

import logging
# Logger Interface like .Net ILogger
# from ILogger import ILogger
from utils.networkLogger import NetworkLogger
from logging.handlers import RotatingFileHandler

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()

class JSONFormatter(logging.Formatter):
    def format(self, record):
        base = {
            "ts": datetime.now(timezone.utc).isoformat(), # datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        # Merge any structured data passed via `extra`
        if hasattr(record, "extra_data"):
            base.update(record.extra_data) # type: ignore[attr-defined]
        return json.dumps(base)

def _make_logger(node_id: int, log_dir="logs", console_log_level=logging.DEBUG):

    script_filename = os.path.basename(__file__)  # e.g., "myscript.py"
    app_name, _ = os.path.splitext(script_filename)
    os.makedirs(log_dir, exist_ok=True)
    logger = logging.getLogger(f"{app_name}{node_id}")
    logger.setLevel(console_log_level)  # debug-level for local dev; filter in handler if needed

    format = "[%(asctime)s] [%(levelname)s] %(message)s"

    # avoid duplicate handlers on reload
    if not logger.handlers:
        # human-readable rotating file
        fh = RotatingFileHandler(f"{log_dir}/node_{node_id}.log", maxBytes=4*1024*1024, backupCount=5)
        fh.setLevel(logging.INFO)
        fh.setFormatter(JSONFormatter())
        logger.addHandler(fh)

        # console
        ch = logging.StreamHandler()
        ch.setLevel(console_log_level)
        ch.setFormatter(logging.Formatter(format))
        logger.addHandler(ch)

        logger.propagate = False  # prevent duplicate output via root logger

    return logger

@dataclass
class PaxosLogEntry:
    round: int
    timestamp: datetime
    from_node_id: int
    from_node_role: str
    from_node_state: str
    to_node_id: int
    to_node_role: str
    to_node_state: str
    action: str
    action_value: str
    consensus_value: str
    consensus_reached: bool

class PaxosLogger(NetworkLogger):
    def __init__(self, round, node_id: int, log_dir="logs", console_log_level=logging.INFO, base_url="http://10.10.0.100:5000/api/logger", verbose=False, post=True):
        super(PaxosLogger, self).__init__(base_url=base_url, verbose=verbose, post=post)
        print(f"PaxosLogger init with base_url: {base_url}")
        self._round = round
    
        # --- Set up internal Python logger ---
        self.node_id = node_id # or "global"
        filename=f"paxosresult_{self.node_id}.csv"
        self.entries = []
        self.filename = filename
        self._logger = _make_logger(node_id=self.node_id, log_dir=log_dir, console_log_level=console_log_level)

    @property
    def round(self):
        return self._round

    @round.setter
    def round(self, value):
        if isinstance(value, int) and value >= 0:
            self._round = value
        else:
            raise ValueError("Consensus round must be non-negative number")

    def record_log(self, from_node_id, from_node_role, from_node_state, to_node_id, to_node_role, to_node_state, action, action_value, consensus_value, consensus_reached):
        # Automatically reverse sender/receiver for RECEIVE actions
        if str(action).startswith("RECEIVE"):
            from_node_id, to_node_id = to_node_id, from_node_id
            from_node_role, to_node_role = to_node_role, from_node_role
            from_node_state, to_node_state = to_node_state, from_node_state
        entry = PaxosLogEntry(
            round=self.round,
            timestamp=time.time_ns() / 1_000_000_000, # datetime.fromtimestamp(time.perf_counter_ns()/ 1_000_000_000), # datetime.now(),
            from_node_id=from_node_id,
            from_node_role=from_node_role,
            from_node_state=from_node_state,
            to_node_id=to_node_id,
            to_node_role=to_node_role,
            to_node_state=to_node_state,
            action=action,
            action_value=str(action_value),
            consensus_value=str(consensus_value),
            consensus_reached=consensus_reached
        )
        self.entries.append(entry)
        
    def save_to_csv(self):
        with open(self.filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Round', 'Timestamp', 'From Node ID', 'From Node Role', 'From Node State', 'To Node ID', 'To Node Role', 'To Node State', 'Action', 'Action Value', 'Consensus Value', 'Consensus Reached'])
            for entry in self.entries:
                writer.writerow([
                    entry.round,
                    entry.timestamp, # .strftime("%Y-%m-%d %H:%M:%S"),  # Ensuring timestamp is formatted properly
                    entry.from_node_id, entry.from_node_role, entry.from_node_state,
                    entry.to_node_id, entry.to_node_role, entry.to_node_state, entry.action, entry.action_value,
                    entry.consensus_value, entry.consensus_reached
                ])
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.save_to_csv()
        if exc_type:
            self._logger.error(
                "Exception during PaxosLogger context",
                exc_info=(exc_type, exc_val, exc_tb)
            )

