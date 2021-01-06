from drf_triad_permissions.policies import BasicPolicy, Policy  # noqa


class UserBasedPolicy(Policy):
    # This policy means:
    # Any action that matches ID from the object will be allowed
    # Any action that matches username from the URL will be allowed
    allow = [
        "{resource}::id:{obj.id}::{action}",
        "{resource}::user:{url.username}::{action}",
    ]
    deny = [
        "{resource}::user:second::poke",
    ]
