# -*- coding: utf-8 -*-

"""seamm_dashboard_client
Plots for computational materials/molecular science
"""

# Bring up the classes so that they appear to be directly in
# the seamm_dashboard_client

# Main classes
from .dashboard import Dashboard  # noqa: F401
from .dashboard import DashboardConnectionError  # noqa: F401
from .dashboard import DashboardLoginError  # noqa: F401
from .dashboard import DashboardNotRunningError  # noqa: F401
from .dashboard import DashboardSubmitError  # noqa: F401
from .dashboard import DashboardTimeoutError  # noqa: F401
from .dashboard import DashboardUnknownError  # noqa: F401

# Handle versioneer
from ._version import get_versions

__author__ = """Paul Saxe"""
__email__ = "psaxe@molssi.org"
versions = get_versions()
__version__ = versions["version"]
__git_revision__ = versions["full-revisionid"]
del get_versions, versions
