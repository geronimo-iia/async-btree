from pkg_resources import DistributionNotFound, get_distribution

from .analyze import Node, analyze, stringify_analyze
from .control import decision, fallback, repeat_until, selector, sequence
from .decorator import (
    alias,
    always_failure,
    always_success,
    decorate,
    inverter,
    is_failure,
    is_success,
    retry,
    retry_until_failed,
    retry_until_success,
)
from .definition import (
    FAILURE,
    SUCCESS,
    AsyncInnerFunction,
    CallableFunction,
    ExceptionDecorator,
    NodeMetadata,
    node_metadata,
)
from .leaf import action, condition
from .parallele import parallele
from .utils import afilter, amap, run


__all__ = [
    'Node',
    'analyze',
    'stringify_analyze',
    'decision',
    'fallback',
    'repeat_until',
    'selector',
    'sequence',
    'alias',
    'always_failure',
    'always_success',
    'decorate',
    'inverter',
    'is_failure',
    'is_success',
    'retry',
    'retry_until_failed',
    'retry_until_success',
    'FAILURE',
    'SUCCESS',
    'AsyncInnerFunction',
    'CallableFunction',
    'ExceptionDecorator',
    'NodeMetadata',
    'node_metadata',
    'action',
    'condition',
    'parallele',
    'afilter',
    'amap',
    'run',
]

try:
    __version__ = get_distribution('async-btree').version
except DistributionNotFound:  # pragma: no cover
    __version__ = '(local)'
