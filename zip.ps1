$sourceFiles = @(
    "interpreterv3.py"
    "v3_class.py"
    "v3_env.py"
    "v3_object.py"
    "v3_type_value.py"
    "README.md"
)

$zipFile = "00-interpreterv3.zip"

if (Test-Path $zipFile) {
    Remove-Item -Path $zipFile -Force
}

Add-Type -A 'System.IO.Compression.FileSystem'

$compressionLevel = [System.IO.Compression.CompressionLevel]::Optimal

$zipArchive = [System.IO.Compression.ZipFile]::Open($zipFile, 'Create')

foreach ($file in $sourceFiles) {
    [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile(
        $zipArchive,
        $file,
        $file,
        $compressionLevel
    )
}

$zipArchive.Dispose()