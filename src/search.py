"""LinkedIn search functionality."""
from typing import List
from src.browser import LinkedInBrowser
from src.rate_limiter import RateLimiter
import config


class LinkedInSearch:
    """Handles LinkedIn search operations."""
    
    def __init__(self, browser: LinkedInBrowser, rate_limiter: RateLimiter):
        self.browser = browser
        self.rate_limiter = rate_limiter
    
    async def search_ctos(self, keywords: List[str] = None, max_results: int = 50) -> List[str]:
        """
        Search for CTO profiles on LinkedIn.
        
        Args:
            keywords: Search keywords (defaults to config.SEARCH_KEYWORDS)
            max_results: Maximum number of profile URLs to return
        
        Returns:
            List of profile URLs
        """
        if keywords is None:
            keywords = config.SEARCH_KEYWORDS
        
        profile_urls = []
        
        for keyword in keywords:
            print(f"\n🔍 Searching for: {keyword}")
            
            # Build search URL for people with specific job title
            search_query = keyword.replace(" ", "%20")
            search_url = f"https://www.linkedin.com/search/results/people/?keywords={search_query}&origin=GLOBAL_SEARCH_HEADER"
            
            await self.rate_limiter.wait_before_action("search")
            await self.browser.page.goto(search_url)
            await self.browser.random_delay(3, 5)
            
            # Scroll to load more results
            await self.browser.human_like_scroll()
            await self.rate_limiter.wait_before_action("scroll")
            
            # Extract profile URLs from search results
            urls = await self._extract_profile_urls()
            profile_urls.extend(urls)
            
            print(f"✓ Found {len(urls)} profiles for '{keyword}'")
            
            # Stop if we have enough results
            if len(profile_urls) >= max_results:
                break
        
        # Remove duplicates and limit to max_results
        profile_urls = list(dict.fromkeys(profile_urls))[:max_results]
        print(f"\n✓ Total unique profiles found: {len(profile_urls)}")
        
        return profile_urls
    
    async def _extract_profile_urls(self) -> List[str]:
        """Extract profile URLs from current search results page."""
        try:
            # Wait for search results to load
            await self.browser.page.wait_for_selector('.reusable-search__result-container', timeout=10000)
            
            # Extract all profile links
            profile_links = await self.browser.page.query_selector_all('a.app-aware-link')
            
            urls = []
            for link in profile_links:
                href = await link.get_attribute('href')
                if href and '/in/' in href and 'miniProfileUrn' not in href:
                    # Clean URL (remove query parameters)
                    clean_url = href.split('?')[0]
                    if clean_url not in urls:
                        urls.append(clean_url)
            
            return urls
            
        except Exception as e:
            print(f"⚠ Error extracting profile URLs: {str(e)}")
            return []
    
    async def search_by_company(self, company_name: str) -> List[str]:
        """
        Search for CTOs at a specific company.
        
        Args:
            company_name: Name of the company
        
        Returns:
            List of CTO profile URLs at that company
        """
        print(f"\n🔍 Searching for CTOs at: {company_name}")
        
        # Build search URL for CTO at specific company
        search_query = f"CTO%20{company_name.replace(' ', '%20')}"
        search_url = f"https://www.linkedin.com/search/results/people/?keywords={search_query}&origin=GLOBAL_SEARCH_HEADER"
        
        await self.rate_limiter.wait_before_action("search")
        await self.browser.page.goto(search_url)
        await self.browser.random_delay(3, 5)
        
        # Scroll and extract
        await self.browser.human_like_scroll()
        urls = await self._extract_profile_urls()
        
        print(f"✓ Found {len(urls)} potential CTOs at {company_name}")
        return urls
