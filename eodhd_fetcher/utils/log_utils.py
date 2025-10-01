import sys
def info(msg: str) -> None:
    print(msg)

def warn(msg: str) -> None:
    print(f"WARN: {msg}", file=sys.stderr)
    
def error(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)