pyinstaller -y --onefile --noupx -c --distpath=../../release/win --workpath=../tmp win.dumpscraper.spec
COPY ..\templates\settings-dist.json ..\..\release\win\settings-dist.json

pause