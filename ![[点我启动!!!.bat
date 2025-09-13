@echo off
CHCP 65001

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

REM 使用项目自带的 Python 环境.
set "PYTHON_PATH=%~dp0runtime\python31211\bin\python.exe"

REM 检查项目自带的 Python 是否存在.
if not exist "%PYTHON_PATH%" (
    echo 错误：找不到项目自带的 Python 环境.
    echo 路径：%PYTHON_PATH%.
    echo 请确认 runtime\python31211\bin\python.exe 文件存在.
    pause
    exit /b 1
)

echo 使用项目自带的 Python: %PYTHON_PATH%

:start
REM 检查 runtime/.initialized 文件是否存在.
set "INITIALIZED_PATH=%~dp0runtime\.initialized"
if not exist "%INITIALIZED_PATH%" (
    echo 检测到 runtime/.initialized 不存在，正在执行模块更新...
    "%PYTHON_PATH%" update_modules.py
) else (
    echo runtime/.initialized 存在，跳过模块更新.
)

"%PYTHON_PATH%" main.py
pause