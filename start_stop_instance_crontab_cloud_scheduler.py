'''
import base64
import googleapiclient.discovery

def stop_all_vms(data, context):
    project = 'l1-team-testing' # Replace with your GCP project ID
    compute = googleapiclient.discovery.build('compute', 'v1')
    zones = compute.zones().list(project=project).execute()
    for zone in zones.get('items', []):
        instances = compute.instances().list(project=project, 
zone=zone['name']).execute()
        for instance in instances.get('items', []):
            compute.instances().stop(project=project, zone=zone['name'], 
instance=instance['name']).execute()
    return 'VMs stopping process initiated successfully'
'''
import base64
from googleapiclient import discovery
from google.cloud import pubsub_v1

def stop_all_vms(data, context):
    project = 'l1-team-testing'  # Replace with your GCP project ID
    compute = discovery.build('compute', 'v1')
    zones = compute.zones().list(project=project).execute()

    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project, 'emailtopic')

    for zone in zones.get('items', []):
        instances = compute.instances().list(project=project, 
zone=zone['name']).execute()
        for instance in instances.get('items', []):
            # Get the instance object.
            instance_obj = compute.instances().get(project=project, 
zone=zone['name'], instance=instance['name']).execute()
            # Get the metadata for the instance.
            metadata = instance_obj.get('metadata', {})
            # Get the status of the instance.
            status = instance_obj.get('status', '')
            # Check if the status of the instance is TERMINATED.
            if status == 'TERMINATED':
                # Get the value of the 'owner' metadata key.
                owner_email = None
                if 'owner' in metadata:
                    owner_email = metadata['owner']
            
            compute.instances().stop(project=project, zone=zone['name'], 
instance=instance['name']).execute()

            message = {
                'instance_name': instance['name'],
                'owner_email': owner_email
            }
            publisher.publish(topic_path, data=str(message).encode())

    return 'VMs stopping process initiated successfully'

