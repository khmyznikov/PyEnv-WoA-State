
## Test suites to check compatibility of Python libraries with Windows arm64

### compat_run - handpicked set of onnx oriented libraries and workflows

Run from PowerShell Admin:
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

#### Parameters

- pythonPath: Path to python executable
- hfToken: Hugging Face API token
- Debug: Debug mode (temp files are not deleted)
- useCacheDir: Use python cache directory
- librariesToTest: Custom list of libraries to test
- workflowsToTest: Custom list of workflows to test

#### Example

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


### common installation fixes
```
& "C:\Program Files\Microsoft Visual Studio\2022\Enterprise\VC\Auxiliary\Build\vcvarsarm64.bat"
$env:TEMP = "C:/temp"
$env:TMP = "C:/temp"
```