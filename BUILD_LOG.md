# Build Log

## Build Failure - 2026-08-26 14:39:53

### Build FAILED (exit 1)
```njust.exe : Set-Location 'D:\Dev\repos\arr-mcp\native'
At C:\Users\sandr\.gemini\antigravity\brain\be84629a-7705-4f3a-898a-e5f3e12f7306\scratch\build_15_repos.ps1:127 char:20
+     $buildOutput = & just build-native 2>&1
+                    ~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : NotSpecified: (Set-Location 'D...arr-mcp\native':String) [], RemoteException
    + FullyQualifiedErrorId : NativeCommandError
 
$env:Path = "$env:USERPROFILE\.cargo\bin;$env:Path"
.\build.ps1
.\build.ps1 : The term '.\build.ps1' is not recognized as the name of a cmdlet, function, script file, or operable 
program. Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
At line:1 char:1
+ .\build.ps1
+ ~~~~~~~~~~~
    + CategoryInfo          : ObjectNotFound: (.\build.ps1:String) [], CommandNotFoundException
    + FullyQualifiedErrorId : CommandNotFoundException
 
error: Recipe `build-native` failed on line 32 with exit code 1

```
