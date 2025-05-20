## Test suites and track issues regarding the compatibility of Python libraries with Windows Arm64

This repository contains scripts to test compatibility of Python libraries with Windows Arm64 as well as performance benchmarks between x64 and Arm64.

Check the **[list of libraries🐍](https://github.com/khmyznikov/PyEnv-WoA-State/issues/1)** that have known compatibility issues with Windows Arm64


### get_missing_wheels

Get the list of top 1000 libraries from PyPi and filter out the ones that are not available for Arm64.

```powershell
python get_missing_wheels.py
```

```powershell
.\test_missing_wheels.ps1 -PackageListFile "log\missing_packages_list_2025-10-30_15-30-45.txt" -pythonPath "C:\Program Files\Python312\python.exe" -RetainEnvironments -useCacheDir
```

### compat_run
handpicked set of ML oriented libraries and workflows

```powershell
.\compat_run.ps1 -pythonPath "C:\Program Files\Python312\python.exe" -hfToken "TOKEN" -Debug
```

#### Typical python path
```
"C:\Users\${USER}\AppData\Local\Programs\Python\${VERSION}\python.exe"
"C:\Program Files\${VERSION}\python.exe"
```

#### Requirements

* [Latest VC Redist](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170#latest-microsoft-visual-c-redistributable-version)
* [Visual Studio with C++ development package](https://visualstudio.microsoft.com/thank-you-downloading-visual-studio/?sku=Community&channel=Release&version=VS2022)

#### common installation fixes
```
& "C:\Program Files\Microsoft Visual Studio\2022\Enterprise\VC\Auxiliary\Build\vcvarsarm64.bat"
$env:TEMP = "C:/temp"
$env:TMP = "C:/temp"
```

#### Parameters

- *pythonPath*: Path to python executable
- *hfToken*: Hugging Face API token
- *Debug*: Debug mode (temp files are not deleted)
- *useCacheDir*: Use python cache directory
- *librariesToTest*: Custom list of libraries to test
- *workflowsToTest*: Custom list of workflows to test

### Examples

#### skip all tests
```powershell
.\compat_run.ps1 -pythonPath "C:\Program Files\Python312\python.exe"  -librariesToTest @() -workflowsToTest @()
```
#### run some tests
```powershell
.\compat_run.ps1 -pythonPath "C:\Program Files\Python312\python.exe"  -librariesToTest "pandas", "scipy" -workflowsToTest "torch", "olive"
```

## perf_run
performance benchmark between x64 and arm64 (or between any two versions of python)

```powershell
.\perf_run.ps1 -pythonPath1 "C:\Program Files\Python312\python.exe" -pythonPath2 "C:\Users\AppData\Local\Programs\Python\Python312-arm64\python.exe"
```