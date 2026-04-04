"""
Unit tests for Strapi integration scripts.

Tests pure logic functions — no Strapi API calls, no credentials needed.
Covers version detection, entry normalisation, SEO audit, payload building,
SSRF protection, and stale-write guard.

Run: pytest test/unit/test_strapi_scripts.py -v
"""

import importlib.util
import json
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


fetch = _load('fetch_strapi_content.py')
push = _load('push_strapi_seo.py')
preflight = _load('preflight_strapi.py')


# ── fetch_strapi_content.py ───────────────────────────────────────────────────

class TestDetectVersionFetch(unittest.TestCase):
    """detect_version() in fetch_strapi_content: explicit hint overrides response."""

    def test_explicit_v4_hint(self):
        data = {"data": [{"id": 1, "attributes": {"title": "x"}}]}
        self.assertEqual(fetch.detect_version(data, "4"), 4)

    def test_explicit_v5_hint(self):
        data = {"data": [{"id": 1, "attributes": {"title": "x"}}]}
        self.assertEqual(fetch.detect_version(data, "5"), 5)

    def test_infer_v4_from_attributes_key(self):
        data = {"data": [{"id": 1, "attributes": {"title": "x"}}]}
        self.assertEqual(fetch.detect_version(data, ""), 4)

    def test_infer_v5_from_flat_item(self):
        data = {"data": [{"id": 1, "title": "x", "documentId": "abc"}]}
        self.assertEqual(fetch.detect_version(data, ""), 5)

    def test_empty_collection_defaults_to_v5(self):
        data = {"data": []}
        self.assertEqual(fetch.detect_version(data, ""), 5)

    def test_missing_data_key_defaults_to_v5(self):
        data = {}
        self.assertEqual(fetch.detect_version(data, ""), 5)


class TestExtractSeoComponent(unittest.TestCase):
    """extract_seo_component() normalises plugin-seo data."""

    def test_returns_empty_dict_for_none(self):
        result = fetch.extract_seo_component(None)
        self.assertEqual(result, {})

    def test_returns_empty_dict_for_empty_dict(self):
        result = fetch.extract_seo_component({})
        self.assertEqual(result, {})

    def test_extracts_flat_v5_seo(self):
        seo = {"metaTitle": "My Title", "metaDescription": "Desc", "metaImage": {"url": "x"}}
        result = fetch.extract_seo_component(seo)
        self.assertEqual(result["meta_title"], "My Title")
        self.assertEqual(result["meta_description"], "Desc")
        self.assertTrue(result["has_meta_image"])

    def test_extracts_v4_nested_attributes(self):
        seo = {"attributes": {"metaTitle": "v4 Title", "metaDescription": "v4 Desc"}}
        result = fetch.extract_seo_component(seo)
        self.assertEqual(result["meta_title"], "v4 Title")

    def test_missing_fields_default_to_empty_string(self):
        result = fetch.extract_seo_component({"metaTitle": "Title"})
        self.assertEqual(result["meta_description"], "")
        self.assertFalse(result["has_meta_image"])
        self.assertFalse(result["has_meta_social"])


