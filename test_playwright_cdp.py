import asyncio
from playwright.async_api import async_playwright
import os
import time
import subprocess

async def test_cdp():
    print("Killing existing Antigravity...")
    os.system("pkill -9 antigravity")
    time.sleep(1)
    
    print("Launching Antigravity with CDP port 9222...")
    # Launch in background
    subprocess.Popen(["/opt/Antigravity/antigravity", "--remote-debugging-port=9222"], 
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    time.sleep(5) # wait for IDE to initialize and open port
    
    print("Connecting Playwright over CDP...")
    try:
        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            contexts = browser.contexts
            if not contexts:
                print("No contexts found!")
                return
            
            context = contexts[0]
            pages = context.pages
            print(f"Connected! Pages open: {len(pages)}")
            
            for page in pages:
                print(f" - Page URL: {page.url}")
                print(f" - Page Title: {await page.title()}")
                
            await browser.close()
            print("Successfully connected and disconnected!")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_cdp())
