import sys
if sys.version_info < (3, 8):
    raise Exception("Python 3.8 or higher is required.")

from typing import Final, Optional, TypedDict

class User(TypedDict, total=False):
    name: Optional[str]
    email: Optional[str]
    signingKey: Optional[str]
    github: Optional[str]

# Configuration begins here.
user: Final[User] = {
    'name': None,
    'email': None,
    # path to SSH key, e.g. "~/.ssh/id_ed25519"
    'signingKey': None,
    'github': None,
    }

