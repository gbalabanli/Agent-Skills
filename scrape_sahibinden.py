#!/usr/bin/env python3
"""
Selenium scraper for sahibinden.com rental listings
Searches for rental houses in Istanbul Maltepe Altintepe
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import json
from datetime import datetime


def setup_driver():
    """Configure and return Chrome WebDriver with anti-detection measures"""
    chrome_options = Options()

    # Anti-detection settings
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--disable-features=IsolateOrigins,site-per-process")
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    # Uncomment below to run in headless mode (may trigger anti-bot measures)
    # chrome_options.add_argument('--headless')

    # Create driver
    driver = webdriver.Chrome(options=chrome_options)

    # Remove webdriver property to avoid detection
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )

    return driver


def scrape_sahibinden_rentals(
    driver, url="https://www.sahibinden.com/kiralik-daire/istanbul-maltepe-altintepe"
):
    """
    Scrape rental listings from sahibinden.com
    """
    listings = []

    try:
        print(f"Navigating to: {url}")
        driver.get(url)

        # Wait for page to load (check for search results container)
        wait = WebDriverWait(driver, 10)

        # Handle cookie consent if present
        try:
            cookie_button = wait.until(
                EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
            )
            cookie_button.click()
            print("[OK] Accepted cookies")
            time.sleep(1)
        except TimeoutException:
            print("No cookie banner found or already accepted")
        except Exception as e:
            print(f"Cookie handling error: {e}")

        # Wait for listings to load
        print("Waiting for listings to load...")
        time.sleep(3)

        # Try different selectors for listings
        selectors_to_try = [
            "#searchResultsTable tr.searchResultsItem",
            ".searchResultsItem",
            "[data-id]",
            ".classified-list-content",
            "tr.listing-item",
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
            print("Taking screenshot to debug...")
            driver.save_screenshot("sahibinden_debug.png")
            print("Screenshot saved as sahibinden_debug.png")

            # Try to get page source for analysis
            page_source = driver.page_source
            with open("sahibinden_page_source.html", "w", encoding="utf-8") as f:
                f.write(page_source)
            print("Page source saved as sahibinden_page_source.html")

            return []

        print(f"\nProcessing {len(listing_elements)} listings...")

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
                    ]
                    for title_sel in title_selectors:
                        try:
                            title_elem = element.find_element(
                                By.CSS_SELECTOR, title_sel
                            )
                            listing["title"] = (
                                title_elem.get_attribute("title") or title_elem.text
                            )
                            if listing["title"]:
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
                    ]
                    for price_sel in price_selectors:
                        try:
                            price_elem = element.find_element(
                                By.CSS_SELECTOR, price_sel
                            )
                            listing["price"] = price_elem.text.strip()
                            if listing["price"]:
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
                    ]
                    for loc_sel in location_selectors:
                        try:
                            loc_elem = element.find_element(By.CSS_SELECTOR, loc_sel)
                            listing["location"] = loc_elem.text.strip()
                            if listing["location"]:
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
                    ]
                    for room_sel in room_selectors:
                        try:
                            room_elem = element.find_element(By.CSS_SELECTOR, room_sel)
                            listing["rooms"] = room_elem.text.strip()
                            if listing["rooms"]:
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
                    ]
                    for sqm_sel in sqm_selectors:
                        try:
                            sqm_elem = element.find_element(By.CSS_SELECTOR, sqm_sel)
                            sqm_text = sqm_elem.text.strip()
                            if "m²" in sqm_text or sqm_text.replace(" ", "").isdigit():
                                listing["square_meters"] = sqm_text
                                break
                        except:
                            continue
                except:
                    listing["square_meters"] = "N/A"

                if listing.get("title") and listing["title"] != "N/A":
                    listings.append(listing)

            except Exception as e:
                print(f"Error processing listing {idx}: {e}")
                continue

        return listings

    except Exception as e:
        print(f"Error during scraping: {e}")
        import traceback

        traceback.print_exc()
        return []


def print_listings(listings):
    """Print listings in a formatted way"""
    if not listings:
        print("\n[ERROR] No listings found")
        return

    print(f"\n{'=' * 80}")
    print(f"Found {len(listings)} Rental Listings")
    print(f"{'=' * 80}\n")

    for idx, listing in enumerate(listings, 1):
        print(f"Listing #{idx}")
        print(f"  Title: {listing.get('title', 'N/A')}")
        print(f"  Price: {listing.get('price', 'N/A')}")
        print(f"  Location: {listing.get('location', 'N/A')}")
        print(f"  Rooms: {listing.get('rooms', 'N/A')}")
        print(f"  Size: {listing.get('square_meters', 'N/A')}")
        print(f"  URL: {listing.get('url', 'N/A')}")
        print(f"  ID: {listing.get('id', 'N/A')}")
        print("-" * 80)


def save_listings(listings, filename=None):
    """Save listings to JSON file"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sahibinden_listings_{timestamp}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(listings, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] Saved {len(listings)} listings to: {filename}")


def main():
    """Main function"""
    driver = None

    try:
        print("=" * 80)
        print("Sahibinden.com Rental Scraper")
        print("Searching: Istanbul Maltepe Altintepe")
        print("=" * 80)

        # Setup driver
        print("\nInitializing Chrome WebDriver...")
        driver = setup_driver()

        # Scrape listings
        listings = scrape_sahibinden_rentals(driver)

        # Display results
        print_listings(listings)

        # Save results
        if listings:
            save_listings(listings)

            # Also save as CSV for easy viewing
            import csv

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"sahibinden_listings_{timestamp}.csv"

            with open(csv_filename, "w", newline="", encoding="utf-8-sig") as f:
                if listings:
                    writer = csv.DictWriter(f, fieldnames=listings[0].keys())
                    writer.writeheader()
                    writer.writerows(listings)

            print(f"[OK] Also saved to CSV: {csv_filename}")

        # Keep browser open for a bit so user can see
        print("\nBrowser will remain open for 10 seconds...")
        time.sleep(10)

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback

        traceback.print_exc()

    finally:
        if driver:
            print("\nClosing browser...")
            driver.quit()


if __name__ == "__main__":
    main()
