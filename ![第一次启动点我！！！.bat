@echo off
setlocal enabledelayedexpansion

chcp 65001 >nul

REM 检测是否在压缩包内运行
set "CURRENT_PATH=%~dp0"
echo %CURRENT_PATH% | findstr /i "temp" >nul && set "IN_ARCHIVE=1" || set "IN_ARCHIVE=0"
echo %CURRENT_PATH% | findstr /i "tmp" >nul && set "IN_ARCHIVE=1"
echo %CURRENT_PATH% | findstr /i "rar$" >nul && set "IN_ARCHIVE=1"
echo %CURRENT_PATH% | findstr /i "zip$" >nul && set "IN_ARCHIVE=1"
echo %CURRENT_PATH% | findstr /i "7z$" >nul && set "IN_ARCHIVE=1"

if "%IN_ARCHIVE%"=="1" (
    echo -   
    echo ==========================================.
    echo        我草，你是不是脑子有坑啊？
    echo ==========================================.
    echo -
    echo 你™直接在压缩包里运行脚本？你是天才还是傻逼？.
    echo 这种操作也就你能想得出来，孙笑川都得给你磕一个！.
    echo -
    echo 你™不知道解压吗？小学没毕业？.
    echo -
    echo 赶紧给老子滚去解压！.
    echo 要不然程序出了问题，老子可不管！.
    echo -
    echo 操你妈的，赶紧按任意键给老子滚蛋！.
    echo ==========================================.
    echo -
    echo 按任意键退出，然后给老子滚去解压！.
    echo 以上所有文字由Gemini AI生成，如果有任何不满，请投诉Gemini谢谢.
    pause >nul
    exit /b 1
)

REM 保存当前目录
set "CURRENT_DIR=%CD%"

REM 查找所有 Python 版本
echo 正在查找 Python 版本...
for /f "tokens=*" %%i in ('where python') do (
    echo 检查 Python 路径: %%i
    "%%i" -c "import sys; exit(0) if sys.version_info[0] == 3 and sys.version_info[1] == 12 else exit(1)" && (
        set "PYTHON_PATH=%%i"
        goto :found_python
    )
)

echo 未找到符合要求的 Python 版本（3.12.x），将尝试自动安装 Python 3.12.8...

REM 下载Python 3.12.8安装包
powershell -Command "(New-Object System.Net.WebClient).DownloadFile('https://mirrors.aliyun.com/python-release/windows/python-3.12.8-amd64.exe', 'python-3.12.8-amd64.exe')"
if not exist "python-3.12.8-amd64.exe" (
    echo 下载Python安装包失败.
    pause
    exit /b 1
)
echo.
echo Python 安装包已下载为 python-3.12.8-amd64.exe.
echo 请手动运行此安装程序完成 Python 3.12.8 的安装.
echo 安装时请确保勾选 "Add Python 3.12 to PATH" 选项.
echo 安装完成后，请重新运行此脚本.
echo.
pause
exit /b 1

:found_python
echo 找到符合要求的 Python: %PYTHON_PATH%

REM 检查虚拟环境是否存在且可用
if exist "venv" (
    echo 检测到现有虚拟环境，正在检查是否可用...
    call venv\Scripts\activate.bat
    python -c "import sys; exit(0) if sys.version_info[0] == 3 and sys.version_info[1] == 12 else exit(1)" && (
        echo 虚拟环境可用
        goto :choose_pip_source
    )
    echo 虚拟环境不可用，将创建新的虚拟环境
    rmdir /s /q venv
)

echo 正在创建虚拟环境...
"%PYTHON_PATH%" -m venv venv
call venv\Scripts\activate.bat

:choose_pip_source
echo.
echo 请选择pip下载源:
echo 1. 阿里云 (https://mirrors.aliyun.com/pypi/simple) [推荐]
echo 2. 清华 (https://pypi.tuna.tsinghua.edu.cn/simple)
echo 3. 豆瓣 (https://pypi.douban.com/simple)
echo 4. 官方 (https://pypi.org/simple)
set /p PIP_SRC_CHOICE=请输入数字选择 [1-4]，回车默认1:
if "%PIP_SRC_CHOICE%"=="" set PIP_SRC_CHOICE=1
if "%PIP_SRC_CHOICE%"=="1" set PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple
if "%PIP_SRC_CHOICE%"=="2" set PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
if "%PIP_SRC_CHOICE%"=="3" set PIP_INDEX_URL=https://pypi.douban.com/simple
if "%PIP_SRC_CHOICE%"=="4" set PIP_INDEX_URL=https://pypi.org/simple

:install_deps
REM 更新 pip
echo 正在更新 pip...
python -m pip install -i %PIP_INDEX_URL% --upgrade pip

REM 安装依赖
echo 正在安装依赖...
pip install -i %PIP_INDEX_URL% -r requirements.txt --upgrade

REM 调用init_napcat.py更新配置

python init_napcat.py

echo 安装完成！请运行启动脚本！

REM 调用config_manager.py

python config_manager.py
echo.

pause