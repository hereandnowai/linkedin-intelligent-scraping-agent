# Quick Start Guide

## Installation

1. **Create virtual environment**

   ```bash
   python3 -m venv venv
   ```

2. **Activate virtual environment**

   ```bash
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright browsers**
   ```bash
   playwright install chromium
   ```

## Configuration (Optional)

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
LINKEDIN_EMAIL=your-email@example.com
LINKEDIN_PASSWORD=your-password
OPENAI_API_KEY=sk-your-api-key-here  # Optional but recommended
```

## Usage

### Basic Usage

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Scrape 10 CTO profiles (default)
python main.py
```

### Common Commands

```bash
# Scrape 20 profiles
python main.py --max-profiles 20

# Use custom keywords
python main.py --keywords "CTO" "VP Engineering" "Chief Architect"

# Scrape specific URLs
python main.py --urls "https://linkedin.com/in/profile1" "https://linkedin.com/in/profile2"

# Export only to JSON
python main.py --format json

# Skip CTO validation
python main.py --no-validate --max-profiles 15
```

## Output

Data will be saved to the `data/` directory:

- `cto_profiles_YYYYMMDD_HHMMSS.json`
- `cto_profiles_YYYYMMDD_HHMMSS.csv`

## ⚠️ Important

- This tool violates LinkedIn's Terms of Service
- Use at your own risk
- Start with small numbers (5-10 profiles)
- Increase delays if you get warnings
- For educational purposes only

## Troubleshooting

**Login fails?**

- Check your credentials
- Complete verification/CAPTCHA manually in browser window
- Delete `cookies/linkedin_session.json` and try again

**No profiles found?**

- Try different keywords
- Verify your LinkedIn account has search access
- Check you're logged in successfully

**Getting blocked?**

- Reduce `MAX_PROFILES_PER_SESSION` in config
- Increase delays between actions
- Wait several hours before next session

## Help

For more information:

```bash
python main.py --help
```

See `README.md` for detailed documentation.
