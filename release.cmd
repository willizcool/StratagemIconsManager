rm -r ./dist
pyinstaller -F --noconsole --icon=./resource/deps/Helldivers.ico .\StratagemIconManager.py
cp ./readme.md ./dist/readme.txt
cp ./IconData.json ./dist/
cp ./resource/deps/Helldivers.ico ./dist/
rm ./resource/deps/save_data.json
rm -r ./resource/temp
xcopy /i /s /e /y "./resource" "./dist/resource"
xcopy /i /s /e /y "./EditableSheets" "./dist/EditableSheets"
pause