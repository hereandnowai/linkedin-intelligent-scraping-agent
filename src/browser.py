"""Browser initialization and management using Playwright."""
import asyncio
import random
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from typing import Optional
import config


class LinkedInBrowser:
    """Manages Playwright browser instance with anti-detection measures."""
    
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
    
    async def initialize(self) -> None:
        """Initialize Playwright browser with custom settings."""
        self.playwright = await async_playwright().start()
        
        # Launch browser with realistic settings
        self.browser = await self.playwright.chromium.launch(
            headless=config.HEADLESS,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox'
            ]
        )
        
        # Create context with realistic viewport and user agent
        self.context = await self.browser.new_context(
            user_agent=config.USER_AGENT,
            viewport={'width': 1920, 'height': 1080},
            locale='en-US',
            timezone_id='America/New_York'
        )
        
        # Add extra headers to appear more human-like
        await self.context.set_extra_http_headers({
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        })
        
        # Create page
        self.page = await self.context.new_page()
        
        # Inject scripts to hide automation
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        print("✓ Browser initialized successfully")
    
    async def random_delay(self, min_seconds: Optional[int] = None, max_seconds: Optional[int] = None) -> None:
        """Add random delay to mimic human behavior."""
        min_delay = min_seconds or config.MIN_DELAY_SECONDS
        max_delay = max_seconds or config.MAX_DELAY_SECONDS
        delay = random.uniform(min_delay, max_delay)
        await asyncio.sleep(delay)
    
    async def human_like_scroll(self) -> None:
        """Scroll the page in a human-like manner."""
        scroll_steps = random.randint(3, 6)
        for _ in range(scroll_steps):
            await self.page.evaluate(f"window.scrollBy(0, {random.randint(200, 500)})")
            await asyncio.sleep(random.uniform(0.3, 0.8))
    
    async def save_cookies(self, filename: str) -> None:
        """Save cookies to file for session persistence."""
        import json
        cookies = await self.context.cookies()
        filepath = f"{config.COOKIES_DIR}/{filename}"
        with open(filepath, 'w') as f:
            json.dump(cookies, f)
        print(f"✓ Cookies saved to {filepath}")
    
    async def load_cookies(self, filename: str) -> bool:
        """Load cookies from file."""
        import json
        filepath = f"{config.COOKIES_DIR}/{filename}"
        try:
            with open(filepath, 'r') as f:
                cookies = json.load(f)
            await self.context.add_cookies(cookies)
            print(f"✓ Cookies loaded from {filepath}")
            return True
        except FileNotFoundError:
            print(f"⚠ Cookie file not found: {filepath}")
            return False
    
    async def close(self) -> None:
        """Close browser and cleanup."""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        print("✓ Browser closed")
