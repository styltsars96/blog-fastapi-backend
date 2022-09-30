#!/usr/bin/env bash

# DEV NOTE: How to exclude development tools and other non-essential requirements, and put them in dev_extra_req.txt
# Follow these steps create exclusion lines, when a non-essential requirement has been added to add bellow... BASH:
# pip freeze > temp.txt
# comm --nocheck-order -13 requirements.txt temp.txt | grep -v "pkg-resources==" | grep -v "pkg_resources==" > dev_extra_requirements.txt # This keeps all the dev extras in another file
# rm temp.txt
# cat dev_extra_requirements.txt | cut -d'=' -f1 > temp.txt
# sed 's/^/grep -v "/; s/$/==" |/' temp.txt # copy this output and paste them bellow the | grep -v "pkg_resources==" \ and replace all for changes!
# rm temp.txt

# Install extra development tool requirements with:
# pip install -r dev_extra_req.txt

cd "$(dirname "$0")"/.. || exit

# shellcheck disable=SC1091
source venv/bin/activate

# NOTE: Add this in order to exclude requirement: grep -v "my_excluded_package==" |
pip freeze |
    grep -v "pkg-resources" |
    grep -v "pkg_resources" |
    grep -v "black==" |
    grep -v "mccabe==" |
    grep -v "pylint==" |
    grep -v "flake8" >requirements.txt
