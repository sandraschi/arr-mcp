# Per-repo fleet start config for arr-mcp
# Edit ports/backend target here - start.ps1 is fleet-standard.
@{
    Name         = 'arr-mcp'
    BackendPort  = 10938
    FrontendPort = 10939
    HealthPath   = '/api/health'
    WebRoot      = 'webapp'
    Backend = @{
        Kind       = 'module-serve'
        Module     = 'arr_mcp'
        ServeArgs  = @('--http', '--port', '10938')
        SyncExtras = @('dev')
    }
    Frontend = @{
        Kind           = 'vite-npm'
        PackageManager = 'npm'
        PortEnvVar     = 'VITE_PORT'
        ApiTargetEnv   = 'VITE_API_TARGET'
    }
}
