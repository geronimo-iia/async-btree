from pkg_resources import DistributionNotFound, get_distribution


try:
    __version__ = get_distribution('async-btree').version
except DistributionNotFound:
    __version__ = '(local)'
