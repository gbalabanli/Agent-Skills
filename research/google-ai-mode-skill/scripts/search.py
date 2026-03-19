#!/usr/bin/env python3
"""
-------------------------------------------------------------------------------
Google AI Mode Search
-------------------------------------------------------------------------------
Searches Google's AI mode (udm=50) and extracts AI-generated overviews with
citations for use in Claude Code.

Features:
- Automatic captcha detection
- Graceful error handling
- Citation extraction with sources
- HTML to Markdown conversion

Usage:
  python scripts/run.py search.py --query "Your search query"
  python scripts/run.py search.py --query "..." --show-browser
"""

import sys
import os
import time
import json
import argparse
import re
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime

# Third-party imports
from patchright.sync_api import sync_playwright, Page
from bs4 import BeautifulSoup

# Local imports
from browser_utils import BrowserFactory
from config import USER_AGENT, PAGE_LOAD_TIMEOUT, AI_RESPONSE_TIMEOUT, RESULTS_DIR, BROWSER_PROFILE_DIR, LOGS_DIR
from logger import get_logger

try:
    from html_to_markdown import convert, ConversionOptions
except ImportError:
    # Fallback if html-to-markdown not available
    print("⚠️  Warning: html-to-markdown not found, trying markdownify...")
    try:
        from markdownify import markdownify as md
        def convert(html, options=None):
            return md(html)
        ConversionOptions = None
    except ImportError:
        print("⚠️  Warning: markdownify not found either, using html2text...")
        try:
            import html2text
            h = html2text.HTML2Text()
            h.body_width = 0
            def convert(html, options=None):
                return h.handle(html)
            ConversionOptions = None
        except ImportError:
            print("❌ Error: No HTML to Markdown converter found!")
            print("   Install one of: html-to-markdown, markdownify, or html2text")
            sys.exit(1)

# =============================================================================
# MULTI-LANGUAGE SELECTORS (DE/EN/NL support)
# =============================================================================

# Citation button selectors - ALL languages
CITATION_SELECTORS = [
    '[aria-label="View related links"]',           # English
    '[aria-label*="Related links"]',               # English partial
    '[aria-label="Zugehörige Links anzeigen"]',    # German
    '[aria-label*="Zugehörige Links"]',            # German partial
    '[aria-label*="Gerelateerde links"]',          # Dutch partial
    'button[aria-label*="links" i]',               # Generic case-insensitive
]

MAIN_CONTENT_SELECTORS = [
    '[data-container-id="main-col"]',
    '[role="main"]',
    'main',
    '#search',
    'body',
]

SIDEBAR_SELECTORS = [
    '[data-container-id="rhs-col"]',
    '[role="complementary"]',
    'aside',
]

# AI Completion Detection - Multi-language
AI_COMPLETION_BUTTON = '[aria-label*="feedback" i]'  # Language-independent
AI_COMPLETION_TIMEOUT = 15000  # 15 seconds (SERPO proven)
CAPTCHA_SOLVE_TIMEOUT = 180

# Text-based completion indicators (fallback)
AI_COMPLETION_TEXT_INDICATORS = [
    # English
    'AI-generated', 'AI Overview', 'Generative AI is experimental',
    # German
    'KI-Antworten', 'KI-generiert', 'Generative KI',
    # Dutch
    'AI-gegenereerd', 'AI-overzicht',
    # Spanish
    'Las respuestas de la IA', 'Resumen de IA', 'Información general de IA',
    # French
    'Réponses IA', "Aperçu de l'IA", "Vue d'ensemble de l'IA",
    # Italian
    'Risposte IA', "Panoramica IA", "Panoramica dell'IA",
]

# Disclaimer cutoff markers (remove everything after these)
CUTOFF_MARKERS = [
    # German
    'KI-Antworten können Fehler enthalten',
    'Öffentlicher Link wird erstellt',
    # English
    'AI-generated answers may contain mistakes',
    'AI can make mistakes',
    'Generative AI is experimental',
    # Dutch
    'AI-reacties kunnen fouten bevatten',
    # Spanish
    'Las respuestas de la IA pueden contener errores',
    'pueden contener errores',
    'Más información',
    # French
    "Les réponses de l'IA peuvent contenir des erreurs",
    'peuvent contenir des erreurs',
    'Plus d\'informations',
    # Italian
    "Le risposte dell'IA possono contenere errori",
    'possono contenere errori',
    'Ulteriori informazioni',
]

# AI Mode not available indicators (region/language restrictions)
AI_MODE_NOT_AVAILABLE = [
    # French
    "Le Mode IA n'est pas disponible dans votre pays ou votre langue",
    "Mode IA n'est pas disponible",
    "Découvrez le Mode IA",
    # English
    "AI Mode is not available in your country or language",
    "AI Mode isn't available",
    # German
    "Der KI-Modus ist in Ihrem Land oder Ihrer Sprache nicht verfügbar",
    "KI-Modus ist nicht verfügbar",
    # Spanish
    "El modo de IA no está disponible en tu país o idioma",
    # Italian
    "La modalità IA non è disponibile nel tuo Paese o nella tua lingua",
    # Dutch
    "AI-modus is niet beschikbaar in uw land of taal",
]

