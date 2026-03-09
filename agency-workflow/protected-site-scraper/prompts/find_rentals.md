# Find Rentals on Sahibinden.com

Use this prompt to search for rental properties on sahibinden.com using the protected-site-scraper skill.

## Usage

When the user asks to find rentals on sahibinden.com, use this prompt template:

```
I need to find rental properties on sahibinden.com.

Location details:
- City: {city}
- District: {district}  
- Neighborhood: {neighborhood}

Requirements:
1. Use the protected-site-scraper skill
2. Scrape rental listings (kiralik-daire)
3. Save results to both JSON and CSV
4. Handle Turkish characters properly
5. Show summary of findings

Execute the sahibinden_rentals.py example with the specified location.
```

## Examples

### Example 1: Basic Search
User: "Find me rental houses in Istanbul Maltepe Altintepe"

Action: Run sahibinden_rentals.py with:
- city: istanbul
- district: maltepe
- neighborhood: altintepe

### Example 2: District Only
User: "Show me rentals in Ankara Çankaya"

Action: Run sahibinden_rentals.py with:
- city: ankara
- district: çankaya
- neighborhood: (omit)

### Example 3: City Wide
User: "Find apartments for rent in Izmir"

Action: Run sahibinden_rentals.py with:
- city: izmir
- district: (omit)
- neighborhood: (omit)

## Implementation

```python
# Use the scraper
from examples.sahibinden_rentals import SahibindenScraper

scraper = SahibindenScraper()
listings = scraper.scrape_rentals(
    city="istanbul",
    district="maltepe",
    neighborhood="altintepe"
)

# Display results
for listing in listings[:5]:  # Show first 5
    print(f"{listing['title'][:60]}... - {listing['price']}")

# Save
scraper.save_results(listings, "istanbul_maltepe_rentals")
```

## Expected Output

The scraper will:
1. Launch undetected Chrome
2. Navigate to sahibinden.com
3. Bypass Cloudflare protection
4. Extract 20-50 rental listings
5. Save to JSON and CSV files
6. Display summary in console

## Troubleshooting

If no listings found:
- Check if the location names are spelled correctly
- Try with/without Turkish characters (ı, ş, ğ, ü, ö, ç)
- The scraper auto-converts Turkish chars to ASCII for URLs

If Cloudflare blocks:
- Increase wait timeout in the script
- Try running without headless mode
- Check Chrome version compatibility
