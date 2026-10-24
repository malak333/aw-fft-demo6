#!/usr/bin/env python3
"""Automated tests for the Final Fantasy Tactics website.

Validates HTML structure, accessibility, content accuracy, and responsive design.
Run with: python test_website.py
"""

import html.parser
import os
import re
import sys
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INDEX_PATH = BASE_DIR / "index.html"
STYLES_PATH = BASE_DIR / "styles.css"
SCRIPT_PATH = BASE_DIR / "script.js"


class TestFilesExist(unittest.TestCase):
    """Verify all required project files exist."""

    def test_index_html_exists(self):
        self.assertTrue(INDEX_PATH.exists(), "index.html should exist")

    def test_styles_css_exists(self):
        self.assertTrue(STYLES_PATH.exists(), "styles.css should exist")

    def test_script_js_exists(self):
        self.assertTrue(SCRIPT_PATH.exists(), "script.js should exist")

    def test_readme_exists(self):
        readme = BASE_DIR / "README.md"
        self.assertTrue(readme.exists(), "README.md should exist")


class TestHTMLStructure(unittest.TestCase):
    """Validate the HTML document structure."""

    @classmethod
    def setUpClass(cls):
        cls.html = INDEX_PATH.read_text(encoding="utf-8")

    def test_doctype_present(self):
        self.assertTrue(
            self.html.strip().startswith("<!DOCTYPE html>"),
            "Document should start with <!DOCTYPE html>",
        )

    def test_html_lang_attribute(self):
        match = re.search(r'<html[^>]*\blang="([^"]+)"', self.html)
        self.assertIsNotNone(match, '<html> should have a lang attribute')
        self.assertEqual(match.group(1), "en", 'lang should be "en"')

    def test_charset_meta(self):
        self.assertIn(
            'charset="UTF-8"',
            self.html,
            'Meta charset should be UTF-8',
        )

    def test_viewport_meta(self):
        self.assertIn(
            'name="viewport"',
            self.html,
            "Viewport meta tag should be present",
        )

    def test_title_present(self):
        match = re.search(r'<title>(.*?)</title>', self.html, re.DOTALL)
        self.assertIsNotNone(match, "<title> tag should be present")
        title = match.group(1).strip()
        self.assertTrue(
            len(title) > 0 and len(title) < 70,
            f"Title should be non-empty and under 70 chars, got: '{title}'",
        )
        self.assertIn(
            "Final Fantasy Tactics",
            title,
            "Title should mention Final Fantasy Tactics",
        )

    def test_stylesheet_link(self):
        self.assertIn(
            'href="styles.css"',
            self.html,
            "Should link to styles.css",
        )

    def test_script_link(self):
        self.assertIn(
            'src="script.js"',
            self.html,
            "Should link to script.js",
        )

    def test_semantic_main_element(self):
        self.assertIn(
            "<main", self.html, "Should use <main> element for main content"
        )

    def test_semantic_header_element(self):
        self.assertIn(
            "<header", self.html, "Should use <header> element"
        )

    def test_semantic_footer_element(self):
        self.assertIn(
            "<footer", self.html, "Should use <footer> element"
        )

    def test_semantic_nav_element(self):
        self.assertIn(
            "<nav", self.html, "Should use <nav> element"
        )

    def test_no_broken_tags(self):
        """Check for obviously unclosed or mismatched tags."""
        open_tags = re.findall(r'<(\w+)[^>]*?(?<!/)>', self.html)
        close_tags = re.findall(r'</(\w+)>', self.html)
        # Self-closing tags that don't need closing
        void_elements = {
            "meta", "link", "img", "br", "hr", "input", "area", "base",
            "col", "embed", "param", "source", "track", "wbr",
        }
        unclosed = []
        for tag in open_tags:
            if tag.lower() not in void_elements and tag.lower() not in close_tags:
                unclosed.append(tag)
        self.assertEqual(
            unclosed, [],
            f"Potentially unclosed tags: {unclosed}",
        )