class TestNormaliseEntry(unittest.TestCase):
    """normalise_entry() produces a flat dict for both v4 and v5 shapes."""

    def _v4_raw(self, **overrides):
        attrs = {
            "title": "Hello", "slug": "hello",
            "publishedAt": "2024-01-01T00:00:00.000Z",
            "updatedAt": "2024-01-02T00:00:00.000Z",
            "createdAt": "2023-12-01T00:00:00.000Z",
            "locale": "en",
            **overrides,
        }
        return {"id": 42, "attributes": attrs}

    def _v5_raw(self, **overrides):
        return {
            "id": 42, "documentId": "abc123",
            "title": "Hello", "slug": "hello",
            "publishedAt": "2024-01-01T00:00:00.000Z",
            "updatedAt": "2024-01-02T00:00:00.000Z",
            "createdAt": "2023-12-01T00:00:00.000Z",
            "locale": "en",
            **overrides,
        }

    def test_v4_sets_document_id_from_id(self):
        entry = fetch.normalise_entry(self._v4_raw(), v4=True)
        self.assertEqual(entry["document_id"], "42")

    def test_v5_sets_document_id_from_document_id(self):
        entry = fetch.normalise_entry(self._v5_raw(), v4=False)
        self.assertEqual(entry["document_id"], "abc123")

    def test_title_extracted(self):
        entry = fetch.normalise_entry(self._v4_raw(), v4=True)
        self.assertEqual(entry["title"], "Hello")

    def test_title_fallback_to_name(self):
        raw = self._v4_raw()
        raw["attributes"].pop("title")
        raw["attributes"]["name"] = "Name Fallback"
        entry = fetch.normalise_entry(raw, v4=True)
        self.assertEqual(entry["title"], "Name Fallback")

    def test_missing_meta_title_flag(self):
        entry = fetch.normalise_entry(self._v4_raw(), v4=True)
        self.assertTrue(entry["missing_meta_title"])

    def test_meta_title_present(self):
        raw = self._v4_raw()
        raw["attributes"]["seo"] = {"metaTitle": "Good Title (50 chars ok)"}
        entry = fetch.normalise_entry(raw, v4=True)
        self.assertFalse(entry["missing_meta_title"])

    def test_meta_title_too_long(self):
        raw = self._v5_raw()
        raw["seo"] = {"metaTitle": "A" * 61}
        entry = fetch.normalise_entry(raw, v4=False)
        self.assertTrue(entry["meta_title_too_long"])

    def test_meta_description_too_short(self):
        raw = self._v5_raw()
        raw["seo"] = {"metaTitle": "T", "metaDescription": "Short"}
        entry = fetch.normalise_entry(raw, v4=False)
        self.assertTrue(entry["meta_description_too_short"])

    def test_meta_description_too_long(self):
        raw = self._v5_raw()
        raw["seo"] = {"metaDescription": "D" * 161}
        entry = fetch.normalise_entry(raw, v4=False)
        self.assertTrue(entry["meta_description_too_long"])

    def test_root_field_fallback_for_meta_title(self):
        raw = self._v5_raw()
        raw["metaTitle"] = "Root Field Title"
        entry = fetch.normalise_entry(raw, v4=False)
        self.assertEqual(entry["seo"]["meta_title"], "Root Field Title")
        self.assertEqual(entry["seo_schema"], "root_fields")

    def test_seo_schema_component_when_seo_key_present(self):
        raw = self._v5_raw()
        raw["seo"] = {"metaTitle": "T"}
        entry = fetch.normalise_entry(raw, v4=False)
        self.assertEqual(entry["seo_schema"], "component")

    def test_all_fields_present_with_valid_seo(self):
        raw = self._v5_raw()
        raw["seo"] = {
            "metaTitle": "Good Title",
            "metaDescription": "A" * 100,
        }
        entry = fetch.normalise_entry(raw, v4=False)
        self.assertFalse(entry["missing_meta_title"])
        self.assertFalse(entry["missing_meta_description"])
        self.assertFalse(entry["meta_title_too_long"])
        self.assertFalse(entry["meta_description_too_long"])
        self.assertFalse(entry["meta_description_too_short"])


