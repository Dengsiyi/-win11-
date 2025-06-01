@echo off
echo Fixing directory names...
if exist "toolsX" ren "toolsX" "tools"

echo Deleting unnecessary files...
if exist "按键精灵.spec" del "按键精灵.spec"
if exist "按键精灵安装包.sed" del "按键精灵安装包.sed"

echo Done!
