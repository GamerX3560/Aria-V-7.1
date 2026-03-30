"""
ARIA v6 — Browser Agent
Web navigation and scraping using Scrapling stealth sessions.
"""

from agents.base_agent import BaseAgent
from typing import Tuple


class BrowserAgent(BaseAgent):
    """
    Specialized agent for web-related tasks:
    - Searching the web
    - Scraping protected sites (via Scrapling)
    - Filling forms
    - Reading web content
    
    Uses Scrapling's StealthySession for anti-bot bypass
    and the browser-use library for DOM interaction.
    """

    def __init__(self):
        super().__init__(
            name="browser",
            role="browsing the web, searching online, scraping websites, and extracting web data",
            agent_type="browser"
        )

    async def process(self, task: str, context: str = "") -> Tuple[str, bool]:
        """Execute web tasks using Scrapling or browser-use."""
        self.status = "browsing"
        try:
            from scrapling.fetchers import StealthySession
            
            with StealthySession(headless=True) as session:
                page = session.fetch(task if task.startswith("http") else f"https://www.google.com/search?q={task}")
                title = ""
                try:
                    title_elements = page.css('title')
                    if title_elements:
                        title = title_elements[0].text
                except Exception:
                    title = "Unknown"
                
                # Extract text content
                text_content = []
                for element in page.css('p, h1, h2, h3, li')[:20]:
                    try:
                        text = element.text.strip()
                        if text and len(text) > 10:
                            text_content.append(text)
                    except Exception:
                        continue
                
                result = f"Page: {title}\n\n" + "\n".join(text_content[:15])
                self.success = True
                self.last_answer = result
                self.status = "done"
                return result, True

        except ImportError:
            # Fallback: use the browser_agent.py skill
            from core.tool_executor import execute
            result = execute(f'python3 ~/aria/skills/browser_agent.py "{task}"', timeout=60)
            success = "ERROR" not in result
            self.success = success
            self.last_answer = result
            self.status = "done"
            return result, success
        except Exception as e:
            self.status = "error"
            self.success = False
            return f"Browser agent error: {e}", False