class TestAccessibility(unittest.TestCase):
    """Validate accessibility features."""

    @classmethod
    def setUpClass(cls):
        cls.html = INDEX_PATH.read_text(encoding="utf-8")

    def test_aria_labels_present(self):
        """Check that navigation has an aria-label."""
        self.assertIn(
            'aria-label',
            self.html,
            "Should have at least one aria-label attribute",
        )

    def test_heading_hierarchy(self):
        """Verify heading levels are in order (h1 -> h2 -> h3)."""
        headings = re.findall(r'<h([1-6])[^>]*>(.*?)</h\1>', self.html, re.DOTALL)
        if len(headings) == 0:
            self.fail("No headings found in the document")

        prev_level = 0
        for level_str, _ in headings:
            level = int(level_str)
            # Headings should not skip more than one level
            if level > prev_level + 1 and prev_level > 0:
                self.fail(
                    f"Heading level skipped: h{prev_level} -> h{level}. "
                    "Headings should not skip levels."
                )
            prev_level = level

        # First heading should be h1
        self.assertEqual(
            int(headings[0][0]), 1,
            "First heading should be <h1>",
        )

    def test_single_h1(self):
        """There should be exactly one h1 element."""
        h1_count = len(re.findall(r'<h1[^>]*>', self.html))
        self.assertEqual(
            h1_count, 1,
            "There should be exactly one <h1> element",
        )

    def test_nav_has_aria_label(self):
        """The <nav> element should have an aria-label."""
        nav_match = re.search(
            r'<nav[^>]*aria-label="([^"]+)"[^>]*>',
            self.html,
        )
        self.assertIsNotNone(
            nav_match,
            "<nav> element should have an aria-label attribute",
        )

    def test_focus_indicators_in_css(self):
        """CSS should define focus indicators."""
        css = STYLES_PATH.read_text(encoding="utf-8")
        self.assertIn(
            ":focus", css,
            "CSS should define :focus styles for accessibility",
        )

    def test_no_empty_links(self):
        """Check that all <a> tags have non-empty text content."""
        links = re.findall(r'<a[^>]*>(.*?)</a>', self.html, re.DOTALL)
        for i, link_text in enumerate(links):
            stripped = link_text.strip()
            self.assertTrue(
                len(stripped) > 0,
                f"Link #{i + 1} has empty text content",
            )

    def test_no_empty_images(self):
        """Check that all <img> tags have alt attributes."""
        img_tags = re.findall(r'<img[^>]*>', self.html)
        for img in img_tags:
            self.assertIn(
                'alt=', img,
                "All <img> tags should have an alt attribute",
            )


