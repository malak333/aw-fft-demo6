#!/usr/bin/env python3
"""Browser tests for the Final Fantasy Tactics website.

Validates responsive layout, navigation, and content visibility
using Playwright Async API. Run with: python test_browser.py
"""

import asyncio
import unittest
from pathlib import Path

from playwright.async_api import async_playwright

BASE_DIR = Path(__file__).resolve().parent
HTML_PATH = BASE_DIR / "index.html"


class TestBrowserLayout(unittest.TestCase):
    """Validate browser rendering of the website."""

    @classmethod
    def setUpClass(cls):
        cls.html_url = f"file://{HTML_PATH.resolve()}"

    def _run_async(self, coro):
        """Run an async coroutine from a sync test method."""
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    async def _open_page(self, viewport_width, viewport_height):
        """Open the page at the given viewport size (without navigating)."""
        pw = await async_playwright().start()
        browser = await pw.chromium.launch()
        context = await browser.new_context(
            viewport={"width": viewport_width, "height": viewport_height}
        )
        page = await context.new_page()
        return pw, browser, context, page

    async def _navigate(self, page):
        """Navigate to the HTML page."""
        await page.goto(self.html_url, wait_until="domcontentloaded")

    async def _close(self, pw, browser, context, page):
        """Close the page and context."""
        await page.close()
        await context.close()
        await browser.close()
        await pw.stop()

    def test_no_horizontal_overflow_desktop(self):
        """Desktop viewport should not have horizontal overflow."""
        async def _check():
            pw, browser, context, page = await self._open_page(1280, 800)
            try:
                await self._navigate(page)
                scroll_width = await page.evaluate("document.documentElement.scrollWidth")
                client_width = await page.evaluate("document.documentElement.clientWidth")
                self.assertLessEqual(
                    scroll_width,
                    client_width,
                    f"Horizontal overflow detected: scrollWidth={scroll_width}, clientWidth={client_width}",
                )
            finally:
                await self._close(pw, browser, context, page)
        self._run_async(_check())

    def test_no_horizontal_overflow_mobile(self):
        """Mobile viewport should not have horizontal overflow."""
        async def _check():
            pw, browser, context, page = await self._open_page(375, 667)
            try:
                await self._navigate(page)
                scroll_width = await page.evaluate("document.documentElement.scrollWidth")
                client_width = await page.evaluate("document.documentElement.clientWidth")
                self.assertLessEqual(
                    scroll_width,
                    client_width,
                    f"Horizontal overflow detected: scrollWidth={scroll_width}, clientWidth={client_width}",
                )
            finally:
                await self._close(pw, browser, context, page)
        self._run_async(_check())

    def test_no_horizontal_overflow_tablet(self):
        """Tablet viewport should not have horizontal overflow."""
        async def _check():
            pw, browser, context, page = await self._open_page(768, 1024)
            try:
                await self._navigate(page)
                scroll_width = await page.evaluate("document.documentElement.scrollWidth")
                client_width = await page.evaluate("document.documentElement.clientWidth")
                self.assertLessEqual(
                    scroll_width,
                    client_width,
                    f"Horizontal overflow detected: scrollWidth={scroll_width}, clientWidth={client_width}",
                )
            finally:
                await self._close(pw, browser, context, page)
        self._run_async(_check())

    def test_main_content_visible_desktop(self):
        """Main content should be visible in desktop viewport."""
        async def _check():
            pw, browser, context, page = await self._open_page(1280, 800)
            try:
                await self._navigate(page)
                main = page.locator("main")
                self.assertTrue(
                    await main.is_visible(),
                    "Main content should be visible",
                )
            finally:
                await self._close(pw, browser, context, page)
        self._run_async(_check())

    def test_main_content_visible_mobile(self):
        """Main content should be visible in mobile viewport."""
        async def _check():
            pw, browser, context, page = await self._open_page(375, 667)
            try:
                await self._navigate(page)
                main = page.locator("main")
                self.assertTrue(
                    await main.is_visible(),
                    "Main content should be visible on mobile",
                )
            finally:
                await self._close(pw, browser, context, page)
        self._run_async(_check())

    def test_navigation_visible_desktop(self):
        """Navigation should be visible in desktop viewport."""
        async def _check():
            pw, browser, context, page = await self._open_page(1280, 800)
            try:
                await self._navigate(page)
                nav = page.locator("#main-nav")
                self.assertTrue(
                    await nav.is_visible(),
                    "Navigation should be visible on desktop",
                )
            finally:
                await self._close(pw, browser, context, page)
        self._run_async(_check())

    def test_navigation_visible_mobile(self):
        """Navigation should be visible in mobile viewport."""
        async def _check():
            pw, browser, context, page = await self._open_page(375, 667)
            try:
                await self._navigate(page)
                nav = page.locator("#main-nav")
                self.assertTrue(
                    await nav.is_visible(),
                    "Navigation should be visible on mobile",
                )
            finally:
                await self._close(pw, browser, context, page)
        self._run_async(_check())

    def test_nav_links_clickable_desktop(self):
        """Navigation links should be clickable and navigate to sections."""
        async def _check():
            pw, browser, context, page = await self._open_page(1280, 800)
            try:
                await self._navigate(page)
                # Scroll to top first to ensure we're not already at the target
                await page.evaluate("window.scrollTo(0, 0)")
                await page.wait_for_timeout(100)

                overview_link = page.locator('#main-nav a[href="#overview"]')
                await overview_link.click()
                # Wait for smooth scroll to complete
                await page.wait_for_timeout(500)

                # Verify the section heading is fully visible below the sticky header
                header = page.locator("#main-header")
                header_rect = await header.evaluate("el => el.getBoundingClientRect()")
                header_bottom = header_rect["bottom"]
                viewport_height = await page.evaluate("window.innerHeight")
                overview = page.locator("#overview h2")
                heading_rect = await overview.evaluate("el => el.getBoundingClientRect()")
                heading_top = heading_rect["top"]
                heading_bottom = heading_rect["bottom"]
                self.assertGreaterEqual(
                    heading_top,
                    header_bottom,
                    f"Overview heading should be below the sticky header (header_bottom={header_bottom}px, heading_top={heading_top}px)",
                )
                self.assertLessEqual(
                    heading_bottom,
                    viewport_height,
                    f"Overview heading should be within the viewport (viewport={viewport_height}px, heading_bottom={heading_bottom}px)",
                )
            finally:
                await self._close(pw, browser, context, page)
        self._run_async(_check())

    def test_nav_links_clickable_mobile(self):
        """Navigation links should be clickable and navigate to sections on mobile."""
        async def _check():
            pw, browser, context, page = await self._open_page(375, 667)
            try:
                await self._navigate(page)
                # Scroll to top first to ensure we're not already at the target
                await page.evaluate("window.scrollTo(0, 0)")
                await page.wait_for_timeout(100)

                story_link = page.locator('#main-nav a[href="#story"]')
                await story_link.click()
                # Wait for smooth scroll to complete
                await page.wait_for_timeout(500)

                # Verify the section heading is fully visible below the sticky header
                header = page.locator("#main-header")
                header_rect = await header.evaluate("el => el.getBoundingClientRect()")
                header_bottom = header_rect["bottom"]
                viewport_height = await page.evaluate("window.innerHeight")
                story = page.locator("#story h2")
                heading_rect = await story.evaluate("el => el.getBoundingClientRect()")
                heading_top = heading_rect["top"]
                heading_bottom = heading_rect["bottom"]
                self.assertGreaterEqual(
                    heading_top,
                    header_bottom,
                    f"Story heading should be below the sticky header (header_bottom={header_bottom}px, heading_top={heading_top}px)",
                )
                self.assertLessEqual(
                    heading_bottom,
                    viewport_height,
                    f"Story heading should be within the viewport (viewport={viewport_height}px, heading_bottom={heading_bottom}px)",
                )
            finally:
                await self._close(pw, browser, context, page)
        self._run_async(_check())

    def test_nav_links_clickable_mobile_short(self):
        """Navigation links should be clickable and navigate to sections at 375x600 mobile height."""
        async def _check():
            pw, browser, context, page = await self._open_page(375, 600)
            try:
                await self._navigate(page)
                # Scroll to top first to ensure we're not already at the target
                await page.evaluate("window.scrollTo(0, 0)")
                await page.wait_for_timeout(100)

                story_link = page.locator('#main-nav a[href="#story"]')
                await story_link.click()
                # Wait for smooth scroll to complete
                await page.wait_for_timeout(500)

                # Verify the section heading is fully visible below the sticky header
                header = page.locator("#main-header")
                header_rect = await header.evaluate("el => el.getBoundingClientRect()")
                header_bottom = header_rect["bottom"]
                viewport_height = await page.evaluate("window.innerHeight")
                story = page.locator("#story h2")
                heading_rect = await story.evaluate("el => el.getBoundingClientRect()")
                heading_top = heading_rect["top"]
                heading_bottom = heading_rect["bottom"]
                self.assertGreaterEqual(
                    heading_top,
                    header_bottom,
                    f"Story heading should be below the sticky header at 375x600 (header_bottom={header_bottom}px, heading_top={heading_top}px)",
                )
                self.assertLessEqual(
                    heading_bottom,
                    viewport_height,
                    f"Story heading should be within the viewport at 375x600 (viewport={viewport_height}px, heading_bottom={heading_bottom}px)",
                )
            finally:
                await self._close(pw, browser, context, page)
        self._run_async(_check())

    def test_mobile_short_viewport_header_height(self):
        """At 375x320 viewport, the header should not consume most of the screen.

        Reproducer: at 375x320, all six nav links stack vertically. Without the fix,
        the sticky header becomes ~300px tall, leaving almost no room for content.
        The fix disables sticky positioning at <=480px, so the header height should
        be reasonable (under 150px) and sufficient content should remain visible.
        """
        async def _check():
            pw, browser, context, page = await self._open_page(375, 320)
            try:
                await self._navigate(page)
                await page.evaluate("window.scrollTo(0, 0)")
                await page.wait_for_timeout(100)

                header = page.locator("#main-header")
                header_rect = await header.evaluate("el => el.getBoundingClientRect()")
                header_height = header_rect["bottom"] - header_rect["top"]
                viewport_height = await page.evaluate("window.innerHeight")

                # Header should not consume most of the viewport
                self.assertLess(
                    header_height,
                    150,
                    f"Header height ({header_height}px) should be under 150px at 375x320 viewport (viewport_height={viewport_height}px)",
                )

                # Verify that the header is not sticky at this viewport width
                header_position = await header.evaluate("el => getComputedStyle(el).position")
                self.assertNotEqual(
                    header_position,
                    "sticky",
                    "Header should not be sticky at <=480px viewport width",
                )

                # Verify sufficient content remains visible below the header
                main = page.locator("main")
                main_rect = await main.evaluate("el => el.getBoundingClientRect()")
                content_top = main_rect["top"]
                content_bottom = main_rect["bottom"]
                visible_content_height = max(0, min(content_bottom, viewport_height) - max(content_top, header_rect["bottom"]))
                self.assertGreater(
                    visible_content_height,
                    50,
                    f"At least 50px of content should be visible below the header at 375x320 (visible_content_height={visible_content_height}px)",
                )
            finally:
                await self._close(pw, browser, context, page)
        self._run_async(_check())

    def test_hero_section_content_visible(self):
        """Hero section should display its content."""
        async def _check():
            pw, browser, context, page = await self._open_page(1280, 800)
            try:
                await self._navigate(page)
                hero = page.locator(".hero")
                self.assertTrue(await hero.is_visible(), "Hero section should be visible")
                h1 = hero.locator("h1")
                self.assertTrue(await h1.is_visible(), "Hero h1 should be visible")
                h1_text = await h1.inner_text()
                self.assertIn(
                    "Final Fantasy Tactics",
                    h1_text,
                    "Hero h1 should contain 'Final Fantasy Tactics'",
                )
            finally:
                await self._close(pw, browser, context, page)
        self._run_async(_check())

    def test_all_sections_rendered(self):
        """All major sections should be rendered in the DOM."""
        async def _check():
            pw, browser, context, page = await self._open_page(1280, 800)
            try:
                await self._navigate(page)
                sections = ["overview", "story", "gameplay", "jobs", "music", "legacy"]
                for section_id in sections:
                    section = page.locator(f"#{section_id}")
                    self.assertTrue(
                        await section.is_visible(),
                        f"Section '{section_id}' should be rendered and visible",
                    )
            finally:
                await self._close(pw, browser, context, page)
        self._run_async(_check())

    def test_footer_visible(self):
        """Footer should be visible."""
        async def _check():
            pw, browser, context, page = await self._open_page(1280, 800)
            try:
                await self._navigate(page)
                footer = page.locator("#main-footer")
                self.assertTrue(
                    await footer.is_visible(),
                    "Footer should be visible",
                )
            finally:
                await self._close(pw, browser, context, page)
        self._run_async(_check())

    def test_no_console_errors(self):
        """Page should load without JavaScript console errors."""
        async def _check():
            errors = []
            pw, browser, context, page = await self._open_page(1280, 800)
            try:
                # Register listeners BEFORE navigation to catch all errors
                page.on("console", lambda msg: errors.append(msg) if msg.type == "error" else None)
                page.on("pageerror", lambda err: errors.append(err))
                await self._navigate(page)
                await page.wait_for_timeout(300)
                console_errors = [str(e) for e in errors if hasattr(e, 'type') and e.type == 'error']
                page_errors = [str(e) for e in errors if not hasattr(e, 'type')]
                self.assertEqual(
                    console_errors,
                    [],
                    f"Console errors detected: {console_errors}",
                )
                self.assertEqual(
                    page_errors,
                    [],
                    f"Uncaught exceptions detected: {page_errors}",
                )
            finally:
                await self._close(pw, browser, context, page)
        self._run_async(_check())

    def test_console_error_detection_works(self):
        """Verify that the console error listener actually catches injected errors."""
        async def _check():
            errors = []
            pw, browser, context, page = await self._open_page(1280, 800)
            try:
                # Register listeners BEFORE navigation
                page.on("console", lambda msg: errors.append(msg) if msg.type == "error" else None)
                page.on("pageerror", lambda err: errors.append(err))
                await self._navigate(page)
                # Inject a console.error to verify the listener catches it
                await page.evaluate("console.error('test-error-injection')")
                await page.wait_for_timeout(100)
                self.assertGreater(
                    len(errors), 0,
                    "Console error listener should have caught the injected error",
                )
                # Verify it was a console error, not a pageerror
                console_errors = [e for e in errors if hasattr(e, 'type') and e.type == 'error']
                self.assertGreater(
                    len(console_errors), 0,
                    "Should have caught a console error",
                )
            finally:
                await self._close(pw, browser, context, page)
        self._run_async(_check())

    def test_startup_console_error_detected(self):
        """Verify that startup console.error errors are caught by the listener."""
        async def _check():
            errors = []
            pw, browser, context, page = await self._open_page(1280, 800)
            try:
                # Register listeners BEFORE navigation
                page.on("console", lambda msg: errors.append(msg) if msg.type == "error" else None)
                page.on("pageerror", lambda err: errors.append(err))
                # Inject a startup console.error via init script (runs before page load)
                await page.add_init_script('console.error("startup-probe-error")')
                await self._navigate(page)
                await page.wait_for_timeout(300)
                console_errors = [e for e in errors if hasattr(e, 'type') and e.type == 'error']
                self.assertGreater(
                    len(console_errors), 0,
                    "Startup console.error should have been caught",
                )
            finally:
                await self._close(pw, browser, context, page)
        self._run_async(_check())

    def test_startup_page_error_detected(self):
        """Verify that startup uncaught exceptions are caught by the pageerror listener."""
        async def _check():
            errors = []
            pw, browser, context, page = await self._open_page(1280, 800)
            try:
                # Register listeners BEFORE navigation
                page.on("console", lambda msg: errors.append(msg) if msg.type == "error" else None)
                page.on("pageerror", lambda err: errors.append(err))
                # Inject a startup uncaught exception via init script
                await page.add_init_script('throw new Error("startup-probe-exception")')
                await self._navigate(page)
                await page.wait_for_timeout(300)
                page_errors = [str(e) for e in errors if not hasattr(e, 'type')]
                self.assertGreater(
                    len(page_errors), 0,
                    f"Startup uncaught exception should have been caught. Got: {page_errors}",
                )
            finally:
                await self._close(pw, browser, context, page)
        self._run_async(_check())

    def test_page_error_detection_works(self):
        """Verify that the pageerror listener catches uncaught exceptions."""
        async def _check():
            errors = []
            pw, browser, context, page = await self._open_page(1280, 800)
            try:
                page.on("console", lambda msg: errors.append(msg) if msg.type == "error" else None)
                page.on("pageerror", lambda err: errors.append(err))
                await page.add_init_script("throw new Error('test-page-error')")
                await self._navigate(page)
                await page.wait_for_timeout(300)
                page_errors = [str(e) for e in errors if not hasattr(e, 'type')]
                self.assertGreater(
                    len(page_errors), 0,
                    f"pageerror listener should have caught the uncaught exception. Got: {page_errors}",
                )
            finally:
                await self._close(pw, browser, context, page)
        self._run_async(_check())

    def test_nav_links_disabled_script_fails(self):
        """Navigation should fail when script.js is disabled and default action prevented."""
        async def _check():
            pw, browser, context, page = await self._open_page(1280, 800)
            try:
                # Disable script.js by blocking it, and prevent default anchor navigation
                await page.route("**/script.js", lambda route: route.abort())
                await page.add_init_script("""document.addEventListener('DOMContentLoaded', () => { document.querySelectorAll('#main-nav a[href^="#"]').forEach(a => a.addEventListener('click', e => e.preventDefault())); });""")
                await self._navigate(page)
                await page.evaluate("window.scrollTo(0, 0)")
                await page.wait_for_timeout(100)

                legacy_link = page.locator('#main-nav a[href="#legacy"]')
                await legacy_link.click()
                await page.wait_for_timeout(500)

                # Verify the section is NOT in the viewport (navigation was prevented)
                legacy = page.locator("#legacy")
                legacy_rect = await legacy.evaluate("el => el.getBoundingClientRect()")
                legacy_top = legacy_rect["top"]
                self.assertGreater(
                    legacy_top,
                    200,
                    "Legacy section should NOT have scrolled into view when navigation is disabled",
                )
            finally:
                await self._close(pw, browser, context, page)
        self._run_async(_check())

    def test_fragment_navigation_mobile_short(self):
        """Loading page with fragment URL at 375x600 should offset heading below sticky header."""
        async def _check():
            pw, browser, context, page = await self._open_page(375, 600)
            try:
                # Navigate directly to the page with a fragment
                await page.goto(self.html_url + "#story", wait_until="domcontentloaded")
                await page.wait_for_timeout(300)

                # Verify the section heading is fully visible below the sticky header
                header = page.locator("#main-header")
                header_rect = await header.evaluate("el => el.getBoundingClientRect()")
                header_bottom = header_rect["bottom"]
                viewport_height = await page.evaluate("window.innerHeight")
                story = page.locator("#story h2")
                heading_rect = await story.evaluate("el => el.getBoundingClientRect()")
                heading_top = heading_rect["top"]
                heading_bottom = heading_rect["bottom"]
                self.assertGreaterEqual(
                    heading_top,
                    header_bottom,
                    f"Story heading should be below the sticky header at 375x600 fragment load (header_bottom={header_bottom}px, heading_top={heading_top}px)",
                )
                self.assertLessEqual(
                    heading_bottom,
                    viewport_height,
                    f"Story heading should be within the viewport at 375x600 fragment load (viewport={viewport_height}px, heading_bottom={heading_bottom}px)",
                )
            finally:
                await self._close(pw, browser, context, page)
        self._run_async(_check())

    def test_fragment_navigation_desktop(self):
        """Loading page with fragment URL on desktop should offset heading below sticky header."""
        async def _check():
            pw, browser, context, page = await self._open_page(1280, 800)
            try:
                # Navigate directly to the page with a fragment
                await page.goto(self.html_url + "#legacy", wait_until="domcontentloaded")
                await page.wait_for_timeout(300)

                # Verify the section heading is fully visible below the sticky header
                header = page.locator("#main-header")
                header_rect = await header.evaluate("el => el.getBoundingClientRect()")
                header_bottom = header_rect["bottom"]
                viewport_height = await page.evaluate("window.innerHeight")
                legacy = page.locator("#legacy h2")
                heading_rect = await legacy.evaluate("el => el.getBoundingClientRect()")
                heading_top = heading_rect["top"]
                heading_bottom = heading_rect["bottom"]
                self.assertGreaterEqual(
                    heading_top,
                    header_bottom,
                    f"Legacy heading should be below the sticky header on desktop fragment load (header_bottom={header_bottom}px, heading_top={heading_top}px)",
                )
                self.assertLessEqual(
                    heading_bottom,
                    viewport_height,
                    f"Legacy heading should be within the viewport on desktop fragment load (viewport={viewport_height}px, heading_bottom={heading_bottom}px)",
                )
            finally:
                await self._close(pw, browser, context, page)
        self._run_async(_check())

    def test_click_story_updates_url_and_history(self):
        """Clicking Story should update the URL fragment and add a history entry."""
        async def _check():
            pw, browser, context, page = await self._open_page(1280, 800)
            try:
                await self._navigate(page)
                await page.evaluate("window.scrollTo(0, 0)")
                await page.wait_for_timeout(100)

                initial_url = page.url
                self.assertNotIn("#story", initial_url, "Initial URL should not have #story fragment")

                story_link = page.locator('#main-nav a[href="#story"]')
                await story_link.click()
                await page.wait_for_timeout(500)

                current_url = page.url
                self.assertIn("#story", current_url, "URL should contain #story fragment after clicking Story")

                # Verify the section heading is below the sticky header
                header = page.locator("#main-header")
                header_rect = await header.evaluate("el => el.getBoundingClientRect()")
                header_bottom = header_rect["bottom"]
                viewport_height = await page.evaluate("window.innerHeight")
                story = page.locator("#story h2")
                heading_rect = await story.evaluate("el => el.getBoundingClientRect()")
                heading_top = heading_rect["top"]
                heading_bottom = heading_rect["bottom"]
                self.assertGreaterEqual(
                    heading_top,
                    header_bottom,
                    "Story heading should be below the sticky header",
                )
                self.assertLessEqual(
                    heading_bottom,
                    viewport_height,
                    "Story heading should be within the viewport",
                )
            finally:
                await self._close(pw, browser, context, page)
        self._run_async(_check())

    def test_reload_preserves_fragment(self):
        """Reloading the page with a fragment should preserve the fragment and target position."""
        async def _check():
            pw, browser, context, page = await self._open_page(1280, 800)
            try:
                await self._navigate(page)
                await page.evaluate("window.scrollTo(0, 0)")
                await page.wait_for_timeout(100)

                story_link = page.locator('#main-nav a[href="#story"]')
                await story_link.click()
                await page.wait_for_timeout(500)

                # Verify fragment is in URL
                current_url = page.url
                self.assertIn("#story", current_url, "URL should contain #story fragment")

                # Reload the page
                await page.reload(wait_until="domcontentloaded")
                await page.wait_for_timeout(500)

                # Verify fragment is still in URL after reload
                reloaded_url = page.url
                self.assertIn("#story", reloaded_url, "URL should still contain #story fragment after reload")

                # Verify the section heading is below the sticky header
                header = page.locator("#main-header")
                header_rect = await header.evaluate("el => el.getBoundingClientRect()")
                header_bottom = header_rect["bottom"]
                viewport_height = await page.evaluate("window.innerHeight")
                story = page.locator("#story h2")
                heading_rect = await story.evaluate("el => el.getBoundingClientRect()")
                heading_top = heading_rect["top"]
                heading_bottom = heading_rect["bottom"]
                self.assertGreaterEqual(
                    heading_top,
                    header_bottom,
                    "Story heading should be below the sticky header after reload",
                )
                self.assertLessEqual(
                    heading_bottom,
                    viewport_height,
                    "Story heading should be within the viewport after reload",
                )
            finally:
                await self._close(pw, browser, context, page)
        self._run_async(_check())

    def test_back_forward_navigation(self):
        """Navigating between sections and using Back/Forward should restore fragments and positions."""
        async def _check():
            pw, browser, context, page = await self._open_page(1280, 800)
            try:
                await self._navigate(page)
                await page.evaluate("window.scrollTo(0, 0)")
                await page.wait_for_timeout(100)

                # Click Story
                story_link = page.locator('#main-nav a[href="#story"]')
                await story_link.click()
                await page.wait_for_timeout(500)
                url_story = page.url
                self.assertIn("#story", url_story, "URL should contain #story after clicking Story")

                # Click Gameplay
                gameplay_link = page.locator('#main-nav a[href="#gameplay"]')
                await gameplay_link.click()
                await page.wait_for_timeout(500)
                url_gameplay = page.url
                self.assertIn("#gameplay", url_gameplay, "URL should contain #gameplay after clicking Gameplay")

                # Go Back
                await page.go_back()
                await page.wait_for_timeout(500)
                url_back = page.url
                self.assertIn("#story", url_back, "URL should contain #story after going back")

                # Go Forward
                await page.go_forward()
                await page.wait_for_timeout(500)
                url_forward = page.url
                self.assertIn("#gameplay", url_forward, "URL should contain #gameplay after going forward")
            finally:
                await self._close(pw, browser, context, page)
        self._run_async(_check())

    def test_current_section_no_duplicate_history(self):
        """Clicking the current section should not add a duplicate history entry."""
        async def _check():
            pw, browser, context, page = await self._open_page(1280, 800)
            try:
                await self._navigate(page)
                await page.evaluate("window.scrollTo(0, 0)")
                await page.wait_for_timeout(100)

                initial_url = page.url
                initial_history_length = await page.evaluate("() => window.history.length")

                story_link = page.locator('#main-nav a[href="#story"]')
                await story_link.click()
                await page.wait_for_timeout(500)

                # First click should set #story and add one history entry
                url_after_first = page.url
                self.assertIn("#story", url_after_first, "URL should contain #story after first Story click")
                history_after_first = await page.evaluate("() => window.history.length")
                self.assertEqual(history_after_first, initial_history_length + 1, "First click should add one history entry")

                # Click Story again
                await story_link.click()
                await page.wait_for_timeout(500)

                # Second click should retain #story without increasing history length
                url_after_second = page.url
                self.assertIn("#story", url_after_second, "URL should still contain #story after second Story click")
                history_after_second = await page.evaluate("() => window.history.length")
                self.assertEqual(history_after_second, history_after_first, "Second click should not add a duplicate history entry")

                # Navigate back - should go to the original URL without fragment
                await page.go_back()
                await page.wait_for_timeout(300)
                url_after_back = page.url
                self.assertEqual(url_after_back, initial_url, "Back after a repeated Story click should return to the original URL")

                # Navigate forward - should return to #story
                await page.go_forward()
                await page.wait_for_timeout(300)
                url_after_forward = page.url
                self.assertIn("#story", url_after_forward, "Forward should return to #story")
            finally:
                await self._close(pw, browser, context, page)
        self._run_async(_check())

    def test_invalid_fragment_no_error(self):
        """Loading page with an invalid fragment should not cause script errors."""
        async def _check():
            errors = []
            pw, browser, context, page = await self._open_page(1280, 800)
            try:
                page.on("console", lambda msg: errors.append(msg) if msg.type == "error" else None)
                page.on("pageerror", lambda err: errors.append(err))
                await page.goto(self.html_url + "#nonexistent-section", wait_until="domcontentloaded")
                await page.wait_for_timeout(300)

                console_errors = [str(e) for e in errors if hasattr(e, 'type') and e.type == 'error']
                page_errors = [str(e) for e in errors if not hasattr(e, 'type')]
                self.assertEqual(
                    console_errors,
                    [],
                    f"No console errors should occur with invalid fragment. Got: {console_errors}",
                )
                self.assertEqual(
                    page_errors,
                    [],
                    f"No uncaught exceptions should occur with invalid fragment. Got: {page_errors}",
                )
            finally:
                await self._close(pw, browser, context, page)
        self._run_async(_check())

    def test_empty_fragment_no_error(self):
        """Loading page with an empty fragment (#) should not cause script errors."""
        async def _check():
            errors = []
            pw, browser, context, page = await self._open_page(1280, 800)
            try:
                page.on("console", lambda msg: errors.append(msg) if msg.type == "error" else None)
                page.on("pageerror", lambda err: errors.append(err))
                await page.goto(self.html_url + "#", wait_until="domcontentloaded")
                await page.wait_for_timeout(300)

                console_errors = [str(e) for e in errors if hasattr(e, 'type') and e.type == 'error']
                page_errors = [str(e) for e in errors if not hasattr(e, 'type')]
                self.assertEqual(
                    console_errors,
                    [],
                    f"No console errors should occur with empty fragment. Got: {console_errors}",
                )
                self.assertEqual(
                    page_errors,
                    [],
                    f"No uncaught exceptions should occur with empty fragment. Got: {page_errors}",
                )
            finally:
                await self._close(pw, browser, context, page)
        self._run_async(_check())

    def test_navigation_toggle_desktop_tablet(self):
        """Nav toggle should be hidden on desktop and tablet viewports; nav links visible."""
        async def _check():
            for width, height in [(1280, 800), (768, 1024)]:
                pw, browser, context, page = await self._open_page(width, height)
                try:
                    await self._navigate(page)
                    await page.wait_for_timeout(100)

                    # Assert exactly one toggle button exists
                    toggle_count = await page.locator('#nav-toggle').count()
                    self.assertEqual(toggle_count, 1, f"At {width}x{height} exactly one #nav-toggle should exist")

                    # Assert toggle is hidden (display: none)
                    toggle = page.locator('#nav-toggle')
                    display = await toggle.evaluate("el => window.getComputedStyle(el).display")
                    self.assertEqual(
                        display, 'none',
                        f"At {width}x{height} #nav-toggle computed display should be 'none', got '{display}'",
                    )

                    # Assert navigation links are visible
                    nav_links = page.locator('.nav-links a')
                    count = await nav_links.count()
                    self.assertGreater(count, 0, f"At {width}x{height} nav-links should have links")
                    for i in range(count):
                        self.assertTrue(
                            await nav_links.nth(i).is_visible(),
                            f"At {width}x{height} nav-link {i} should be visible",
                        )
                finally:
                    await self._close(pw, browser, context, page)
        self._run_async(_check())

    def test_navigation_toggle_short_mobile(self):
        """Nav toggle should be visible at 375x320; clicking opens/closes navigation."""
        async def _check():
            pw, browser, context, page = await self._open_page(375, 320)
            try:
                await self._navigate(page)
                await page.wait_for_timeout(100)

                # Assert toggle is visible
                toggle = page.locator('#nav-toggle')
                self.assertTrue(await toggle.is_visible(), "#nav-toggle should be visible at 375x320")
                display = await toggle.evaluate("el => window.getComputedStyle(el).display")
                self.assertNotEqual(display, 'none', "#nav-toggle computed display should not be 'none' at 375x320")

                # Assert aria-expanded starts as false
                aria_expanded = await toggle.get_attribute('aria-expanded')
                self.assertEqual(aria_expanded, 'false', "aria-expanded should start as 'false'")

                # Assert nav links are hidden initially
                nav_links = page.locator('.nav-links')
                self.assertFalse(
                    await nav_links.is_visible(),
                    "Nav links should be hidden initially at 375x320",
                )

                # Click to open
                await toggle.click()
                await page.wait_for_timeout(200)

                # Assert aria-expanded is now true
                aria_expanded = await toggle.get_attribute('aria-expanded')
                self.assertEqual(aria_expanded, 'true', "aria-expanded should be 'true' after opening")

                # Assert nav links are now visible
                self.assertTrue(
                    await nav_links.is_visible(),
                    "Nav links should be visible after clicking toggle",
                )

                # Click again to close
                await toggle.click()
                await page.wait_for_timeout(200)

                # Assert aria-expanded is back to false
                aria_expanded = await toggle.get_attribute('aria-expanded')
                self.assertEqual(aria_expanded, 'false', "aria-expanded should be 'false' after closing")

                # Assert nav links are hidden again
                self.assertFalse(
                    await nav_links.is_visible(),
                    "Nav links should be hidden after closing toggle",
                )
            finally:
                await self._close(pw, browser, context, page)
        self._run_async(_check())

    def test_navigation_toggle_click_link_closes_menu(self):
        """Clicking a nav link while menu is open should close the menu."""
        async def _check():
            pw, browser, context, page = await self._open_page(375, 320)
            try:
                await self._navigate(page)
                await page.wait_for_timeout(100)

                # Open the menu
                toggle = page.locator('#nav-toggle')
                await toggle.click()
                await page.wait_for_timeout(200)

                # Verify menu is open
                nav_links = page.locator('.nav-links')
                self.assertTrue(await nav_links.is_visible(), "Nav links should be visible after opening")

                # Click a nav link (e.g., Story)
                story_link = page.locator('#main-nav a[href="#story"]')
                await story_link.click()
                await page.wait_for_timeout(300)

                # Verify menu is closed
                self.assertFalse(
                    await nav_links.is_visible(),
                    "Nav links should be hidden after clicking a link",
                )

                # Verify aria-expanded is false
                aria_expanded = await toggle.get_attribute('aria-expanded')
                self.assertEqual(aria_expanded, 'false', "aria-expanded should be 'false' after clicking a link")
            finally:
                await self._close(pw, browser, context, page)
        self._run_async(_check())

    def test_mobile_navigation_story_visible_at_375x375(self):
        """At 375x375, clicking Story from the hamburger menu should scroll to the
        Story heading which remains fully visible within the viewport, below the header."""
        async def _check():
            pw, browser, context, page = await self._open_page(375, 375)
            try:
                await self._navigate(page)
                await page.wait_for_timeout(100)

                # Open the hamburger menu
                toggle = page.locator('#nav-toggle')
                self.assertTrue(await toggle.is_visible(), "#nav-toggle should be visible at 375x375")
                await toggle.click()
                await page.wait_for_timeout(300)

                # Verify menu is open
                nav_links = page.locator('.nav-links')
                self.assertTrue(
                    await nav_links.is_visible(),
                    "Nav links should be visible after opening hamburger menu",
                )

                # Click the Story link
                story_link = page.locator('#main-nav a[href="#story"]')
                await story_link.click()
                # Wait for scroll and any transition to settle
                await page.wait_for_timeout(800)

                # Verify menu is closed
                self.assertFalse(
                    await nav_links.is_visible(),
                    "Nav links should be hidden after clicking a link",
                )

                # Verify aria-expanded is false
                aria_expanded = await toggle.get_attribute('aria-expanded')
                self.assertEqual(
                    aria_expanded, 'false',
                    "aria-expanded should be 'false' after clicking a link",
                )

                # Verify the Story heading is fully inside the viewport
                story_heading = page.locator('#story h2')
                self.assertTrue(
                    await story_heading.is_visible(),
                    "Story h2 heading should be visible",
                )

                # Get the bounding box of the heading and the viewport
                heading_box = await story_heading.bounding_box()
                viewport_height = 375

                # The heading must have a positive height
                self.assertGreater(
                    heading_box['height'], 0,
                    f"Story heading should have a positive height, got height={heading_box['height']}",
                )

                # The heading must be below the top of the viewport (below any header)
                # and its top must be within the viewport
                self.assertGreaterEqual(
                    heading_box['y'], 0,
                    f"Story heading should be below or at the viewport top, got y={heading_box['y']}",
                )
                self.assertLessEqual(
                    heading_box['y'],
                    viewport_height,
                    f"Story heading top should be within the viewport. "
                    f"Heading top y={heading_box['y']}, "
                    f"viewport height={viewport_height}",
                )
                # The heading must be fully inside the viewport (bottom within viewport)
                self.assertLessEqual(
                    heading_box['y'] + heading_box['height'],
                    viewport_height,
                    f"Story heading should be fully within the viewport. "
                    f"Heading bottom y={heading_box['y'] + heading_box['height']}, "
                    f"viewport height={viewport_height}",
                )
            finally:
                await self._close(pw, browser, context, page)
        self._run_async(_check())

    def test_history_back_collapses_mobile_menu(self):
        """Navigating back with the mobile menu expanded should collapse the menu
        and scroll the target heading below the collapsed header."""
        async def _check():
            pw, browser, context, page = await self._open_page(375, 375)
            try:
                # Navigate to Overview first
                await self._navigate(page)
                await page.wait_for_timeout(100)

                # Open the hamburger menu to access the Story link
                toggle = page.locator('#nav-toggle')
                await toggle.click()
                await page.wait_for_timeout(300)

                # Navigate to Story via the nav link
                story_link = page.locator('#main-nav a[href="#story"]')
                await story_link.click()
                await page.wait_for_timeout(500)

                # Verify we are on the Story section
                self.assertIn("#story", page.url, "URL should contain #story after clicking Story")

                # Scroll to the page top
                await page.evaluate("window.scrollTo(0, 0)")
                await page.wait_for_timeout(100)

                # Expand the hamburger menu
                toggle = page.locator('#nav-toggle')
                await toggle.click()
                await page.wait_for_timeout(300)

                # Verify menu is open
                nav_links = page.locator('.nav-links')
                self.assertTrue(
                    await nav_links.is_visible(),
                    "Nav links should be visible after opening hamburger menu",
                )
                aria_expanded = await toggle.get_attribute('aria-expanded')
                self.assertEqual(
                    aria_expanded, 'true',
                    "aria-expanded should be 'true' after opening",
                )

                # Trigger browser Back
                await page.go_back()
                await page.wait_for_timeout(800)

                # Verify the fragment identifies Overview (no fragment)
                self.assertNotIn("#story", page.url, "URL should not contain #story after going back")

                # Verify the menu is closed
                self.assertFalse(
                    await nav_links.is_visible(),
                    "Nav links should be hidden after going back",
                )

                # Verify aria-expanded is false
                aria_expanded = await toggle.get_attribute('aria-expanded')
                self.assertEqual(
                    aria_expanded, 'false',
                    "aria-expanded should be 'false' after going back",
                )

                # Verify the Overview heading is visible below the collapsed header and within the viewport
                overview_heading = page.locator('#overview h2')
                self.assertTrue(
                    await overview_heading.is_visible(),
                    "Overview h2 heading should be visible",
                )

                heading_box = await overview_heading.bounding_box()
                header = page.locator("#main-header")
                header_rect = await header.evaluate("el => el.getBoundingClientRect()")
                header_bottom = header_rect["bottom"]
                viewport_height = await page.evaluate("window.innerHeight")

                # The heading should be below the collapsed header
                self.assertGreaterEqual(
                    heading_box['y'],
                    header_bottom - 5,
                    f"Overview heading should be below the collapsed header. "
                    f"Heading top y={heading_box['y']}, header_bottom={header_bottom}",
                )

                # The heading should be within the viewport
                self.assertLessEqual(
                    heading_box['y'],
                    viewport_height,
                    f"Overview heading top should be within the viewport. "
                    f"Heading top y={heading_box['y']}, viewport height={viewport_height}",
                )

                # The heading should be fully inside the viewport
                self.assertLessEqual(
                    heading_box['y'] + heading_box['height'],
                    viewport_height,
                    f"Overview heading should be fully within the viewport. "
                    f"Heading bottom y={heading_box['y'] + heading_box['height']}, "
                    f"viewport height={viewport_height}",
                )
            finally:
                await self._close(pw, browser, context, page)
        self._run_async(_check())


if __name__ == "__main__":
    unittest.main()
