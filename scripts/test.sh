#!/usr/bin/env bash
set -euo pipefail
python -m scripts.build_fixtures
python -m unittest discover -s tests -v
python -m scripts.run_afims_t
python -m scripts.verify_release
python -m scripts.run_final_confidence
python -m scripts.build_release_readiness
python -m scripts.check_external_tools
