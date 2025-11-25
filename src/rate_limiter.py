"""Rate limiting to avoid detection."""
import asyncio
import random
from datetime import datetime, timedelta
from typing import Optional
import config


class RateLimiter:
    """Manages rate limiting and human-like delays."""
    
    def __init__(self):
        self.profile_count = 0
        self.session_start = datetime.now()
        self.last_action_time = None
        self.max_profiles = config.MAX_PROFILES_PER_SESSION
    
    async def wait_before_action(self, action_type: str = "default") -> None:
        """
        Wait before performing an action with human-like delays.
        
        Args:
            action_type: Type of action (affects delay duration)
        """
        # Different delays for different actions
        delays = {
            "search": (2, 4),
            "profile_visit": (3, 7),
            "scroll": (1, 2),
            "default": (config.MIN_DELAY_SECONDS, config.MAX_DELAY_SECONDS)
        }
        
        min_delay, max_delay = delays.get(action_type, delays["default"])
        delay = random.uniform(min_delay, max_delay)
        
        # Add occasional longer pauses to mimic human behavior
        if random.random() < 0.1:  # 10% chance of longer pause
            delay += random.uniform(3, 8)
            print(f"⏸ Taking a short break ({delay:.1f}s)...")
        
        await asyncio.sleep(delay)
        self.last_action_time = datetime.now()
    
    def increment_profile_count(self) -> None:
        """Increment profile counter and check limits."""
        self.profile_count += 1
        
        if self.profile_count >= self.max_profiles:
            print(f"\n⚠ Reached session limit of {self.max_profiles} profiles")
            print("Consider taking a break to avoid detection")
    
    def should_continue(self) -> bool:
        """Check if we should continue scraping."""
        return self.profile_count < self.max_profiles
    
    def get_stats(self) -> dict:
        """Get current session statistics."""
        elapsed = datetime.now() - self.session_start
        return {
            "profiles_scraped": self.profile_count,
            "session_duration": str(elapsed).split('.')[0],
            "profiles_remaining": max(0, self.max_profiles - self.profile_count)
        }
    
    async def simulate_break(self, duration_seconds: Optional[int] = None) -> None:
        """Simulate a break period."""
        if duration_seconds is None:
            duration_seconds = random.randint(30, 90)
        
        print(f"\n⏸ Simulating human break for {duration_seconds} seconds...")
        await asyncio.sleep(duration_seconds)
