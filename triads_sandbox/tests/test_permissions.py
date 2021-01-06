from django.test import Client, SimpleTestCase, TestCase

from basic.models import Entity, User

from drf_triad_permissions.permissions import NO_MATCH, clean_no_match
from drf_triad_permissions.settings import NON_STRICT_PLACEHOLDER, TRIAD_DIVIDER


class CleanNoMatchTestCase(SimpleTestCase):
    def test_prefix(self):
        self.assertEqual(
            clean_no_match(f"wawa{TRIAD_DIVIDER})(*@awhyn45z#($*@#*${NO_MATCH}"),
            f"wawa{TRIAD_DIVIDER}{NON_STRICT_PLACEHOLDER}",
        )

    def test_suffix(self):
        self.assertEqual(
            clean_no_match(f"{NO_MATCH})(*@awhyn45z#($*@#*${TRIAD_DIVIDER}wawa"),
            f"{NON_STRICT_PLACEHOLDER}{TRIAD_DIVIDER}wawa",
        )

    def test_both(self):
        self.assertEqual(
            clean_no_match(f"wawa{TRIAD_DIVIDER})(*@awhyn45z#($*@#*${NO_MATCH})(*@awhyn45z#($*@#*${TRIAD_DIVIDER}wawa"),
            f"wawa{TRIAD_DIVIDER}{NON_STRICT_PLACEHOLDER}{TRIAD_DIVIDER}wawa",
        )


class APIProbingTestCase(TestCase):
    """
    Probes all URLs from users with varying permissions.
    Tests actual response vs. expectation.
    """

    @classmethod
    def setUpClass(cls):
        cls.first = User.objects.create(username="first")
        cls.second = User.objects.create(username="second")
        cls.entity = Entity.objects.create(slug="ent1", user=cls.first)
        cls.entity2 = Entity.objects.create(slug="ent2", user=cls.second)

    @classmethod
    def tearDownClass(cls):
        User.objects.all().delete()
        Entity.objects.all().delete()

    def check(self, url, user, expectations):
        client = Client()
        HUMAN_EXPECTATIONS = {
            "accepted": [200, 204, 400],
            "method-not-allowed": [405],
            "denied": [403],
        }
        if user:
            client.force_login(user=user)
        for method, expectation in expectations.items():
            response = getattr(client, method)(url, content_type="application/json")
            code = response.status_code
            expected_codes = HUMAN_EXPECTATIONS[expectation]
            self.assertIn(code, expected_codes, f"User {user} on {method}:{url} got unexpected {code}.")

    def test_user_list(self):
        url = "/api/users/"
        anonymous_expectations = {
            "get": "denied",
            "post": "denied",
            "put": "denied",
            "patch": "denied",
            "delete": "denied",
        }
        authenticated_user_expectations = {
            "get": "accepted",
            "post": "denied",
            "put": "denied",
            "patch": "denied",
            "delete": "denied",
        }
        self.check(url, None, anonymous_expectations)
        self.check(url, self.first, authenticated_user_expectations)
        self.check(url, self.second, authenticated_user_expectations)

    def test_user_detail(self):
        url = f"/api/users/{self.first.pk}/"
        anonymous_expectations = {
            "get": "denied",
            "post": "denied",
            "put": "denied",
            "patch": "denied",
            "delete": "denied",
        }
        self_user_expectations = {
            "get": "accepted",
            "post": "method-not-allowed",
            "put": "accepted",
            "patch": "accepted",
            "delete": "accepted",
        }
        other_user_expectations = {
            "get": "accepted",
            "post": "method-not-allowed",
            "put": "denied",
            "patch": "denied",
            "delete": "denied",
        }
        self.check(url, None, anonymous_expectations)
        self.check(url, self.first, self_user_expectations)
        self.check(url, self.second, other_user_expectations)

    def test_entity_list(self):
        url = f"/api/entities-by-user/{self.first.username}/"
        anonymous_expectations = {
            "get": "denied",
            "post": "denied",
            "put": "denied",
            "patch": "denied",
            "delete": "denied",
        }
        first_user_expectations = {
            "get": "accepted",
            "post": "accepted",
            "put": "method-not-allowed",
            "patch": "method-not-allowed",
            "delete": "method-not-allowed",
        }
        second_user_expectations = {
            "get": "accepted",
            "post": "denied",
            "put": "denied",
            "patch": "denied",
            "delete": "denied",
        }
        self.check(url, None, anonymous_expectations)
        self.check(url, self.first, first_user_expectations)
        self.check(url, self.second, second_user_expectations)

    def test_entity_detail(self):
        url = f"/api/entities-by-user/{self.first.username}/{self.entity.slug}/"
        anonymous_expectations = {
            "get": "denied",
            "post": "denied",
            "put": "denied",
            "patch": "denied",
            "delete": "denied",
        }
        referred_user_expectations = {
            "get": "accepted",
            "post": "method-not-allowed",
            "put": "accepted",
            "patch": "accepted",
            "delete": "accepted",
        }
        other_user_expectations = {
            "get": "accepted",
            "post": "method-not-allowed",
            "put": "denied",
            "patch": "denied",
            "delete": "denied",
        }
        self.check(url, None, anonymous_expectations)
        self.check(url, self.first, referred_user_expectations)
        self.check(url, self.second, other_user_expectations)

    def test_entity_poke(self):
        url = f"/api/entities-by-user/{self.first.username}/{self.entity.slug}/poke/"
        anonymous_expectations = {
            "get": "denied",
            "post": "denied",
            "put": "denied",
            "patch": "denied",
            "delete": "denied",
        }
        referred_user_expectations = {
            "get": "method-not-allowed",
            "post": "accepted",
            "put": "method-not-allowed",
            "patch": "method-not-allowed",
            "delete": "method-not-allowed",
        }
        other_user_expectations = {
            "get": "method-not-allowed",
            "post": "denied",
            "put": "method-not-allowed",
            "patch": "method-not-allowed",
            "delete": "method-not-allowed",
        }
        self.check(url, None, anonymous_expectations)
        self.check(url, self.first, referred_user_expectations)
        self.check(url, self.second, other_user_expectations)

    def test_entity_poke_disabled_policy(self):
        url = f"/api/entities-by-user/{self.second.username}/{self.entity2.slug}/poke/"
        anonymous_expectations = {
            "get": "denied",
            "post": "denied",
            "put": "denied",
            "patch": "denied",
            "delete": "denied",
        }
        referred_user_expectations = {
            "get": "method-not-allowed",
            "post": "denied",  # from policy.deny
            "put": "method-not-allowed",
            "patch": "method-not-allowed",
            "delete": "method-not-allowed",
        }
        other_user_expectations = {
            "get": "method-not-allowed",
            "post": "denied",
            "put": "method-not-allowed",
            "patch": "method-not-allowed",
            "delete": "method-not-allowed",
        }
        self.check(url, None, anonymous_expectations)
        self.check(url, self.second, referred_user_expectations)
        self.check(url, self.first, other_user_expectations)
