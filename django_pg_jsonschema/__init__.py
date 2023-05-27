from pkg_resources import DistributionNotFound, get_distribution

# Get the package version, or none if not installed.
try:
    __version__ = get_distribution('django-pg-jsonschema').version
except DistributionNotFound:
    __version__ = None
