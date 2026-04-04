"""
Unit tests for WordPress, Contentful, and Ghost integration scripts.

Tests pure logic functions — no API calls, no credentials needed.
Covers SEO field extraction, entry normalisation, SEO audit, and
SSRF protection for all three new CMS integrations.

Run: pytest test/unit/test_cms_scripts.py -v
"""

import importlib.util
import os
import sys
import unittest

# ── Load scripts without executing main() ────────────────────────────────────

def _load(name):
    path = os.path.join(
        os.path.dirname(__file__), '..', '..', 'skills', 'seo-analysis', 'scripts', name
    )
    spec = importlib.util.spec_from_file_location(name.replace('.py', ''), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


wp_fetch = _load('fetch_wordpress_content.py')
cf_fetch = _load('fetch_contentful_content.py')
ghost_fetch = _load('fetch_ghost_content.py')
cms_detect = _load('cms_detect.py')


# ── cms_detect.py ─────────────────────────────────────────────────────────────

class TestCmsDetectEnvParsing(unittest.TestCase):
    """load_env_file() correctly parses .env file lines."""

    def test_parses_simple_key_value(self):
        import tempfile, os
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("WP_URL=https://example.com\n")
            tmp = f.name
        try:
            result = cms_detect.load_env_file(tmp)
            self.assertEqual(result.get("WP_URL"), "https://example.com")
        finally:
            os.unlink(tmp)

    def test_strips_quotes(self):
        import tempfile, os
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write('WP_URL="https://quoted.com"\n')
            tmp = f.name
        try:
            result = cms_detect.load_env_file(tmp)
            self.assertEqual(result.get("WP_URL"), "https://quoted.com")
        finally:
            os.unlink(tmp)

    def test_skips_comments(self):
        import tempfile, os
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("# This is a comment\nWP_URL=https://example.com\n")
            tmp = f.name
        try:
            result = cms_detect.load_env_file(tmp)
            self.assertNotIn("# This is a comment", result)
            self.assertIn("WP_URL", result)
        finally:
            os.unlink(tmp)

    def test_skips_lines_without_equals(self):
        import tempfile, os
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("JUST_A_VALUE\nWP_URL=https://example.com\n")
            tmp = f.name
        try:
            result = cms_detect.load_env_file(tmp)
            self.assertNotIn("JUST_A_VALUE", result)
        finally:
            os.unlink(tmp)

    def test_missing_file_returns_empty(self):
        result = cms_detect.load_env_file("/nonexistent/.env")
        self.assertEqual(result, {})


# ── fetch_wordpress_content.py ────────────────────────────────────────────────

class TestWordPressExtractSeoFields(unittest.TestCase):
    """extract_seo_fields() pulls SEO data from Yoast and RankMath."""

    def _item(self, **kwargs):
        return kwargs

    def test_yoast_head_json_extracted(self):
        item = {
            "yoast_head_json": {
                "title": "SEO Title | Site",
                "description": "A 120-char meta description for this post.",
                "og_image": [{"url": "https://example.com/img.jpg"}],
                "og_title": "OG Title",
            }
        }
        result = wp_fetch.extract_seo_fields(item)
        self.assertEqual(result["meta_title"], "SEO Title | Site")
        self.assertEqual(result["meta_description"], "A 120-char meta description for this post.")
        self.assertTrue(result["has_meta_image"])
        self.assertTrue(result["has_meta_social"])

    def test_rank_math_meta_extracted_when_no_yoast(self):
        item = {
            "meta": {
                "rank_math_title": "RankMath Title",
                "rank_math_description": "RankMath description here.",
            }
        }
        result = wp_fetch.extract_seo_fields(item)
        self.assertEqual(result["meta_title"], "RankMath Title")
        self.assertEqual(result["meta_description"], "RankMath description here.")

    def test_yoast_takes_priority_over_rank_math(self):
        item = {
            "yoast_head_json": {"title": "Yoast Title", "description": "Yoast desc."},
            "meta": {"rank_math_title": "RankMath Title"},
        }
        result = wp_fetch.extract_seo_fields(item)
        self.assertEqual(result["meta_title"], "Yoast Title")

    def test_no_seo_plugin_returns_empty_meta_title(self):
        """Without Yoast or RankMath, meta_title should be empty — NOT the post title."""
        item = {
            "title": {"rendered": "Post Title"},
            "yoast_head_json": None,
        }
        result = wp_fetch.extract_seo_fields(item)
        self.assertEqual(result["meta_title"], "")
        self.assertEqual(result["meta_description"], "")

    def test_partial_yoast_missing_description(self):
        item = {"yoast_head_json": {"title": "Title Only"}}
        result = wp_fetch.extract_seo_fields(item)
        self.assertEqual(result["meta_title"], "Title Only")
        self.assertEqual(result["meta_description"], "")
        self.assertFalse(result["has_meta_image"])
        self.assertFalse(result["has_meta_social"])


class TestWordPressNormaliseEntry(unittest.TestCase):
    """normalise_entry() produces the shared CMS entry format."""

    def _wp_item(self, **overrides):
        base = {
            "id": 123,
            "slug": "hello-world",
            "title": {"rendered": "Hello World"},
            "date_gmt": "2024-01-15T10:00:00",
            "modified_gmt": "2024-02-01T12:00:00",
            "yoast_head_json": {
                "title": "Hello World | Blog",
                "description": "A short description for this post.",
            },
        }
        base.update(overrides)
        return base

    def test_document_id_is_string(self):
        result = wp_fetch.normalise_entry(self._wp_item())
        self.assertEqual(result["document_id"], "123")
        self.assertIsInstance(result["document_id"], str)

    def test_slug_extracted(self):
        result = wp_fetch.normalise_entry(self._wp_item())
        self.assertEqual(result["slug"], "hello-world")

    def test_seo_fields_extracted(self):
        result = wp_fetch.normalise_entry(self._wp_item())
        self.assertEqual(result["seo"]["meta_title"], "Hello World | Blog")
        self.assertFalse(result["missing_meta_title"])

    def test_missing_meta_title_flagged(self):
        item = self._wp_item()
        item.pop("yoast_head_json")
        result = wp_fetch.normalise_entry(item)
        self.assertTrue(result["missing_meta_title"])
        # Must not fall back to post title
        self.assertEqual(result["seo"]["meta_title"], "")

    def test_meta_title_too_long_flagged(self):
        item = self._wp_item()
        item["yoast_head_json"]["title"] = "A" * 61
        result = wp_fetch.normalise_entry(item)
        self.assertTrue(result["meta_title_too_long"])

    def test_meta_title_exactly_60_not_flagged(self):
        item = self._wp_item()
        item["yoast_head_json"]["title"] = "A" * 60
        result = wp_fetch.normalise_entry(item)
        self.assertFalse(result["meta_title_too_long"])

    def test_meta_description_too_short_flagged(self):
        item = self._wp_item()
        item["yoast_head_json"]["description"] = "Too short."
        result = wp_fetch.normalise_entry(item)
        self.assertTrue(result["meta_description_too_short"])

    def test_meta_description_too_long_flagged(self):
        item = self._wp_item()
        item["yoast_head_json"]["description"] = "A" * 161
        result = wp_fetch.normalise_entry(item)
        self.assertTrue(result["meta_description_too_long"])

    def test_meta_description_in_range_not_flagged(self):
        item = self._wp_item()
        item["yoast_head_json"]["description"] = "A" * 100
        result = wp_fetch.normalise_entry(item)
        self.assertFalse(result["meta_description_too_short"])
        self.assertFalse(result["meta_description_too_long"])


class TestWordPressSeoAudit(unittest.TestCase):
    """build_seo_audit() correctly counts SEO issues across entries."""

    def _entry(self, meta_title="", meta_description=""):
        tlen = len(meta_title)
        dlen = len(meta_description)
        return {
            "document_id": "1",
            "title": "Post",
            "slug": "post",
            "seo": {"meta_title": meta_title, "meta_description": meta_description},
            "missing_meta_title": not meta_title,
            "missing_meta_description": not meta_description,
            "meta_title_too_long": tlen > 60,
            "meta_description_too_long": dlen > 160,
            "meta_description_too_short": 0 < dlen < 70,
        }

    def test_complete_entry_counted(self):
        entries = [self._entry("Good Title", "A" * 100)]
        audit = wp_fetch.build_seo_audit(entries)
        self.assertEqual(audit["complete_seo"], 1)
        self.assertEqual(audit["missing_meta_title"], 0)

    def test_missing_title_counted(self):
        entries = [self._entry("", "A" * 100)]
        audit = wp_fetch.build_seo_audit(entries)
        self.assertEqual(audit["missing_meta_title"], 1)
        self.assertEqual(audit["complete_seo"], 0)

    def test_multiple_issues_on_same_entry_counts_once_in_complete(self):
        entries = [self._entry("", "")]  # missing both
        audit = wp_fetch.build_seo_audit(entries)
        self.assertEqual(audit["missing_meta_title"], 1)
        self.assertEqual(audit["missing_meta_description"], 1)
        self.assertEqual(audit["complete_seo"], 0)  # only 1 broken entry, not 2


# ── fetch_contentful_content.py ───────────────────────────────────────────────

class TestContentfulExtractSeoFields(unittest.TestCase):
    """extract_seo_fields() handles Contentful SEO patterns."""

    def test_direct_seo_fields_extracted(self):
        fields = {"seoTitle": "Contentful SEO Title", "seoDescription": "A good description here."}
        result = cf_fetch.extract_seo_fields(fields, {})
        self.assertEqual(result["meta_title"], "Contentful SEO Title")
        self.assertEqual(result["meta_description"], "A good description here.")

    def test_meta_title_field_names(self):
        for key in ("metaTitle", "seoTitle", "seo_title", "meta_title"):
            with self.subTest(key=key):
                fields = {key: f"Title via {key}"}
                result = cf_fetch.extract_seo_fields(fields, {})
                self.assertEqual(result["meta_title"], f"Title via {key}")

    def test_meta_description_field_names(self):
        for key in ("metaDescription", "seoDescription", "seo_description", "meta_description"):
            with self.subTest(key=key):
                fields = {key: f"Desc via {key}"}
                result = cf_fetch.extract_seo_fields(fields, {})
                self.assertEqual(result["meta_description"], f"Desc via {key}")

    def test_linked_seo_entry_resolved(self):
        """fields.seo link → resolved entry with title/description."""
        seo_entry_id = "seo123"
        fields = {
            "seo": {"sys": {"type": "Link", "linkType": "Entry", "id": seo_entry_id}}
        }
        includes_by_id = {
            seo_entry_id: {
                "fields": {
                    "title": "Linked SEO Title",
                    "description": "Linked SEO description text here.",
                }
            }
        }
        result = cf_fetch.extract_seo_fields(fields, includes_by_id)
        self.assertEqual(result["meta_title"], "Linked SEO Title")
        self.assertEqual(result["meta_description"], "Linked SEO description text here.")

    def test_linked_seo_entry_not_in_includes_returns_empty(self):
        """If the linked entry isn't in includes, fall through gracefully."""
        fields = {
            "seo": {"sys": {"type": "Link", "linkType": "Entry", "id": "missing-id"}}
        }
        result = cf_fetch.extract_seo_fields(fields, {})
        self.assertEqual(result["meta_title"], "")
        self.assertEqual(result["meta_description"], "")

    def test_no_seo_fields_returns_empty_meta_title(self):
        """When no explicit SEO fields exist, meta_title must be empty — not the content title.
        An entry using only its content title should be flagged as missing_meta_title=True."""
        fields = {"title": "Content Title Only"}
        result = cf_fetch.extract_seo_fields(fields, {})
        self.assertEqual(result["meta_title"], "")

    def test_no_fields_returns_empty(self):
        result = cf_fetch.extract_seo_fields({}, {})
        self.assertEqual(result["meta_title"], "")
        self.assertEqual(result["meta_description"], "")


class TestContentfulNormaliseEntry(unittest.TestCase):
    """normalise_entry() maps Contentful entry shape to shared format."""

    def _cf_item(self, **field_overrides):
        fields = {
            "title": "My Article",
            "slug": "my-article",
            "seoTitle": "My Article | Brand",
            "seoDescription": "A" * 100,
            **field_overrides,
        }
        return {
            "sys": {
                "id": "cf123",
                "createdAt": "2024-01-01T00:00:00Z",
                "updatedAt": "2024-02-01T00:00:00Z",
                "locale": "en-US",
            },
            "fields": fields,
        }

    def test_document_id_from_sys_id(self):
        result = cf_fetch.normalise_entry(self._cf_item(), {})
        self.assertEqual(result["document_id"], "cf123")

    def test_slug_extracted(self):
        result = cf_fetch.normalise_entry(self._cf_item(), {})
        self.assertEqual(result["slug"], "my-article")

    def test_seo_title_extracted(self):
        result = cf_fetch.normalise_entry(self._cf_item(), {})
        self.assertEqual(result["seo"]["meta_title"], "My Article | Brand")
        self.assertFalse(result["missing_meta_title"])

    def test_missing_seo_title_flagged(self):
        result = cf_fetch.normalise_entry(self._cf_item(seoTitle=None), {})
        self.assertTrue(result["missing_meta_title"])

    def test_locale_from_sys(self):
        result = cf_fetch.normalise_entry(self._cf_item(), {})
        self.assertEqual(result["locale"], "en-US")

    def test_url_field_used_as_slug_fallback(self):
        item = self._cf_item()
        del item["fields"]["slug"]
        item["fields"]["url"] = "/my-url"
        result = cf_fetch.normalise_entry(item, {})
        self.assertEqual(result["slug"], "/my-url")


# ── fetch_ghost_content.py ────────────────────────────────────────────────────

class TestGhostNormaliseEntry(unittest.TestCase):
    """normalise_entry() maps Ghost post/page to shared format."""

    def _ghost_item(self, **overrides):
        base = {
            "id": "ghost-id-abc",
            "title": "My Ghost Post",
            "slug": "my-ghost-post",
            "published_at": "2024-01-15T10:00:00.000Z",
            "updated_at": "2024-02-01T12:00:00.000Z",
            "meta_title": "Ghost SEO Title | Brand",
            "meta_description": "A" * 100,
            "og_image": "https://example.com/og.jpg",
            "og_title": "OG Title",
        }
        base.update(overrides)
        return base

    def test_document_id_from_id(self):
        result = ghost_fetch.normalise_entry(self._ghost_item())
        self.assertEqual(result["document_id"], "ghost-id-abc")

    def test_slug_extracted(self):
        result = ghost_fetch.normalise_entry(self._ghost_item())
        self.assertEqual(result["slug"], "my-ghost-post")

    def test_meta_title_extracted(self):
        result = ghost_fetch.normalise_entry(self._ghost_item())
        self.assertEqual(result["seo"]["meta_title"], "Ghost SEO Title | Brand")
        self.assertFalse(result["missing_meta_title"])

    def test_null_meta_title_flagged_as_missing(self):
        """Ghost returns null for meta_title when not set — must flag as missing."""
        item = self._ghost_item(meta_title=None)
        result = ghost_fetch.normalise_entry(item)
        self.assertTrue(result["missing_meta_title"])
        # Must NOT fall back to the post title
        self.assertEqual(result["seo"]["meta_title"], "")

    def test_og_image_detected(self):
        result = ghost_fetch.normalise_entry(self._ghost_item())
        self.assertTrue(result["seo"]["has_meta_image"])

    def test_no_og_image(self):
        item = self._ghost_item(og_image=None)
        result = ghost_fetch.normalise_entry(item)
        self.assertFalse(result["seo"]["has_meta_image"])

    def test_og_title_marks_has_meta_social(self):
        result = ghost_fetch.normalise_entry(self._ghost_item())
        self.assertTrue(result["seo"]["has_meta_social"])

    def test_no_social_fields(self):
        item = self._ghost_item(og_title=None, og_image=None)
        # twitter_title not in item either
        result = ghost_fetch.normalise_entry(item)
        self.assertFalse(result["seo"]["has_meta_social"])

    def test_meta_title_too_long_flagged(self):
        item = self._ghost_item(meta_title="A" * 61)
        result = ghost_fetch.normalise_entry(item)
        self.assertTrue(result["meta_title_too_long"])

    def test_meta_description_too_short_flagged(self):
        item = self._ghost_item(meta_description="Short.")
        result = ghost_fetch.normalise_entry(item)
        self.assertTrue(result["meta_description_too_short"])

    def test_missing_meta_description_not_flagged_as_too_short(self):
        """Empty description should be missing_meta_description=True, not too_short."""
        item = self._ghost_item(meta_description=None)
        result = ghost_fetch.normalise_entry(item)
        self.assertTrue(result["missing_meta_description"])
        self.assertFalse(result["meta_description_too_short"])  # 0 chars → not "too short"


# ── SSRF protection (shared logic, tested via WordPress) ──────────────────────

class TestSsrfProtection(unittest.TestCase):
    """_is_private_ip() blocks loopback, RFC1918, link-local addresses."""

    def test_loopback_blocked(self):
        self.assertTrue(wp_fetch._is_private_ip("127.0.0.1"))
        self.assertTrue(wp_fetch._is_private_ip("::1"))

    def test_private_rfc1918_blocked(self):
        self.assertTrue(wp_fetch._is_private_ip("10.0.0.1"))
        self.assertTrue(wp_fetch._is_private_ip("192.168.1.1"))
        self.assertTrue(wp_fetch._is_private_ip("172.16.0.1"))
        self.assertTrue(wp_fetch._is_private_ip("172.31.255.255"))

    def test_public_ip_allowed(self):
        self.assertFalse(wp_fetch._is_private_ip("8.8.8.8"))
        self.assertFalse(wp_fetch._is_private_ip("104.21.1.1"))

    def test_invalid_ip_returns_false(self):
        self.assertFalse(wp_fetch._is_private_ip("not-an-ip"))
        self.assertFalse(wp_fetch._is_private_ip(""))


# ── WordPress auth header ─────────────────────────────────────────────────────

class TestWordPressAuthHeader(unittest.TestCase):
    """make_auth_header() strips spaces from Application Passwords."""

    def test_spaces_stripped_from_password(self):
        header = wp_fetch.make_auth_header("admin", "xxxx xxxx xxxx xxxx")
        import base64
        decoded = base64.b64decode(header.split(" ")[1]).decode()
        self.assertEqual(decoded, "admin:xxxxxxxxxxxxxxxx")

    def test_password_without_spaces_unchanged(self):
        header = wp_fetch.make_auth_header("user", "plainpassword")
        import base64
        decoded = base64.b64decode(header.split(" ")[1]).decode()
        self.assertEqual(decoded, "user:plainpassword")

    def test_header_is_basic_scheme(self):
        header = wp_fetch.make_auth_header("u", "p")
        self.assertTrue(header.startswith("Basic "))


# ── SEO audit (Ghost, same logic as WordPress) ────────────────────────────────

class TestGhostSeoAudit(unittest.TestCase):

    def _entry(self, meta_title="", meta_description=""):
        tlen = len(meta_title)
        dlen = len(meta_description)
        return {
            "document_id": "1",
            "title": "Post",
            "slug": "post",
            "seo": {"meta_title": meta_title, "meta_description": meta_description},
            "missing_meta_title": not meta_title,
            "missing_meta_description": not meta_description,
            "meta_title_too_long": tlen > 60,
            "meta_description_too_long": dlen > 160,
            "meta_description_too_short": 0 < dlen < 70,
        }

    def test_empty_list_returns_zeroes(self):
        audit = ghost_fetch.build_seo_audit([])
        self.assertEqual(audit["total"], 0)
        self.assertEqual(audit["complete_seo"], 0)
        self.assertEqual(audit["missing_meta_title"], 0)

    def test_all_complete_returns_full_count(self):
        entries = [self._entry("Good Title", "A" * 100) for _ in range(5)]
        audit = ghost_fetch.build_seo_audit(entries)
        self.assertEqual(audit["complete_seo"], 5)
        self.assertEqual(audit["missing_meta_title"], 0)

    def test_mixed_entries_correctly_counted(self):
        # Each entry needs a unique document_id — build_seo_audit uses a set of
        # broken IDs to count complete entries, so duplicate IDs would collapse.
        entries = [
            {**self._entry("Title", "A" * 100), "document_id": "1"},    # complete
            {**self._entry("", "A" * 100), "document_id": "2"},          # missing title
            {**self._entry("Title", ""), "document_id": "3"},             # missing desc
            {**self._entry("A" * 61, "A" * 100), "document_id": "4"},    # title too long
        ]
        audit = ghost_fetch.build_seo_audit(entries)
        self.assertEqual(audit["total"], 4)
        self.assertEqual(audit["complete_seo"], 1)
        self.assertEqual(audit["missing_meta_title"], 1)
        self.assertEqual(audit["missing_meta_description"], 1)
        self.assertEqual(audit["meta_title_too_long"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
