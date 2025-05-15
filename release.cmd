rm -r ./dist
pyinstaller -F --collect-submodules "bpy" --noconsole --collect-all "bpy" --icon=./resource/deps/Helldivers.ico .\StratagemIconManager.py
cp ./readme.txt ./dist/
cp ./IconData.json ./dist/
cp ./resource/deps/Helldivers.ico ./dist/
rm ./resource/deps/save_data.json
rm -r ./resource/temp
xcopy /i /s /e /y "./resource" "./dist/resource"
xcopy /i /s /e /y "./EditableSheets" "./dist/EditableSheets"
pause