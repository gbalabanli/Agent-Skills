#!/usr/bin/env python3
"""
Enhanced Selenium scraper for sahibinden.com using undetected-chromedriver
Searches for rental houses in Istanbul Maltepe Altintepe
"""

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import json
from datetime import datetime


def create_options():
    """Create Chrome options"""
    options = uc.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    return options


def setup_driver():
    """Configure and return undetected Chrome WebDriver"""
    print("[INFO] Starting undetected Chrome...")

    # Try with default settings first
    try:
        options = create_options()
        driver = uc.Chrome(options=options)
        return driver
    except Exception as e:
        print(f"[WARN] Failed with default settings: {e}")

    # Try to get Chrome version and use it
    print("[INFO] Trying with specific Chrome version...")
    import subprocess

    try:
        result = subprocess.run(
            [
                "reg",
                "query",
                r"HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon",
                "/v",
                "version",
            ],
            capture_output=True,
            text=True,
        )
        version_line = [
            line for line in result.stdout.split("\n") if "version" in line.lower()
        ]
        if version_line:
            version = version_line[0].split()[-1]
            major_version = int(version.split(".")[0])
            print(f"[INFO] Detected Chrome version: {version} (major: {major_version})")
            options = create_options()
            driver = uc.Chrome(options=options, version_main=major_version)
            return driver
    except Exception as e:
        print(f"[WARN] Could not detect version: {e}")

    # Fallback to hardcoded version
    print("[INFO] Using fallback version 145...")
    options = create_options()
    driver = uc.Chrome(options=options, version_main=145)
    return driver


def wait_for_cloudflare(driver, timeout=30):
    """Wait for Cloudflare challenge to complete"""
    print("[INFO] Waiting for Cloudflare verification...")
    start_time = time.time()

    while time.time() - start_time < timeout:
        current_url = driver.current_url
        page_title = driver.title

        # Check if we're past the challenge page
        if (
            "cloudflare" not in page_title.lower()
            and "just a moment" not in page_title.lower()
        ):
            if "sahibinden.com" in current_url and "kiralik" in current_url:
                print("[OK] Cloudflare verification passed!")
                return True

        # Check for challenge completion indicators
        try:
            # Look for the actual listing content
            if (
                driver.find_elements(By.CSS_SELECTOR, "#searchResultsTable")
                or driver.find_elements(By.CSS_SELECTOR, ".searchResultsItem")
                or driver.find_elements(By.CSS_SELECTOR, "[data-id]")
            ):
                print("[OK] Listings found - verification complete!")
                return True
        except:
            pass

        time.sleep(2)

    print("[WARN] Timeout waiting for Cloudflare")
    return False


