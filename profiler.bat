@echo off
setlocal EnableDelayedExpansion
title Chay Libass Profiler Hang Loat
color 0A

:: Yeu cau nhap danh sach tap
set /p EP_LIST="Nhap danh sach tap can xu ly (VD: 1 3 5 09 12 hoac 80-90): "

:: Kiem tra dieu kien nhap
if "!EP_LIST!"=="" (
    echo Ban chua nhap tap nao!
    pause
    exit /b
)

echo.
echo ====================================================
echo BAT DAU XU LY CAC TAP: !EP_LIST!
echo ====================================================
echo.

:: Vong lap xu ly tung phan tu trong danh sach
FOR %%I IN (!EP_LIST!) DO (
    set "ITEM=%%I"
    
    :: Kiem tra xem phan tu co chua dau "-" khong
    if "!ITEM:-=!"=="!ITEM!" (
        :: Neu khong co dau "-", xu ly nhu 1 tap don le
        call :ProcessEpisode !ITEM!
    ) else (
        :: Neu co dau "-", xu ly nhu 1 khoang (range)
        for /F "tokens=1,2 delims=-" %%A in ("!ITEM!") do (
            set "START=%%A"
            set "END=%%B"
            
            :: Loai bo so 0 o dau de mang khong bi loi he co so 8 (Octal)
            if "!START:~0,1!"=="0" set "START=!START:~1!"
            if "!START:~0,1!"=="0" set "START=!START:~1!"
            if "!END:~0,1!"=="0" set "END=!END:~1!"
            if "!END:~0,1!"=="0" set "END=!END:~1!"
            
            :: Vong lap tu START den END
            for /L %%J in (!START!, 1, !END!) do (
                call :ProcessEpisode %%J
            )
        )
    )
)

echo ====================================================
echo DA XU LY XONG TOAN BO DANH SACH!
echo ====================================================
pause
exit /b

:: ========================================================
:: HAM XU LY TUNG TAP PHIM (Subroutine)
:: ========================================================
:ProcessEpisode
set "EP=%1"

:: Gan vao bien EP va tu dong them so 0 neu la so co 1 chu so
if "%EP:~1,1%"=="" set "EP=0%EP%"

echo ----------------------------------------------------
echo [*] DANG XU LY TAP %EP%...
echo ----------------------------------------------------

:: Kiem tra xem file .ass co ton tai khong de tranh loi
if exist "D:\fansub\Shingeki-no-Kyojin\OVA %EP%\SGKOVA %EP% - TS.ass" (
    :: 1. Chay profiler
    libass_profiler.exe "D:\fansub\Shingeki-no-Kyojin\OVA %EP%\SGKOVA %EP% - TS.ass"
    
    :: 2. Chay python tao bieu do
    "C:\Users\ACER\AppData\Local\Programs\Python\Python312\python.exe" graph.py -i output.csv -o AoT_OVA_%EP%.png
    
    echo [OK] Da hoan thanh tap %EP%!
) else (
    echo [LOI] Khong tim thay file "Shingeki %EP% - TS.ass". Bo qua tap nay!
)
echo.
exit /b