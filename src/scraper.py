"""Profile scraping functionality."""
from typing import Dict, Optional, List
from bs4 import BeautifulSoup
from src.browser import LinkedInBrowser
from src.rate_limiter import RateLimiter
import config


class LinkedInScraper:
    """Scrapes individual LinkedIn profiles."""
    
    def __init__(self, browser: LinkedInBrowser, rate_limiter: RateLimiter):
        self.browser = browser
        self.rate_limiter = rate_limiter
    
    async def scrape_profile(self, profile_url: str) -> Optional[Dict]:
        """
        Scrape data from a LinkedIn profile.
        
        Args:
            profile_url: URL of the LinkedIn profile
        
        Returns:
            Dictionary containing profile data or None if failed
        """
        try:
            print(f"\n📄 Scraping: {profile_url}")
            
            # Navigate to profile
            await self.rate_limiter.wait_before_action("profile_visit")
            await self.browser.page.goto(profile_url, wait_until="networkidle")
            await self.browser.random_delay(3, 5)
            
            # Scroll to load all content
            await self.browser.human_like_scroll()
            await self.browser.random_delay(2, 3)
            
            # Extract data
            profile_data = {
                "profile_url": profile_url,
                "name": await self._extract_name(),
                "headline": await self._extract_headline(),
                "location": await self._extract_location(),
                "about": await self._extract_about(),
                "current_company": await self._extract_current_company(),
                "current_position": await self._extract_current_position(),
                "experience": await self._extract_experience(),
                "education": await self._extract_education(),
                "skills": await self._extract_skills()
            }
            
            # Increment profile counter
            self.rate_limiter.increment_profile_count()
            
            print(f"✓ Successfully scraped: {profile_data.get('name', 'Unknown')}")
            return profile_data
            
        except Exception as e:
            print(f"✗ Error scraping profile: {str(e)}")
            return None
    
    async def _extract_name(self) -> str:
        """Extract profile name."""
        try:
            name_element = await self.browser.page.query_selector('h1.text-heading-xlarge')
            if name_element:
                return await name_element.inner_text()
        except:
            pass
        return "N/A"
    
    async def _extract_headline(self) -> str:
        """Extract profile headline."""
        try:
            headline_element = await self.browser.page.query_selector('div.text-body-medium')
            if headline_element:
                return await headline_element.inner_text()
        except:
            pass
        return "N/A"
    
    async def _extract_location(self) -> str:
        """Extract location."""
        try:
            location_element = await self.browser.page.query_selector('span.text-body-small.inline')
            if location_element:
                return await location_element.inner_text()
        except:
            pass
        return "N/A"
    
    async def _extract_about(self) -> str:
        """Extract About section."""
        try:
            # Click "Show more" if present
            try:
                show_more = await self.browser.page.query_selector('button[aria-label*="more"]')
                if show_more:
                    await show_more.click()
                    await self.browser.random_delay(0.5, 1)
            except:
                pass
            
            about_element = await self.browser.page.query_selector('div.display-flex.ph5.pv3')
            if about_element:
                text = await about_element.inner_text()
                return text.strip()
        except:
            pass
        return "N/A"
    
    async def _extract_current_company(self) -> str:
        """Extract current company name."""
        try:
            # Look for the first experience entry
            exp_section = await self.browser.page.query_selector('#experience')
            if exp_section:
                parent = await exp_section.evaluate_handle('element => element.parentElement')
                company_element = await parent.query_selector('span.t-14.t-normal span[aria-hidden="true"]')
                if company_element:
                    return await company_element.inner_text()
        except:
            pass
        return "N/A"
    
    async def _extract_current_position(self) -> str:
        """Extract current job title."""
        try:
            exp_section = await self.browser.page.query_selector('#experience')
            if exp_section:
                parent = await exp_section.evaluate_handle('element => element.parentElement')
                title_element = await parent.query_selector('span[aria-hidden="true"]')
                if title_element:
                    return await title_element.inner_text()
        except:
            pass
        return "N/A"
    
    async def _extract_experience(self) -> List[Dict]:
        """Extract work experience."""
        experiences = []
        try:
            # Find all experience items
            exp_items = await self.browser.page.query_selector_all('li.artdeco-list__item')
            
            for item in exp_items[:5]:  # Get top 5 experiences
                try:
                    text = await item.inner_text()
                    # Parse the text (basic parsing, will be improved by AI)
                    lines = text.split('\n')
                    if len(lines) >= 2:
                        experiences.append({
                            "title": lines[0],
                            "details": " | ".join(lines[1:])
                        })
                except:
                    continue
        except:
            pass
        return experiences
    
    async def _extract_education(self) -> List[Dict]:
        """Extract education."""
        education = []
        try:
            # Find education section
            edu_section = await self.browser.page.query_selector('#education')
            if edu_section:
                parent = await edu_section.evaluate_handle('element => element.parentElement')
                edu_items = await parent.query_selector_all('li.artdeco-list__item')
                
                for item in edu_items[:3]:  # Get top 3 education entries
                    try:
                        text = await item.inner_text()
                        lines = text.split('\n')
                        if len(lines) >= 1:
                            education.append({
                                "school": lines[0],
                                "details": " | ".join(lines[1:]) if len(lines) > 1 else ""
                            })
                    except:
                        continue
        except:
            pass
        return education
    
    async def _extract_skills(self) -> List[str]:
        """Extract skills."""
        skills = []
        try:
            # Try to navigate to skills section
            skills_section = await self.browser.page.query_selector('#skills')
            if skills_section:
                # Click to expand skills
                try:
                    show_all = await self.browser.page.query_selector('a[href*="details/skills"]')
                    if show_all:
                        await show_all.click()
                        await self.browser.random_delay(1, 2)
                        
                        # Extract skill names
                        skill_elements = await self.browser.page.query_selector_all('span.mr1.t-bold span[aria-hidden="true"]')
                        for elem in skill_elements[:10]:  # Get top 10 skills
                            skill_text = await elem.inner_text()
                            if skill_text:
                                skills.append(skill_text.strip())
                        
                        # Go back
                        await self.browser.page.go_back()
                        await self.browser.random_delay(1, 2)
                except:
                    pass
        except:
            pass
        return skills