class TestContent(unittest.TestCase):
    """Validate content accuracy and completeness."""

    @classmethod
    def setUpClass(cls):
        cls.html = INDEX_PATH.read_text(encoding="utf-8")

    def _extract_section(self, section_id):
        """Extract the text content of a section by its ID."""
        pattern = r'id="' + section_id + r'"[^>]*>(.*?)</section>'
        match = re.search(pattern, self.html, re.DOTALL)
        if match:
            # Strip HTML tags to get plain text
            text = re.sub(r'<[^>]+>', ' ', match.group(1))
            return text
        return ""

    def test_section_overview_exists(self):
        self.assertIn(
            'id="overview"', self.html,
            "Should have an 'overview' section",
        )

    def test_section_story_exists(self):
        self.assertIn(
            'id="story"', self.html,
            "Should have a 'story' section",
        )

    def test_section_gameplay_exists(self):
        self.assertIn(
            'id="gameplay"', self.html,
            "Should have a 'gameplay' section",
        )

    def test_section_jobs_exists(self):
        self.assertIn(
            'id="jobs"', self.html,
            "Should have a 'jobs' section",
        )

    def test_section_music_exists(self):
        self.assertIn(
            'id="music"', self.html,
            "Should have a 'music' section",
        )

    def test_section_legacy_exists(self):
        self.assertIn(
            'id="legacy"', self.html,
            "Should have a 'legacy' section",
        )

    def test_navigation_links_to_sections(self):
        """All nav links should point to existing section IDs."""
        nav_links = re.findall(
            r'<a\s+href="#([^"]+)"', self.html
        )
        for link_id in nav_links:
            self.assertIn(
                f'id="{link_id}"', self.html,
                f"Nav link to '#{link_id}' should have a matching section",
            )

    def test_story_mentions_ramza(self):
        self.assertIn(
            "Ramza", self.html,
            "Story section should mention Ramza Beoulve",
        )

    def test_story_mentions_delita(self):
        self.assertIn(
            "Delita", self.html,
            "Story section should mention Delita Heiral",
        )

    def test_story_mentions_ivalice(self):
        self.assertIn(
            "Ivalice", self.html,
            "Story section should mention the world of Ivalice",
        )

    def test_gameplay_mentions_grid(self):
        self.assertIn(
            "grid", self.html.lower(),
            "Gameplay section should mention grid-based combat",
        )

    def test_job_system_mentioned(self):
        self.assertIn(
            "job", self.html.lower(),
            "Should discuss the job system",
        )

    def test_license_board_not_in_fft(self):
        """License Board is a Final Fantasy XII mechanic, not FFT."""
        self.assertNotIn(
            "License Board", self.html,
            "FFT should not mention the License Board mechanic (that is from FF XII)",
        )

    def test_music_section_mentions_composer(self):
        self.assertIn(
            "Sakimoto", self.html,
            "Music section should mention composer Hitoshi Sakimoto",
        )

    def test_release_date_japan(self):
        self.assertIn(
            "1997", self.html,
            "Should mention the 1997 Japanese release",
        )

    def test_release_date_na(self):
        self.assertIn(
            "1998", self.html,
            "Should mention the 1998 North American release",
        )

    def test_playstation_mentioned(self):
        self.assertIn(
            "PlayStation", self.html,
            "Should mention the PlayStation platform",
        )

    def test_square_mentioned(self):
        self.assertIn(
            "Square", self.html,
            "Should mention Square as the developer/publisher",
        )

    def test_publisher_attribution_correct(self):
        """Square published the Japanese release; Sony Computer Entertainment published the North American release."""
        overview_section = self._extract_section("overview")
        # Square must be identified as developer
        self.assertIn(
            "developed by Square",
            overview_section,
            "Square should be identified as the developer",
        )
        # Square must be identified as Japanese publisher
        self.assertIn(
            "Square published",
            overview_section,
            "Square should be identified as the Japanese publisher",
        )
        # Sony Computer Entertainment must be identified as North American publisher
        self.assertIn(
            "Sony Computer Entertainment",
            overview_section,
            "Sony Computer Entertainment should be identified as the North American publisher",
        )
        # Verify the regional mapping: Square -> Japan, Sony -> North America
        square_idx = overview_section.find("Square published")
        sony_idx = overview_section.find("Sony Computer Entertainment")
        self.assertGreater(
            square_idx, -1,
            "Square published reference must exist",
        )
        self.assertGreater(
            sony_idx, -1,
            "Sony Computer Entertainment reference must exist",
        )
        # The Square published reference should mention Japan
        square_context = overview_section[square_idx:square_idx + 200]
        self.assertIn(
            "Japan",
            square_context,
            "Square's publishing should be associated with Japan",
        )
        # The Sony reference should mention North America
        sony_context = overview_section[sony_idx:sony_idx + 200]
        self.assertIn(
            "North America",
            sony_context,
            "Sony Computer Entertainment's publishing should be associated with North America",
        )

    def test_publisher_attribution_not_sole_square(self):
        """The overview must not attribute publication solely to Square."""
        overview_section = self._extract_section("overview")
        self.assertNotIn(
            "published by Square for the Sony PlayStation",
            overview_section,
            "Overview must not say 'published by Square' without distinguishing regional publishers",
        )

    def test_readme_publisher_attribution_correct(self):
        """README must correctly distinguish Square (Japan) and Sony Computer Entertainment (NA)."""
        readme = (BASE_DIR / "README.md").read_text(encoding="utf-8")
        # Square must be identified as developer
        self.assertIn(
            "developed by Square",
            readme,
            "README should identify Square as the developer",
        )
        # Square must be identified as Japanese publisher
        self.assertIn(
            "Square published",
            readme,
            "README should identify Square as the Japanese publisher",
        )
        # Sony Computer Entertainment must be identified as North American publisher
        self.assertIn(
            "Sony Computer Entertainment",
            readme,
            "README should identify Sony Computer Entertainment as the North American publisher",
        )
        # Verify regional mapping in README
        square_idx = readme.find("Square published")
        sony_idx = readme.find("Sony Computer Entertainment")
        self.assertGreater(square_idx, -1, "Square published reference must exist in README")
        self.assertGreater(sony_idx, -1, "Sony Computer Entertainment reference must exist in README")
        square_context = readme[square_idx:square_idx + 200]
        self.assertIn(
            "Japan",
            square_context,
            "README should associate Square with Japan",
        )
        sony_context = readme[sony_idx:sony_idx + 200]
        self.assertIn(
            "North America",
            sony_context,
            "README should associate Sony Computer Entertainment with North America",
        )

    def test_war_of_lions_mentioned(self):
        """Should distinguish original from the PSP remake."""
        self.assertIn(
            "War of the Lions", self.html,
            "Should mention the PSP remake for context",
        )

    def test_no_external_image_dependencies(self):
        """The page should work without external images."""
        img_tags = re.findall(r'<img[^>]*src="([^"]+)"[^>]*>', self.html)
        external = [src for src in img_tags if src.startswith("http")]
        self.assertEqual(
            external, [],
            "Should not depend on external images",
        )

    def test_ramza_is_third_son(self):
        """Ramza is the third son of House Beoulve, after Dycedarg and Zalbag."""
        story_section = self._extract_section("story")
        self.assertIn(
            "third son",
            story_section.lower(),
            "Ramza should be described as the third son of House Beoulve",
        )
        self.assertNotIn(
            "second son",
            story_section.lower(),
            "Ramza should NOT be described as the second son",
        )

    def test_story_mentions_brothers(self):
        """Story should mention Ramza's older brothers Dycedarg and Zalbag."""
        story_section = self._extract_section("story")
        self.assertIn(
            "Dycedarg",
            story_section,
            "Story should mention Dycedarg",
        )
        self.assertIn(
            "Zalbag",
            story_section,
            "Story should mention Zalbag",
        )

    def test_break_system_correct(self):
        """Break system should reference Weapon Break / Armor Break skills, not elemental affinity."""
        gameplay_section = self._extract_section("gameplay")
        self.assertIn(
            "Weapon Break",
            gameplay_section,
            "Gameplay should mention Weapon Break ability",
        )
        self.assertIn(
            "Armor Break",
            gameplay_section,
            "Gameplay should mention Armor Break ability",
        )
        # Verify that elemental affinity does NOT cause equipment to break
        self.assertNotIn(
            "elemental weapons can break",
            gameplay_section.lower(),
            "Elemental affinity should NOT be described as causing equipment to break",
        )

    def test_no_red_mage_in_playable_jobs(self):
        """Red Mage is not a playable job in the PS1 FFT."""
        jobs_section = self._extract_section("jobs")
        self.assertNotIn(
            "Red Mage",
            jobs_section,
            "Red Mage should not appear in the job list",
        )

    def test_no_paladin_in_playable_jobs(self):
        """Paladin is not a playable job in the PS1 FFT."""
        jobs_section = self._extract_section("jobs")
        self.assertNotIn(
            "Paladin",
            jobs_section,
            "Paladin should not appear in the job list",
        )

    def test_no_ronin_in_playable_jobs(self):
        """Ronin is not a playable job in the PS1 FFT."""
        jobs_section = self._extract_section("jobs")
        self.assertNotIn(
            "Ronin",
            jobs_section,
            "Ronin should not appear in the job list",
        )

    def test_no_blue_mage_in_playable_jobs(self):
        """Blue Mage is not a playable job in the PS1 FFT."""
        jobs_section = self._extract_section("jobs")
        self.assertNotIn(
            "Blue Mage",
            jobs_section,
            "Blue Mage should not appear in the job list",
        )

    def test_time_mage_in_unlockable_jobs(self):
        """Time Mage should be listed as an unlockable job, not character-exclusive."""
        jobs_section = self._extract_section("jobs")
        self.assertIn(
            "Time Mage",
            jobs_section,
            "Time Mage should appear in the job list",
        )

    def test_dancer_in_unlockable_jobs(self):
        """Dancer should be listed as an unlockable job."""
        jobs_section = self._extract_section("jobs")
        self.assertIn(
            "Dancer",
            jobs_section,
            "Dancer should appear in the job list",
        )

    def test_summoner_in_unlockable_jobs(self):
        """Summoner should be listed as an unlockable job."""
        jobs_section = self._extract_section("jobs")
        self.assertIn(
            "Summoner",
            jobs_section,
            "Summoner should appear in the job list",
        )

    def test_standard_jobs_present(self):
        """Verify key standard PS1 jobs are present in the job list."""
        jobs_section = self._extract_section("jobs")
        required_jobs = ["Squire", "Knight", "Archer", "Monk", "Wizard", "Thief", "Samurai", "Ninja", "Geomancer", "Chemist", "Lancer", "Bard", "Oracle", "Mediator", "Calculator", "Mime", "Priest", "Summoner", "Time Mage", "Dancer"]
        for job in required_jobs:
            self.assertIn(
                job,
                jobs_section,
                f"Standard job '{job}' should be listed",
            )

    def test_lancer_prerequisite_is_thief_level_3(self):
        """Lancer requires Thief job level 3, not Squire level."""
        jobs_section = self._extract_section("jobs")
        self.assertIn(
            "Thief job level 3",
            jobs_section,
            "Job Advancement should state that Lancer requires Thief job level 3",
        )
        # Ensure the incorrect Squire-only prerequisite is not stated
        self.assertNotIn(
            "Squire job", jobs_section.lower().split("lancer")[0] if "lancer" in jobs_section.lower() else "",
            "Lancer prerequisite should not mention Squire job level",
        )

    def test_jp_does_not_purchase_stats(self):
        """JP should not be described as purchasing stat boosts."""
        jobs_section = self._extract_section("jobs")
        self.assertNotIn(
            "stat boosts",
            jobs_section.lower(),
            "JP should not be described as purchasing stat boosts",
        )
        # Verify that stats grow through leveling, not JP
        self.assertIn(
            "stats grow through leveling",
            jobs_section,
            "Jobs section should state that stats grow through leveling",
        )
        self.assertIn(
            "not through JP purchases",
            jobs_section,
            "Jobs section should clarify that stats do not grow through JP purchases",
        )
        # Verify that stats grow through leveling, not JP
        self.assertIn(
            "leveling",
            jobs_section.lower(),
            "Jobs section should mention that stats grow through leveling",
        )

    def test_no_ballad_of_the_fox(self):
        """Ballad of the Fox is not on the FFT soundtrack."""
        music_section = self._extract_section("music")
        self.assertNotIn(
            "Ballad of the Fox",
            music_section,
            "Ballad of the Fox should not appear in the soundtrack list",
        )

    def test_no_march_of_the_lions(self):
        """March of the Lions is not on the FFT soundtrack."""
        music_section = self._extract_section("music")
        self.assertNotIn(
            "March of the Lions",
            music_section,
            "March of the Lions should not appear in the soundtrack list",
        )

    def test_no_theme_of_love_in_music(self):
        """Theme of Love is not on the original FFT soundtrack."""
        music_section = self._extract_section("music")
        self.assertNotIn(
            "Theme of Love",
            music_section,
            "Theme of Love should not appear in the soundtrack list",
        )

    def test_verified_tracks_present(self):
        """Verify that known FFT soundtrack tracks are listed."""
        music_section = self._extract_section("music")
        self.assertIn(
            "Trisection",
            music_section,
            "Trisection should be listed as a soundtrack track",
        )
        self.assertIn(
            "Antipyretic",
            music_section,
            "Antipyretic should be listed as a soundtrack track",
        )
        self.assertIn(
            "Battle on the Bridge",
            music_section,
            "Battle on the Bridge should be listed as a soundtrack track",
        )


