import sys

if sys.version_info < (3, 10):
    raise Exception("Python 3.10 or higher is required.")

from typing import Final, TypedDict


class User(TypedDict, total=False):
    name: str | None
    email: str | None
    signingKey: str | None
    github: str | None


# Configuration begins here.
user: Final[User] = {
    "name": None,
    "email": None,
    # path to SSH key, e.g. "~/.ssh/id_ed25519"
    "signingKey": None,
    "github": None,
}
