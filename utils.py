# utils.py
import pickle, os, platform, subprocess

def load_authorized(path="encodings/authorized.pkl"):
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return pickle.load(f)

def lock_workstation():
    """Cross-platform examples to lock workstation. Choose what's applicable."""
    sys = platform.system()
    try:
        if sys == "Windows":
            # Windows Lock
            import ctypes
            ctypes.windll.user32.LockWorkStation()
        elif sys == "Linux":
            # common command for GNOME
            subprocess.run(["gnome-screensaver-command", "-l"])
        elif sys == "Darwin":
            # macOS – show lock screen
            subprocess.run(["/System/Library/CoreServices/Menu Extras/User.menu/Contents/Resources/CGSession", "-suspend"])
        else:
            print("Lock not implemented for platform:", sys)
    except Exception as e:
        print("Failed to lock workstation:", e)
