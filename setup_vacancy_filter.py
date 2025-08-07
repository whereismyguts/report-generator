#!/usr/bin/env python3
"""
Setup script for vacancy filtering system
Helps with initial configuration and testing
"""

import sys
import os

# Add package to path if needed
package_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if package_path not in sys.path:
    sys.path.insert(0, package_path)

# Import from the new module structure
from ks_reporter.scripts.setup_vacancy_filter import main

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
