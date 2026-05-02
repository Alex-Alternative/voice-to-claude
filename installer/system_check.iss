{ installer/system_check.iss
  --------------------------
  Pascal mirror of system_check.classify(). Used during the Inno wizard
  pages BEFORE Koda.exe is extracted. Determines tier so the soft-warn
  / Power Mode pages can be shown ahead of the file extraction step.

  After extraction, koda.iss runs Koda.exe --detect-hardware --json for
  the authoritative classification (which can verify CUDA runtime
  usability, something Pascal cannot).

  Constants come from installer/thresholds.iss (auto-generated).

  IMPORTANT: This file is #include'd by koda.iss INSIDE the [Code]
  section. It must not contain its own [Code] header.
}

{ Win32 types — must be declared before external function decls that reference them.
  PascalScript doesn't ship TMemoryStatusEx or TSystemInfo, so we declare both. }
type
  TMemoryStatusEx = record
    dwLength: DWORD;
    dwMemoryLoad: DWORD;
    ullTotalPhys: Int64;
    ullAvailPhys: Int64;
    ullTotalPageFile: Int64;
    ullAvailPageFile: Int64;
    ullTotalVirtual: Int64;
    ullAvailVirtual: Int64;
    ullAvailExtendedVirtual: Int64;
  end;

  TSystemInfoLocal = record
    wProcessorArchitecture: Word;
    wReserved: Word;
    dwPageSize: DWORD;
    lpMinimumApplicationAddress: DWORD;
    lpMaximumApplicationAddress: DWORD;
    dwActiveProcessorMask: DWORD;
    dwNumberOfProcessors: DWORD;
    dwProcessorType: DWORD;
    dwAllocationGranularity: DWORD;
    wProcessorLevel: Word;
    wProcessorRevision: Word;
  end;

{ Win32 imports }
function GlobalMemoryStatusEx(var lpBuffer: TMemoryStatusEx): BOOL;
  external 'GlobalMemoryStatusEx@kernel32.dll stdcall';

procedure GetNativeSystemInfo(var lpSystemInfo: TSystemInfoLocal);
  external 'GetNativeSystemInfo@kernel32.dll stdcall';

{ Detection helpers }

function DetectRamGB: Double;
var
  Mem: TMemoryStatusEx;
begin
  Mem.dwLength := SizeOf(Mem);
  if GlobalMemoryStatusEx(Mem) then
    Result := Mem.ullTotalPhys / (1024 * 1024 * 1024)
  else
    Result := -1;  { detection failure }
end;

function DetectCores: Integer;
var
  SysInfo: TSystemInfoLocal;
begin
  GetNativeSystemInfo(SysInfo);
  Result := Integer(SysInfo.dwNumberOfProcessors);
end;

function DetectFreeDiskGB: Double;
var
  FreeBytes: Cardinal;
begin
  { GetSpaceOnDisk returns free MB; convert to GB }
  if GetSpaceOnDisk(ExpandConstant('{sd}\'), True, FreeBytes, FreeBytes) then
    Result := FreeBytes / 1024
  else
    Result := -1;
end;

function DetectWinBuild: Integer;
var
  WinVer: TWindowsVersion;
begin
  GetWindowsVersionEx(WinVer);
  Result := WinVer.Build;
end;

function DetectCpuName: String;
begin
  if not RegQueryStringValue(
    HKEY_LOCAL_MACHINE,
    'HARDWARE\DESCRIPTION\System\CentralProcessor\0',
    'ProcessorNameString',
    Result
  ) then
    Result := '';
end;

function DetectNvidiaGpuPresent: Boolean;
var
  ResultCode, FSize: Integer;
  TempPath: String;
  Contents: AnsiString;
begin
  { Run nvidia-smi, redirect output to a temp file. If it exists and is
    non-empty, NVIDIA GPU is present. PascalScript's FileSize takes two
    args (name + var size), so we just LoadStringFromFile and look at
    Length -- simpler and avoids the temp-path-with-spaces nested-quote bug. }
  TempPath := ExpandConstant('{tmp}\nvidia_check.txt');
  Exec(
    ExpandConstant('{cmd}'),
    '/c nvidia-smi --query-gpu=name --format=csv,noheader > "' + TempPath + '" 2>NUL',
    '', SW_HIDE, ewWaitUntilTerminated, ResultCode
  );
  FSize := 0;
  if FileExists(TempPath) and LoadStringFromFile(TempPath, Contents) then
    FSize := Length(Trim(String(Contents)));
  Result := FSize > 0;
end;

function IsLowPowerCpu(const CpuName: String): Boolean;
var
  Patterns, NameLower, Pattern: String;
  PipeIdx: Integer;
begin
  { CPU_LOW_POWER_PATTERNS_PIPE is a #define from thresholds.iss — pipe-
    delimited substrings to scan for. PascalScript const blocks don't
    support typed array constants, so we emit a delimited string and
    walk it here. }
  Patterns := '{#CPU_LOW_POWER_PATTERNS_PIPE}';
  NameLower := Lowercase(CpuName);
  Result := False;
  while Length(Patterns) > 0 do
  begin
    PipeIdx := Pos('|', Patterns);
    if PipeIdx = 0 then
    begin
      Pattern := Patterns;
      Patterns := '';
    end
    else
    begin
      Pattern := Copy(Patterns, 1, PipeIdx - 1);
      Patterns := Copy(Patterns, PipeIdx + 1, MaxInt);
    end;
    if (Pattern <> '') and (Pos(Pattern, NameLower) > 0) then
    begin
      Result := True;
      Exit;
    end;
  end;
end;

{ Tier classifier — returns one of: 'BLOCKED', 'MINIMUM', 'RECOMMENDED', 'POWER' }

function ClassifyTier: String;
var
  RamGB, FreeDiskGB: Double;
  Cores, WinBuild: Integer;
  CpuName: String;
  HasNvidia, IsLowPower: Boolean;
begin
  RamGB := DetectRamGB;
  Cores := DetectCores;
  FreeDiskGB := DetectFreeDiskGB;
  WinBuild := DetectWinBuild;
  CpuName := DetectCpuName;
  HasNvidia := DetectNvidiaGpuPresent;
  IsLowPower := IsLowPowerCpu(CpuName);

  { BLOCKED checks }
  if (RamGB > 0) and (RamGB < {#RAM_BLOCKED_MIN_GB}) then begin
    Result := 'BLOCKED';
    Exit;
  end;
  if (FreeDiskGB > 0) and (FreeDiskGB < {#DISK_BLOCKED_MIN_FREE_GB}) then begin
    Result := 'BLOCKED';
    Exit;
  end;
  if (WinBuild > 0) and (WinBuild < {#WIN_BLOCKED_MIN_BUILD}) then begin
    Result := 'BLOCKED';
    Exit;
  end;

  { POWER tier — Pascal cannot verify CUDA runtime, so we treat NVIDIA-presence
    as POWER-eligible. The post-extract Koda.exe --detect-hardware call will
    correct to RECOMMENDED if CUDA runtime isn't usable. }
  if HasNvidia then begin
    Result := 'POWER';
    Exit;
  end;

  { MINIMUM checks }
  if (Cores < {#CORES_MIN_RECOMMENDED}) or
     (RamGB < {#RAM_MIN_RECOMMENDED_GB}) or
     IsLowPower then begin
    Result := 'MINIMUM';
    Exit;
  end;

  Result := 'RECOMMENDED';
end;
