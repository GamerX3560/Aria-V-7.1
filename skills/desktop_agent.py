import os
import subprocess
import time
import asyncio
from loguru import logger as log

class DesktopAgent:
    """Agent for controlling the Linux Wayland desktop natively via ydotool."""
    
    def __init__(self):
        self.ensure_daemon()
    
    def ensure_daemon(self):
        """Ensure ydotoold is running."""
        try:
            # Check if ydotoold is running
            subprocess.run(["pgrep", "ydotoold"], check=True, stdout=subprocess.DEVNULL)
            log.info("ydotoold is already running.")
        except subprocess.CalledProcessError:
            log.info("Starting ydotoold in the background...")
            # We try running it directly. Note: on some systems it needs sudo, 
            # but usually it works if user is in input group.
            os.system("ydotoold &")
            time.sleep(1)

    def mouse_move(self, x: int, y: int):
        """Move mouse to absolute coordinates."""
        try:
            subprocess.run(["ydotool", "mousemove", "-a", str(x), str(y)], check=True)
            return True
        except Exception as e:
            log.error(f"Mouse move failed: {e}")
            return False

    def mouse_click(self, button: str = "left"):
        """Click the mouse. button can be 'left', 'right', 'middle'."""
        btns = {"left": "0xC0", "right": "0xC1", "middle": "0xC2"} # ydotool left/right hex codes
        # Actually ydotool click uses: 0xC0=left, 0xC1=right, 0xC2=middle.
        btn_code = btns.get(button.lower(), "0xC0")
        try:
            subprocess.run(["ydotool", "click", btn_code], check=True)
            return True
        except Exception as e:
            log.error(f"Mouse click failed: {e}")
            return False

    def type_text(self, text: str):
        """Type text string."""
        try:
            subprocess.run(["ydotool", "type", text], check=True)
            return True
        except Exception as e:
            log.error(f"Type text failed: {e}")
            return False

    def press_key(self, keycode: str):
        """Press a specific key (e.g., 'enter', 'esc', 'ctrl+c')."""
        try:
            subprocess.run(["ydotool", "key", keycode], check=True)
            return True
        except Exception as e:
            log.error(f"Key press failed: {e}")
            return False

async def handle_desktop_command(action: str, **kwargs) -> str:
    """Router hook for desktop automation."""
    agent = DesktopAgent()
    if action == "mouse_move":
        success = agent.mouse_move(kwargs.get("x", 0), kwargs.get("y", 0))
        return "Moved mouse." if success else "Failed to move mouse."
    elif action == "mouse_click":
        success = agent.mouse_click(kwargs.get("button", "left"))
        return "Clicked mouse." if success else "Failed to click."
    elif action == "type_text":
        success = agent.type_text(kwargs.get("text", ""))
        return "Typed text." if success else "Failed to type."
    elif action == "press_key":
        success = agent.press_key(kwargs.get("key", "enter"))
        return f"Pressed key {kwargs.get('key')}." if success else "Failed to press key."
        return f"Unknown desktop action: {action}"

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="ARIA Desktop GUI Agent")
    subparsers = parser.add_subparsers(dest="action", help="Action to perform")
    
    # Move
    parser_move = subparsers.add_parser("move", help="Move mouse to X Y")
    parser_move.add_argument("x", type=int)
    parser_move.add_argument("y", type=int)
    
    # Click
    parser_click = subparsers.add_parser("click", help="Click mouse button")
    parser_click.add_argument("button", choices=["left", "right", "middle"], default="left", nargs="?")
    
    # Type
    parser_type = subparsers.add_parser("type", help="Type text")
    parser_type.add_argument("text", type=str)
    
    # Key
    parser_key = subparsers.add_parser("key", help="Press key (e.g., enter, esc)")
    parser_key.add_argument("key", type=str)
    
    args = parser.parse_args()
    
    if args.action == "move":
        print(asyncio.run(handle_desktop_command("mouse_move", x=args.x, y=args.y)))
    elif args.action == "click":
        print(asyncio.run(handle_desktop_command("mouse_click", button=args.button)))
    elif args.action == "type":
        print(asyncio.run(handle_desktop_command("type_text", text=args.text)))
    elif args.action == "key":
        print(asyncio.run(handle_desktop_command("press_key", key=args.key)))
    else:
        parser.print_help()
