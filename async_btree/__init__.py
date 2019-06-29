from pkg_resources import DistributionNotFound, get_distribution

from .definition import (
    CallableFunction,
    SUCCESS,
    FAILURE,
    ExceptionDecorator,
    NodeMetadata,
    node_metadata,
)

from .analyze import (
    Node,
    analyze,
    print_analyze
)

from .utils import (
    amap,
    afilter
)

try:
    __version__ = get_distribution('async-btree').version
except DistributionNotFound:
    __version__ = '(local)'
