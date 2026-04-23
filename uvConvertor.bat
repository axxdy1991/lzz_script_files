@echo off
chcp 65001 >nul

echo 正在初始化依赖环境...

:: ==============================
:: 步骤 0: 查找当前目录下的 .uvprojx 文件
:: ==============================
set "PROJECT_FILE="
for %%f in (*.uvprojx) do (
    set "PROJECT_FILE=%%f"
    goto :FoundFile
)

:FoundFile
if "%PROJECT_FILE%"=="" (
    echo.
    echo 错误：在当前文件夹中未找到任何 .uvprojx 文件！
    echo 无法继续转换。
    pause
    exit /b
)
echo 找到项目文件: %PROJECT_FILE%
echo.

:: ==============================
:: 步骤 1: 检查并删除当前文件夹的 .dep 文件
:: ==============================
if exist "*.dep" (
    echo 检测到当前文件夹存在 .dep 文件，正在删除...
    del /q "*.dep"
    echo 删除完成。
) else (
    echo 当前文件夹无 .dep 文件，跳过删除。
)

:: ==============================
:: 步骤 2: 检查 Objects 文件夹并复制
:: ==============================
if exist ".\Objects\*.dep" (
    echo 正在从 Objects 文件夹复制 .dep 文件...
    copy ".\Objects\*.dep" ".\" >nul
    
    if %errorlevel% == 0 (
        echo 复制成功！
        goto :StartConvert
    ) else (
        echo.
        echo 错误：从 Objects 复制文件失败！
        pause
        exit /b
    )
) else (
    echo.
    echo 错误：Objects 文件夹中未找到 .dep 文件！
    echo 规则要求必须获取依赖文件。
    echo 转换终止。
    pause
    exit /b
)

:: ==============================
:: 步骤 3: 执行转换
:: ==============================
:StartConvert
echo.
echo 正在转换 Keil 项目...

REM 使用步骤 0 中找到的 %PROJECT_FILE% 变量
.\uvConvertor-CLI.exe -f ".\%PROJECT_FILE%" -o .\..\..\..\

if %errorlevel% == 0 (
    echo.
	if exist *.dep (
        echo 正在删除 .dep 文件...
        del /q *.dep
    )
    echo 转换成功！3秒后自动打开 Cursor...
    timeout /t 3 >nul
    if exist "C:\Users\zhengzhi.lu\AppData\Local\Programs\cursor\Cursor.exe" (
        start "" "C:\Users\zhengzhi.lu\AppData\Local\Programs\cursor\Cursor.exe" .\..\..\..\
    ) else (
        echo 警告：未找到 Cursor.exe，请检查路径。
        pause
    )
    exit
) else (
    echo.
    echo 转换失败！错误码：%errorlevel%
    pause
)