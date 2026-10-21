"""Run the offline suite; this entry point never calls a model provider."""
import subprocess
import sys

if __name__ == "__main__":
    raise SystemExit(subprocess.call([sys.executable, "-m", "pytest"]))
