# Generate agricultural permits CSV based on real Ministry of Agriculture 2021 policy
$csvPath = "agricultural_permits_dataset.csv"

# Real structure types from the policy document
$structure_types = @(
    'חממה', 'בית אריזה', 'מחסן חקלאי', 'סככת ציוד', 'לול', 'רפת',
    'כבשייה', 'אורווה', 'בית דבש - מכון רדייה', 'בית אריזה פרחים', 
    'חממת קנאביס רפואי', 'בריכת דגים', 'גת - יקב', 'בד שמן זית',
    'בית אריזה תות', 'מחסן קירור'
)

# Real regions
$regions = @('גליל', 'עמקים', 'שרון', 'שפלה', 'נגב', 'ערבה', 'עמק המעיינות', 'גולן', 'יהודה ושומרון')

# Districts
$districts = @('מחוז צפון', 'מחוז חיפה', 'מחוז מרכז', 'מחוז ירושלים', 'מחוז תל אביב', 'מחוז דרום')

$random = [System.Random]::new(42)

$data = @()

for ($i = 1; $i -le 600; $i++) {
    $app_id = "AG-{0}-{1:D4}" -f (Get-Date).Year, $i
    $struct = $structure_types[$random.Next(0, $structure_types.Length)]
    $region = $regions[$random.Next(0, $regions.Length)]
    $district = $districts[$random.Next(0, $districts.Length)]
    
    # Farm size in dunams (realistic per structure type)
    switch -Wildcard ($struct) {
        'חממה'                   { $farm_dunams = $random.Next(10, 150) }
        'בית אריזה*'             { $farm_dunams = $random.Next(20, 150) }
        'לול'                    { $farm_dunams = $random.Next(5, 50) }
        'רפת'                    { $farm_dunams = $random.Next(20, 200) }
        'בית דבש*'               { $farm_dunams = $random.Next(50, 300) }  # represented as number of hives /10
        'חממת קנאביס רפואי'      { $farm_dunams = $random.Next(2, 20) }
        default                   { $farm_dunams = $random.Next(5, 100) }
    }

    # Area requested (sqm) - based on real policy thresholds
    switch -Wildcard ($struct) {
        'חממה' {
            if ($farm_dunams -lt 20)  { $area_requested = $random.Next(200, 500) }
            elseif ($farm_dunams -le 50)  { $area_requested = $random.Next(500, 700) }  # ~670 sqm policy
            elseif ($farm_dunams -le 150) { $area_requested = $random.Next(700, 1100) } # ~990 sqm policy
            else                          { $area_requested = $random.Next(1000, 5000) }
        }
        'רפת' {
            $num_cows = $random.Next(20, 350)
            if ($num_cows -le 100) { $area_requested = $random.Next(300, 500) }  # ~410 sqm policy
            else                    { $area_requested = $random.Next(400, 600) } # ~480 sqm policy
        }
        'בית דבש*' {
            $num_hives = $random.Next(200, 4000)
            $area_requested = [math]::Min($random.Next(200, 1200), 1000)  # max 1000 sqm per policy
        }
        'חממת קנאביס רפואי' {
            $area_requested = $random.Next(300, 2500)  # 750-2000 sqm per policy
        }
        'מחסן חקלאי'   { $area_requested = $random.Next(10, 400) }
        'סככת ציוד'    { $area_requested = $random.Next(20, 300) }
        default         { $area_requested = $random.Next(50, 800) }
    }

    # Number of animals (where relevant)
    $num_animals = 0
    if ($struct -eq 'לול')         { $num_animals = $random.Next(500, 100000) }
    elseif ($struct -eq 'רפת')     { $num_animals = $random.Next(20, 350) }
    elseif ($struct -eq 'כבשייה') { $num_animals = $random.Next(50, 500) }
    elseif ($struct -eq 'אורווה')  { $num_animals = $random.Next(5, 30) }

    # Distance from road (meters)
    $dist_road = [math]::Round($random.NextDouble() * 195 + 5, 1)
    
    # Distance from residential area (meters) - policy: 100-300m for lul
    $dist_residential = [math]::Round($random.NextDouble() * 990 + 10, 1)

    # Building height (max 10m per policy)
    $height_m = [math]::Round($random.NextDouble() * 10 + 1.5, 1)

    # Has solar panels on roof
    $has_solar = @($true, $false)[$random.Next(0, 2)]
    
    # Is in agricultural zone (valid zoning is required by policy)
    $is_agricultural_zone = @($true, $true, $true, $false)[$random.Next(0, 4)]
    
    # Has approved plan (TAMA compliance)
    $tama_compliant = @($true, $true, $false)[$random.Next(0, 3)]

    # Applicant recommendation letter exists
    $has_recommendation = @($true, $false)[$random.Next(0, 2)]

    # ============================================================
    # DECISION LOGIC based on REAL MINISTRY OF AGRICULTURE POLICY
    # ============================================================
    $rejection_reasons = @()
    $correction_reasons = @()

    # Rule 1: Zoning must be agricultural
    if (-not $is_agricultural_zone) {
        $rejection_reasons += "המגרש אינו ייעוד חקלאי"
    }

    # Rule 2: TAMA compliance required
    if (-not $tama_compliant) {
        $rejection_reasons += "אי-עמידה בתמ''א 35/1"
    }

    # Rule 3: Height must not exceed 10m
    if ($height_m -gt 10) {
        $correction_reasons += "גובה המבנה חורג מ-10 מטר"
    }

    # Rule 4: Chicken coops distance from residential
    if ($struct -eq 'לול' -and $dist_residential -lt 100) {
        $rejection_reasons += "לול - מרחק ממגורים קטן מ-100 מטר"
    } elseif ($struct -eq 'לול' -and $dist_residential -lt 300) {
        $correction_reasons += "לול - מרחק ממגורים בין 100-300 מטר (דורש בחינה וטרינרית)"
    }

    # Rule 5: Area within policy limits
    if ($struct -like 'בית דבש*' -and $area_requested -gt 1000) {
        $correction_reasons += "שטח מכון רדייה חורג מ-1,000 מ''ר"
    }
    if ($struct -eq 'חממת קנאביס רפואי' -and $area_requested -gt 2000) {
        $rejection_reasons += "שטח חממת קנאביס חורג מ-2,000 מ''ר"
    }

    # Rule 6: Setback from road boundary (min 5m per policy)
    if ($dist_road -lt 5) {
        $rejection_reasons += "מרחק מגבול הכביש פחות מ-5 מטר"
    } elseif ($dist_road -lt 10) {
        $correction_reasons += "מרחק מכביש ראשי נמוך (פחות מ-10 מטר)"
    }

    # Rule 7: Recommendation letter missing for large builds
    if ($area_requested -gt 1000 -and -not $has_recommendation) {
        $correction_reasons += "חסר מכתב המלצה לבנייה מעל 1,000 מ''ר"
    }

    # Determine final status
    if ($rejection_reasons.Count -gt 0) {
        $status = 'נדחה'
        $reason = $rejection_reasons -join "; "
    } elseif ($correction_reasons.Count -gt 0) {
        $status = 'דרוש תיקון'
        $reason = $correction_reasons -join "; "
    } else {
        $status = 'מאושר'
        $reason = ''
    }

    $data += [PSCustomObject]@{
        'מזהה_בקשה'                     = $app_id
        'מחוז'                           = $district
        'אזור'                           = $region
        'סוג_מבנה'                       = $struct
        'שטח_מבוקש_מ2'                  = $area_requested
        'שטח_חקלאי_בדונם'               = $farm_dunams
        'מספר_בעלי_חיים'                = $num_animals
        'מרחק_מכביש_מטר'               = $dist_road
        'מרחק_ממגורים_מטר'             = $dist_residential
        'גובה_מבנה_מטר'                 = $height_m
        'פנלים_סולאריים'                = $has_solar
        'ייעוד_חקלאי'                   = $is_agricultural_zone
        'עמידה_בתמא'                    = $tama_compliant
        'מכתב_המלצה'                    = $has_recommendation
        'סטטוס_אישור'                   = $status
        'סיבת_ההחלטה'                   = $reason
    }
}

$data | Export-Csv -Path $csvPath -NoTypeInformation -Encoding UTF8
Write-Host "CSV created successfully with $($data.Count) rows at: $csvPath"
$data | Group-Object סטטוס_אישור | ForEach-Object { Write-Host "  $($_.Name): $($_.Count) records" }
