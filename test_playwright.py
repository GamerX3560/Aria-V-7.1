from playwright.sync_api import sync_playwright
import time

def test():
    with sync_playwright() as p:
        try:
            print("Launching Antigravity via Playwright (Electron)...")
            # We pass the executable path. Often Electron apps need an entry point or just the executable.
            # We also pass the user data dir so it retains logins/projects.
            app = p.electron.launch(
                executable_path="/opt/Antigravity/antigravity",
                args=["--user-data-dir=/home/gamerx/.config/Antigravity"]
            )
            print("App Launched!")
            
            # Get the first window
            window = app.first_window()
            print("Window URL:", window.url)
            print("Window Title:", window.title())
            
            # Wait a few seconds to let it load
            time.sleep(3)
            print("Current HTML snapshot summary:")
            content = window.content()
            print(f"Content length: {len(content)} bytes")
            
            # Attempt to find some text or elements
            app.close()
            print("Success!")
        except Exception as e:
            print(f"Failed: {e}")

if __name__ == "__main__":
    test()
