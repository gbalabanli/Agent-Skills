"""
Protected Site Scraper Core Module

A robust scraper for sites protected by Cloudflare, DataDome, and other anti-bot systems.
Uses undetected-chromedriver to bypass detection.
"""

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException,
)
import time
import json
import csv
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
import sys
import io
import subprocess
import os


class ProtectedSiteScraper:
    """
    Base scraper class for protected websites.

    Handles:
    - Chrome driver setup with anti-detection
    - Cloudflare/anti-bot protection bypass
    - Safe text extraction with encoding handling
    - Data export to JSON/CSV
    """

    def __init__(self, chrome_version: Optional[int] = None):
        """
        Initialize scraper.

        Args:
            chrome_version: Specific Chrome major version (e.g., 120).
                          Auto-detected if None.
        """
        self.chrome_version = chrome_version
        self.driver = None

    def create_options(
        self,
        headless: bool = False,
        window_size: tuple = (1920, 1080),
        disable_images: bool = False,
    ) -> uc.ChromeOptions:
        """
        Create Chrome options with anti-detection settings.

        Args:
            headless: Run without visible window (not recommended for protected sites)
            window_size: Browser window size
            disable_images: Disable images for faster loading

        Returns:
            Configured ChromeOptions
        """
        options = uc.ChromeOptions()

        # Anti-detection settings
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-features=IsolateOrigins,site-per-process")

        # Window settings
        options.add_argument(f"--window-size={window_size[0]},{window_size[1]}")
        if not headless:
            options.add_argument("--start-maximized")

        # Disable notifications
        options.add_argument("--disable-notifications")

        # Disable images for faster loading (optional)
        if disable_images:
            prefs = {"profile.managed_default_content_settings.images": 2}
            options.add_experimental_option("prefs", prefs)

        return options

    def setup_driver(
        self,
        headless: bool = False,
        window_size: tuple = (1920, 1080),
        disable_images: bool = False,
        user_agent: Optional[str] = None,
    ) -> uc.Chrome:
        """
        Setup undetected Chrome driver.

        Args:
            headless: Run without visible window
            window_size: Browser window size
            disable_images: Disable images for faster loading
            user_agent: Custom user agent string

        Returns:
            Configured Chrome WebDriver instance
        """
        options = self.create_options(headless, window_size, disable_images)

        if user_agent:
            options.add_argument(f"--user-agent={user_agent}")

        print("[INFO] Starting undetected Chrome...")

        try:
            # Try with default settings first
            if self.chrome_version:
                driver = uc.Chrome(options=options, version_main=self.chrome_version)
            else:
                driver = uc.Chrome(options=options)

            # Give browser time to fully initialize
            time.sleep(3)

            # Verify driver is working
            _ = driver.current_url

            self.driver = driver
            print("[OK] Chrome driver initialized successfully")
            return driver

        except Exception as e:
            print(f"[WARN] Failed with default settings: {e}")
            print("[INFO] Trying to auto-detect Chrome version...")

            # Try to detect Chrome version
            try:
                version = self._detect_chrome_version()
                if version:
                    print(f"[INFO] Detected Chrome version: {version}")
                    options = self.create_options(headless, window_size, disable_images)
                    if user_agent:
                        options.add_argument(f"--user-agent={user_agent}")
                    driver = uc.Chrome(options=options, version_main=version)
                    time.sleep(3)
                    _ = driver.current_url
                    self.driver = driver
                    print("[OK] Chrome driver initialized successfully")
                    return driver
            except Exception as e2:
                print(f"[WARN] Could not detect version: {e2}")

            # Fallback versions to try
            fallback_versions = [120, 119, 118, 117, 116]
            for version in fallback_versions:
                try:
                    print(f"[INFO] Trying Chrome version {version}...")
                    options = self.create_options(headless, window_size, disable_images)
                    if user_agent:
                        options.add_argument(f"--user-agent={user_agent}")
                    driver = uc.Chrome(options=options, version_main=version)
                    time.sleep(3)
                    _ = driver.current_url
                    self.driver = driver
                    print("[OK] Chrome driver initialized successfully")
                    return driver
                except Exception as e3:
                    print(f"[WARN] Version {version} failed: {e3}")
                    continue

            raise Exception("Could not initialize Chrome driver")

    def _detect_chrome_version(self) -> Optional[int]:
        """Auto-detect Chrome version from registry (Windows) or command."""
        try:
            if sys.platform == "win32":
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
                for line in result.stdout.split("\n"):
                    if "version" in line.lower():
                        version = line.split()[-1]
                        return int(version.split(".")[0])
            else:
                # Linux/Mac
                result = subprocess.run(
                    ["google-chrome", "--version"], capture_output=True, text=True
                )
                version_str = result.stdout.strip()
                if version_str:
                    # Extract number from "Google Chrome 120.0.0.0"
                    import re

                    match = re.search(r"(\d+)", version_str)
                    if match:
                        return int(match.group(1))
        except:
            pass
        return None

    def wait_for_protection_to_clear(
        self,
        driver: uc.Chrome,
        timeout: int = 30,
        check_selectors: Optional[List[str]] = None,
    ) -> bool:
        """
        Wait for Cloudflare or other anti-bot protection to complete.

        Args:
            driver: Chrome WebDriver instance
            timeout: Maximum wait time in seconds
            check_selectors: Optional list of selectors to check for content

        Returns:
            True if protection cleared, False if timeout
        """
        print("[INFO] Waiting for anti-bot protection to clear...")
        start_time = time.time()

        # Default selectors to check for actual content
        if not check_selectors:
            check_selectors = [
                "#searchResultsTable",
                ".listings",
                ".content",
                "[data-id]",
                "main",
                "article",
            ]

        while time.time() - start_time < timeout:
            try:
                # Check if we're on a challenge page
                title = driver.title.lower()
                if "just a moment" in title or "cloudflare" in title:
                    time.sleep(2)
                    continue

                # Check for actual content
                for selector in check_selectors:
                    try:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements and any(e.is_displayed() for e in elements):
                            print("[OK] Protection cleared, content found!")
                            return True
                    except:
                        continue

                # Check if page has loaded useful content
                page_source = driver.page_source
                if len(page_source) > 1000 and "challenge" not in page_source.lower():
                    # Additional check - see if we have meaningful content
                    if any(
                        selector.replace(".", "").replace("#", "") in page_source
                        for selector in check_selectors
                    ):
                        print("[OK] Protection cleared!")
                        return True

            except Exception as e:
                print(f"[DEBUG] Check error: {e}")

            time.sleep(1)

        print(f"[WARN] Timeout waiting for protection to clear ({timeout}s)")
        return False

    def safe_find_elements(self, driver: uc.Chrome, selectors: List[str]) -> List:
        """
        Try multiple selectors and return elements from first successful one.

        Args:
            driver: Chrome WebDriver instance
            selectors: List of CSS selectors to try

        Returns:
            List of found elements (empty if none work)
        """
        for selector in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    return elements
            except:
                continue
        return []

    def extract_with_fallback(self, element, selectors: List[str]) -> str:
        """
        Extract text from element using multiple selector fallbacks.

        Args:
            element: WebElement to search within
            selectors: List of CSS selectors to try

        Returns:
            Extracted text or "N/A"
        """
        for selector in selectors:
            try:
                elem = element.find_element(By.CSS_SELECTOR, selector)
                text = elem.get_attribute("title") or elem.text
                if text and text.strip():
                    return text.strip()
            except:
                continue
        return "N/A"

    @staticmethod
    def safe_print(text: str):
        """
        Print text safely handling encoding issues (Turkish chars, etc.).

        Args:
            text: Text to print
        """
        # Force UTF-8 output
        if sys.stdout.encoding != "utf-8":
            sys.stdout = io.TextIOWrapper(
                sys.stdout.buffer, encoding="utf-8", errors="replace"
            )

        try:
            print(text)
        except UnicodeEncodeError:
            # Replace problematic Turkish characters
            text_str = str(text)
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

    def save_results(
        self,
        data: List[Dict],
        filename: Optional[str] = None,
        formats: List[str] = ["json", "csv"],
    ) -> Dict[str, str]:
        """
        Save scraped data to files.

        Args:
            data: List of dictionaries with scraped data
            filename: Base filename (timestamp used if None)
            formats: List of formats to save (json, csv)

        Returns:
            Dictionary mapping format to saved filepath
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"scraped_data_{timestamp}"

        saved_files = {}

        # Save JSON
        if "json" in formats:
            json_file = f"{filename}.json"
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            saved_files["json"] = json_file
            print(f"[OK] Saved JSON: {json_file}")

        # Save CSV
        if "csv" in formats and data:
            csv_file = f"{filename}.csv"
            with open(csv_file, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            saved_files["csv"] = csv_file
            print(f"[OK] Saved CSV: {csv_file}")

        return saved_files

    def quit(self):
        """Safely quit the driver."""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures driver quits."""
        self.quit()
        return False


