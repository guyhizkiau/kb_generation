<# 
Test-Entra-ClientSecret.ps1
Purpose: Validate that a client secret works by obtaining a token via client_credentials.
Requirements: The app must have at least one application permission consented if you plan to call an API.
By default we just fetch/parse the token, which proves the secret is valid.
#>

param(
  [Parameter(Mandatory = $true)]
  [string]$TenantId,

  [Parameter(Mandatory = $true)]
  [string]$ClientId,

  [Parameter(Mandatory = $true)]
  [string]$ClientSecret,

  # Token audience. For Microsoft Graph use: https://graph.microsoft.com/.default
  # You can change this to another resource (e.g., your API) if needed.
  [Parameter(Mandatory = $false)]
  [string]$Scope = "https://graph.microsoft.com/.default",

  # Optional: try a harmless Graph call to prove the token works against Graph.
  # Requires appropriate APP permissions to be granted (e.g., Application.Read.All).
  [switch]$TryGraph
)

$tokenUrl = "https://login.microsoftonline.com/$TenantId/oauth2/v2.0/token"

Write-Host "Requesting token (client_credentials) for scope: $Scope" -ForegroundColor Cyan

try {
  $token = Invoke-RestMethod -Method POST -Uri $tokenUrl -Body @{
    client_id     = $ClientId
    client_secret = $ClientSecret
    scope         = $Scope
    grant_type    = "client_credentials"
  }

  if (-not $token.access_token) {
    throw "No access_token returned."
  }

  $accessToken = $token.access_token
  Write-Host "`n✅ Client secret is valid. Token obtained." -ForegroundColor Green
  Write-Host ("Access Token (truncated): {0}..." -f $accessToken.Substring(0,40))

  # Decode JWT claims (header & payload)
  function Decode-JwtPart([string]$part) {
    $pad = (4 - ($part.Length % 4)) % 4
    $partPadded = $part + ('=' * $pad)
    [System.Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($partPadded))
  }

  $jwtParts = $accessToken -split '\.'
  if ($jwtParts.Length -ge 2) {
    $headerJson  = Decode-JwtPart $jwtParts[0]
    $claimsJson  = Decode-JwtPart $jwtParts[1]
    Write-Host "`n--- Token Header ---" -ForegroundColor DarkCyan
    $headerJson | ConvertFrom-Json | Format-List
    Write-Host "`n--- Token Claims ---" -ForegroundColor DarkCyan
    $claimsJson | ConvertFrom-Json | Format-List
  } else {
    Write-Host "Warning: Token did not look like a JWT." -ForegroundColor DarkYellow
  }

  if ($TryGraph) {
    try {
      Write-Host "`nCalling Graph to prove token works..." -ForegroundColor Cyan
      # This endpoint requires appropriate APP permissions; adjust if needed.
      $resp = Invoke-RestMethod -Method GET -Uri "https://graph.microsoft.com/v1.0/organization" -Headers @{
        Authorization = "Bearer $accessToken"
      }
      Write-Host "Graph call succeeded." -ForegroundColor Green
      $resp.value | Select-Object id, displayName, tenantType | Format-List
    } catch {
      Write-Host "Graph call failed (token ok, but permission may be missing or consent not granted):" -ForegroundColor DarkYellow
      Write-Host $_.Exception.Message
    }
  }

} catch {
  $raw = $_.ErrorDetails.Message
  if ($raw) {
    try { $err = $raw | ConvertFrom-Json } catch { $err = $null }
    if ($err) {
      Write-Host "`n❌ Token request failed:" -ForegroundColor Red
      Write-Host ("error            : {0}" -f $err.error)
      Write-Host ("error_description: {0}" -f $err.error_description)
      if ($err.error -eq "invalid_client" -and $err.error_description -match "7000215|7000218") {
        Write-Host "`nHints:" -ForegroundColor DarkYellow
        Write-Host " - Verify ClientId and ClientSecret are correct and active."
        Write-Host " - Ensure you're using the correct tenant (TenantId)."
        Write-Host " - For v2 endpoint, use scope '.../.default' (e.g., https://graph.microsoft.com/.default)."
        Write-Host " - If calling an API, ensure application permissions are granted/admin-consented."
      }
    } else {
      Write-Host "`n❌ Token request failed: $raw" -ForegroundColor Red
    }
  } else {
    Write-Host "`n❌ Token request failed: $($_.Exception.Message)" -ForegroundColor Red
  }
  exit 1
}
