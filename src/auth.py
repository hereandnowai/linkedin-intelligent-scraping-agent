"""LinkedIn authentication handler."""
import getpass
from typing import Optional
from src.browser import LinkedInBrowser
import config


class LinkedInAuth:
    """Handles LinkedIn login and session management."""
    
    def __init__(self, browser: LinkedInBrowser):
        self.browser = browser
        self.is_authenticated = False
    
    async def login(self, email: Optional[str] = None, password: Optional[str] = None) -> bool:
        """
        Login to LinkedIn.
        
        Args:
            email: LinkedIn email (optional, will prompt if not provided)
            password: LinkedIn password (optional, will prompt if not provided)
        
        Returns:
            bool: True if login successful, False otherwise
        """
        # Try to load existing cookies first
        if await self.browser.load_cookies("linkedin_session.json"):
            await self.browser.page.goto("https://www.linkedin.com/feed/")
            await self.browser.random_delay(2, 3)
            
            # Check if still logged in
            if await self._is_logged_in():
                print("✓ Logged in using saved session")
                self.is_authenticated = True
                return True
            else:
                print("⚠ Saved session expired, logging in again...")
        
        # Get credentials
        if not email:
            email = config.LINKEDIN_EMAIL or input("LinkedIn Email: ")
        if not password:
            password = config.LINKEDIN_PASSWORD or getpass.getpass("LinkedIn Password: ")
        
        # Navigate to LinkedIn login page
        print("Navigating to LinkedIn login page...")
        await self.browser.page.goto("https://www.linkedin.com/login")
        await self.browser.random_delay()
        
        # Fill in credentials
        print("Entering credentials...")
        await self.browser.page.fill('input[name="session_key"]', email)
        await self.browser.random_delay(0.5, 1.5)
        await self.browser.page.fill('input[name="session_password"]', password)
        await self.browser.random_delay(0.5, 1.5)
        
        # Click sign in button
        print("Clicking sign in...")
        await self.browser.page.click('button[type="submit"]')
        
        # Wait for navigation
        try:
            await self.browser.page.wait_for_url("**/feed/**", timeout=15000)
            print("✓ Login successful!")
            
            # Save cookies for future sessions
            await self.browser.save_cookies("linkedin_session.json")
            
            self.is_authenticated = True
            return True
            
        except Exception as e:
            # Check if verification is needed
            if "checkpoint" in self.browser.page.url or "challenge" in self.browser.page.url:
                print("\n⚠ LinkedIn requires verification (CAPTCHA or security check)")
                print("Please complete the verification manually in the browser window...")
                print("Press Enter when done...")
                input()
                
                # Check if now logged in
                if await self._is_logged_in():
                    await self.browser.save_cookies("linkedin_session.json")
                    self.is_authenticated = True
                    return True
            
            print(f"✗ Login failed: {str(e)}")
            return False
    
    async def _is_logged_in(self) -> bool:
        """Check if currently logged into LinkedIn."""
        try:
            # Check for elements that only appear when logged in
            await self.browser.page.wait_for_selector('nav', timeout=5000)
            current_url = self.browser.page.url
            return "linkedin.com" in current_url and "login" not in current_url
        except:
            return False
    
    async def logout(self) -> None:
        """Logout from LinkedIn."""
        if self.is_authenticated:
            try:
                await self.browser.page.goto("https://www.linkedin.com/m/logout")
                print("✓ Logged out successfully")
                self.is_authenticated = False
            except Exception as e:
                print(f"⚠ Error during logout: {str(e)}")
