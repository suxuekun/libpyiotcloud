# IoT Portal with Jenkins CI/CD automation

Jenkins support for automated integration/deployment for IoT portal is now available [here](http://ec2-3-86-65-191.compute-1.amazonaws.com:8080/).

<img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/jenkins.png" width="800"/>

<img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/jenkins_2.png" width="800"/>

<img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/jenkins_3.png" width="800"/>


### Jenkins pipeline
A Jenkins pipeline is created for IoT Portal via [Jenkinsfile](https://github.com/richmondu/libpyiotcloud/blob/master/Jenkinsfile) which allows fully-automated deployment to AWS EC2.

<img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/jenkins_jenkinsfile.png" width="800"/>

The pipeline basically stops the currently running docker containers and then build and run the updated code from the specified repository.


### Continuous Deployment/Delivery

Previous method (manual):
1. Connect to AWS EC2 using WinSCP and transfer the latest code.
2. Connect to AWS EC2 using Putty and set all the environment variables for IoT Portal.
3. Stop docker images using the following commands:
   - docker-compose down
   - docker-compose remove 
   - docker network prune -f
4. Build new docker images using the following command:
   - docker-compose build --no-cache
5. Run docker images using 
   - docker-compose up -d

New method (fully automated - using Jenkins):
1. make sure Github webhook is Active for the Jenkins URL 
   - http://ec2-3-86-65-191.compute-1.amazonaws.com:8080/github-webhook/
2. commit new code to repository
   - this triggers the Jenkins pipeline to stop, build and run the new code.


### Continuous Integration

TODO: Add automated testing for all container services from the webapp to the restapi.