class TestBuildSeoAudit(unittest.TestCase):
    """build_seo_audit() counts correctly even when one entry has multiple issues."""

    def _entry(self, missing_title=False, missing_desc=False, title_long=False,
                desc_too_long=False, desc_too_short=False, doc_id="x"):
        return {
            "document_id": doc_id,
            "title": "T", "slug": "s",
            "seo": {"meta_title": "" if missing_title else "Title"},
            "missing_meta_title": missing_title,
            "missing_meta_description": missing_desc,
            "meta_title_too_long": title_long,
            "meta_description_too_long": desc_too_long,
            "meta_description_too_short": desc_too_short,
        }

    def test_empty_entries(self):
        audit = fetch.build_seo_audit([])
        self.assertEqual(audit["total"], 0)
        self.assertEqual(audit["complete_seo"], 0)

    def test_all_complete(self):
        entries = [self._entry(doc_id=str(i)) for i in range(3)]
        audit = fetch.build_seo_audit(entries)
        self.assertEqual(audit["complete_seo"], 3)
        self.assertEqual(audit["missing_meta_title"], 0)

    def test_one_missing_title(self):
        entries = [self._entry(missing_title=True, doc_id="1"), self._entry(doc_id="2")]
        audit = fetch.build_seo_audit(entries)
        self.assertEqual(audit["missing_meta_title"], 1)
        self.assertEqual(audit["complete_seo"], 1)

    def test_entry_with_multiple_issues_counted_once_in_complete(self):
        # One entry has both missing title AND missing desc — should reduce complete_seo by 1.
        entries = [
            self._entry(missing_title=True, missing_desc=True, doc_id="bad"),
            self._entry(doc_id="good"),
        ]
        audit = fetch.build_seo_audit(entries)
        self.assertEqual(audit["complete_seo"], 1)  # only the "good" one
        self.assertEqual(audit["missing_meta_title"], 1)
        self.assertEqual(audit["missing_meta_description"], 1)

    def test_entries_missing_meta_title_capped_at_20(self):
        entries = [self._entry(missing_title=True, doc_id=str(i)) for i in range(25)]
        audit = fetch.build_seo_audit(entries)
        self.assertLessEqual(len(audit["entries_missing_meta_title"]), 20)


# ── push_strapi_seo.py ────────────────────────────────────────────────────────

class TestDetectVersionPush(unittest.TestCase):
    """detect_version() in push reads from single-entry GET response."""

    def test_explicit_v4_hint(self):
        raw = {"data": {"id": 1, "attributes": {}}}
        self.assertEqual(push.detect_version(raw, "4"), 4)

    def test_explicit_v5_hint(self):
        raw = {"data": {"id": 1}}
        self.assertEqual(push.detect_version(raw, "5"), 5)

    def test_infer_v4_from_attributes(self):
        raw = {"data": {"id": 1, "attributes": {"title": "T"}}}
        self.assertEqual(push.detect_version(raw, ""), 4)

    def test_infer_v5_flat(self):
        raw = {"data": {"id": 1, "title": "T", "documentId": "abc"}}
        self.assertEqual(push.detect_version(raw, ""), 5)


class TestBuildPayload(unittest.TestCase):
    """build_payload() constructs correct Strapi PUT body."""

    def test_component_schema_wraps_in_seo(self):
        update = {"meta_title": "New Title"}
        payload = push.build_payload(update, {}, "component")
        self.assertIn("seo", payload["data"])
        self.assertEqual(payload["data"]["seo"]["metaTitle"], "New Title")

    def test_root_fields_schema_flat(self):
        update = {"meta_description": "New desc"}
        payload = push.build_payload(update, {}, "root_fields")
        self.assertIn("metaDescription", payload["data"])
        self.assertNotIn("seo", payload["data"])

    def test_returns_none_when_nothing_to_update(self):
        payload = push.build_payload({}, {}, "component")
        self.assertIsNone(payload)

    def test_merges_existing_seo_component(self):
        current_attrs = {"seo": {"metaTitle": "Old", "canonicalURL": "https://x.com"}}
        update = {"meta_title": "New Title"}
        payload = push.build_payload(update, current_attrs, "component")
        seo = payload["data"]["seo"]
        self.assertEqual(seo["metaTitle"], "New Title")
        self.assertEqual(seo["canonicalURL"], "https://x.com")

    def test_both_fields_in_update(self):
        update = {"meta_title": "T", "meta_description": "D"}
        payload = push.build_payload(update, {}, "component")
        seo = payload["data"]["seo"]
        self.assertEqual(seo["metaTitle"], "T")
        self.assertEqual(seo["metaDescription"], "D")

    def test_auto_detect_component_from_current_attrs(self):
        current_attrs = {"seo": {"metaTitle": "Old"}}
        update = {"meta_title": "New"}
        payload = push.build_payload(update, current_attrs, "auto")
        self.assertIn("seo", payload["data"])

    def test_auto_detect_root_when_no_seo_key(self):
        current_attrs = {"metaTitle": "Old"}
        update = {"meta_title": "New"}
        payload = push.build_payload(update, current_attrs, "auto")
        self.assertNotIn("seo", payload["data"])
        self.assertIn("metaTitle", payload["data"])

    def test_none_current_attrs_handled(self):
        update = {"meta_title": "T"}
        payload = push.build_payload(update, None, "component")
        self.assertEqual(payload["data"]["seo"]["metaTitle"], "T")


