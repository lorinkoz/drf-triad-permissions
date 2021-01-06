from drf_triad_permissions.permissions import get_triad_permission


class Policy:
    allow = None
    deny = None

    @classmethod
    def expand(cls, default_resource=None):
        return [get_triad_permission(allow=cls.allow, deny=cls.deny, default_resource=default_resource)]


class BasicPolicy(Policy):
    allow = [
        "{resource}::all::{action}",
        "{resource}::new::create",
        "{resource}::id:{obj.id}::{action}",
    ]
