---
name: protected-site-scraper
description: Scrape websites protected by Cloudflare, anti-bot systems, and other WAF protections using undetected-chromedriver. Includes support for complex extraction, CAPTCHA handling, and data export. Works with sahibinden.com and similar protected real estate/classified sites.
---

# Protected Site Scraper

## Overview

This skill provides tools to scrape websites that use anti-bot protection (Cloudflare, DataDome, PerimeterX, etc.) using **undetected-chromedriver** - a specialized Selenium wrapper designed to bypass detection.

**Perfect for:**
- Real estate sites (sahibinden.com, emlakjet, etc.)
- Classified listings
- E-commerce with bot protection
- Any site showing "Just a moment..." or CAPTCHA challenges

## When to Use

Use this skill when:
1. Standard requests/httpx fail with 403 errors
2. The site shows Cloudflare challenge pages
3. Selenium without undetected-chromedriver gets blocked
4. You need to scrape JavaScript-heavy protected sites

## Quick Start

```bash
# Install dependencies
pip install undetected-chromedriver selenium

# Run the sahibinden example
python examples/sahibinden_rentals.py --location istanbul-maltepe-altintepe
```

## Usage Patterns

### Pattern 1: Simple Protected Site Scraper

```python
from protected_site_scraper import ProtectedSiteScraper

scraper = ProtectedSiteScraper()
driver = scraper.setup_driver()

# Navigate and scrape
driver.get("https://example.com/listings")
listings = scraper.extract_listings(driver)

scraper.save_results(listings, "output.json")
driver.quit()
```

### Pattern 2: Custom Extraction

```python
from protected_site_scraper import ProtectedSiteScraper
from selenium.webdriver.common.by import By

scraper = ProtectedSiteScraper()
driver = scraper.setup_driver()

driver.get("https://example.com")

# Wait for Cloudflare
scraper.wait_for_protection_to_clear(driver)

# Custom extraction
elements = driver.find_elements(By.CSS_SELECTOR, ".listing")
data = []
for elem in elements:
    data.append({
        'title': elem.find_element(By.CSS_SELECTOR, '.title').text,
        'price': elem.find_element(By.CSS_SELECTOR, '.price').text,
    })

scraper.save_results(data, "output.json")
driver.quit()
```

### Pattern 3: Sahibinden.com Specific

```python
from examples.sahibinden_rentals import SahibindenScraper

scraper = SahibindenScraper()
listings = scraper.scrape_rentals(
    city="istanbul",
    district="maltepe", 
    neighborhood="altintepe"
)

print(f"Found {len(listings)} listings")
scraper.save_to_csv(listings, "rentals.csv")
```

## Core Components

### 1. ProtectedSiteScraper (Base Class)

**Location:** `protected_site_scraper/core.py`

**Key Methods:**
- `setup_driver(headless=False)` - Initialize undetected Chrome
- `wait_for_protection_to_clear(driver, timeout=30)` - Wait for Cloudflare/anti-bot
- `safe_find_elements(driver, selectors)` - Try multiple selectors
- `extract_with_fallback(element, selectors)` - Extract text with fallback
- `save_results(data, filename)` - Save to JSON/CSV
- `safe_print(text)` - Handle Turkish/special characters in console

### 2. Site-Specific Scrapers

**Location:** `examples/`

- `sahibinden_rentals.py` - Complete working example for sahibinden.com
- `template_scraper.py` - Template for new sites

### 3. Prompts

**Location:** `prompts/`

- `find_rentals.md` - Prompt to find rentals on sahibinden
- `scrape_generic.md` - Generic scraping prompt template

## Configuration

### Environment Variables

```bash
# Optional: Set Chrome binary path if not default
CHROME_BINARY_PATH="C:\Program Files\Google\Chrome\Application\chrome.exe"

# Optional: Set specific Chrome version
CHROME_VERSION="120"
```

### Driver Options

```python
from protected_site_scraper import ProtectedSiteScraper

scraper = ProtectedSiteScraper()

# Custom options
driver = scraper.setup_driver(
    headless=False,  # Show browser window
    window_size=(1920, 1080),
    user_agent="Custom User Agent",
    disable_images=True,  # Faster loading
    proxy="http://proxy:8080"  # Use proxy
)
```

