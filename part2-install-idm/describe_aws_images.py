import boto3

ec2_client = boto3.client('ec2', region_name='us-east-1') # Change as appropriate

response = ec2_client.describe_images(
          Owners=['679593333241'], # CentOS
        )

amis = sorted(response['Images'],
                      key=lambda x: x['CreationDate'],
                                    reverse=True)
for ami in amis:
    name = ami.get("Name")
    if name and 'centos' in name.lower():
      print('Name: ' + name)

print(amis[0])
