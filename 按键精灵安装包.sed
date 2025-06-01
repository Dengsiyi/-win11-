[Version]
Class=IEXPRESS
SEDVersion=3
[Options]
PackagePurpose=InstallApp
ShowInstallProgramWindow=1
HideExtractAnimation=0
UseLongFileName=1
InsideCompressed=0
CAB_FixedSize=0
CAB_ResvCodeSigning=0
RebootMode=N
InstallPrompt=%InstallPrompt%
DisplayLicense=%DisplayLicense%
FinishMessage=%FinishMessage%
TargetName=%TargetName%
FriendlyName=%FriendlyName%
AppLaunched=%AppLaunched%
PostInstallCmd=%PostInstallCmd%
AdminQuietInstCmd=%AdminQuietInstCmd%
UserQuietInstCmd=%UserQuietInstCmd%
SourceFiles=SourceFiles

[Strings]
InstallPrompt=确定要安装按键精灵吗？
DisplayLicense=
FinishMessage=安装完成！
TargetName=D:\STARAIGAMEPLAY\anjianjingling\按键精灵安装包.exe
FriendlyName=按键精灵 - Windows 11自动化工具
AppLaunched=install.bat
PostInstallCmd=
AdminQuietInstCmd=
UserQuietInstCmd=
FILE0="按键精灵.exe"
FILE1="install.bat"

[SourceFiles]
SourceFiles0=D:\STARAIGAMEPLAY\anjianjingling\dist
SourceFiles1=D:\STARAIGAMEPLAY\anjianjingling

[SourceFiles0]
%FILE0%=

[SourceFiles1]
%FILE1%=
