# Credentials Folder

## The purpose of this folder is to store all credentials needed to log into your server and databases. This is important for many reasons. But the two most important reasons is
    1. Grading , servers and databases will be logged into to check code and functionality of application. Not changes will be unless directed and coordinated with the team.
    2. Help. If a class TA or class CTO needs to help a team with an issue, this folder will help facilitate this giving the TA or CTO all needed info AND instructions for logging into your team's server. 


# Below is a list of items required. Missing items will causes points to be deducted from multiple milestone submissions.

1. Server IP:			3.17.190.122
2. SSH Username:		ubuntu
3. SSH <KEY>:			credentials/648team13.pem
4. Database IP/Port:		x.x.x.x:3306
5. MySQL user: 			root
6. MySQL pw:			team13
7. Database name:		appdb
8. Log into server via SSH with command:
		ssh -i "648team13.pem" ubuntu@ec2-3-17-190-122.us-east-2.compute.amazonaws.com
	Open Mysql with command (password above):
		sudo mysql -u root -p

# Most important things to Remember
## These values need to kept update to date throughout the semester. <br>
## <strong>Failure to do so will result it points be deducted from milestone submissions.</strong><br>
## You may store the most of the above in this README.md file. DO NOT Store the SSH key or any keys in this README.md file.
