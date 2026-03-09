"""
Sahibinden.com Rental Listings Scraper
Complete working example using the protected-site-scraper skill.

This scraper extracts rental listings from sahibinden.com, bypassing Cloudflare protection.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from protected_site_scraper import ProtectedSiteScraper, ListingExtractor
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import argparse
from typing import List, Dict, Optional


class SahibindenScraper(ProtectedSiteScraper):
    """
    Specialized scraper for sahibinden.com rental listings.
    """

    BASE_URL = "https://www.sahibinden.com/kiralik-daire"

    # Field selectors for sahibinden listings
    FIELD_SELECTORS = {
        "title": [
            "td a.classifiedTitle",
            ".classifiedTitle",
            "h3 a",
            ".title",
            "a[title]",
        ],
        "price": [".searchResultsPriceValue", ".price", "td:nth-child(7) div"],
        "location": [".searchResultsLocationValue", ".location", "td:nth-child(8) div"],
        "rooms": [".searchResultsAttributeValue", ".rooms", "td:nth-child(4) div"],
        "square_meters": ["td:nth-child(5) div", ".square-meter", ".area"],
    }

    LISTING_SELECTORS = [
        "#searchResultsTable tr.searchResultsItem",
        ".searchResultsItem",
        "[data-id]",
    ]

    def build_url(
        self,
        city: Optional[str] = None,
        district: Optional[str] = None,
        neighborhood: Optional[str] = None,
    ) -> str:
        """
        Build sahibinden URL for specific location.

        Args:
            city: City name (e.g., "istanbul")
            district: District name (e.g., "maltepe")
            neighborhood: Neighborhood name (e.g., "altintepe")

        Returns:
            Complete URL
        """
        parts = [self.BASE_URL]

        if city:
            city_slug = (
                city.lower()
                .replace(" ", "-")
                .replace("ı", "i")
                .replace("ş", "s")
                .replace("ğ", "g")
                .replace("ü", "u")
                .replace("ö", "o")
                .replace("ç", "c")
            )
            parts.append(city_slug)

            if district:
                district_slug = (
                    district.lower()
                    .replace(" ", "-")
                    .replace("ı", "i")
                    .replace("ş", "s")
                    .replace("ğ", "g")
                    .replace("ü", "u")
                    .replace("ö", "o")
                    .replace("ç", "c")
                )
                parts.append(district_slug)

                if neighborhood:
                    neighborhood_slug = (
                        neighborhood.lower()
                        .replace(" ", "-")
                        .replace("ı", "i")
                        .replace("ş", "s")
                        .replace("ğ", "g")
                        .replace("ü", "u")
                        .replace("ö", "o")
                        .replace("ç", "c")
                    )
                    parts.append(neighborhood_slug)

        return "/".join(parts)

    def scrape_rentals(
        self,
        city: Optional[str] = None,
        district: Optional[str] = None,
        neighborhood: Optional[str] = None,
        url: Optional[str] = None,
        max_pages: int = 1,
    ) -> List[Dict]:
        """
        Scrape rental listings from sahibinden.com.

        Args:
            city: City name (e.g., "istanbul")
            district: District name (e.g., "maltepe")
            neighborhood: Neighborhood name (e.g., "altintepe")
            url: Direct URL (overrides city/district/neighborhood)
            max_pages: Maximum pages to scrape

        Returns:
            List of rental listings
        """
        # Build URL if not provided
        if not url:
            url = self.build_url(city, district, neighborhood)

        self.safe_print(f"[INFO] Scraping: {url}")

        # Setup driver
        driver = self.setup_driver()
        all_listings = []

        try:
            # Navigate to page
            driver.get(url)

            # Wait for Cloudflare protection
            if not self.wait_for_protection_to_clear(driver, timeout=30):
                self.safe_print("[ERROR] Could not bypass protection")
                return []

            # Wait for listings to load
            time.sleep(2)

            # Find listings using multiple selectors
            listing_elements = self.safe_find_elements(driver, self.LISTING_SELECTORS)

            if not listing_elements:
                self.safe_print("[WARN] No listings found")
                # Save debug info
                driver.save_screenshot("sahibinden_debug.png")
                with open("sahibinden_debug.html", "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                return []

            self.safe_print(f"[OK] Found {len(listing_elements)} listings")

            # Extract data from each listing
            extractor = ListingExtractor(self.FIELD_SELECTORS)

            for idx, element in enumerate(listing_elements, 1):
                try:
                    # Extract basic fields
                    listing = extractor.extract(element)

                    # Extract ID
                    try:
                        listing_id = element.get_attribute(
                            "data-id"
                        ) or element.get_attribute("id")
                        listing["id"] = listing_id
                    except:
                        listing["id"] = f"item_{idx}"

                    # Extract URL
                    try:
                        link_elem = element.find_element(By.CSS_SELECTOR, "a")
                        href = link_elem.get_attribute("href")
                        if href and not href.startswith("http"):
                            href = "https://www.sahibinden.com" + href
                        listing["url"] = href
                    except:
                        listing["url"] = "N/A"

                    # Only add if we have a valid title
                    if listing.get("title") and listing["title"] != "N/A":
                        all_listings.append(listing)
                        self.safe_print(
                            f"[OK] Extracted {idx}: {listing['title'][:50]}..."
                        )

                except Exception as e:
                    self.safe_print(f"[WARN] Error on listing {idx}: {e}")
                    continue

            return all_listings

        except Exception as e:
            self.safe_print(f"[ERROR] Scraping failed: {e}")
            import traceback

            traceback.print_exc()
            return []

        finally:
            driver.quit()

    def save_to_csv(self, listings: List[Dict], filename: str):
        """Save listings to CSV file."""
        self.save_results(listings, filename, formats=["csv"])

    def save_to_json(self, listings: List[Dict], filename: str):
        """Save listings to JSON file."""
        self.save_results(listings, filename, formats=["json"])


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Scrape rental listings from sahibinden.com"
    )
    parser.add_argument("--city", default="istanbul", help="City name")
    parser.add_argument("--district", default="maltepe", help="District name")
    parser.add_argument("--neighborhood", default="altintepe", help="Neighborhood name")
    parser.add_argument("--url", help="Direct URL (overrides location args)")
    parser.add_argument(
        "--output", "-o", default="sahibinden_rentals", help="Output filename"
    )
    parser.add_argument(
        "--format",
        choices=["json", "csv", "both"],
        default="both",
        help="Output format",
    )
    parser.add_argument("--chrome-version", type=int, help="Chrome major version")

    args = parser.parse_args()

    # Create scraper
    scraper = SahibindenScraper(chrome_version=args.chrome_version)

    # Scrape listings
    listings = scraper.scrape_rentals(
        city=args.city,
        district=args.district,
        neighborhood=args.neighborhood,
        url=args.url,
    )

    if not listings:
        print("[ERROR] No listings found")
        return 1

    # Save results
    formats = []
    if args.format in ["json", "both"]:
        formats.append("json")
    if args.format in ["csv", "both"]:
        formats.append("csv")

    saved = scraper.save_results(listings, args.output, formats=formats)

    # Print summary
    print(f"\n{'=' * 80}")
    print(f"Scraping Complete!")
    print(f"{'=' * 80}")
    print(f"Total listings: {len(listings)}")
    for fmt, filepath in saved.items():
        print(f"Saved to: {filepath}")
    print(f"{'=' * 80}\n")

    return 0


if __name__ == "__main__":
    exit(main())