## Advanced Features

### Handling Pagination

```python
def scrape_all_pages(scraper, driver, base_url):
    all_listings = []
    page = 1
    
    while True:
        url = f"{base_url}?page={page}"
        driver.get(url)
        scraper.wait_for_protection_to_clear(driver)
        
        listings = scraper.extract_listings(driver)
        if not listings:
            break
            
        all_listings.extend(listings)
        page += 1
        
        # Check for next button
        try:
            next_btn = driver.find_element(By.CSS_SELECTOR, ".next")
            if not next_btn.is_enabled():
                break
        except:
            break
    
    return all_listings
```

### Custom Field Extraction

```python
def extract_custom_fields(element):
    """Define custom extraction logic"""
    fields = {}
    
    # Try multiple selectors for each field
    field_selectors = {
        'title': ['.title', 'h1', 'h2', '.listing-title'],
        'price': ['.price', '.cost', '[data-price]'],
        'location': ['.location', '.address', '.place'],
        'rooms': ['.rooms', '.oda', '[data-rooms]'],
        'area': ['.area', '.square-meter', '[data-area]'],
    }
    
    for field, selectors in field_selectors.items():
        fields[field] = scraper.extract_with_fallback(element, selectors)
    
    return fields
```

### Error Recovery

```python
from selenium.common.exceptions import TimeoutException, WebDriverException

def scrape_with_retry(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            driver.get(url)
            scraper.wait_for_protection_to_clear(driver, timeout=30)
            return scraper.extract_listings(driver)
        except TimeoutException:
            print(f"Attempt {attempt + 1} failed, retrying...")
            time.sleep(5)
        except WebDriverException as e:
            print(f"Browser error: {e}")
            # Restart driver
            driver.quit()
            driver = scraper.setup_driver()
    
    return []
```

## Anti-Detection Tips

1. **Don't use headless mode** - It triggers more detection
2. **Add realistic delays** - Use `time.sleep()` between actions
3. **Use realistic User-Agent** - The scraper handles this automatically
4. **Avoid rapid requests** - Add delays between page loads
5. **Rotate proxies** - For high-volume scraping
6. **Handle cookies** - Accept or manage cookies appropriately

## Troubleshooting

### "Session not created" Error

```python
# Chrome version mismatch - specify version
driver = uc.Chrome(options=options, version_main=120)
```

### Cloudflare Challenge Not Passing

```python
# Increase wait time
scraper.wait_for_protection_to_clear(driver, timeout=60)

# Or check for specific elements
WebDriverWait(driver, 60).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, ".content"))
)
```

### Elements Not Found

```python
# Try multiple selectors
selectors = [
    "#searchResultsTable",
    ".listings",
    "[data-listings]"
]

for selector in selectors:
    elements = driver.find_elements(By.CSS_SELECTOR, selector)
    if elements:
        break
```

## Examples

### Sahibinden.com - Rental Listings

```bash
python examples/sahibinden_rentals.py \
    --city istanbul \
    --district maltepe \
    --neighborhood altintepe \
    --output rentals.json
```

### Generic Site Template

```python
# examples/template_scraper.py
from protected_site_scraper import ProtectedSiteScraper

class MySiteScraper(ProtectedSiteScraper):
    def scrape(self, url):
        driver = self.setup_driver()
        driver.get(url)
        
        self.wait_for_protection_to_clear(driver)
        
        # Your extraction logic here
        data = self.extract_listings(driver)
        
        driver.quit()
        return data

if __name__ == "__main__":
    scraper = MySiteScraper()
    results = scraper.scrape("https://example.com/listings")
    scraper.save_results(results, "output.json")
```

## Best Practices

1. **Always quit driver** - Use try/finally or context managers
2. **Save incrementally** - Don't lose data on crashes
3. **Respect robots.txt** - Check if scraping is allowed
4. **Rate limiting** - Don't overwhelm servers
5. **Legal compliance** - Check website terms of service

## Dependencies

```
undetected-chromedriver>=3.5.0
selenium>=4.15.0
webdriver-manager>=4.0.0
```

## License

MIT - Use responsibly and comply with website terms of service.
