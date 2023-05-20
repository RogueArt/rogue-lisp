$sourceFiles = @(
    "interpreterv2.py"
    "v2_class_def.py"
    "v2_method_def.py"
    "v2_object_def.py"
    "v2_value_def.py"
)

$zipFile = "interpreterv2.zip"

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