def scrape_sahibinden_rentals(
    driver, url="https://www.sahibinden.com/kiralik-daire/istanbul-maltepe-altintepe"
):
    """Scrape rental listings from sahibinden.com"""
    listings = []

    try:
        print(f"[INFO] Navigating to: {url}")
        driver.get(url)

        # Wait for Cloudflare verification
        if not wait_for_cloudflare(driver, timeout=30):
            print("[ERROR] Could not bypass Cloudflare protection")
            print("[INFO] Taking screenshot...")
            driver.save_screenshot("sahibinden_cloudflare.png")
            return []

        # Additional wait for listings to load
        print("[INFO] Waiting for listings to load...")
        time.sleep(3)

        # Wait for the search results table
        wait = WebDriverWait(driver, 15)
        try:
            wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#searchResultsTable"))
            )
            print("[OK] Search results table found")
        except TimeoutException:
            print("[WARN] Could not find search results table")

        # Try different selectors for listings
        selectors_to_try = [
            "#searchResultsTable tr.searchResultsItem",
            ".searchResultsItem",
            "[data-id]",
            ".classified-list-content",
            "tr.listing-item",
            ".listing-item",
        ]

        listing_elements = []
        for selector in selectors_to_try:
            try:
                listing_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if listing_elements:
                    print(
                        f"[OK] Found {len(listing_elements)} listings using selector: {selector}"
                    )
                    break
            except Exception as e:
                continue

        if not listing_elements:
            print("[WARN] Could not find listings with standard selectors")
            print("[INFO] Taking screenshot and saving page source for debugging...")
            driver.save_screenshot("sahibinden_debug.png")

            page_source = driver.page_source
            with open("sahibinden_page_debug.html", "w", encoding="utf-8") as f:
                f.write(page_source)
            print("[INFO] Debug files saved")

            return []

        print(f"\n[INFO] Processing {len(listing_elements)} listings...")

        for idx, element in enumerate(listing_elements, 1):
            try:
                listing = {}

                # Extract listing ID
                try:
                    listing_id = element.get_attribute(
                        "data-id"
                    ) or element.get_attribute("id")
                    listing["id"] = listing_id
                except:
                    listing["id"] = f"item_{idx}"

                # Extract title
                try:
                    title_selectors = [
                        "td a.classifiedTitle",
                        ".classifiedTitle",
                        "h3 a",
                        ".title",
                        "a[title]",
                        ".listing-title",
                    ]
                    for title_sel in title_selectors:
                        try:
                            title_elem = element.find_element(
                                By.CSS_SELECTOR, title_sel
                            )
                            listing["title"] = (
                                title_elem.get_attribute("title") or title_elem.text
                            )
                            if listing["title"] and listing["title"].strip():
                                break
                        except:
                            continue
                except:
                    listing["title"] = "N/A"

                # Extract price
                try:
                    price_selectors = [
                        ".searchResultsPriceValue",
                        ".price",
                        "td:nth-child(7) div",
                        "[class*='price']",
                        ".listing-price",
                    ]
                    for price_sel in price_selectors:
                        try:
                            price_elem = element.find_element(
                                By.CSS_SELECTOR, price_sel
                            )
                            listing["price"] = price_elem.text.strip()
                            if listing["price"] and listing["price"].strip():
                                break
                        except:
                            continue
                except:
                    listing["price"] = "N/A"

                # Extract location
                try:
                    location_selectors = [
                        ".searchResultsLocationValue",
                        ".location",
                        "td:nth-child(8) div",
                        "[class*='location']",
                        ".listing-location",
                    ]
                    for loc_sel in location_selectors:
                        try:
                            loc_elem = element.find_element(By.CSS_SELECTOR, loc_sel)
                            listing["location"] = loc_elem.text.strip()
                            if listing["location"] and listing["location"].strip():
                                break
                        except:
                            continue
                except:
                    listing["location"] = "N/A"

                # Extract link
                try:
                    link_elem = element.find_element(By.CSS_SELECTOR, "a")
                    href = link_elem.get_attribute("href")
                    if href and not href.startswith("http"):
                        href = "https://www.sahibinden.com" + href
                    listing["url"] = href
                except:
                    listing["url"] = "N/A"

                # Extract room count
                try:
                    room_selectors = [
                        ".searchResultsAttributeValue",
                        ".rooms",
                        "td:nth-child(4) div",
                        ".listing-rooms",
                    ]
                    for room_sel in room_selectors:
                        try:
                            room_elem = element.find_element(By.CSS_SELECTOR, room_sel)
                            listing["rooms"] = room_elem.text.strip()
                            if listing["rooms"] and listing["rooms"].strip():
                                break
                        except:
                            continue
                except:
                    listing["rooms"] = "N/A"

                # Extract square meters
                try:
                    sqm_selectors = [
                        "td:nth-child(5) div",
                        ".square-meter",
                        "[class*='square']",
                        ".listing-size",
                    ]
                    for sqm_sel in sqm_selectors:
                        try:
                            sqm_elem = element.find_element(By.CSS_SELECTOR, sqm_sel)
                            sqm_text = sqm_elem.text.strip()
                            if sqm_text and (
                                "m" in sqm_text
                                or sqm_text.replace(" ", "").replace(".", "").isdigit()
                            ):
                                listing["square_meters"] = sqm_text
                                break
                        except:
                            continue
                except:
                    listing["square_meters"] = "N/A"

                # Only add if we have at least a title
                if (
                    listing.get("title")
                    and listing["title"] != "N/A"
                    and listing["title"].strip()
                ):
                    listings.append(listing)
                    safe_print(
                        f"[OK] Extracted listing {idx}: {listing['title'][:50]}..."
                    )

            except Exception as e:
                print(f"[WARN] Error processing listing {idx}: {e}")
                continue

        return listings

    except Exception as e:
        print(f"[ERROR] Error during scraping: {e}")
        import traceback

        traceback.print_exc()
        return []


