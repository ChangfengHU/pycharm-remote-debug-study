import os
import sys
import time


def compute_fibonacci(n: int) -> int:
    """A small CPU task to make stepping visible in debugger."""
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def run_server() -> None:
    """Simple loop to keep process alive for remote debug attach."""
    print("Example app started. PID:", os.getpid())
    print("Set BREAKPOINT in compute_fibonacci or below.\n")

    # Demo workload
    for i in range(10, 20):
        value = compute_fibonacci(i)
        print(f"fib({i}) = {value}")
        time.sleep(0.5)

    # Keep process alive for attach testing
    print("Entering idle loop. Attach your debugger now…")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down…")


if __name__ == "__main__":
    # Optional: enable via env var so script works with or without debugger.
    # If PYCHARM_REMOTE=1, connect to a PyCharm Debug Server at host:port.
    if os.getenv("PYCHARM_REMOTE") == "1":
        try:
            import pydevd_pycharm  # type: ignore
        except Exception as e:
            print("pydevd_pycharm not found. Install with: pip install pydevd-pycharm")
            print("Error:", e)
        else:
            host = os.getenv("PYCHARM_REMOTE_HOST", "127.0.0.1")
            port_str = os.getenv("PYCHARM_REMOTE_PORT", "5454")
            try:
                port = int(port_str)
            except ValueError:
                print(f"Invalid PYCHARM_REMOTE_PORT '{port_str}', falling back to 5454")
                port = 5454

            print(f"Connecting to PyCharm Debug Server at {host}:{port} …")
            try:
                # Newer pydevd versions use snake_case kwargs
                pydevd_pycharm.settrace(
                    host=host,
                    port=port,
                    stdout_to_server=True,
                    stderr_to_server=True,
                    suspend=False,
                )
            except TypeError:
                # Backward compatibility with older camelCase kwargs
                pydevd_pycharm.settrace(
                    host=host,
                    port=port,
                    stdoutToServer=True,
                    stderrToServer=True,
                    suspend=False,
                )

    # Allow a short run mode for CI/tooling so we don't block forever
    if os.getenv("SHORT_RUN") == "1":
        print("SHORT_RUN=1 → running short demo…")
        for i in range(10, 13):
            value = compute_fibonacci(i)
            print(f"fib({i}) = {value}")
            time.sleep(0.2)
        print("Short demo done.")
    else:
        run_server()