# =============================================================================
# JAVASCRIPT INJECTION CODE
# =============================================================================
DOM_INJECTION_SCRIPT = '''
async () => {
    // Helper: Prüft ob ein Element visuell für den User sichtbar ist
    function isVisible(el) {
        if (!el) return false;
        const style = window.getComputedStyle(el);
        const rect = el.getBoundingClientRect();
        return style.display !== 'none' &&
               style.visibility !== 'hidden' &&
               style.opacity !== '0' &&
               el.offsetParent !== null &&
               rect.width > 0 &&
               rect.height > 0;
    }

    function findVisibleContainer(selectors) {
        for (const selector of selectors) {
            const matches = Array.from(document.querySelectorAll(selector));
            for (const match of matches) {
                if (isVisible(match)) {
                    return match;
                }
            }
        }
        return null;
    }

    function findSidebar() {
        const selectors = %SIDEBAR_SELECTORS%;
        const sidebar = findVisibleContainer(selectors);
        if (sidebar) return sidebar;

        const allCandidates = Array.from(document.querySelectorAll('[aria-label], [role], aside, section, div'));
        return allCandidates.find((el) => {
            if (!isVisible(el)) return false;
            const text = (el.innerText || '').toLowerCase();
            return text.includes('sources') ||
                   text.includes('related links') ||
                   text.includes('quellen') ||
                   text.includes('links');
        }) || null;
    }

    const mainSelectors = %MAIN_CONTENT_SELECTORS%;
    let mainCol = null;

    for (const selector of mainSelectors) {
        const matches = Array.from(document.querySelectorAll(selector));
        for (const candidate of matches) {
            if (!isVisible(candidate)) continue;
            const hasCitationButtons = %CITATION_SELECTORS%.some((citationSelector) =>
                Array.from(candidate.querySelectorAll(citationSelector)).some(isVisible)
            );
            const text = (candidate.innerText || '').toLowerCase();
            const looksLikeAiBlock = text.includes('ai overview') ||
                                     text.includes('ai-generated') ||
                                     text.includes('generative ai') ||
                                     text.includes('ki-antworten') ||
                                     text.includes('ki-generiert');

            if (hasCitationButtons || looksLikeAiBlock) {
                mainCol = candidate;
                break;
            }
        }
        if (mainCol) break;
    }

    if (!mainCol) {
        mainCol = findVisibleContainer(mainSelectors);
    }
    if (!mainCol) return { error: 'main content container not found' };

    // SERPO OPTIMIZATION: Expand "Show more" buttons first
    try {
        const showMoreBtns = Array.from(mainCol.querySelectorAll('[aria-expanded="false"]'));
        for (const btn of showMoreBtns) {
            if (isVisible(btn) && (btn.innerText.includes('Show more') ||
                                   btn.innerText.includes('Mehr anzeigen') ||
                                   btn.innerText.includes('Meer weergeven'))) {
                btn.click();
                await new Promise(r => setTimeout(r, 200));
            }
        }
    } catch (e) {
        console.warn('Show more expansion failed', e);
    }

    // MULTI-LANGUAGE: Try citation selectors in order (injected from Python)
    const selectors = %CITATION_SELECTORS%;
    let buttons = [];

    for (const selector of selectors) {
        buttons = Array.from(mainCol.querySelectorAll(selector));
        if (buttons.filter(isVisible).length > 0) {
            console.log(`Found ${buttons.length} citation buttons with: ${selector}`);
            break;
        }
    }

    const allCitations = [];
    let markerIndex = 0;

    for (const btn of buttons) {
        // Ignoriere unsichtbare "Geister"-Buttons im DOM
        if (!isVisible(btn)) continue;

        // 1. Marker [CITE-N] visuell einfügen (SERPO: wrapped in <code> tag!)
        const markerId = markerIndex++;
        const marker = document.createElement('span');
        marker.className = 'citation-marker';
        marker.innerHTML = `<code>[CITE-${markerId}]</code>`;

        // Marker hinter dem Button platzieren
        if (btn.nextSibling) {
            btn.parentNode.insertBefore(marker, btn.nextSibling);
        } else {
            btn.parentNode.appendChild(marker);
        }

        // 2. Button klicken, um Quellen in der Seitenleiste zu laden
        try {
            btn.scrollIntoView({ behavior: 'instant', block: 'center' });

            // Zähle sichtbare Links VOR dem Klick
            const countVisibleLinks = () => {
                const rhsCol = findSidebar();
                if (!rhsCol) return 0;
                return Array.from(rhsCol.querySelectorAll('a[href]')).filter(isVisible).length;
            };
            const beforeCount = countVisibleLinks();

            btn.click();

            // Smart Wait: Warte kurz, ob sich Links ändern (max 300ms)
            const startTime = Date.now();
            while (Date.now() - startTime < 300) {
                await new Promise(r => setTimeout(r, 10));
                if (countVisibleLinks() !== beforeCount) break;
            }
            // Kurzer Puffer für Animationen
            await new Promise(r => setTimeout(r, 50));

        } catch (e) {
            console.warn('Click failed', e);
        }

        // 3. Quellen aus der Seitenleiste (rhs-col) extrahieren
        const sources = [];
        const seen = new Set();
        const rhsCol = findSidebar();

        if (rhsCol) {
            const links = Array.from(rhsCol.querySelectorAll('a[href]'));
            for (const link of links) {
                if (!isVisible(link)) continue;

                const url = link.href;
                const title = link.innerText.trim() || link.getAttribute('aria-label') || '';

                // Google-Interne Domains filtern
                const skipDomains = ['google.com', 'google.de', 'gstatic.com', 'support.google.com'];

                if (url && url.startsWith('http') && !skipDomains.some(d => url.includes(d)) && !seen.has(url)) {
                    seen.add(url);
                    sources.push({
                        title: title,
                        url: url,
                        source: new URL(url).hostname
                    });
                }
            }
        }

        allCitations.push({ marker_id: markerId, sources: sources });
    }

    // Rückgabe: Das modifizierte HTML (mit Markern) + die extrahierten Quellen
    return {
        html: mainCol.innerHTML,
        citations: allCitations
    };
}
'''

