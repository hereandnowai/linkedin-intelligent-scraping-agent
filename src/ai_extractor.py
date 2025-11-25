"""AI-powered data extraction and normalization."""
from typing import Dict, Optional, List
import json
import config


class AIExtractor:
    """Uses AI to extract and normalize profile data."""
    
    def __init__(self):
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize OpenAI client if API key is available."""
        if config.OPENAI_API_KEY:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=config.OPENAI_API_KEY)
                print("✓ AI extraction enabled (OpenAI)")
            except ImportError:
                print("⚠ OpenAI package not installed. AI extraction disabled.")
                self.client = None
        else:
            print("ℹ No OpenAI API key found. AI extraction disabled.")
            self.client = None
    
    def enhance_profile_data(self, raw_data: Dict) -> Dict:
        """
        Enhance and normalize profile data using AI.
        
        Args:
            raw_data: Raw scraped profile data
        
        Returns:
            Enhanced and normalized profile data
        """
        if not self.client:
            # Return raw data if AI is not available
            return self._basic_enhancement(raw_data)
        
        try:
            # Create prompt for AI
            prompt = self._create_enhancement_prompt(raw_data)
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a data extraction assistant. Extract and normalize LinkedIn profile information into a structured format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            # Parse AI response
            enhanced_data = json.loads(response.choices[0].message.content)
            
            # Merge with original data
            return {**raw_data, **enhanced_data}
            
        except Exception as e:
            print(f"⚠ AI enhancement failed: {str(e)}")
            return self._basic_enhancement(raw_data)
    
    def _create_enhancement_prompt(self, raw_data: Dict) -> str:
        """Create prompt for AI enhancement."""
        return f"""
Extract and normalize the following LinkedIn profile data:

Profile Data:
{json.dumps(raw_data, indent=2)}

Please provide the following in JSON format:
1. cleaned_name: Full name (cleaned)
2. job_title: Current job title
3. company_name: Current company name
4. years_of_experience: Estimated years of experience (integer)
5. key_skills: Top 5 relevant technical skills (list)
6. education_summary: Highest degree and institution
7. is_cto: Boolean indicating if this person is actually a CTO or similar C-level technology role
8. summary: Brief 2-sentence professional summary

Return only valid JSON.
"""
    
    def _basic_enhancement(self, raw_data: Dict) -> Dict:
        """Basic enhancement without AI."""
        enhanced = raw_data.copy()
        
        # Clean and normalize data
        enhanced['cleaned_name'] = raw_data.get('name', 'N/A').strip()
        enhanced['job_title'] = raw_data.get('current_position', 'N/A').strip()
        enhanced['company_name'] = raw_data.get('current_company', 'N/A').strip()
        
        # Estimate if CTO based on headline/title
        headline = raw_data.get('headline', '').lower()
        position = raw_data.get('current_position', '').lower()
        enhanced['is_cto'] = any(term in headline or term in position 
                                 for term in ['cto', 'chief technology', 'vp technology', 'vp engineering'])
        
        # Extract top skills
        skills = raw_data.get('skills', [])
        enhanced['key_skills'] = skills[:5] if skills else []
        
        # Education summary
        education = raw_data.get('education', [])
        if education and len(education) > 0:
            enhanced['education_summary'] = education[0].get('school', 'N/A')
        else:
            enhanced['education_summary'] = 'N/A'
        
        return enhanced
    
    def validate_cto_profile(self, profile_data: Dict) -> bool:
        """
        Validate if a profile is actually a CTO.
        
        Args:
            profile_data: Profile data to validate
        
        Returns:
            True if profile appears to be a CTO, False otherwise
        """
        if 'is_cto' in profile_data:
            return profile_data['is_cto']
        
        # Fallback validation
        headline = profile_data.get('headline', '').lower()
        position = profile_data.get('current_position', '').lower()
        
        cto_keywords = [
            'cto', 'chief technology officer', 'chief technical officer',
            'vp technology', 'vp of technology', 'vp engineering',
            'vp of engineering', 'head of technology', 'head of engineering'
        ]
        
        return any(keyword in headline or keyword in position for keyword in cto_keywords)
