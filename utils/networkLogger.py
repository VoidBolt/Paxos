import json
import traceback
import threading
import datetime
import requests
from urllib3.exceptions import NewConnectionError
from formatting import install_rich, print_jq

# works with report_server but both still need work, but this is better since it implements the standard logger interface!
#from networking.report_server import main

# Logger Interface like .Net ILogger
from ILogger import ILogger

class NetworkLogger(ILogger):
    def __init__(
        self,
        base_url="http://127.0.0.1:5000/api/logger",
        verbose=False,
        post=True,
    ):
        self.base_url = base_url.rstrip("/")
        self.verbose = verbose
        self.post = post

        print(f"NetworkLogger init with base_url: {base_url}")
        # Optional rich console
        self.console = install_rich()
        self._print = self.console.print if self.console else print
        self._log = self.console.log if self.console else print

    # ----------------------------------------------------------------------
    # 🧩 Public Standard Logging Interface
    # ----------------------------------------------------------------------
    def log(self, level, msg, **kwargs):
        """Generic log method (level can be DEBUG, INFO, WARNING, ERROR, CRITICAL)"""
        level_name = str(level).upper()
        self._send(level_name, msg, **kwargs)

    def debug(self, msg, **kwargs):
        self._send("DEBUG", msg, **kwargs)

    def info(self, msg, **kwargs):
        self._send("INFO", msg, **kwargs)

    def warning(self, msg, **kwargs):
        self._send("WARN", msg, **kwargs)

    def error(self, msg, **kwargs):
        self._send("ERROR", msg, **kwargs)

    def critical(self, msg, **kwargs):
        self._send("CRITICAL", msg, **kwargs)

    # ----------------------------------------------------------------------
    # ⚙️ Internal helpers
    # ----------------------------------------------------------------------
    def _send(self, level, *args, err=None, blocking=False, jq=False, **kwargs):
        """
        Internal core logic for all log levels.
        Automatically serializes arguments and exceptions, posts asynchronously if needed.
        """
        # Safe formatting
        formatted = self._format_args_for_logging(*args)
        exception_info = self._wrap_exception(err)

        if jq and self.verbose:
            print_jq(formatted)
        elif self.verbose:
            self._print(f"[{level}] {' '.join(formatted)}")

        if not self.post:
            return

        payload = {
            "message": formatted,
            "error": exception_info,
            "extra": kwargs,
            "timestamp": str(datetime.datetime.utcnow()),
        }

        endpoint = f"{self.base_url}/{self._resolve_endpoint(level, bool(err))}"

        if blocking:
            self._post(payload, endpoint)
        else:
            threading.Thread(target=self._post, args=(payload, endpoint)).start()

    def _resolve_endpoint(self, level, has_exception):

        """Map logging levels and Ex variants to API endpoints"""
        if has_exception:
            return f"{level.capitalize()}Ex"
        elif level == "DEBUG":
            return "DebugEx"
        elif level == "INFO":
            return "LogEx"
        elif level == "WARN":
            return "WarnEx"
        elif level == "ERROR":
            return "ErrorEx"
        elif level == "CRITICAL":
            return "CriticalEx"
        else:
            return level.capitalize()

    def _format_args_for_logging(self, *args):
        """Convert any combination of objects into readable strings."""
        formatted = []
        for a in args:
            try:
                if isinstance(a, (dict, list)):
                    formatted.append(json.dumps(a, indent=2, default=str))
                else:
                    formatted.append(str(a))
            except Exception:
                formatted.append(repr(a))
        return formatted

    def _wrap_exception(self, e):
        if e is None:
            return None
        return {
            "type": type(e).__name__,
            "message": str(e),
            "traceback": traceback.format_exception(type(e), e, e.__traceback__),
        }

    def _post(self, payload, endpoint):
        headers = {"Content-Type": "application/json"}
        try:
            response = requests.post(endpoint, json=payload, headers=headers, timeout=5)
            if self.verbose:
                self._print(f"POST {endpoint} [{response.status_code}]")
        except (requests.exceptions.RequestException, NewConnectionError) as e:
            if self.verbose:
                self._print(f"⚠️ Failed to post log: {e}")

    # ----------------------------------------------------------------------
    # 🧮 Specialized methods from legacy logger
    # ----------------------------------------------------------------------
    def dataframe(self, df, blocking=False):
        """Send pandas DataFrame to DF endpoint"""
        endpoint = f"{self.base_url}/DF"
        payload = df.to_json()
        if blocking:
            self._post(payload, endpoint)
        else:
            threading.Thread(target=self._post, args=(payload, endpoint)).start()

    def json(self, obj, blocking=False):
        """Send arbitrary JSON to json endpoint"""
        endpoint = f"{self.base_url}/json"
        payload = json.dumps(obj, default=str)
        if blocking:
            self._post(payload, endpoint)
        else:
            threading.Thread(target=self._post, args=(payload, endpoint)).start()


# ----------------------------------------------------------------------
# 🧪 Example usage
# ----------------------------------------------------------------------
if __name__ == "__main__":
    logger = NetworkLogger(verbose=True, post=True)

    logger.debug("Debugging something", user="admin", session=123)
    logger.info("Started process", pid=42)
    logger.warning("Low disk space", free_gb=1.2)
    logger.error("Error while loading config", path="/etc/config.json")

    try:
        1 / 0
    except Exception as e:
        logger.critical("Unhandled exception in task", err=e)