# =============================================================================
# CAPTCHA DETECTION (3-Layer Strategy)
# =============================================================================

def detect_captcha(page: Page) -> bool:
    """
    Erkennt ob Google ein Captcha zeigt (3-Layer Detection)

    Layer 1: URL contains /sorry/index
    Layer 2: Body text contains "unusual traffic"
    Layer 3: Page content is very short (< 600 chars)

    Returns True if ANY layer detects CAPTCHA
    """

    # LAYER 1: URL-Check (Most reliable!)
    # Google's CAPTCHA pages always redirect to /sorry/index
    try:
        current_url = page.url
        if '/sorry/index' in current_url or 'google.com/sorry' in current_url:
            print("    🔍 CAPTCHA detected (Layer 1: URL contains /sorry/index)")
            return True
    except:
        pass

    # LAYER 2: Text-Check
    # CAPTCHA pages contain "unusual traffic" text
    try:
        body = page.inner_text('body')
        body_lower = body.lower()

        unusual_traffic_indicators = [
            'unusual traffic',
            'ungewöhnlichen datenverkehr',
            'unsere systeme haben',
            'our systems have detected'
        ]

        for indicator in unusual_traffic_indicators:
            if indicator in body_lower:
                print(f"    🔍 CAPTCHA detected (Layer 2: Text contains '{indicator}')")
                return True
    except:
        pass

    # LAYER 3: Length-Check
    # CAPTCHA pages are very short (< 600 chars)
    # Real AI Overview pages are much longer (usually > 2000 chars)
    try:
        body = page.inner_text('body')
        body_length = len(body.strip())

        if body_length < 600:
            # Double-check with text to avoid false positives
            body_lower = body.lower()
            if 'captcha' in body_lower or 'unusual' in body_lower or 'über diese seite' in body_lower:
                print(f"    🔍 CAPTCHA detected (Layer 3: Page too short - {body_length} chars)")
                return True
    except:
        pass

    # LEGACY: Element-based detection (backup)
    # Less reliable but catches some edge cases
    captcha_selectors = [
        'div#recaptcha',
        'iframe[src*="recaptcha"]',
        '[id*="captcha"]',
    ]

    for selector in captcha_selectors:
        try:
            if page.query_selector(selector):
                print(f"    🔍 CAPTCHA detected (Legacy: Element {selector} found)")
                return True
        except:
            pass

    return False


def build_google_search_url(query: str, ai_mode: bool = True) -> str:
    """Build a Google AI Mode or classic web-search URL for the given query."""
    encoded_query = query.replace(' ', '+')
    if ai_mode:
        return f"https://www.google.com/search?udm=50&q={encoded_query}"
    return f"https://www.google.com/search?q={encoded_query}"

# =============================================================================
# MAIN SCRAPER CLASS
# =============================================================================

