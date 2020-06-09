from django.test import SimpleTestCase

from drf_triad_permissions.utils import triad_superset


class TriadSupersetTestCase(SimpleTestCase):
    """
    Tests `utils.triad_superset`.
    """

    def test_triad_superset(self):
        self.assertEqual(set(triad_superset(["*::*::*", "*::*::c", "a::*::*", "*::b::*", "a::b::c"])), set(["*::*::*"]))
        self.assertEqual(
            set(triad_superset(["*::*::c", "a::*::*", "*::b::*", "a::b::c"])), set(["*::*::c", "a::*::*", "*::b::*"])
        )
        self.assertEqual(
            set(triad_superset(["*::*::c", "a::*::*", "*::b::*", "b::c::d"])),
            set(["*::*::c", "a::*::*", "*::b::*", "b::c::d"]),
        )
        self.assertEqual(set(triad_superset(["a::b::c", "a::b::c", "a::b::c"])), set(["a::b::c"]))
        self.assertEqual(set(triad_superset(["a::b::c", "b::c::d", "c::d::e"])), set(["a::b::c", "b::c::d", "c::d::e"]))
