@echo off
chcp 65001 >nul
title 创建初始化标记文件

echo =====================================================================
echo  创建 .initialized 标记文件
echo  用于手动标记一键包已初始化完成，跳过首次运行的初始化流程
echo =====================================================================
echo.

REM 设置路径
set "RUNTIME_PATH=%~dp0runtime"
set "INITIALIZED_PATH=%RUNTIME_PATH%\.initialized"

REM 检查 runtime 目录是否存在，不存在则创建
if not exist "%RUNTIME_PATH%" (
    echo 正在创建 runtime 目录...
    mkdir "%RUNTIME_PATH%"
)

REM 创建 .initialized 文件
echo initialized> "%INITIALIZED_PATH%"

if exist "%INITIALIZED_PATH%" (
    echo.
    echo ✓ 已成功创建初始化标记文件: %INITIALIZED_PATH%
    echo 下次启动时将跳过首次运行的初始化流程
) else (
    echo.
    echo ✗ 创建标记文件失败，请检查是否有写入权限
)

echo.
pause