class GoogleAIScraper:
    def __init__(self, headless: bool = True, logger=None):
        self.headless = headless
        self.logger = logger if logger else get_logger(debug=False)
        self.pw = None
        self.ctx = None  # Persistent context (no separate browser object needed)
        self.page = None

    def start(self):
        """Startet den Browser mit PERSISTENT CONTEXT"""
        self.logger.debug(f"Starting browser with persistent context (headless={self.headless})...")
        self.logger.debug(f"Profile directory: {BROWSER_PROFILE_DIR}")
        self.pw = sync_playwright().start()
        factory = BrowserFactory()
        # Use persistent context - keeps cookies/session between runs!
        self.ctx = factory.launch_persistent_context(self.pw, headless=self.headless)
        self.logger.info("✅ Persistent context launched (cookies preserved!)")
        self.page = self.ctx.new_page()
        self.logger.debug("Browser page created")

    def stop(self):
        """Beendet den Browser"""
        self.logger.debug("Cleaning up browser resources...")
        try:
            if self.page:
                page = self.page
                self.page = None
                page.close()
                self.logger.debug("Page closed")
        except BaseException as e:
            self.logger.debug(f"Error closing page: {e}")
        try:
            if self.ctx:
                ctx = self.ctx
                self.ctx = None
                ctx.close()
                self.logger.debug("Persistent context closed (profile saved)")
        except BaseException as e:
            self.logger.debug(f"Error closing context: {e}")
        try:
            if self.pw:
                pw = self.pw
                self.pw = None
                pw.stop()
                self.logger.debug("Playwright stopped")
        except BaseException as e:
            self.logger.debug(f"Error stopping playwright: {e}")

    def _clean_html_pre_processing(self, html: str) -> str:
        """Entfernt störende Links aus Code-Blöcken vor der Markdown-Konvertierung"""
        soup = BeautifulSoup(html, 'html.parser')

        # <a> Tags in <pre> und <code> entfernen
        for block in soup.find_all(['pre', 'code']):
            for link in block.find_all('a', href=True):
                # Ersetze Link durch reinen Text (URL)
                link.replace_with(link.get('href', ''))

        return str(soup)

    def _extract_sidebar_fallback(self) -> List[Dict]:
        """
        SERPO-inspired fallback: Extract sources from sidebar when DOM injection fails

        Triggered when:
        - No citation buttons found
        - DOM injection returns empty citations
        - JavaScript errors

        Returns:
            List[Dict]: [{'title': str, 'url': str, 'source': str}, ...]
        """
        try:
            self.logger.debug("Sidebar fallback: extracting sources...")

            # Get sidebar container
            sidebar = None
            for selector in SIDEBAR_SELECTORS:
                sidebar = self.page.query_selector(selector)
                if sidebar:
                    break
            if not sidebar:
                self.logger.debug("Sidebar not found")
                return []

            # Extract all links
            links = sidebar.query_selector_all('a[href]')
            sources = []
            seen_urls = set()

            # Filter domains (same as DOM injection)
            skip_domains = ['google.com', 'google.de', 'gstatic.com', 'support.google.com']

            for link in links:
                try:
                    url = link.get_attribute('href')
                    title = link.inner_text().strip() or link.get_attribute('aria-label') or ''

                    # Skip invalid/duplicate/Google URLs
                    if not url or not url.startswith('http') or url in seen_urls:
                        continue
                    if any(domain in url for domain in skip_domains):
                        continue

                    # Parse domain
                    from urllib.parse import urlparse
                    domain = urlparse(url).hostname or ''

                    sources.append({
                        'title': title,
                        'url': url,
                        'source': domain
                    })
                    seen_urls.add(url)

                except Exception as e:
                    self.logger.debug(f"Link parse error: {e}")
                    continue

            self.logger.info(f"Sidebar fallback: {len(sources)} sources")
            return sources

        except Exception as e:
            self.logger.error(f"Sidebar fallback failed: {e}")
            return []

    def _dump_debug_page_state(self, reason: str) -> Optional[Path]:
        """Persist the current page HTML to logs for DOM troubleshooting."""
        if not self.page or not self.logger.debug_enabled:
            return None

        try:
            LOGS_DIR.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            safe_reason = re.sub(r'[^a-zA-Z0-9]+', '_', reason).strip('_') or "page_state"
            dump_path = LOGS_DIR / f"debug_{timestamp}_{safe_reason}.html"
            dump_path.write_text(self.page.content(), encoding="utf-8")
            self.logger.debug(f"Saved page dump: {dump_path}")
            return dump_path
        except Exception as e:
            self.logger.debug(f"Failed to save page dump: {e}")
            return None

    def _wait_for_captcha_to_clear(self) -> bool:
        """Wait for the manual CAPTCHA page to clear before scraping."""
        if not self.page:
            return False

        deadline = time.time() + CAPTCHA_SOLVE_TIMEOUT
        self.logger.info(f"Waiting up to {CAPTCHA_SOLVE_TIMEOUT}s for CAPTCHA to clear...")

        while time.time() < deadline:
            try:
                if not detect_captcha(self.page):
                    self.logger.info("CAPTCHA cleared; continuing.")
                    return True
            except Exception as e:
                if "browser has been closed" in str(e).lower() or "target closed" in str(e).lower():
                    self.logger.error("Browser closed while waiting for CAPTCHA to clear")
                    return False
                self.logger.debug(f"CAPTCHA wait check failed: {e}")

            try:
                self.page.wait_for_timeout(1000)
            except Exception:
                time.sleep(1)

        self.logger.warning("Timed out waiting for CAPTCHA to clear")
        return False

    def _embed_citations(self, markdown: str, citations: List[Dict]) -> tuple:
        """Ersetzt [CITE-N] Marker durch [1][2] Fußnoten"""
        modified_md = markdown
        citation_sources = []

        # Sortieren (höchste ID zuerst), damit beim Ersetzen Indizes stimmen
        citations_sorted = sorted(citations, key=lambda c: c.get('marker_id', 999), reverse=True)

        for citation in citations_sorted:
            marker_id = citation.get('marker_id')
            marker = f'[CITE-{marker_id}]'
            sources = citation.get('sources', [])

            if sources:
                start_idx = len(citation_sources)
                # Erzeuge Fußnoten-String: [1][2]
                footnotes = ''.join(f'[{start_idx + i + 1}]' for i in range(len(sources)))

                # Ersetze den Marker im Text
                if marker in modified_md:
                    modified_md = modified_md.replace(marker, footnotes, 1)
                    citation_sources.extend(sources)

        # Entferne übrig gebliebene Marker (falls keine Sources gefunden wurden)
        modified_md = re.sub(r'\[CITE-\d+\]', '', modified_md)

        return modified_md, citation_sources

    def _format_web_results_fallback(self, results: List[Dict[str, str]], query: str) -> Dict[str, Any]:
        """Format classic Google web results into the skill's markdown output."""
        markdown_lines = [
            "# Google Web Results Fallback",
            "",
            "AI Mode extraction was unavailable, so this answer was assembled from classic Google results using browser scraping.",
            "",
            f"Query: `{query}`",
            "",
        ]
        sources = []

        for idx, result in enumerate(results, 1):
            title = (result.get('title') or f"Result {idx}").strip()
            snippet = (result.get('snippet') or "").strip()
            url = (result.get('url') or "").strip()
            display_url = (result.get('display_url') or result.get('source') or "").strip()

            markdown_lines.append(f"{idx}. **{title}** [{idx}]")
            if snippet:
                markdown_lines.append(f"   {snippet}")
            if display_url:
                markdown_lines.append(f"   `{display_url}`")
            markdown_lines.append("")

            sources.append({
                "title": title,
                "url": url,
                "source": result.get('source') or display_url,
            })

        markdown_lines.extend(["---", "", "## Sources:", ""])
        for idx, source in enumerate(sources, 1):
            markdown_lines.append(f"[{idx}] {source['title']}  ")
            markdown_lines.append(source["url"])
            markdown_lines.append("")

        return {
            "success": True,
            "markdown": "\n".join(markdown_lines).strip(),
            "sources": sources,
            "source_url": build_google_search_url(query, ai_mode=False),
            "query": query,
            "mode": "web_results_fallback",
        }

    def _extract_classic_google_results(self, query: str) -> List[Dict[str, str]]:
        """Fallback to classic Google web results using browser scraping techniques."""
        if not self.page:
            return []

        fallback_url = build_google_search_url(query, ai_mode=False)
        print("  🌐 Falling back to classic Google web results...")
        self.logger.info(f"Classic web-results fallback: {fallback_url}")

        try:
            self.page.goto(fallback_url, wait_until="domcontentloaded", timeout=PAGE_LOAD_TIMEOUT)
            self.page.wait_for_timeout(1500)
        except Exception as e:
            self.logger.error(f"Classic Google fallback navigation failed: {e}")
            return []

        if detect_captcha(self.page):
            self.logger.warning("Classic Google fallback also hit CAPTCHA")
            return []

        extraction_script = """
() => {
    const results = [];
    const seen = new Set();
    const blocks = Array.from(document.querySelectorAll('div.g, div.MjjYud, div[data-snc], div.Gx5Zad'));

    function textOrEmpty(el) {
        return el ? (el.innerText || el.textContent || '').trim() : '';
    }

    for (const block of blocks) {
        const h3 = block.querySelector('h3');
        if (!h3) continue;

        let anchor = h3.closest('a[href]');
        if (!anchor) {
            anchor = block.querySelector('a[href]');
        }
        if (!anchor) continue;

        const url = anchor.href || '';
        if (!url.startsWith('http')) continue;
        if (url.includes('google.com')) continue;
        if (seen.has(url)) continue;

        const snippet = textOrEmpty(
            block.querySelector('div.VwiC3b, div[data-sncf="1"], span.aCOpRe, div.yXK7lf, div.s3v9rd')
        );
        const displayUrl = textOrEmpty(
            block.querySelector('cite, div.YrbPuc, span.OSrXXb, span.qzEoUe')
        );

        seen.add(url);
        results.push({
            title: textOrEmpty(h3),
            url,
            snippet,
            display_url: displayUrl,
            source: (() => {
                try { return new URL(url).hostname; } catch { return displayUrl; }
            })(),
        });

        if (results.length >= 5) break;
    }

    return results;
}
"""

        try:
            results = self.page.evaluate(extraction_script)
            self.logger.info(f"Classic Google fallback extracted {len(results)} results")
            return results or []
        except Exception as e:
            self.logger.error(f"Classic Google fallback extraction failed: {e}")
            return []

    def _build_web_results_fallback(self, query: str, reason: str) -> Dict[str, Any]:
        """Try classic Google web-result scraping when AI Mode extraction fails."""
        self.logger.warning(f"Attempting web-results fallback because: {reason}")
        results = self._extract_classic_google_results(query)
        if results:
            fallback_result = self._format_web_results_fallback(results, query)
            fallback_result["fallback_reason"] = reason
            return fallback_result
        return {
            "success": False,
            "error": reason,
            "message": "AI Mode extraction failed and classic web-results fallback returned no results.",
        }

    def scrape(self, query: str) -> Dict[str, Any]:
        """Führt den kompletten Scraping-Prozess durch"""
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")

        url = build_google_search_url(query, ai_mode=True)
        print(f"  🌐 Loading Query: {query[:50]}...")
        self.logger.debug(f"Navigating to: {url}")

        try:
            self.page.goto(url, wait_until="domcontentloaded", timeout=PAGE_LOAD_TIMEOUT)
            self.logger.debug("Page loaded successfully")
        except Exception as e:
            # Check for browser closed error
            self.logger.error(f"Page load failed: {e}")
            if "browser has been closed" in str(e).lower() or "target closed" in str(e).lower():
                return {
                    "success": False,
                    "error": "BROWSER_CLOSED_BY_USER",
                    "message": "Browser wurde vom User geschlossen"
                }
            return {"success": False, "error": f"Page load timeout: {e}"}

        # CAPTCHA CHECK (nach page load)
        print(f"  🔍 Checking for CAPTCHA...")
        self.logger.debug("Checking for CAPTCHA...")
        if detect_captcha(self.page):
            self.logger.warning("CAPTCHA detected")
            if self.headless:
                # Headless mode: Error zurückgeben
                self.logger.info("Running in headless mode - returning CAPTCHA error")
                return {
                    "success": False,
                    "error": "CAPTCHA_REQUIRED",
                    "message": "Google requires CAPTCHA verification. Please run again with --show-browser flag."
                }
            else:
                # Visible mode: Informiere User, aber KEIN Polling!
                # Der "Waiting for AI content" Loop unten wartet automatisch
                print("⚠️  CAPTCHA DETECTED - Browser bleibt offen")
                print("   Bitte lösen Sie das Captcha im Browser")
                print("   Script wartet auf das Verschwinden der CAPTCHA-Seite...")
                self.logger.info("CAPTCHA detected - waiting for user to solve and AI content to appear...")
                if not self._wait_for_captcha_to_clear():
                    dump_path = self._dump_debug_page_state("captcha_not_cleared")
                    if dump_path:
                        self.logger.error(f"Page dump saved to: {dump_path}")
                    return {
                        "success": False,
                        "error": "CAPTCHA_NOT_CLEARED",
                        "message": f"CAPTCHA page did not clear within {CAPTCHA_SOLVE_TIMEOUT} seconds."
                    }
        else:
            self.logger.debug("No CAPTCHA detected, proceeding...")

        # CHECK FOR AI MODE AVAILABILITY (region/language restrictions)
        print(f"  🌍 Checking AI Mode availability...")
        self.logger.debug("Checking if AI Mode is available in this region/language...")
        try:
            body_text = self.page.inner_text('body')
            if any(indicator in body_text for indicator in AI_MODE_NOT_AVAILABLE):
                self.logger.error("AI Mode not available in this region/language")
                print(f"  ❌ AI Mode not available in your country/language")
                return {
                    "success": False,
                    "error": "AI_MODE_NOT_AVAILABLE",
                    "message": "Google AI Mode is not available in your country or language. Please use a proxy/VPN to access from a supported region (e.g., US, UK, Germany).",
                    "suggestion": "Try using a proxy/VPN and ensure browser locale is set to a supported language."
                }
            else:
                self.logger.debug("AI Mode available, proceeding...")
        except Exception as e:
            self.logger.debug(f"Could not check AI Mode availability: {e}")
            # Proceed anyway - don't block on this check

        # HYBRID AI COMPLETION DETECTION (SERPO method + Multi-language fallback)
        print(f"  ⏳ Waiting for AI completion...")
        self.logger.debug("Starting hybrid completion detection...")
        ai_ready = False

        # OVERALL TIMEOUT: 40 seconds total, then proceed anyway
        overall_deadline = time.time() + 40

        # PRIMARY: Button-based detection (DUAL METHOD - ultra-robust!)
        # Method 1: SVG-based detection (100% reliable, language-independent!)
        remaining_time = int((overall_deadline - time.time()) * 1000)
        if remaining_time > 0 and not ai_ready:
            try:
                self.logger.debug("Method 1: Attempting SVG thumbs-up icon detection...")
                svg_selector = 'button svg[viewBox="3 3 18 18"]'
                self.page.wait_for_selector(
                    svg_selector,
                    timeout=min(AI_COMPLETION_TIMEOUT, remaining_time),
                    state='visible'
                )
                ai_ready = True
                self.logger.info("✅ Thumbs UP SVG detected!")
                print(f"  ✅ AI complete (Thumbs UP SVG detected!)")

            except Exception as svg_error:
                # Method 2: aria-label detection (fallback)
                self.logger.debug(f"Method 1 failed: {svg_error}")
                remaining_time = int((overall_deadline - time.time()) * 1000)
                if remaining_time > 0 and not ai_ready:
                    try:
                        self.logger.debug(f"Method 2: Attempting aria-label detection: {AI_COMPLETION_BUTTON}")
                        self.page.wait_for_selector(
                            AI_COMPLETION_BUTTON,
                            timeout=min(AI_COMPLETION_TIMEOUT, remaining_time),
                            state='visible'
                        )
                        ai_ready = True
                        self.logger.info("✅ AI complete via aria-label button")
                        print(f"  ✅ AI complete (button aria-label detected)")

                    except Exception as aria_error:
                        # Method 3: Text-based detection (multi-language fallback)
                        self.logger.debug(f"Method 2 failed: {svg_error}")
                        self.logger.debug("Both button methods failed, trying text detection...")
                        print(f"  ⏳ Button not found, trying text detection (multi-lang)...")

                        # Text fallback: Poll until overall deadline
                        while time.time() < overall_deadline and not ai_ready:
                            try:
                                body = self.page.inner_text('body')
                                if any(indicator in body for indicator in AI_COMPLETION_TEXT_INDICATORS):
                                    ai_ready = True
                                    self.logger.info(f"✅ AI complete via text")
                                    print(f"  ✅ AI complete (text detected)")
                                    break
                            except Exception as e:
                                if "browser has been closed" in str(e).lower() or "target closed" in str(e).lower():
                                    self.logger.error("Browser closed while waiting for AI content")
                                    return {
                                        "success": False,
                                        "error": "BROWSER_CLOSED_BY_USER",
                                        "message": "Browser wurde vom User geschlossen"
                                    }
                            time.sleep(1)

        # FINAL TIMEOUT FALLBACK: After 40 seconds, proceed with whatever is loaded
        if not ai_ready:
            elapsed = int(time.time() - (overall_deadline - 40))
            if elapsed >= 40:
                self.logger.warning(f"⏱️  40s timeout reached - proceeding with loaded content")
                print(f"  ⏱️  Timeout (40s) - scraping loaded content")
                ai_ready = True  # Proceed anyway
            else:
                self.logger.warning("AI completion not detected (proceeding anyway)")
                print(f"  ⚠️  No completion indicator (proceeding)")

        # JavaScript Injection (DOM Marker & Extraction)
        print(f"  📚 Injecting Markers & Extracting Sources...")
        self.logger.debug("Starting JavaScript DOM injection...")
        try:
            # Inject citation selectors into JavaScript
            script_with_selectors = DOM_INJECTION_SCRIPT.replace(
                '%CITATION_SELECTORS%',
                json.dumps(CITATION_SELECTORS)
            )
            script_with_selectors = script_with_selectors.replace(
                '%MAIN_CONTENT_SELECTORS%',
                json.dumps(MAIN_CONTENT_SELECTORS)
            )
            script_with_selectors = script_with_selectors.replace(
                '%SIDEBAR_SELECTORS%',
                json.dumps(SIDEBAR_SELECTORS)
            )
            data = self.page.evaluate(script_with_selectors)
            self.logger.debug("JavaScript injection successful")
        except Exception as e:
            # Check for browser closed
            self.logger.error(f"JavaScript injection failed: {e}")
            if "browser has been closed" in str(e).lower() or "target closed" in str(e).lower():
                return {
                    "success": False,
                    "error": "BROWSER_CLOSED_BY_USER",
                    "message": "Browser wurde vom User geschlossen"
                }
            dump_path = self._dump_debug_page_state("js_injection_failed")
            if dump_path:
                self.logger.error(f"Page dump saved to: {dump_path}")
            return {"success": False, "error": f"JS Injection failed: {e}"}

        if 'error' in data:
            self.logger.error(f"JS script returned error: {data['error']}")
            dump_path = self._dump_debug_page_state("dom_container_missing")
            if dump_path:
                self.logger.error(f"Page dump saved to: {dump_path}")
            return self._build_web_results_fallback(query, data['error'])

        html_content = data['html']
        citations = data['citations']
        self.logger.debug(f"DOM injection: {len(citations)} citation groups")

        # SIDEBAR FALLBACK: If DOM injection returned no citations
        if len(citations) == 0:
            self.logger.info("No citations from DOM, triggering sidebar fallback...")
            print(f"  📌 No citation buttons, trying sidebar...")

            fallback_sources = self._extract_sidebar_fallback()

            if fallback_sources:
                # Create single citation group with all sidebar sources
                citations = [{
                    'marker_id': 0,
                    'sources': fallback_sources
                }]
                self.logger.info(f"✅ Sidebar fallback: {len(fallback_sources)} sources")
                print(f"  ✅ Sidebar fallback: {len(fallback_sources)} sources")
            else:
                self.logger.warning("No sources found (DOM + sidebar both empty)")
                print(f"  ⚠️  No sources found (DOM + sidebar both empty)")

        # HTML Cleanup
        self.logger.debug("Cleaning HTML content...")
        html_cleaned = self._clean_html_pre_processing(html_content)

        # Convert to Markdown
        print(f"  🔄 Converting HTML to Markdown...")
        self.logger.debug("Converting HTML to Markdown...")
        if ConversionOptions:
            options = ConversionOptions(
                heading_style="atx",
                list_indent_width=2,
                bullets="*+- ",
                wrap=False
            )
            markdown = convert(html_cleaned, options)
        else:
            markdown = convert(html_cleaned)

        # Post-Processing (Text Cleanup)
        self.logger.debug("Starting post-processing...")

        # Entferne Highlighting-Marker (==), die Google/Converter erzeugt
        markdown = markdown.replace('==', '')

        # Entferne Base64 Bilder
        markdown = re.sub(r'!\[[^\]]*\]\(data:image/[^)]+\)', '', markdown)

        # Entferne leere Links
        markdown = re.sub(r'\[\]\([^)]+\)', '', markdown)

        # RADIKALER CUT-OFF: Alles ab dem AI-Disclaimer entfernen
        cut_off_markers = [
            'KI-Antworten können Fehler enthalten',
            'AI-generated answers may contain mistakes',
            'Öffentlicher Link wird erstellt'
        ]

        for marker in cut_off_markers:
            if marker in markdown:
                markdown = markdown.split(marker)[0]
                self.logger.debug(f"Cut off content at marker: {marker[:30]}...")

        # SMART LINE MERGING (Fix broken sentences)
        markdown = re.sub(r'([^\.\!\?\:\;\n])\n+\s*(\*\*)', r'\1 \2', markdown)
        markdown = re.sub(r'([^\.\!\?\:\;\n])\n+\s*([a-zäöü])', r'\1 \2', markdown)

        # Finales Trimmen
        markdown = markdown.strip()

        # Entferne alleinstehende Punkte auf eigener Zeile (nach dem Cut-off)
        markdown = re.sub(r'^\s*\.\s*$', '', markdown, flags=re.MULTILINE)

        # Leere Zeilen reduzieren
        markdown = re.sub(r'\n{3,}', '\n\n', markdown).strip()

        # Citations einfügen
        print(f"  📌 Embedding {len(citations)} citations...")
        self.logger.debug(f"Embedding {len(citations)} citation groups...")
        markdown, sources = self._embed_citations(markdown, citations)
        self.logger.debug(f"Total sources embedded: {len(sources)}")

        # Quellenverzeichnis anhängen
        if sources:
            self.logger.debug("Appending sources section...")
            markdown += "\n\n---\n\n## Sources:\n\n"
            for i, source in enumerate(sources, 1):
                markdown += f"[{i}] {source.get('title', 'Link')}  \n{source.get('url')}\n\n"
        elif len(markdown.strip()) < 120:
            return self._build_web_results_fallback(query, "AI content too short and no sources found")

        self.logger.info(f"Scraping completed successfully - {len(sources)} sources, {len(markdown)} chars")
        return {
            "success": True,
            "markdown": markdown,
            "sources": sources,
            "source_url": url,
            "query": query
        }

