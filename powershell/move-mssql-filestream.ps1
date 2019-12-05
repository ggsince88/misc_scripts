$startTime = (Get-Date)
# STOP REPL AGENT
$old_filestream_path = 'D:\Data\DB_DocumentObjects'

$filestream_drive = 'G:\'
$filestream_root = $filestream_drive + 'DATA\'
$filestream_path = $filestream_root + 'DB_DocumentObjects'

$db = 'DATABASE'

$sql_acl = Get-Acl -Path $old_filestream_path

New-Item -ItemType Directory -Path $filestream_drive -Name 'DATA'

Set-Acl -Path $filestream_root -AclObject $sql_acl

$sql_query = @"
ALTER DATABASE $db
MODIFY FILE ( NAME = DocumentObjects, FILENAME = '$filestream_path' );
GO
"@

$filestream_query = @"
Select * FROM sys.master_files
WHERE name = 'DocumentObjects'
"@

Invoke-DbaQuery -SqlInstance $env:COMPUTERNAME -Query $sql_query -Database 'master' -ErrorAction Stop

Set-DbaDbState -SqlInstance $env:COMPUTERNAME -Database $db -SingleUser -Force

Set-DbaDbState -SqlInstance $env:COMPUTERNAME -Database $db -Offline

Move-Item -Path $old_filestream_path -Destination $filestream_path -ErrorAction Stop

Set-DbaDbState -SqlInstance $env:COMPUTERNAME -Database $db -Online

Set-DbaDbState -SqlInstance $env:COMPUTERNAME -Database $db -MultiUser

Invoke-DbaQuery -SqlInstance $env:COMPUTERNAME -Query $filestream_query -Database 'master' | Select name, physical_name
$endTime = (Get-Date)
'Duration: {0:mm} min {0:ss} sec' -f ($endTime-$startTime)
