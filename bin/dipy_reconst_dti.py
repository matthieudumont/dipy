#! /usr/bin/env python

from __future__ import division, print_function

from dipy.workflows.flow_runner import run_flow
from dipy.workflows.reconst import ReconstDtiFlow

if __name__ == "__main__":
    run_flow(ReconstDtiFlow())
