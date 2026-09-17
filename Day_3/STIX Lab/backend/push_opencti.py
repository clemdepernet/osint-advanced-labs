#!/usr/bin/env python3
"""push_opencti.py - load a bundle into OpenCTI (TP part 4e, reference).

OpenCTI is the team knowledge graph. This is how a bundle lands there via pycti.
Reference only: it needs a running OpenCTI instance + token, so it is not run in
class. Read it to understand the last hop of the pipeline.
    pip install pycti
    export OPENCTI_URL=... OPENCTI_TOKEN=...
"""
from __future__ import annotations
import os, pathlib

EXAMPLE = '''
from pycti import OpenCTIApiClient
client = OpenCTIApiClient(os.environ["OPENCTI_URL"], os.environ["OPENCTI_TOKEN"])
bundle = pathlib.Path("data/bundle.json").read_text()
client.stix2.import_bundle_from_json(bundle, update=True)   # idempotent upsert
# TAXII alternative: POST the bundle to a TAXII 2.1 collection with taxii2-client.
'''

if __name__ == "__main__":
    print("Reference only - see the code below. Needs a running OpenCTI + token.")
    print(EXAMPLE)
