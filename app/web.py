import os
from flask import Flask, jsonify, request

try:
    import pydevd_pycharm  # type: ignore
except Exception:
    pydevd_pycharm = None

app = Flask(__name__)


def maybe_connect_debugger() -> dict:
    if os.getenv("PYCHARM_REMOTE") != "1":
        return {"connected": False, "reason": "PYCHARM_REMOTE not set to 1"}

    if pydevd_pycharm is None:
        return {"connected": False, "reason": "pydevd_pycharm not installed"}

    host = os.getenv("PYCHARM_REMOTE_HOST", "192.168.10.106")
    port_str = os.getenv("PYCHARM_REMOTE_PORT", "5454")
    try:
        port = int(port_str)
    except ValueError:
        port = 5454

    try:
        try:
            # Prefer snake_case for new versions
            pydevd_pycharm.settrace(
                host=host,
                port=port,
                stdout_to_server=True,
                stderr_to_server=True,
                suspend=False,
            )
        except TypeError:
            # Fallback to camelCase for older versions
            pydevd_pycharm.settrace(
                host=host,
                port=port,
                stdoutToServer=True,
                stderrToServer=True,
                suspend=False,
            )
    except Exception as e:
        return {
            "connected": False,
            "host": host,
            "port": port,
            "error": str(e),
            "exc_type": e.__class__.__name__,
        }

    return {"connected": True, "host": host, "port": port}


@app.before_request
def auto_attach_if_enabled():
    # If AUTO_ATTACH_ON_REQUEST=1, try to attach the debugger on every request
    if os.getenv("AUTO_ATTACH_ON_REQUEST") == "1":
        # Avoid re-attaching too often: only attempt once per-process
        flag = "_pycharm_attached"
        if not getattr(app, flag, False):
            result = maybe_connect_debugger()
            if result.get("connected"):
                setattr(app, flag, True)

@app.get("/")
def index():
    return jsonify({"status": "ok", "message": "Flask app running. Call /debug to attach debugger."})


@app.get("/debug")
def debug_attach():
    result = maybe_connect_debugger()
    return jsonify({"action": "debug_attach", **result})


@app.get("/fib/<int:n>")
def fib(n: int):
    # A small function to set breakpoints on
    def compute_fibonacci(k: int) -> int:
        if k <= 1:
            return k
        a, b = 0, 1
        for _ in range(2, k + 1):
            a, b = b, a + b
        return b

    value = compute_fibonacci(n)
    return jsonify({"n": n, "fib": value})


if __name__ == "__main__":
    # Default to port 5455 as requested
    port_str = os.getenv("PORT", "5455")
    try:
        port = int(port_str)
    except ValueError:
        port = 5455

    # When using uvicorn-like managers we won't run this block
    app.run(host="0.0.0.0", port=port)