class TestCSS(unittest.TestCase):
    """Validate CSS quality and responsiveness."""

    @classmethod
    def setUpClass(cls):
        cls.css = STYLES_PATH.read_text(encoding="utf-8")

    def test_media_queries_present(self):
        """Should have responsive media queries."""
        media_count = len(re.findall(r'@media', self.css))
        self.assertGreater(
            media_count, 0,
            "CSS should contain at least one @media query",
        )

    def test_mobile_breakpoint(self):
        """Should have a mobile breakpoint."""
        self.assertIn(
            "max-width",
            self.css,
            "CSS should define max-width media queries for mobile",
        )

    def test_box_sizing_reset(self):
        """Should include a box-sizing reset."""
        self.assertIn(
            "box-sizing",
            self.css,
            "CSS should reset box-sizing for consistent layout",
        )

    def test_print_styles(self):
        """Should include print styles."""
        self.assertIn(
            "@media print",
            self.css,
            "CSS should include print styles",
        )

    def test_no_important_overuse(self):
        """Should not overuse !important."""
        important_count = len(re.findall(r'!important', self.css))
        self.assertLessEqual(
            important_count, 3,
            f"CSS should not use !important more than 3 times (found {important_count})",
        )


class TestJavaScript(unittest.TestCase):
    """Validate JavaScript quality."""

    @classmethod
    def setUpClass(cls):
        cls.js = SCRIPT_PATH.read_text(encoding="utf-8")

    def test_dom_ready_wrapper(self):
        """Should wrap code in DOMContentLoaded or similar."""
        self.assertTrue(
            "DOMContentLoaded" in self.js or "addEventListener" in self.js,
            "JS should use DOMContentLoaded or addEventListener for initialization",
        )

    def test_no_alert_or_confirm(self):
        """Should not use alert() or confirm()."""
        self.assertNotIn(
            "alert(", self.js,
            "Should not use alert()",
        )
        self.assertNotIn(
            "confirm(", self.js,
            "Should not use confirm()",
        )

    def test_no_inline_event_handlers(self):
        """JS file should not contain HTML-like inline handlers."""
        self.assertNotIn(
            "onclick=", self.js,
            "JS should not contain inline event handlers",
        )