# =============================================================================
# CLI ENTRY POINT
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Google AI Mode Search")

    # Input Arguments
    parser.add_argument("--query", type=str, help="Full search query")
    parser.add_argument("--city", type=str, help="City name (e.g. 'Münster')")
    parser.add_argument("--plz", type=str, help="Postal code")
    parser.add_argument("--topic", type=str, default="Mietspiegel 2026", help="Topic for constructed query")

    # Options
    parser.add_argument("--output", type=str, help="Custom output filename")
    parser.add_argument("--show-browser", action="store_true", help="Run browser visibly (for debugging or captcha solving)")
    parser.add_argument("--json", action="store_true", help="Save raw JSON alongside Markdown")
    parser.add_argument("--debug", action="store_true", help="Enable verbose debug logging to logs/ folder")
    parser.add_argument("--save", action="store_true", help="Save results to skill results/ folder instead of current directory")

    args = parser.parse_args()

    # Query Construction Logic
    query = ""
    if args.query:
        query = args.query
    elif args.city:
        plz_part = f" {args.plz}" if args.plz else ""
        query = f"{args.topic} {args.city}{plz_part}"
    else:
        print("❌ Error: You must provide either --query OR --city")
        parser.print_help()
        sys.exit(1)

    print("=" * 60)
    print(f"🚀 GOOGLE AI MODE SEARCH")
    print(f"   Query: '{query}'")
    print(f"   Mode:  {'Visible' if args.show_browser else 'Headless'}")
    if args.debug:
        print(f"   Debug: Enabled (logs will be saved)")
    if args.save:
        print(f"   Save:  Results folder")
    print("=" * 60)

    # Initialize logger
    logger = get_logger(debug=args.debug)
    logger.info(f"Starting search for: {query}")
    logger.debug(f"Arguments: show_browser={args.show_browser}, debug={args.debug}, save={args.save}")

    scraper = GoogleAIScraper(headless=not args.show_browser, logger=logger)

    try:
        scraper.start()
        result = scraper.scrape(query)

        if result['success']:
            print("\n✅ SEARCH SUCCESSFUL")
            print("-" * 60)
            logger.info("Search completed successfully")

            # Filename Generation
            if args.output:
                # User specified output path
                out_path = Path(args.output)
                logger.debug(f"Using custom output path: {out_path}")
            elif args.save:
                # Save to skill results/ folder with timestamp
                RESULTS_DIR.mkdir(exist_ok=True)
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                safe_name = re.sub(r'[^a-zA-Z0-9]', '_', query[:40]).strip('_')
                out_path = RESULTS_DIR / f"{timestamp}_{safe_name}.md"
                logger.debug(f"Saving to results folder: {out_path}")
            else:
                # Current directory (default)
                safe_name = re.sub(r'[^a-zA-Z0-9]', '_', query[:40]).strip('_')
                out_path = Path(f"result_{safe_name}.md")
                logger.debug(f"Saving to current directory: {out_path}")

            # Write Markdown
            logger.debug(f"Writing markdown to: {out_path}")
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(result['markdown'])
            print(f"📄 Saved Markdown: {out_path}")
            logger.info(f"Markdown saved: {out_path}")

            # Write JSON if requested
            if args.json:
                json_path = out_path.with_suffix('.json')
                logger.debug(f"Writing JSON to: {json_path}")
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                print(f"💾 Saved JSON:     {json_path}")
                logger.info(f"JSON saved: {json_path}")

            # Preview (First 500 chars)
            print("\n--- PREVIEW ---")
            print(result['markdown'][:500] + "\n...")

        else:
            print("\n❌ SEARCH FAILED")
            print(f"Error: {result.get('error')}")
            print(f"Message: {result.get('message', '')}")
            if result.get('suggestion'):
                print(f"Suggestion: {result.get('suggestion')}")
            logger.error(f"Search failed: {result.get('error')} - {result.get('message', '')}")

            # Return specific exit codes for different errors
            if result.get('error') == 'CAPTCHA_REQUIRED':
                sys.exit(2)  # Special exit code for captcha
            elif result.get('error') == 'BROWSER_CLOSED_BY_USER':
                sys.exit(3)
            elif result.get('error') == 'AI_MODE_NOT_AVAILABLE':
                sys.exit(4)  # AI Mode not available in region
            else:
                sys.exit(1)

    except KeyboardInterrupt:
        print("\n⚠️  Aborted by User")
        logger.warning("Search aborted by user (Ctrl+C)")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        logger.exception("Unexpected error occurred")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        scraper.stop()
        if logger.debug_enabled and logger.log_file:
            print(f"\n📋 Debug log saved: {logger.log_file}")

if __name__ == "__main__":
    main()
