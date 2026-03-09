#!/usr/bin/env python3
"""
Amazon Turkey iPhone Best Sellers Scraper
Uses the protected-site-scraper skill to find most sold iPhones
"""

import sys
import os

sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "protected-site-scraper"),
)

from protected_site_scraper import ProtectedSiteScraper, ListingExtractor
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from typing import List, Dict


class AmazonTRiPhoneScraper(ProtectedSiteScraper):
    """
    Specialized scraper for Amazon Turkey iPhone best sellers
    """

    BASE_URL = "https://www.amazon.com.tr/s"

    def search_iphones(
        self, sort_by: str = "exact-aware-popularity-rank"
    ) -> List[Dict]:
        """
        Search for iPhones and sort by best sellers

        Args:
            sort_by: Sort parameter (exact-aware-popularity-rank for best sellers)

        Returns:
            List of iPhone listings with details
        """
        # Build search URL
        url = f"{self.BASE_URL}?k=iPhone&s={sort_by}"

        print(f"[INFO] Searching iPhones on Amazon Turkey...")
        print(f"[INFO] URL: {url}")

        driver = self.setup_driver()
        all_iphones = []

        try:
            # Navigate to page
            driver.get(url)

            # Wait for page to load
            time.sleep(3)

            # Wait for results
            wait = WebDriverWait(driver, 10)
            try:
                wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "[data-component-type='s-search-result']")
                    )
                )
                print("[OK] Search results loaded")
            except:
                print("[WARN] Timeout waiting for results")
                return []

            # Find iPhone listings
            selectors = [
                "[data-component-type='s-search-result']",
                ".s-result-item",
                ".a-section.a-spacing-base",
            ]

            listings = self.safe_find_elements(driver, selectors)
            print(f"[OK] Found {len(listings)} iPhone listings")

            # Extract data from each listing
            for idx, listing in enumerate(listings[:10], 1):  # Top 10 best sellers
                try:
                    iphone_data = self.extract_iphone_data(listing, idx)
                    if iphone_data:
                        all_iphones.append(iphone_data)
                        print(
                            f"[OK] Extracted #{idx}: {iphone_data.get('title', 'N/A')[:60]}..."
                        )
                except Exception as e:
                    print(f"[WARN] Error extracting listing {idx}: {e}")

            return all_iphones

        except Exception as e:
            print(f"[ERROR] Scraping failed: {e}")
            import traceback

            traceback.print_exc()
            return []

        finally:
            driver.quit()

    def extract_iphone_data(self, element, rank: int) -> Dict:
        """
        Extract iPhone data from a listing element

        Args:
            element: WebElement representing an iPhone listing
            rank: Ranking position

        Returns:
            Dictionary with iPhone details
        """
        data = {
            "rank": rank,
            "title": "N/A",
            "price": "N/A",
            "rating": "N/A",
            "reviews": "N/A",
            "sales_info": "N/A",
            "url": "N/A",
        }

        try:
            # Extract title
            title_selectors = [
                "h2 a span",
                ".a-size-base-plus",
                ".a-size-medium",
                "h2 span",
            ]
            data["title"] = self.extract_with_fallback(element, title_selectors)

            # Extract price
            price_selectors = [
                ".a-price .a-offscreen",
                ".a-price-whole",
                ".a-price-range",
            ]
            data["price"] = self.extract_with_fallback(element, price_selectors)

            # Extract rating
            try:
                rating_elem = element.find_element(By.CSS_SELECTOR, ".a-icon-alt")
                rating_text = rating_elem.get_attribute("textContent")
                if rating_text:
                    # Extract rating like "4.5 out of 5 stars"
                    parts = rating_text.split()
                    if len(parts) >= 2:
                        data["rating"] = parts[0] + "/5"
            except:
                pass

            # Extract number of reviews
            try:
                reviews_elem = element.find_element(By.CSS_SELECTOR, ".a-size-base")
                reviews_text = reviews_elem.text
                if reviews_text and "değerlendirme" in reviews_text.lower():
                    data["reviews"] = reviews_text.split()[0]
            except:
                pass

            # Extract sales info (e.g., "100+ purchased last month")
            try:
                sales_selectors = [
                    ".a-size-base.a-color-secondary",
                    ".a-size-base-plus.a-color-secondary",
                ]
                for sel in sales_selectors:
                    try:
                        sales_elem = element.find_element(By.CSS_SELECTOR, sel)
                        sales_text = sales_elem.text
                        if sales_text and (
                            "satın alındı" in sales_text.lower()
                            or "purchased" in sales_text.lower()
                        ):
                            data["sales_info"] = sales_text
                            break
                    except:
                        continue
            except:
                pass

            # Extract URL
            try:
                link_elem = element.find_element(By.CSS_SELECTOR, "h2 a")
                href = link_elem.get_attribute("href")
                if href:
                    # Clean URL
                    if "/ref=" in href:
                        href = href.split("/ref=")[0]
                    data["url"] = href
            except:
                pass

            return data

        except Exception as e:
            print(f"[WARN] Error in extract_iphone_data: {e}")
            return data


def main():
    """Main function"""
    print("=" * 80)
    print("Amazon Turkey - Most Sold iPhones Finder")
    print("Using protected-site-scraper skill")
    print("=" * 80)

    scraper = AmazonTRiPhoneScraper()

    # Get best-selling iPhones
    iphones = scraper.search_iphones(sort_by="exact-aware-popularity-rank")

    if not iphones:
        print("\n[ERROR] No iPhone data found")
        return 1

    # Display results
    print("\n" + "=" * 80)
    print("TOP 10 BEST-SELLING IPHONES IN TURKEY")
    print("=" * 80 + "\n")

    for iphone in iphones:
        print(f"Rank #{iphone['rank']}")
        print(f"  Model: {iphone['title']}")
        print(f"  Price: {iphone['price']}")
        print(f"  Rating: {iphone['rating']}")
        print(f"  Reviews: {iphone['reviews']}")
        print(f"  Sales: {iphone['sales_info']}")
        print(f"  URL: {iphone['url']}")
        print("-" * 80)

    # Save results
    filename = "amazon_tr_iphone_bestsellers"
    saved_files = scraper.save_results(iphones, filename, formats=["json", "csv"])

    print("\n" + "=" * 80)
    print("Summary:")
    print(f"  Total iPhones found: {len(iphones)}")
    for fmt, filepath in saved_files.items():
        print(f"  Saved to: {filepath}")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    exit(main())
