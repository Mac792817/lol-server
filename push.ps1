#!/usr/bin/env pwsh
<#
.SYNOPSIS
Git自动推送脚本

.DESCRIPTION
一键提交并推送代码到GitHub，自动生成时间戳作为提交消息
#>

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "          Git 自动推送脚本" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# 检查是否有未跟踪的文件
$untracked = git status | Select-String "Untracked files:"
if ($untracked) {
    Write-Host "发现新文件，正在添加..." -ForegroundColor Yellow
    git add .
}

# 检查是否有修改的文件
$modified = git status | Select-String "modified:"
if ($modified) {
    Write-Host "发现修改的文件，正在添加..." -ForegroundColor Yellow
    git add .
}

# 生成时间戳作为提交消息
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
$commitMsg = "update: $timestamp"

Write-Host ""
Write-Host "提交消息: $commitMsg" -ForegroundColor Green
git commit -m $commitMsg

Write-Host ""
Write-Host "正在推送到 GitHub..." -ForegroundColor Yellow
git push origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Green
    Write-Host "          ✅ 推送成功！" -ForegroundColor Green
    Write-Host "============================================" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Red
    Write-Host "          ❌ 推送失败，请检查网络或配置" -ForegroundColor Red
    Write-Host "============================================" -ForegroundColor Red
}

Write-Host ""
Read-Host "按 Enter 键退出"