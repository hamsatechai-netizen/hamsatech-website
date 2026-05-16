Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Add-Type -AssemblyName System.Drawing

function Get-AverageColor {
  param(
    [Parameter(Mandatory = $true)][System.Drawing.Bitmap]$Bitmap,
    [Parameter(Mandatory = $true)][int]$X,
    [Parameter(Mandatory = $true)][int]$Y,
    [Parameter(Mandatory = $true)][int]$Width,
    [Parameter(Mandatory = $true)][int]$Height
  )

  $sumR = 0
  $sumG = 0
  $sumB = 0
  $count = 0

  for ($yy = $Y; $yy -lt ($Y + $Height); $yy++) {
    for ($xx = $X; $xx -lt ($X + $Width); $xx++) {
      $p = $Bitmap.GetPixel($xx, $yy)
      $sumR += $p.R
      $sumG += $p.G
      $sumB += $p.B
      $count++
    }
  }

  if ($count -eq 0) {
    return [System.Drawing.Color]::FromArgb(0, 0, 0)
  }

  return [System.Drawing.Color]::FromArgb(
    [int][Math]::Round($sumR / $count),
    [int][Math]::Round($sumG / $count),
    [int][Math]::Round($sumB / $count)
  )
}

function New-WhiteMarkFromLogo {
  param(
    [Parameter(Mandatory = $true)][string]$InputPath,
    [Parameter(Mandatory = $true)][string]$Output384Path
  )

  $src = [System.Drawing.Bitmap]::FromFile($InputPath)
  try {
    $bmp = New-Object System.Drawing.Bitmap $src.Width, $src.Height, ([System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    try {
      $g.CompositingMode = [System.Drawing.Drawing2D.CompositingMode]::SourceCopy
      $g.DrawImage($src, 0, 0, $src.Width, $src.Height)
    } finally {
      $g.Dispose()
    }

    $sampleSize = [Math]::Max(6, [int][Math]::Floor($bmp.Width * 0.05))
    $c1 = Get-AverageColor -Bitmap $bmp -X 0 -Y 0 -Width $sampleSize -Height $sampleSize
    $c2 = Get-AverageColor -Bitmap $bmp -X ($bmp.Width - $sampleSize) -Y 0 -Width $sampleSize -Height $sampleSize
    $c3 = Get-AverageColor -Bitmap $bmp -X 0 -Y ($bmp.Height - $sampleSize) -Width $sampleSize -Height $sampleSize
    $c4 = Get-AverageColor -Bitmap $bmp -X ($bmp.Width - $sampleSize) -Y ($bmp.Height - $sampleSize) -Width $sampleSize -Height $sampleSize

    $bg = [System.Drawing.Color]::FromArgb(
      [int][Math]::Round(($c1.R + $c2.R + $c3.R + $c4.R) / 4),
      [int][Math]::Round(($c1.G + $c2.G + $c3.G + $c4.G) / 4),
      [int][Math]::Round(($c1.B + $c2.B + $c3.B + $c4.B) / 4)
    )

    $t0 = 18.0
    $t1 = 70.0

    $minX = $bmp.Width
    $minY = $bmp.Height
    $maxX = -1
    $maxY = -1

    for ($y = 0; $y -lt $bmp.Height; $y++) {
      for ($x = 0; $x -lt $bmp.Width; $x++) {
        $p = $bmp.GetPixel($x, $y)

        $dr = [double]($p.R - $bg.R)
        $dg = [double]($p.G - $bg.G)
        $db = [double]($p.B - $bg.B)
        $dist = [Math]::Sqrt(($dr * $dr) + ($dg * $dg) + ($db * $db))

        $a = 0
        if ($dist -ge $t1) {
          $a = 255
        } elseif ($dist -gt $t0) {
          $a = [int][Math]::Round(255.0 * (($dist - $t0) / ($t1 - $t0)))
        }

        $a = [int][Math]::Round(($a * $p.A) / 255.0)
        if ($a -lt 0) { $a = 0 }
        if ($a -gt 255) { $a = 255 }

        if ($a -gt 12) {
          if ($x -lt $minX) { $minX = $x }
          if ($y -lt $minY) { $minY = $y }
          if ($x -gt $maxX) { $maxX = $x }
          if ($y -gt $maxY) { $maxY = $y }
        }

        $bmp.SetPixel($x, $y, [System.Drawing.Color]::FromArgb($a, 255, 255, 255))
      }
    }

    if ($maxX -lt 0 -or $maxY -lt 0) {
      throw "No foreground pixels detected in $InputPath"
    }

    $bboxW = ($maxX - $minX + 1)
    $bboxH = ($maxY - $minY + 1)
    $side = [Math]::Max($bboxW, $bboxH)
    $pad = [int][Math]::Round($side * 0.12)
    $side = [Math]::Min($bmp.Width, [Math]::Min($bmp.Height, ($side + $pad)))

    $cx = [int][Math]::Round(($minX + $maxX) / 2.0)
    $cy = [int][Math]::Round(($minY + $maxY) / 2.0)
    $cropX = [int][Math]::Round($cx - ($side / 2.0))
    $cropY = [int][Math]::Round($cy - ($side / 2.0))

    if ($cropX -lt 0) { $cropX = 0 }
    if ($cropY -lt 0) { $cropY = 0 }
    if (($cropX + $side) -gt $bmp.Width) { $cropX = $bmp.Width - $side }
    if (($cropY + $side) -gt $bmp.Height) { $cropY = $bmp.Height - $side }

    $crop = New-Object System.Drawing.Bitmap $side, $side, ([System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
    $gc = [System.Drawing.Graphics]::FromImage($crop)
    try {
      $gc.Clear([System.Drawing.Color]::FromArgb(0, 0, 0, 0))
      $gc.CompositingMode = [System.Drawing.Drawing2D.CompositingMode]::SourceOver
      $gc.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
      $gc.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
      $gc.DrawImage($bmp, (New-Object System.Drawing.Rectangle 0, 0, $side, $side), (New-Object System.Drawing.Rectangle $cropX, $cropY, $side, $side), ([System.Drawing.GraphicsUnit]::Pixel))
    } finally {
      $gc.Dispose()
    }

    $out = New-Object System.Drawing.Bitmap 384, 384, ([System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
    $go = [System.Drawing.Graphics]::FromImage($out)
    try {
      $go.Clear([System.Drawing.Color]::FromArgb(0, 0, 0, 0))
      $go.CompositingMode = [System.Drawing.Drawing2D.CompositingMode]::SourceOver
      $go.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
      $go.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
      $go.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
      $go.DrawImage($crop, 0, 0, 384, 384)
    } finally {
      $go.Dispose()
    }

    $out.Save($Output384Path, [System.Drawing.Imaging.ImageFormat]::Png)

    $crop.Dispose()
    $out.Dispose()
    $bmp.Dispose()
  } finally {
    $src.Dispose()
  }
}

function Resize-Png {
  param(
    [Parameter(Mandatory = $true)][string]$InputPath,
    [Parameter(Mandatory = $true)][string]$OutputPath,
    [Parameter(Mandatory = $true)][int]$Size
  )

  $src = [System.Drawing.Bitmap]::FromFile($InputPath)
  try {
    $out = New-Object System.Drawing.Bitmap $Size, $Size, ([System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
    $g = [System.Drawing.Graphics]::FromImage($out)
    try {
      $g.Clear([System.Drawing.Color]::FromArgb(0, 0, 0, 0))
      $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
      $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
      $g.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
      $g.DrawImage($src, 0, 0, $Size, $Size)
    } finally {
      $g.Dispose()
    }

    $out.Save($OutputPath, [System.Drawing.Imaging.ImageFormat]::Png)
    $out.Dispose()
  } finally {
    $src.Dispose()
  }
}

$input = Join-Path $PSScriptRoot '..\\public\\logo-mark-384.png'
$out384 = Join-Path $PSScriptRoot '..\\public\\logo-mark-white-384.png'
$out256 = Join-Path $PSScriptRoot '..\\public\\logo-mark-white-256.png'
$out128 = Join-Path $PSScriptRoot '..\\public\\logo-mark-white-128.png'

New-WhiteMarkFromLogo -InputPath $input -Output384Path $out384
Resize-Png -InputPath $out384 -OutputPath $out256 -Size 256
Resize-Png -InputPath $out384 -OutputPath $out128 -Size 128

Write-Host "Generated:" $out128
Write-Host "Generated:" $out256
Write-Host "Generated:" $out384