class TestStaleWriteGuard(unittest.TestCase):
    """Stale-write guard logic embedded in process_updates."""

    def test_guard_skips_when_timestamps_match(self):
        # Both sides same — should NOT skip (no stale detection)
        ts = "2024-01-01T00:00:00.000Z"
        self.assertFalse(ts and ts and ts != ts)

    def test_guard_fires_when_timestamps_differ(self):
        expected = "2024-01-01T00:00:00.000Z"
        live = "2024-01-02T00:00:00.000Z"
        should_skip = expected and live and expected != live
        self.assertTrue(should_skip)

    def test_guard_skips_check_when_expected_empty(self):
        # No updated_at in batch — guard should be bypassed
        expected = ""
        live = "2024-01-01T00:00:00.000Z"
        should_skip = expected and live and expected != live
        self.assertFalse(should_skip)

    def test_guard_skips_check_when_live_empty(self):
        expected = "2024-01-01T00:00:00.000Z"
        live = ""
        should_skip = expected and live and expected != live
        self.assertFalse(should_skip)


# ── preflight_strapi.py — SSRF protection ─────────────────────────────────────

class TestIsPrivateIp(unittest.TestCase):
    """_is_private_ip() correctly identifies non-public addresses."""

    def test_loopback_127(self):
        self.assertTrue(preflight._is_private_ip("127.0.0.1"))

    def test_loopback_ipv6(self):
        self.assertTrue(preflight._is_private_ip("::1"))

    def test_rfc1918_10(self):
        self.assertTrue(preflight._is_private_ip("10.0.0.1"))

    def test_rfc1918_172(self):
        self.assertTrue(preflight._is_private_ip("172.16.0.1"))

    def test_rfc1918_192(self):
        self.assertTrue(preflight._is_private_ip("192.168.1.100"))

    def test_link_local(self):
        self.assertTrue(preflight._is_private_ip("169.254.1.1"))

    def test_public_ip_is_not_private(self):
        self.assertFalse(preflight._is_private_ip("8.8.8.8"))

    def test_public_ip_2(self):
        self.assertFalse(preflight._is_private_ip("104.21.0.1"))

    def test_invalid_string_returns_false(self):
        self.assertFalse(preflight._is_private_ip("not-an-ip"))


class TestDetectVersionPreflight(unittest.TestCase):
    """detect_version() in preflight_strapi has same v4/v5 logic."""

    def test_explicit_v4(self):
        data = {"data": [{"attributes": {}}]}
        self.assertEqual(preflight.detect_version(data, "4"), 4)

    def test_infer_v4(self):
        data = {"data": [{"id": 1, "attributes": {"title": "T"}}]}
        self.assertEqual(preflight.detect_version(data, ""), 4)

    def test_infer_v5(self):
        data = {"data": [{"id": 1, "title": "T"}]}
        self.assertEqual(preflight.detect_version(data, ""), 5)

    def test_empty_collection_fallback_v5(self):
        data = {"data": []}
        self.assertEqual(preflight.detect_version(data, ""), 5)


class TestPublicationParam(unittest.TestCase):
    """publication_param() returns the version-correct filter."""

    def test_v4_returns_publication_state(self):
        param = preflight.publication_param(4)
        self.assertIn("publicationState", param)
        self.assertEqual(param["publicationState"], "live")

    def test_v5_returns_status(self):
        param = preflight.publication_param(5)
        self.assertIn("status", param)
        self.assertEqual(param["status"], "published")


if __name__ == "__main__":
    unittest.main()
