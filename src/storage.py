"""Data storage and export functionality."""
import json
import pandas as pd
from datetime import datetime
from typing import List, Dict
import config


class DataStorage:
    """Handles data persistence and export."""
    
    def __init__(self):
        self.profiles = []
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def add_profile(self, profile_data: Dict) -> None:
        """
        Add a profile to the storage.
        
        Args:
            profile_data: Profile data dictionary
        """
        if profile_data:
            # Add timestamp
            profile_data['scraped_at'] = datetime.now().isoformat()
            self.profiles.append(profile_data)
            print(f"✓ Saved profile data ({len(self.profiles)} total)")
    
    def export_to_json(self, filename: Optional[str] = None) -> str:
        """
        Export profiles to JSON file.
        
        Args:
            filename: Custom filename (optional)
        
        Returns:
            Path to exported file
        """
        if filename is None:
            filename = f"cto_profiles_{self.session_id}.json"
        
        filepath = f"{config.DATA_DIR}/{filename}"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.profiles, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Exported {len(self.profiles)} profiles to {filepath}")
        return filepath
    
    def export_to_csv(self, filename: Optional[str] = None) -> str:
        """
        Export profiles to CSV file.
        
        Args:
            filename: Custom filename (optional)
        
        Returns:
            Path to exported file
        """
        if filename is None:
            filename = f"cto_profiles_{self.session_id}.csv"
        
        filepath = f"{config.DATA_DIR}/{filename}"
        
        # Flatten nested data for CSV
        flattened_profiles = []
        for profile in self.profiles:
            flat_profile = self._flatten_profile(profile)
            flattened_profiles.append(flat_profile)
        
        # Create DataFrame and export
        df = pd.DataFrame(flattened_profiles)
        df.to_csv(filepath, index=False, encoding='utf-8')
        
        print(f"✓ Exported {len(self.profiles)} profiles to {filepath}")
        return filepath
    
    def _flatten_profile(self, profile: Dict) -> Dict:
        """Flatten nested profile data for CSV export."""
        flat = {}
        
        for key, value in profile.items():
            if isinstance(value, list):
                # Convert lists to strings
                if len(value) > 0 and isinstance(value[0], dict):
                    # List of dicts (experience, education)
                    flat[key] = " | ".join([self._dict_to_string(item) for item in value])
                else:
                    # List of strings (skills)
                    flat[key] = ", ".join(value)
            elif isinstance(value, dict):
                # Nested dict - flatten with prefix
                for nested_key, nested_value in value.items():
                    flat[f"{key}_{nested_key}"] = nested_value
            else:
                flat[key] = value
        
        return flat
    
    def _dict_to_string(self, d: Dict) -> str:
        """Convert dictionary to string representation."""
        return "; ".join([f"{k}: {v}" for k, v in d.items()])
    
    def get_profiles(self) -> List[Dict]:
        """Get all stored profiles."""
        return self.profiles
    
    def get_count(self) -> int:
        """Get number of stored profiles."""
        return len(self.profiles)
    
    def clear(self) -> None:
        """Clear all stored profiles."""
        self.profiles = []
        print("✓ Storage cleared")
    
    def save_incremental(self) -> None:
        """Save current data incrementally (backup)."""
        if self.profiles:
            backup_filename = f"backup_{self.session_id}.json"
            self.export_to_json(backup_filename)
