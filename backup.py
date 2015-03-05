import boto
import boto.utils
import boto.ec2
import boto.ec2.cloudwatch
import datetime
import properties
import logging
import time

logging.basicConfig(filename=properties.log_filename, level=properties.log_lvl)
log = logging.getLogger("Aws-EC2-Backup-Tool")
log.info("AwsBackupTool Start")

def format_name(meta_data):
    return "Backup-" + meta_data["instance-id"] + "-" + str(datetime.datetime.now()).replace(" ", "_").replace(":", "-")


# get instance Metadata infos from
instance_meta = boto.utils.get_instance_metadata()
# the [:-1] in the end of the sentence it's because in the instance metadata there is the az not the region.
region = str(instance_meta['placement']['availability-zone'][:-1])
#format Backup name
name = format_name(instance_meta)
#aws ec2 connection object instance
ec2_conn = boto.ec2.connect_to_region(region)
#aws Cloudwatch connection object instance
cw_conn = boto.ec2.cloudwatch.connect_to_region(region)

try:
    start_time = time.time()
    #image creation
    image_id = ec2_conn.create_image(instance_meta["instance-id"], name, name, True, None, properties.is_dry_run)
    #get image object to add tags
    image = ec2_conn.get_image(image_id)
    #Waiting for the
    log.info("wating for image creation to end")
    while(str(image.state) == "pending"):
        image = ec2_conn.get_image(image_id)
        time.sleep(1)
    time_spent = time.time() - start_time
    log.info("created image : "+image_id+" created in "+str(time_spent)+" Seconds")
    #tag the newly created image
    image.add_tag("date_creation", str(datetime.datetime.now()))
    image.add_tag("created_by", "AwsBackupTool")
    image.add_tag("instance_name",properties.instance_name)
    #Cloud watch add data
    cw_conn.put_metric_data(properties.metric_name, properties.dimensions, value=time_spent, unit="Seconds", dimensions={"instance_id": instance_meta["instance-id"]})
    #remove old images by the date_creation tag
    images = ec2_conn.get_all_images(filters={"tag-value": "AwsBackupTool", "tag-value": properties.instance_name})
    for image in images:
        image_creation_date = datetime.datetime.strptime(image.__dict__["tags"]["date_creation"], "%Y-%m-%d %H:%M:%S.%f")
        limit_date = datetime.datetime.now() - datetime.timedelta(days=properties.days_to_retain)
        if image_creation_date < limit_date:
            image.deregister()
            log.info(str(image)+" deleted, because its retention period was exceeded ")
    log.info("AwsBackupTool Ended")
except boto.exception.BotoServerError as ex:
    log.error(ex)
    cw_conn.put_metric_data(properties.metric_name, properties.dimensions, value="-1", unit="Seconds", dimensions={"instance_id": instance_meta["instance-id"]})
