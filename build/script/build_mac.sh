#!/usr/bin/env bash
pyinstaller -y --onefile --noupx -c --distpath=../../release/mac --workpath=../tmp mac.dumpscraper.spec