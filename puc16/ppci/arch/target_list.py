""" Contains a list of instantiated targets. """

from functools import lru_cache
from .puc16 import PUC16Arch


target_classes = [
    PUC16Arch,
]


target_class_map = {t.name: t for t in target_classes}
target_names = tuple(sorted(target_class_map.keys()))


@lru_cache(maxsize=30)
def create_arch(name, options=None):
    """Get a target architecture by its name. Possibly arch options can be
    given.
    """
    # Create the instance!
    target = target_class_map[name](options=options)
    return target
