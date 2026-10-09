; Fleet Tauri: kill UI + backend before install/uninstall (backend locks resources/*.exe).
; AI-client registration runs via the vendored mcp-clients.nsh include below
; (canonical: mcp-central-docs/scripts/nsis/mcp-clients.nsh).
!define MCP_REG_NAME "arr-mcp"
!define MCP_REG_EXE "arr-mcp-backend.exe"
!include "mcp-clients.nsh"
!macro KillFleetSidecars
  DetailPrint "Stopping fleet processes..."
  ExecWait 'taskkill /F /IM arr-mcp-backend.exe /T' $0
  ExecWait 'taskkill /F /IM arr-mcp-native.exe /T' $0
  !if "${INSTALLMODE}" == "currentUser"
    nsis_tauri_utils::KillProcessCurrentUser "arr-mcp-backend.exe"
    Pop $0
    nsis_tauri_utils::KillProcessCurrentUser "arr-mcp-native.exe"
    Pop $0
  !else
    nsis_tauri_utils::KillProcess "arr-mcp-backend.exe"
    Pop $0
    nsis_tauri_utils::KillProcess "arr-mcp-native.exe"
    Pop $0
  !endif
  Sleep 2000
!macroend

!macro NSIS_HOOK_PREINSTALL
  !insertmacro KillFleetSidecars
!macroend

!macro NSIS_HOOK_PREUNINSTALL
  !insertmacro KillFleetSidecars
!macroend

!macro NSIS_HOOK_POSTINSTALL
  IfFileExists "$INSTDIR\resources\install-mcp-clients.ps1" 0 mcp_hook_done
    DetailPrint "Optional: register arr-mcp in Cursor / Claude Desktop"
    ExecWait 'powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$INSTDIR\resources\install-mcp-clients.ps1" -Interactive'
  mcp_hook_done:
!macroend
