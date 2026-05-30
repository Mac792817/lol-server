@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ============================================
echo         Git 自动推送脚本
echo ============================================

:: 检查是否有未跟踪的文件
git status | findstr "Untracked files:" >nul
if %errorlevel% equ 0 (
    echo 发现新文件，正在添加...
    git add .
)

:: 检查是否有修改的文件
git status | findstr "modified:" >nul
if %errorlevel% equ 0 (
    echo 发现修改的文件，正在添加...
    git add .
)

:: 生成时间戳作为提交消息
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (
    set "month=%%a"
    set "day=%%b"
    set "year=%%c"
)
for /f "tokens=1-2 delims=: " %%a in ('time /t') do (
    set "hour=%%a"
    set "minute=%%b"
)
set "commit_msg=update: %year%-%month%-%day% %hour%:%minute%"

echo.
echo 提交消息: !commit_msg!
git commit -m "!commit_msg!"

echo.
echo 正在推送到 GitHub...
git push origin main

if %errorlevel% equ 0 (
    echo.
    echo ============================================
    echo         ✅ 推送成功！
    echo ============================================
) else (
    echo.
    echo ============================================
    echo         ❌ 推送失败，请检查网络或配置
    echo ============================================
)

pause