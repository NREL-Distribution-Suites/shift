@ECHO OFF

pushd %~dp0

REM Command file for Jupyter Book documentation

if "%JUPYTERBOOK%" == "" (
	set JUPYTERBOOK=jupyter-book
)

%JUPYTERBOOK% >NUL 2>NUL
if errorlevel 9009 (
	echo.
	echo.The 'jupyter-book' command was not found. Make sure you have Jupyter Book
	echo.installed, then set the JUPYTERBOOK environment variable to point to
	echo.the full path of the 'jupyter-book' executable. Alternatively you may
	echo.add Jupyter Book to PATH.
	echo.
	echo.If you don't have Jupyter Book installed, grab it from
	echo.https://jupyterbook.org/
	exit /b 1
)

if "%1" == "" goto help

if "%1" == "clean" goto clean

if "%1" == "html" goto html

goto help

:html
%JUPYTERBOOK% build .
goto end

:clean
if exist _build rmdir /s /q _build
goto end

:help
echo Targets:
echo   make.bat html   Build Jupyter Book HTML docs
echo   make.bat clean  Remove build artifacts

:end
popd
