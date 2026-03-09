# Generic Protected Site Scraper Prompt

Use this template for scraping any site protected by Cloudflare or anti-bot systems.

## Template

```
I need to scrape data from a protected website: {site_url}

Site Details:
- URL: {url}
- Protection Type: {cloudflare/datadome/perimeterx/other}
- Content Type: {listings/products/articles}

Extraction Requirements:
- Listing Container Selector: {selector}
- Fields to Extract:
  - {field1}: {selectors}
  - {field2}: {selectors}
  - ...

Output:
- Format: {json/csv/both}
- Filename: {name}

Additional Options:
- Headless Mode: {yes/no}
- Max Pages: {number}
- Delay Between Requests: {seconds}
```

## Usage Example

User: "Scrape product listings from example-store.com"

Prompt to generate:
```
I need to scrape product listings from example-store.com.

Site Details:
- URL: https://example-store.com/products
- Protection Type: Cloudflare
- Content Type: product listings

Extraction Requirements:
- Listing Container Selector: .product-card
- Fields to Extract:
  - name: ['.product-title', 'h2', 'h3']
  - price: ['.price', '.cost', '[data-price]']
  - image: ['.product-image img']
  - link: ['a.product-link']

Output:
- Format: both
- Filename: example_store_products

Additional Options:
- Headless Mode: no
- Max Pages: 5
- Delay Between Requests: 2
```

## Implementation Pattern

```python
from protected_site_scraper import ProtectedSiteScraper, ListingExtractor, quick_scrape

# Option 1: Quick scrape (simple cases)
data = quick_scrape(
    url="https://example.com/listings",
    listing_selector=".listing-item",
    field_selectors={
        'title': ['.title', 'h2'],
        'price': ['.price'],
        'location': ['.location']
    }
)

# Option 2: Full control (complex cases)
scraper = ProtectedSiteScraper()
with scraper:
    driver = scraper.setup_driver()
    driver.get("https://example.com/listings")
    
    if scraper.wait_for_protection_to_clear(driver):
        listings = driver.find_elements(By.CSS_SELECTOR, ".listing-item")
        
        extractor = ListingExtractor({
            'title': ['.title'],
            'price': ['.price']
        })
        
        data = []
        for listing in listings:
            data.append(extractor.extract(listing))
    
    scraper.save_results(data, "output")

# Option 3: Custom scraper class
class MySiteScraper(ProtectedSiteScraper):
    def scrape(self, url):
        driver = self.setup_driver()
        driver.get(url)
        
        if self.wait_for_protection_to_clear(driver):
            # Custom extraction logic
            listings = driver.find_elements(By.CSS_SELECTOR, ".item")
            data = []
            for item in listings:
                data.append({
                    'title': self.extract_with_fallback(item, ['.title']),
                    'price': self.extract_with_fallback(item, ['.price'])
                })
            return data
        return []

scraper = MySiteScraper()
results = scraper.scrape("https://example.com")
scraper.save_results(results, "output")
```

## Field Selector Tips

1. **Always provide multiple selectors** - Sites change, have fallbacks
2. **Use attribute selectors** - `[data-price]` is more stable than `.price`
3. **Check parent containers** - Sometimes data is in parent, not child
4. **Include ID selectors** - `#searchResultsTable` is very specific

## Common Patterns

### Pagination
```python
def scrape_all_pages(scraper, base_url, max_pages=5):
    all_data = []
    for page in range(1, max_pages + 1):
        url = f"{base_url}?page={page}"
        data = scraper.scrape(url)
        if not data:
            break
        all_data.extend(data)
        time.sleep(2)  # Be nice to the server
    return all_data
```

### Detail Pages
```python
def scrape_with_details(scraper, driver, listing_url):
    driver.get(listing_url)
    scraper.wait_for_protection_to_clear(driver)
    
    # Get basic info from list
    basic = {
        'title': driver.find_element(By.CSS_SELECTOR, '.title').text,
        'price': driver.find_element(By.CSS_SELECTOR, '.price').text
    }
    
    # Click for more details
    detail_link = driver.find_element(By.CSS_SELECTOR, '.detail-link')
    detail_link.click()
    time.sleep(2)
    
    # Get detailed info
    details = {
        'description': driver.find_element(By.CSS_SELECTOR, '.description').text,
        'features': [f.text for f in driver.find_elements(By.CSS_SELECTOR, '.feature')]
    }
    
    return {**basic, **details}
```

### Handling Infinite Scroll
```python
def scroll_to_load_all(driver, scroll_pause=2):
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        # Scroll down
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause)
        
        # Calculate new scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        
        if new_height == last_height:
            break
        last_height = new_height
```
