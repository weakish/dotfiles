from __future__ import annotations
import sys
if sys.version_info < (3, 7):
    raise Exception("Python 3.7 or higher is required.")
elif sys.version_info < (3, 8):
    from typing_extensions import TypedDict
else:
    from typing import TypedDict

from typing import Final, Optional

class User(TypedDict, total=False):
    name: Optional[str]
    email: Optional[str]
    signingkey: Optional[str]
    github: Optional[str]

# Configuration begins here.
user: Final[User] = {
    'name': None,
    'email': None,
    'signingkey': None,
    'github': None,
    }

