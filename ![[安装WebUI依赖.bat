@echo off
chcp 65001 >nul
setlocal

echo.
echo ==============================================.
echo          MaiBot WebUI 依赖安装工具.
echo ==============================================.
echo.

:: 获取当前脚本所在目录
set "SCRIPT_DIR=%~dp0"
set "NODEJS_DIR=%SCRIPT_DIR%runtime\nodejs"
set "PNPM_PATH=%NODEJS_DIR%\pnpm.cmd"
set "HMML_DEMON_DIR=%SCRIPT_DIR%modules\HMMLDemon"

:: 显示路径信息（调试用）
echo.
echo [调试] 脚本目录: %SCRIPT_DIR%.
echo [调试] Node.js 目录: %NODEJS_DIR%.
echo [调试] pnpm 路径: %PNPM_PATH%.
echo [调试] HMMLDemon 目录: %HMML_DEMON_DIR%.
echo.

:: 检查必要路径是否存在
echo.
echo [检查] 验证必要文件和目录....
echo.

if not exist "%NODEJS_DIR%" (
    echo.
    echo [错误] Node.js 路径不存在: %NODEJS_DIR%.
    echo        请确保一键包完整性.
    echo.
    pause
    exit /b 1
)

if not exist "%PNPM_PATH%" (
    echo.
    echo [错误] pnpm 可执行文件不存在: %PNPM_PATH%.
    echo        请确保 Node.js 运行时完整.
    echo.
    pause
    exit /b 1
)

if not exist "%HMML_DEMON_DIR%" (
    echo.
    echo [错误] HMMLDemon 模块路径不存在: %HMML_DEMON_DIR%.
    echo        请确保模块已正确下载.
    echo.
    pause
    exit /b 1
)

if not exist "%HMML_DEMON_DIR%\package.json" (
    echo.
    echo [错误] package.json 文件不存在: %HMML_DEMON_DIR%\package.json.
    echo        请确保 HMMLDemon 模块完整.
    echo.
    pause
    exit /b 1
)

echo.
echo [成功] 所有必要文件检查通过.
echo.

:: 设置环境变量
echo.
echo [信息] 设置 Node.js 环境变量....
echo.
set "PATH=%NODEJS_DIR%;%PATH%"
set "NODE_PATH=%NODEJS_DIR%\node_modules"
set "npm_config_prefix=%NODEJS_DIR%"

:: 验证 Node.js 是否可用
echo [验证] 检查 Node.js 环境....
"%NODEJS_DIR%\node.exe" --version
if %errorlevel% neq 0 (
    echo.
    echo [错误] Node.js 无法正常运行.
    echo        请检查 Node.js 运行时是否完整.
    echo.
    pause
    exit /b 1
)
echo [成功] Node.js 环境验证通过.

:: 显示当前目录
echo.
echo [调试] 当前工作目录: %CD%.
echo [调试] 即将切换到: %HMML_DEMON_DIR%.
echo.

:: 切换到 HMMLDemon 目录
cd /d "%HMML_DEMON_DIR%"
echo.
echo [调试] 切换后当前目录: %CD%.
echo.

:: 尝试安装依赖
echo.
echo ==============================================.
echo          开始安装 WebUI 依赖.
echo ==============================================.
echo.

:: 尝试淘宝源
echo.
echo [尝试 1/4] 使用淘宝源: https://registry.npmmirror.com.
echo [执行] 正在使用淘宝源安装依赖....
echo [命令] "%PNPM_PATH%" install --registry https://registry.npmmirror.com.
echo.
"%PNPM_PATH%" install --registry https://registry.npmmirror.com -C %HMML_DEMON_DIR%
if %errorlevel% equ 0 (
    echo.
    echo ==============================================.
    echo          依赖安装成功！.
    echo ==============================================.
    echo [成功] 使用淘宝源成功安装 WebUI 依赖.
    echo [路径] %HMML_DEMON_DIR%.
    echo.
    echo 现在您可以正常使用 WebUI 功能了！.
    echo.
    pause
)
echo.
echo [失败] 使用淘宝源安装依赖失败，尝试下一个源....
echo.

:: 尝试腾讯源
echo.
echo [尝试 2/4] 使用腾讯源: https://mirrors.cloud.tencent.com/npm/.
echo [执行] 正在使用腾讯源安装依赖....
echo [命令] "%PNPM_PATH%" install --registry https://mirrors.cloud.tencent.com/npm/.
echo.
"%PNPM_PATH%" install --registry https://mirrors.cloud.tencent.com/npm/ -C %HMML_DEMON_DIR%
if %errorlevel% equ 0 (
    echo.
    echo ==============================================.
    echo          依赖安装成功！.
    echo ==============================================.
    echo [成功] 使用腾讯源成功安装 WebUI 依赖.
    echo [路径] %HMML_DEMON_DIR%.
    echo.
    echo 现在您可以正常使用 WebUI 功能了！.
    echo.
    pause
)
echo.
echo [失败] 使用腾讯源安装依赖失败，尝试下一个源....
echo.

:: 尝试华为源
echo.
echo [尝试 3/4] 使用华为源: https://repo.huaweicloud.com/repository/npm/.
echo [执行] 正在使用华为源安装依赖....
echo [命令] "%PNPM_PATH%" install --registry https://repo.huaweicloud.com/repository/npm/.
echo.
"%PNPM_PATH%" install --registry https://repo.huaweicloud.com/repository/npm/ -C %HMML_DEMON_DIR%
if %errorlevel% equ 0 (
    echo.
    echo ==============================================.
    echo          依赖安装成功！.
    echo ==============================================.
    echo [成功] 使用华为源成功安装 WebUI 依赖.
    echo [路径] %HMML_DEMON_DIR%.
    echo.
    echo 现在您可以正常使用 WebUI 功能了！.
    echo.
    pause
)
echo.
echo [失败] 使用华为源安装依赖失败，尝试下一个源....
echo.

:: 尝试官方源
echo.
echo [尝试 4/4] 使用官方源: https://registry.npmjs.org.
echo [执行] 正在使用官方源安装依赖....
echo [命令] "%PNPM_PATH%" install --registry https://registry.npmjs.org.
echo.
"%PNPM_PATH%" install --registry https://registry.npmjs.org -C %HMML_DEMON_DIR%
if %errorlevel% equ 0 (
    echo.
    echo ==============================================.
    echo          依赖安装成功！.
    echo ==============================================.
    echo [成功] 使用官方源成功安装 WebUI 依赖.
    echo [路径] %HMML_DEMON_DIR%.
    echo.
    echo 现在您可以正常使用 WebUI 功能了！.
    echo.
    pause
)
echo.
echo [失败] 使用官方源安装依赖失败.
echo.

:: 所有源都失败了
echo.
echo ==============================================.
echo          依赖安装失败！.
echo ==============================================.
echo [错误] 所有 npm 源都尝试失败.
echo.
echo 可能的解决方案：.
echo 1. 检查网络连接是否正常.
echo 2. 检查防火墙设置.
echo 3. 尝试使用 VPN 或代理.
echo 4. 手动进入 modules\HMMLDemon 目录执行 pnpm install.
echo.
echo 手动安装命令：.
echo   cd "%HMML_DEMON_DIR%".
echo   "%PNPM_PATH%" install.
echo.
pause
