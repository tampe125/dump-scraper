#!/usr/bin/env bash
pyinstaller -y --onefile --noupx -c --distpath=../../release/mac --workpath=../tmp mac.dumpscraper.spec
cp ../templates/settings-dist.json ../../release/mac/settings-dist.json
cp ../templates/run_dumpscraper.sh ../../release/mac/run_dumpscraper.sh