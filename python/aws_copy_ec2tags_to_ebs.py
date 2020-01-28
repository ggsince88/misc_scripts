import boto3
from sys import argv, exit


def get_instance_data(data):
    return data['Instances'][0]


def get_ec2_volumes(instance_data):
    return instance_data['BlockDeviceMappings']


def get_ec2_volume_ids(volume_data):
    return [v['Ebs']['VolumeId'] for v in volume_data]


def get_ec2_tag(tag_data, key):
    return [k for k in tag_data if k['Key'] == key]


def create_volume_tag(ec2_tag, vol_id, tags):
    RESOURCE = boto3.resource('ec2')
    volume = RESOURCE.Volume(vol_id)
    current_vol_tags = volume.tags or []
    filtered_ec2_tag = get_ec2_tag(tags, ec2_tag)
    return volume.create_tags(Tags=current_vol_tags + filtered_ec2_tag)


def main():
    """
    Copies tag (key, value) from ec2 instance to its attached ebs volumes
    script.py TAG-KEY
    """
    CLIENT = boto3.client('ec2')
    # ec2 tag (key) to filter and copy from ec2 to ebs volume
    try:
        ec2_tag = argv[1]
    except IndexError:
        exit('ERROR: No paramter supplied. Must be a valid ec2 tag to copy to ebs volume.')
    # Query AWS for instances
    describe_instances_paginator = CLIENT.get_paginator('describe_instances')
    ec2_instance_pages = describe_instances_paginator.paginate(
        MaxResults=10, Filters=[{'Name': 'tag-key', 'Values': [ec2_tag]}])

    # Iterate through all data
    for page in ec2_instance_pages:
        for instance in page['Reservations']:
            instance_data = get_instance_data(instance)
            instance_volume_ids = get_ec2_volume_ids(get_ec2_volumes(instance_data))
            for volume_id in instance_volume_ids:
                create_volume_tag(ec2_tag, volume_id, instance_data['Tags'])


if __name__ == "__main__":
    main()
