# IoT Portal on automated CI/CD using Jenkins

Jenkins support for automated integration/deployment for IoT portal is now available at http://ec2-3-86-65-191.compute-1.amazonaws.com:8080/


### Jenkins pipeline
A Jenkins pipeline is created for IoT Portal via [Jenkinsfile](https://github.com/richmondu/libpyiotcloud/blob/master/Jenkinsfile) which allows automated deployment to AWS EC2.


### Continuous Deployment/Delivery

Previous method (manual):
1. copy new code to EC2 using WinSCP 
2. connect to EC2 using Putty.
3. stop docker images via "docker-compose down", "docker-compose remove" and "docker network prune -f"
4. build new docker images via "docker-compose build --no-cache"
5. run docker images via "docker-compose up -d"

New method (fully automated with Jenkins):
1. make sure Github webhook is Active for the Jenkins URL (http://ec2-3-86-65-191.compute-1.amazonaws.com:8080/github-webhook/)
2. commit new code to repository
   - this triggers the Jenkins pipeline to stop, build and run the new code.


### Continuous Integration

TODO