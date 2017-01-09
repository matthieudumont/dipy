#!python

from __future__ import division, print_function

from dipy.workflows.flow_runner import run_flow
from dipy.workflows.io import UncompressFlow

if __name__ == "__main__":
    run_flow(UncompressFlow())
