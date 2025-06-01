@echo off 
echo PyInstaller packaging completed! 
echo. 
 
:: Create installer 
echo [3/5] Creating installer... 
mkdir "setup_files" 
copy "%OUTPUT_DIR%\%PROJECT_NAME%.exe" "setup_files\" 
 
:: Create installation script 
echo @echo off > "setup_files\install.bat" 
echo echo Installing %PROJECT_NAME%... >> "setup_files\install.bat" 
echo set INSTALL_DIR=%%USERPROFILE%%\%PROJECT_NAME% >> "setup_files\install.bat" 
echo if not exist "%%INSTALL_DIR%%" mkdir "%%INSTALL_DIR%%" >> "setup_files\install.bat" 
echo copy /y "%PROJECT_NAME%.exe" "%%INSTALL_DIR%%\" >> "setup_files\install.bat" 
echo powershell "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%%USERPROFILE%%\Desktop\%PROJECT_NAME%.lnk'); $Shortcut.TargetPath = '%%INSTALL_DIR%%\%PROJECT_NAME%.exe'; $Shortcut.Save()" >> "setup_files\install.bat" 
echo echo Installation completed! >> "setup_files\install.bat" 
echo pause >> "setup_files\install.bat" 
echo start "" "%%INSTALL_DIR%%\%PROJECT_NAME%.exe" >> "setup_files\install.bat" 
 
:: Create self-extracting launcher 
echo @echo off > "setup_files\setup.bat" 
echo call install.bat >> "setup_files\setup.bat" 
 
:: Create zip file 
echo [4/5] Creating installer package... 
powershell -Command "Compress-Archive -Path 'setup_files\*' -DestinationPath '%INSTALLER_NAME%.zip' -Force" 
copy /b "%INSTALLER_NAME%.zip" "..\%INSTALLER_NAME%.exe" 
echo Installer package created! 
echo. 
 
:: Clean temporary files 
echo [5/5] Cleaning temporary files... 
rd /s /q "setup_files" 
del "%INSTALLER_NAME%.zip" 
echo Cleaning completed! 
echo. 
 
echo ================================================= 
echo             Packaging process completed! 
echo ================================================= 
echo. 
echo Generated files: 
echo - Executable: %OUTPUT_DIR%\%PROJECT_NAME%.exe 
echo - Installer: ..\%INSTALLER_NAME%.exe 
echo. 
echo You can distribute the %INSTALLER_NAME%.exe file to users. 
echo. 
pause 
