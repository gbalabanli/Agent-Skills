"""
Template Scraper for Protected Sites

This is a template you can copy and customize for any protected website.
Just modify the URL, selectors, and field mappings for your target site.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from protected_site_scraper import ProtectedSiteScraper, ListingExtractor
from selenium.webdriver.common.by import By
import time
from typing import List, Dict


class TemplateScraper(ProtectedSiteScraper):
    """
    Template scraper - customize this for your target website.

    To use:
    1. Change the BASE_URL to your target site
    2. Update LISTING_SELECTORS to find listing containers
    3. Update FIELD_SELECTORS to extract data fields
    4. Customize extract_listing() for complex extractions
    """

    # ==========================================
    # CONFIGURE THESE FOR YOUR TARGET SITE
    # ==========================================

    BASE_URL = "https://example.com/listings"  # Change this

    # Try multiple selectors to find listing containers
    LISTING_SELECTORS = [
        ".listing-item",  # Primary selector
        ".product-card",  # Alternative 1
        "[data-listing]",  # Alternative 2
        ".item",  # Alternative 3
        ".searchResultsItem",  # Alternative 4
    ]

    # Field extraction with fallback selectors
    FIELD_SELECTORS = {
        "title": [
            ".title",  # Primary
            "h2",  # Alternative 1
            "h3",  # Alternative 2
            ".listing-title",  # Alternative 3
            "a[title]",  # Alternative 4
        ],
        "price": [".price", ".cost", "[data-price]", ".amount"],
        "description": [".description", ".summary", ".details", "p"],
        "location": [".location", ".address", ".place", ".area"],
        # Add more fields as needed
    }

    # ==========================================
    # CUSTOM EXTRACTION METHOD
    # ==========================================

    def extract_listing(self, element) -> Dict:
        """
        Extract data from a single listing element.

        Customize this method for complex extraction logic.
        The default implementation uses FIELD_SELECTORS.

        Args:
            element: WebElement representing a listing

        Returns:
            Dictionary with extracted data
        """
        data = {}

        # Use the field extractor for standard fields
        extractor = ListingExtractor(self.FIELD_SELECTORS)
        data.update(extractor.extract(element))

        # Add custom fields here if needed
        # Example: Extract ID from data attribute
        try:
            data["id"] = element.get_attribute("data-id")
        except:
            pass

        # Example: Extract URL
        try:
            link = element.find_element(By.CSS_SELECTOR, "a")
            href = link.get_attribute("href")
            if href and not href.startswith("http"):
                href = self.BASE_URL + href
            data["url"] = href
        except:
            pass

        # Example: Extract image URL
        try:
            img = element.find_element(By.CSS_SELECTOR, "img")
            data["image"] = img.get_attribute("src")
        except:
            pass

        return data

    # ==========================================
    # MAIN SCRAPING METHOD
    # ==========================================

    def scrape(self, url: str = None, max_pages: int = 1) -> List[Dict]:
        """
        Main scraping method.

        Args:
            url: URL to scrape (uses BASE_URL if None)
            max_pages: Maximum number of pages to scrape

        Returns:
            List of extracted listings
        """
        url = url or self.BASE_URL
        all_data = []

        self.safe_print(f"[INFO] Starting scrape of: {url}")

        # Setup driver
        driver = self.setup_driver()

        try:
            for page in range(1, max_pages + 1):
                # Build page URL
                page_url = url
                if page > 1:
                    # Adjust this based on site's pagination pattern
                    page_url = f"{url}?page={page}"

                self.safe_print(f"[INFO] Scraping page {page}: {page_url}")

                # Navigate to page
                driver.get(page_url)

                # Wait for protection to clear
                if not self.wait_for_protection_to_clear(driver, timeout=30):
                    self.safe_print("[WARN] Could not bypass protection on this page")
                    break

                # Wait for content to load
                time.sleep(2)

                # Find listings
                listings = self.safe_find_elements(driver, self.LISTING_SELECTORS)

                if not listings:
                    self.safe_print("[WARN] No listings found on this page")
                    # Save debug info
                    driver.save_screenshot("debug_page.png")
                    with open("debug_page.html", "w", encoding="utf-8") as f:
                        f.write(driver.page_source)
                    break

                self.safe_print(f"[OK] Found {len(listings)} listings on page {page}")

                # Extract data from each listing
                for i, listing_elem in enumerate(listings, 1):
                    try:
                        data = self.extract_listing(listing_elem)
                        if data.get("title") and data["title"] != "N/A":
                            all_data.append(data)
                            self.safe_print(
                                f"[OK] Extracted listing {i} on page {page}"
                            )
                    except Exception as e:
                        self.safe_print(f"[WARN] Error extracting listing {i}: {e}")

                # Check for next page button
                if page < max_pages:
                    try:
                        next_btn = driver.find_element(
                            By.CSS_SELECTOR, ".next, .pagination-next, [rel='next']"
                        )
                        if not next_btn.is_enabled():
                            self.safe_print("[INFO] Reached last page")
                            break
                    except:
                        self.safe_print("[INFO] No next page button found")
                        break

                # Delay between pages
                if page < max_pages:
                    time.sleep(3)

            return all_data

        except Exception as e:
            self.safe_print(f"[ERROR] Scraping failed: {e}")
            import traceback

            traceback.print_exc()
            return []

        finally:
            driver.quit()


# ==========================================
# USAGE EXAMPLE
# ==========================================


def main():
    """Example usage."""

    # Create scraper instance
    scraper = TemplateScraper()

    # Scrape the site
    results = scraper.scrape(
        url="https://example.com/listings",  # Change this
        max_pages=2,
    )

    if results:
        # Save results
        scraper.save_results(results, "scraped_data", formats=["json", "csv"])

        # Print summary
        print(f"\n{'=' * 60}")
        print(f"Scraping Complete!")
        print(f"Total items: {len(results)}")
        print(f"{'=' * 60}\n")

        # Print first 3 items
        print("Sample results:")
        for item in results[:3]:
            print(f"  - {item.get('title', 'N/A')[:50]}...")
    else:
        print("[ERROR] No data scraped")


if __name__ == "__main__":
    main()