def safe_print(text):
    """Print text safely handling encoding issues"""
    import sys
    import io

    # Force UTF-8 output
    if sys.stdout.encoding != "utf-8":
        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer, encoding="utf-8", errors="replace"
        )

    try:
        print(text)
    except UnicodeEncodeError:
        # Replace problematic characters
        text_str = str(text)
        # Replace Turkish characters with ASCII equivalents
        turkish_map = {
            "ı": "i",
            "İ": "I",
            "ş": "s",
            "Ş": "S",
            "ğ": "g",
            "Ğ": "G",
            "ü": "u",
            "Ü": "U",
            "ö": "o",
            "Ö": "O",
            "ç": "c",
            "Ç": "C",
        }
        for turkish, ascii_char in turkish_map.items():
            text_str = text_str.replace(turkish, ascii_char)
        print(text_str)


def print_listings(listings):
    """Print listings in a formatted way"""
    if not listings:
        safe_print("\n[ERROR] No listings found")
        return

    safe_print(f"\n{'=' * 80}")
    safe_print(f"Found {len(listings)} Rental Listings")
    safe_print(f"{'=' * 80}\n")

    for idx, listing in enumerate(listings, 1):
        safe_print(f"Listing #{idx}")
        safe_print(f"  Title: {listing.get('title', 'N/A')}")
        safe_print(f"  Price: {listing.get('price', 'N/A')}")
        safe_print(f"  Location: {listing.get('location', 'N/A')}")
        safe_print(f"  Rooms: {listing.get('rooms', 'N/A')}")
        safe_print(f"  Size: {listing.get('square_meters', 'N/A')}")
        safe_print(f"  URL: {listing.get('url', 'N/A')}")
        safe_print(f"  ID: {listing.get('id', 'N/A')}")
        safe_print("-" * 80)


def save_listings(listings, filename=None):
    """Save listings to JSON file"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sahibinden_listings_{timestamp}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(listings, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] Saved {len(listings)} listings to: {filename}")
    return filename


def main():
    """Main function"""
    driver = None

    try:
        print("=" * 80)
        print("Sahibinden.com Rental Scraper (Enhanced)")
        print("Searching: Istanbul Maltepe Altintepe")
        print("=" * 80)

        # Setup driver
        print("\n[INFO] Initializing undetected Chrome WebDriver...")
        driver = setup_driver()

        # Scrape listings
        listings = scrape_sahibinden_rentals(driver)

        # Display results
        print_listings(listings)

        # Save results
        if listings:
            json_file = save_listings(listings)

            # Also save as CSV for easy viewing
            import csv

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"sahibinden_listings_{timestamp}.csv"

            with open(csv_filename, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=listings[0].keys())
                writer.writeheader()
                writer.writerows(listings)

            print(f"[OK] Also saved to CSV: {csv_filename}")

        # Keep browser open for a bit so user can see
        print("\n[INFO] Browser will remain open for 10 seconds...")
        print("[INFO] You can manually interact with the page")
        time.sleep(10)

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback

        traceback.print_exc()

    finally:
        if driver:
            print("\n[INFO] Closing browser...")
            driver.quit()


if __name__ == "__main__":
    main()
