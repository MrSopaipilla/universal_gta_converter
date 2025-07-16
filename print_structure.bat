@echo off
title Ruta del Proyecto
echo =======================================
echo   ESTRUCTURA DEL PROYECTO
echo =======================================
echo.
echo Ruta: %~dp0
echo.
echo Contenido de la carpeta:
echo.
dir /b
echo.
echo Estructura con tree (si está disponible):
tree /f 2>nul || echo Tree no disponible - usar 'dir' para ver contenido
echo.
pause