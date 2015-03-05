#property file

#instance Name
instance_name = "myInstanceToBackup"
#dry run
is_dry_run = False
#Custom Metric Name
metric_name = "EC2BackupTool"
#Custom Metric Dimensions
dimensions = "Backup_duration"
#Log file name
log_filename = "AwsBackupTool.log"
#backup by creating images or disk snapshot, image backup can only be done in no-reboot mode
backup_type = "image" #value {"image", "snapshot"} TODO
#number of days of retention
days_to_retain = 5
#Log lvl
log_lvl = "INFO"