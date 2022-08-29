from troposphere import Base64, ec2, GetAtt, Join, Output, Parameter, Ref, Template
ApplicationPort="3000"

t=Template()
t.set_description("Effective DevOps in AWS: HelloWorld web application")
t.add_parameter(Parameter(
    "KeyName",
    Description="Name of an existing EC2 KeyPair to SSH",
    Type="AWS::EC2::KeyPair::KeyName",
    ConstraintDescription="must be the name of an existing EC2 KeyPair."
))

t.add_resource(ec2.SecurityGroup(
    "InstanceSecurityGroup",
    GroupDescription="Allow SSH and TCP/{} access".format(ApplicationPort),
    SecurityGroupIngress=[
        ec2.SecurityGroupRule(
            IpProtocol="tcp",
            FromPort="22",
            ToPort="22",
            CidrIp="0.0.0.0/0"
        ),
        ec2.SecurityGroupRule(
        IpProtocol="tcp",
        FromPort=ApplicationPort,
        ToPort=ApplicationPort,
        CidrIp="0.0.0.0/0"
        )
    ]
))

ud=Base64(Join('\n',[
    "#!/bin/bash",
    "sudo yum update -y",
    "wget http://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm",
    "sudo rpm -ivh epel-release-latest-7.noarch.rpm",
    "sudo sed -i 's/plugins=1/plugins=0/g' /etc/yum.conf",
    "sudo yum install libuv -y",
    "sudo yum install --enablerepo=epel -y nodejs",
    "mkdir /home/ec2-user/ch02",
    "wget http://bit.ly/2vESNuc -O /home/ec2-user/ch02/helloworld.js",
    "wget https://wn-kvs-bucket.s3.ap-northeast-1.amazonaws.com/helloworld.service",
    "sudo mv helloworld.service /etc/systemd/system/helloworld.service",
    "sudo systemctl daemon-reload",
    "sudo systemctl enable helloworld.service",
    "sudo systemctl start helloworld.service"
]))

t.add_resource(ec2.Instance(
    "instance",
    ImageId="ami-0f36dcfcc94112ea1",
    InstanceType="t2.micro",
    SecurityGroups=[Ref("InstanceSecurityGroup")],
    KeyName=Ref("KeyName"),
    UserData=ud
))

t.add_output(Output(
    "InstancePublicIp",
    Description="Public IP of our instance.",
    Value=GetAtt("instance", "PublicIp")
))

t.add_output(Output(
    "WebUrl",
    Description="Application endpoint",
    Value=Join("", [
        "http://", GetAtt("instance", "PublicDnsName"),
        ":", ApplicationPort
    ])
))

print(t.to_json())
