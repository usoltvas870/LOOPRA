param(
    [Parameter(Mandatory = $true)][ValidateSet("probe", "recognize")][string]$Mode,
    [string]$ImagePath,
    [ValidateSet("en-US", "ru")][string]$Language = "en-US"
)

$ErrorActionPreference = "Stop"

function Convert-WinRtOperation {
    param($Operation, [Type]$ResultType)
    $method = [System.WindowsRuntimeSystemExtensions].GetMethods() |
        Where-Object { $_.Name -eq "AsTask" -and $_.IsGenericMethodDefinition -and $_.GetParameters().Count -eq 1 } |
        Select-Object -First 1
    $task = $method.MakeGenericMethod($ResultType).Invoke($null, @($Operation))
    return $task.GetAwaiter().GetResult()
}

function Get-WinRtType([string]$Name) {
    return [type]$Name
}

try {
    Add-Type -AssemblyName System.Runtime.WindowsRuntime
    $engineType = Get-WinRtType "Windows.Media.Ocr.OcrEngine, Windows.Foundation, ContentType=WindowsRuntime"
    $languageType = Get-WinRtType "Windows.Globalization.Language, Windows.Foundation, ContentType=WindowsRuntime"
    if ($Mode -eq "probe") {
        $languages = @($engineType::AvailableRecognizerLanguages | ForEach-Object { $_.LanguageTag })
        @{ available = $true; engine_id = "windows_media_ocr"; engine_version = [Environment]::OSVersion.Version.ToString(); languages = $languages } | ConvertTo-Json -Compress
        exit 0
    }
    if (-not $ImagePath -or -not [IO.File]::Exists($ImagePath)) { throw "image path does not exist" }
    $supported = @($engineType::AvailableRecognizerLanguages | ForEach-Object { $_.LanguageTag })
    if ($supported -notcontains $Language) { throw "requested Windows OCR language is unavailable: $Language" }
    $storageFileType = Get-WinRtType "Windows.Storage.StorageFile, Windows.Storage, ContentType=WindowsRuntime"
    $accessModeType = Get-WinRtType "Windows.Storage.FileAccessMode, Windows.Storage, ContentType=WindowsRuntime"
    $streamType = Get-WinRtType "Windows.Storage.Streams.IRandomAccessStream, Windows.Storage.Streams, ContentType=WindowsRuntime"
    $decoderType = Get-WinRtType "Windows.Graphics.Imaging.BitmapDecoder, Windows.Graphics.Imaging, ContentType=WindowsRuntime"
    $bitmapType = Get-WinRtType "Windows.Graphics.Imaging.SoftwareBitmap, Windows.Graphics.Imaging, ContentType=WindowsRuntime"
    $resultType = Get-WinRtType "Windows.Media.Ocr.OcrResult, Windows.Foundation, ContentType=WindowsRuntime"
    $file = Convert-WinRtOperation ($storageFileType::GetFileFromPathAsync([IO.Path]::GetFullPath($ImagePath))) $storageFileType
    $stream = Convert-WinRtOperation ($file.OpenAsync([Enum]::Parse($accessModeType, "Read"))) $streamType
    $decoder = Convert-WinRtOperation ($decoderType::CreateAsync($stream)) $decoderType
    $bitmap = Convert-WinRtOperation ($decoder.GetSoftwareBitmapAsync()) $bitmapType
    try {
        $engine = $engineType::TryCreateFromLanguage([Activator]::CreateInstance($languageType, $Language))
        if ($null -eq $engine) { throw "Windows OCR engine could not be created" }
        $result = Convert-WinRtOperation ($engine.RecognizeAsync($bitmap)) $resultType
        $blocks = @()
        $order = 0
        foreach ($line in $result.Lines) {
            foreach ($word in $line.Words) {
                $box = $word.BoundingRect
                $blocks += @{ text = $word.Text; reading_order = $order; box = @{ x = $box.X; y = $box.Y; width = $box.Width; height = $box.Height } }
                $order++
            }
        }
        @{ text = $result.Text; blocks = $blocks; confidence = $null } | ConvertTo-Json -Compress -Depth 5
    } finally {
        $bitmap.Dispose()
        $stream.Dispose()
    }
} catch {
    [Console]::Error.WriteLine("WINDOWS_OCR_ERROR: " + $_.Exception.Message)
    exit 2
}
