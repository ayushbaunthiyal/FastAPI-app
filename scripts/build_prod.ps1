Write-Host "Building Production Docker Images..."
docker-compose -f docker-compose.prod.yml build
if ($LASTEXITCODE -eq 0) {
    Write-Host "Build Successful!" -ForegroundColor Green
} else {
    Write-Host "Build Failed!" -ForegroundColor Red
    exit 1
}
