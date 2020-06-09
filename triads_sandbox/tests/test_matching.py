from django.test import SimpleTestCase

from drf_triad_permissions.matching import match, match_any, match_all


class StrictMatchTestCase(SimpleTestCase):
    """
    Tests `matching.match` in strict mode.
    """

    def test_triad_length(self):
        self.assertEqual(match("", "ok::ok::ok"), None)
        self.assertEqual(match("a", "ok::ok::ok"), None)
        self.assertEqual(match("a::b", "ok::ok::ok"), None)
        self.assertEqual(match("a::b::c::", "ok::ok::ok"), None)
        self.assertEqual(match("a::b::c::d", "ok::ok::ok"), None)
        self.assertEqual(match("ok::ok::ok", "a"), None)
        self.assertEqual(match("ok::ok::ok", "a::b"), None)
        self.assertEqual(match("ok::ok::ok", "a::b::c::"), None)
        self.assertEqual(match("ok::ok::ok", "a::b::c::d"), None)

    def test_matching_exact(self):
        self.assertTrue(match("resource::object::action", "resource::object::action"))

    def test_matching_all_or_asterisk(self):
        # One level
        self.assertTrue(match("resource::object::action", "resource::object::all"))
        self.assertTrue(match("resource::object::action", "resource::object::*"))
        self.assertTrue(match("resource::object::action", "resource::all::action"))
        self.assertTrue(match("resource::object::action", "resource::*::action"))
        self.assertTrue(match("resource::object::action", "all::object::action"))
        self.assertTrue(match("resource::object::action", "*::object::action"))
        # Two levels
        self.assertTrue(match("resource::object::action", "resource::*::all"))
        self.assertTrue(match("resource::object::action", "resource::all::*"))
        self.assertTrue(match("resource::object::action", "*::all::action"))
        self.assertTrue(match("resource::object::action", "all::*::action"))
        self.assertTrue(match("resource::object::action", "all::object::*"))
        self.assertTrue(match("resource::object::action", "*::object::all"))
        # Three levels
        self.assertTrue(match("resource::object::action", "all::*::all"))
        self.assertTrue(match("resource::object::action", "*::all::*"))

    def test_matching_read(self):
        # This can be done at any level, but will happen most likely at the third
        self.assertTrue(match("resource::object::list", "resource::object::read"))
        self.assertTrue(match("resource::object::list", "resource::object::<read>"))
        self.assertTrue(match("resource::object::retrieve", "resource::object::read"))
        self.assertTrue(match("resource::object::retrieve", "resource::object::<read>"))

    def test_matching_write(self):
        # This can be done at any level, but will happen most likely at the third
        self.assertTrue(match("resource::object::create", "resource::object::write"))
        self.assertTrue(match("resource::object::create", "resource::object::<write>"))
        self.assertTrue(match("resource::object::update", "resource::object::write"))
        self.assertTrue(match("resource::object::update", "resource::object::<write>"))
        self.assertTrue(match("resource::object::partial-update", "resource::object::write"))
        self.assertTrue(match("resource::object::partial-update", "resource::object::<write>"))
        self.assertTrue(match("resource::object::destroy", "resource::object::write"))
        self.assertTrue(match("resource::object::destroy", "resource::object::<write>"))

    def test_matching_custom_wildcard(self):
        # Custom wildcard defined in settings
        self.assertTrue(match("resource::object::update", "resource::object::any-update"))
        self.assertTrue(match("resource::object::update", "resource::object::any-update"))
        self.assertTrue(match("resource::object::partial-update", "resource::object::any-update"))
        self.assertTrue(match("resource::object::partial-update", "resource::object::any-update"))

    def test_no_match_exact(self):
        self.assertFalse(match("resource::object::action1", "resource::object::action2"))
        self.assertFalse(match("resource::object1::action", "resource::object2::action"))
        self.assertFalse(match("resource1::object::action", "resource2::object::action"))

    def test_no_match_wildcard_levels(self):
        self.assertFalse(match("resource::object1::action", "resource::object2::*"))
        self.assertFalse(match("resource::object1::action", "resource::object2::*"))
        self.assertFalse(match("resource::object::action1", "resource::*::action2"))
        self.assertFalse(match("resource::object::action1", "resource::*::action2"))
        self.assertFalse(match("resource1::object::action", "resource2::object::*"))
        self.assertFalse(match("resource1::object::action", "resource2::object::*"))


class NoStrictMatchTestCase(SimpleTestCase):
    """
    Tests `matching.match` in NO strict mode.
    """

    def test_matching_some(self):
        # One level
        self.assertTrue(match("resource::object::some", "resource::object::action", strict=False))
        self.assertTrue(match("resource::some::action", "resource::object::action", strict=False))
        self.assertTrue(match("some::object::action", "resource::object::action", strict=False))
        # Two levels
        self.assertTrue(match("resource::some::some", "resource::object::action", strict=False))
        self.assertTrue(match("some::some::action", "resource::object::action", strict=False))
        self.assertTrue(match("some::object::some", "resource::object::action", strict=False))
        # Three levels
        self.assertTrue(match("some::some::some", "resource::object::action", strict=False))


class MatchAnyTestCase(SimpleTestCase):
    """
    Tests `matching.match_any`.
    """

    def test_match_any(self):
        self.assertTrue(match_any("a::b::c", ["a::b::c"]))
        self.assertTrue(match_any("a::b::c", ["a::b::*"]))
        self.assertTrue(match_any("a::b::c", ["a::*::c"]))
        self.assertTrue(match_any("a::b::c", ["*::b::c"]))

    def test_no_match_any(self):
        self.assertFalse(match_any("a::b::c", ["a::b::d"]))
        self.assertFalse(match_any("a::b::c", ["a::c::*"]))
        self.assertFalse(match_any("a::b::c", ["a::*::b"]))
        self.assertFalse(match_any("a::b::c", ["*::a::c"]))


class MatchAllTestCase(SimpleTestCase):
    """
    Tests `matching.match_all`.
    """

    def test_match_all(self):
        self.assertTrue(
            match_all("a::b::c", ["a::b::c", "a::b::*", "a::*::c", "*::b::c", "a::*::*", "*::*::c", "*::b::*", "*::*::*"])
        )

    def test_no_match_all(self):
        self.assertFalse(match_all("a::b::c", ["a::b::c", "a::b::d"]))
        self.assertFalse(match_all("a::b::c", ["a::b::c", "a::c::*"]))
        self.assertFalse(match_all("a::b::c", ["a::b::c", "a::*::b"]))
        self.assertFalse(match_all("a::b::c", ["a::b::c", "*::a::c"]))
