"""Central place for global variables"""

from pathlib import Path

# import threading

# Lock for thread-safe access
# _lock = threading.Lock()

# Global variables
# Get the directory where the script is located
root_path = Path(__file__).parent.resolve()


# def set_root_path(root_path: str):
#     """Set root path variable"""
#     with _lock:
#         globals()["ROOT_PATH"] = root_path
