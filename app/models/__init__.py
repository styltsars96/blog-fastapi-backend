"""
Metadata to be exported!

When making changes to models:
Import Base from all other submodules with models!
"""
# pylint: disable=reimported

from .users import Base
from .posts import Base

METADATA = Base.metadata
