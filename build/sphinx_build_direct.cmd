@echo off
REM Used for build scripts
SET WORK_DIR=%~dp0
SET SPHINX_DIR=C:\TOOLS\python\Python35\Scripts
SET PYTHON35_DIR=C:\TOOLS\python\Python35
SET SPHINX_BUILD=sphinx_build.exe
SET SPHINX_APIDOC=sphinx-apidoc.exe
SET BUILD_DOC_DIR=doc_build
set PYTHONHOME=c:\TOOLS\python\python35
set PYTHONPATH="%PYTHONHOME%\lib\site-packages\Pythonwin";"%PYTHONHOME%\lib\site-packages\win32";"%PYTHONHOME%\lib\site-packages\win32\lib";"%PYTHONHOME%\lib\site-packages\win32com";"%PYTHONHOME%\DLLs";"%PYTHONHOME%\lib";"%PYTHONHOME%\lib\plat-win";"%PYTHONHOME%\lib\lib-tk";"%PYTHONHOME%";"%PYTHONHOME%\lib\site-packages";"%PYTHONHOME%\lib\site-packages\wx-2.8-msw-unicode"

echo Running %SPHINX_DIR%\%SPHINX_BUILD%
echo In: %WORK_DIR%

cd source
%SPHINX_DIR%\sphinx-build.exe -T -a -b html %WORK_DIR%source %WORK_DIR%\doc
cd ..
pause