class TestREADME(unittest.TestCase):
    """Validate README content."""

    @classmethod
    def setUpClass(cls):
        cls.readme = (BASE_DIR / "README.md").read_text(encoding="utf-8")

    def test_readme_has_launch_instructions(self):
        self.assertIn(
            "index.html", self.readme,
            "README should mention how to open index.html",
        )

    def test_readme_has_file_list(self):
        self.assertIn(
            "styles.css", self.readme,
            "README should list styles.css",
        )

    def test_readme_has_about_section(self):
        self.assertIn(
            "About", self.readme,
            "README should have an 'About' section",
        )


class TestNoConsoleErrors(unittest.TestCase):
    """Check for common issues that cause browser console errors."""

    @classmethod
    def setUpClass(cls):
        cls.html = INDEX_PATH.read_text(encoding="utf-8")

    def test_no_javascript_in_href(self):
        """Should not use javascript: in href attributes."""
        self.assertNotIn(
            "javascript:", self.html,
            "Should not use javascript: in href attributes",
        )

    def test_no_inline_styles(self):
        """Should not use inline style attributes (prefer CSS classes)."""
        inline_styles = re.findall(r'<[^>]+\bstyle="[^"]+"', self.html)
        self.assertEqual(
            inline_styles, [],
            "Should not use inline style attributes",
        )

    def test_no_deprecated_tags(self):
        """Should not use deprecated HTML tags."""
        deprecated = ["font", "center", "marquee", "blink", "strike"]
        for tag in deprecated:
            self.assertNotIn(
                f"<{tag}", self.html,
                f"Should not use deprecated <{tag}> tag",
            )


if __name__ == "__main__":
    unittest.main()
