#!/bin/bash

set -eux -o pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"

python -V
python -m pip install -r "${script_dir}/requirements.txt"
python -m pip freeze

pyinstaller \
    --onefile \
    brigadier