class ListingExtractor:
    """
    Helper class for extracting listing data with configurable field selectors.
    """

    def __init__(self, field_config: Dict[str, List[str]]):
        """
        Initialize with field configuration.

        Args:
            field_config: Dictionary mapping field names to list of selectors
                         Example: {'title': ['.title', 'h2'], 'price': ['.price']}
        """
        self.field_config = field_config

    def extract(self, element) -> Dict[str, str]:
        """
        Extract all configured fields from element.

        Args:
            element: WebElement to extract from

        Returns:
            Dictionary with extracted field values
        """
        data = {}
        for field, selectors in self.field_config.items():
            for selector in selectors:
                try:
                    elem = element.find_element(By.CSS_SELECTOR, selector)
                    value = elem.get_attribute("title") or elem.text
                    if value and value.strip():
                        data[field] = value.strip()
                        break
                except:
                    continue
            if field not in data:
                data[field] = "N/A"
        return data


def retry_on_failure(max_retries: int = 3, delay: int = 5):
    """
    Decorator for retrying failed scrape operations.

    Args:
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (TimeoutException, WebDriverException) as e:
                    print(f"[WARN] Attempt {attempt + 1} failed: {e}")
                    if attempt < max_retries - 1:
                        print(f"[INFO] Retrying in {delay} seconds...")
                        time.sleep(delay)
                    else:
                        print("[ERROR] Max retries reached")
                        raise
            return None

        return wrapper

    return decorator


# Convenience function for quick scraping
def quick_scrape(
    url: str,
    listing_selector: str,
    field_selectors: Dict[str, List[str]],
    chrome_version: Optional[int] = None,
) -> List[Dict]:
    """
    Quick scrape function for simple use cases.

    Args:
        url: URL to scrape
        listing_selector: CSS selector for listing containers
        field_selectors: Dictionary mapping field names to selector lists
        chrome_version: Specific Chrome version if needed

    Returns:
        List of extracted data dictionaries
    """
    scraper = ProtectedSiteScraper(chrome_version=chrome_version)
    extractor = ListingExtractor(field_selectors)

    with scraper:
        driver = scraper.setup_driver()
        driver.get(url)

        if not scraper.wait_for_protection_to_clear(driver):
            print("[ERROR] Could not bypass protection")
            return []

        # Wait a bit for content to load
        time.sleep(2)

        # Find listings
        listings = driver.find_elements(By.CSS_SELECTOR, listing_selector)
        print(f"[INFO] Found {len(listings)} listings")

        # Extract data
        data = []
        for i, listing in enumerate(listings, 1):
            try:
                item = extractor.extract(listing)
                data.append(item)
                print(f"[OK] Extracted listing {i}")
            except Exception as e:
                print(f"[WARN] Failed to extract listing {i}: {e}")

        return data
