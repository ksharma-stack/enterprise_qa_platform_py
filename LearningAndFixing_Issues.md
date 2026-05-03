# Command to fix UTF-16 to UTF-8 that happen when we create a file using cmd

## powershell -Command "Get-ChildItem 'c:\Users\kanchan.sharma\Documents\WS\SelfLearning\1_Python\enterprise_qa_platform\src\framework\core\utils\*.py' | ForEach-Object { [System.IO.File]::ReadAllText(`$_.FullName) | Out-File -FilePath `$_.FullName -Encoding UTF8 }"