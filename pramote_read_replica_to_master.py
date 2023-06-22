from googleapiclient import errors
from googleapiclient.discovery import build
import google.auth
from googleapiclient import discovery
from google.cloud import secretmanager_v1
import paramiko
import os



# Get the default credentials
credentials, _ = google.auth.default()
service = discovery.build('sqladmin', 'v1beta4', credentials=credentials)
project_id = 'l1-team-testing'
primary_instance_name = 'veereshprimary2'

def send_email_notification(message):
    # Implement your logic to send an email notification
    pass


def get_active_read_replica_instance_name(project_id, credentials, primary_instance_name):
    # Get the primary instance
    response = service.instances().get(project=project_id, instance=primary_instance_name).execute()
    primary_instance = response
   
    read_replicas = primary_instance['replicaNames']
    print(read_replicas)
    # Select one of the active read replicas

    instance_name=read_replicas[0]
    print('read replica name id is:  '+ instance_name)
    
  # fetch public ip
    response = service.instances().get(project=project_id, instance=instance_name).execute()
    ip_address = response['ipAddresses'][0]['ipAddress']
    print(ip_address)

  #  update_connection_php()
    update_connection_php(ip_address)

    return instance_name

def update_connection_php(ip_address):
    # Set the new host value
    new_host = ip_address
    print('new host'+new_host)
#projects/714904973783/secrets/my-private-key

    # Access the secret from Secret Manager
    client = secretmanager_v1.SecretManagerServiceClient()
    secret_name = f"projects/l1-team-testing/secrets/my-private-key/versions/latest"
    response = client.access_secret_version(name=secret_name)
    private_key = response.payload.data.decode('UTF-8')
   # print(private_key)

    # Write the private key to a temporary file
    with open('/tmp/my-private-key', 'w') as f:
        f.write(private_key)

    # Set the permissions for the private key file
    os.chmod('/tmp/my-private-key', 400)

    # Create an SSH client
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print('came till here')
    #print(private_key)
    # Connect to the remote instance
    ssh.connect(hostname='34.170.174.79', username='jveeresh', key_filename='/tmp/my-private-key',password='passphrase')
    print(private_key)

    # Run the command to update the connection.php file
    try:
     #   cmd = f"sudo sed -i 's/\\$host = .*/\\$host = \\\"{new_host}\\\";/' /var/www/html/CISHack-Vardhaman_Hackathon/connection.php"
        cmd = f"sudo sed -i 's/\\$host =.*/\\$host = \\'1232465\\';/' /var/www/html/CISHack-Vardhaman_Hackathon/connection.php"
        ssh.exec_command(cmd)
        print("changes Sucessfull bro!")
    except paramiko.SSHException as e:
        print("changes failed")
        print(e)
        

    # Run the hostname command
    stdin, stdout, stderr = ssh.exec_command('cat /var/www/html/CISHack-Vardhaman_Hackathon/connection.php')
    output = stdout.read().decode('utf-8')
    print(f"Connected to: {output}")    


def main(data,context):
    # Set the project ID and instance name
    project_id = 'l1-team-testing'
   
    # Get the default credentials
    credentials, _ = google.auth.default()

    instance_name = get_active_read_replica_instance_name(project_id, credentials,primary_instance_name)
'''
    # Promote the read replica to master.
    try:
        service.instances().promoteReplica(project=project_id, instance=instance_name).execute()
        send_email_notification("Read replica promoted to master successfully")
    except errors.HttpError as e:           
        send_email_notification(str(e))
 '''   

if __name__ == "__main__":
    main(data,context)
    #update_connection_php()
