from .permissions import get_triad_permission


class Policy:
    @classmethod
    def actions(cls):
        return {
            key: [x.strip() for x in value]
            for key, value in cls.__dict__.items()
            if not key.startswith("__") and not callable(value)
        }

    @classmethod
    def expand(cls):
        return [get_triad_permission(**cls.actions())]


class BasicPolicy(Policy):
    default = [
        "{resource}::all::{action}",
        "{resource}::new::create",
        "{resource}::id:{obj.id}::{action}",
    ]
