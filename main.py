"""
LinkedIn CTO Scraping Agent

Main application for scraping CTO profiles from LinkedIn.
"""
import asyncio
import argparse
from typing import Optional, List
from src.browser import LinkedInBrowser
from src.auth import LinkedInAuth
from src.search import LinkedInSearch
from src.scraper import LinkedInScraper
from src.ai_extractor import AIExtractor
from src.rate_limiter import RateLimiter
from src.storage import DataStorage
import config


class LinkedInAgent:
    """Main LinkedIn CTO scraping agent."""
    
    def __init__(self):
        self.browser = LinkedInBrowser()
        self.auth = None
        self.search = None
        self.scraper = None
        self.ai_extractor = AIExtractor()
        self.rate_limiter = RateLimiter()
        self.storage = DataStorage()
    
    async def initialize(self) -> None:
        """Initialize all components."""
        print("\n🤖 LinkedIn CTO Scraping Agent")
        print("=" * 50)
        
        await self.browser.initialize()
        
        self.auth = LinkedInAuth(self.browser)
        self.search = LinkedInSearch(self.browser, self.rate_limiter)
        self.scraper = LinkedInScraper(self.browser, self.rate_limiter)
    
    async def login(self, email: Optional[str] = None, password: Optional[str] = None) -> bool:
        """Login to LinkedIn."""
        return await self.auth.login(email, password)
    
    async def scrape_ctos(self, 
                         max_profiles: int = 10,
                         keywords: Optional[List[str]] = None,
                         validate: bool = True) -> None:
        """
        Scrape CTO profiles.
        
        Args:
            max_profiles: Maximum number of profiles to scrape
            keywords: Search keywords (defaults to config)
            validate: Whether to validate that profiles are actually CTOs
        """
        print(f"\n🎯 Target: Scrape up to {max_profiles} CTO profiles")
        print("=" * 50)
        
        # Search for CTOs
        profile_urls = await self.search.search_ctos(keywords, max_results=max_profiles * 2)
        
        if not profile_urls:
            print("\n⚠ No profiles found. Try different search keywords.")
            return
        
        # Scrape each profile
        scraped_count = 0
        for i, url in enumerate(profile_urls, 1):
            if not self.rate_limiter.should_continue() or scraped_count >= max_profiles:
                break
            
            print(f"\n[{i}/{len(profile_urls)}] Processing profile...")
            
            # Scrape profile
            raw_data = await self.scraper.scrape_profile(url)
            
            if raw_data:
                # Enhance with AI
                enhanced_data = self.ai_extractor.enhance_profile_data(raw_data)
                
                # Validate if CTO (if requested)
                if validate:
                    is_cto = self.ai_extractor.validate_cto_profile(enhanced_data)
                    if not is_cto:
                        print("  ⚠ Skipping: Not a CTO profile")
                        continue
                
                # Store profile
                self.storage.add_profile(enhanced_data)
                scraped_count += 1
                
                # Incremental backup every 5 profiles
                if scraped_count % 5 == 0:
                    self.storage.save_incremental()
            
            # Show progress
            stats = self.rate_limiter.get_stats()
            print(f"  📊 Progress: {scraped_count}/{max_profiles} profiles scraped")
        
        print(f"\n✅ Scraping complete! Total profiles: {scraped_count}")
    
    async def scrape_from_urls(self, urls: List[str]) -> None:
        """
        Scrape specific profile URLs.
        
        Args:
            urls: List of LinkedIn profile URLs
        """
        print(f"\n🎯 Scraping {len(urls)} specific profiles")
        print("=" * 50)
        
        for i, url in enumerate(urls, 1):
            if not self.rate_limiter.should_continue():
                break
            
            print(f"\n[{i}/{len(urls)}]")
            
            # Scrape profile
            raw_data = await self.scraper.scrape_profile(url)
            
            if raw_data:
                # Enhance with AI
                enhanced_data = self.ai_extractor.enhance_profile_data(raw_data)
                
                # Store profile
                self.storage.add_profile(enhanced_data)
        
        print(f"\n✅ Scraping complete! Total profiles: {self.storage.get_count()}")
    
    async def export_data(self, format: str = "both") -> None:
        """
        Export scraped data.
        
        Args:
            format: Export format ('json', 'csv', or 'both')
        """
        print(f"\n💾 Exporting data...")
        print("=" * 50)
        
        if self.storage.get_count() == 0:
            print("⚠ No data to export")
            return
        
        if format in ["json", "both"]:
            self.storage.export_to_json()
        
        if format in ["csv", "both"]:
            self.storage.export_to_csv()
    
    async def cleanup(self) -> None:
        """Cleanup and close browser."""
        await self.browser.close()
    
    async def run(self, 
                  max_profiles: int = 10,
                  keywords: Optional[List[str]] = None,
                  export_format: str = "both",
                  profile_urls: Optional[List[str]] = None) -> None:
        """
        Run the complete scraping workflow.
        
        Args:
            max_profiles: Maximum number of profiles to scrape
            keywords: Search keywords
            export_format: Export format
            profile_urls: Specific URLs to scrape (if provided, skips search)
        """
        try:
            # Initialize
            await self.initialize()
            
            # Login
            if not await self.login():
                print("\n✗ Login failed. Exiting.")
                return
            
            print("\n✅ Login successful!")
            
            # Scrape profiles
            if profile_urls:
                await self.scrape_from_urls(profile_urls)
            else:
                await self.scrape_ctos(max_profiles, keywords)
            
            # Export data
            await self.export_data(export_format)
            
            # Show final stats
            stats = self.rate_limiter.get_stats()
            print(f"\n📊 Session Statistics:")
            print(f"  • Profiles scraped: {stats['profiles_scraped']}")
            print(f"  • Session duration: {stats['session_duration']}")
            print(f"  • Data saved to: {config.DATA_DIR}/")
            
        finally:
            await self.cleanup()


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="LinkedIn CTO Scraping Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape 10 CTO profiles
  python main.py --max-profiles 10
  
  # Scrape with custom keywords
  python main.py --max-profiles 20 --keywords "CTO" "Chief Technology Officer"
  
  # Scrape specific URLs
  python main.py --urls "https://linkedin.com/in/profile1" "https://linkedin.com/in/profile2"
  
  # Export only to JSON
  python main.py --max-profiles 5 --format json
        """
    )
    
    parser.add_argument(
        "--max-profiles",
        type=int,
        default=10,
        help="Maximum number of profiles to scrape (default: 10)"
    )
    
    parser.add_argument(
        "--keywords",
        nargs="+",
        default=None,
        help="Search keywords (default: CTO, Chief Technology Officer)"
    )
    
    parser.add_argument(
        "--format",
        choices=["json", "csv", "both"],
        default="both",
        help="Export format (default: both)"
    )
    
    parser.add_argument(
        "--urls",
        nargs="+",
        default=None,
        help="Specific LinkedIn profile URLs to scrape"
    )
    
    parser.add_argument(
        "--no-validate",
        action="store_true",
        help="Skip CTO validation (scrape all found profiles)"
    )
    
    args = parser.parse_args()
    
    # Create and run agent
    agent = LinkedInAgent()
    await agent.run(
        max_profiles=args.max_profiles,
        keywords=args.keywords,
        export_format=args.format,
        profile_urls=args.urls
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠ Interrupted by user. Exiting...")
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        raise
