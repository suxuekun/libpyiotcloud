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

<b>Previous method</b> (manual):
1. Connect to AWS EC2 using <b>WinSCP</b> and transfer the latest code.
2. Connect to AWS EC2 using <b>Putty</b> and set all the environment variables for IoT Portal.
3. Stop docker images using the following commands:
   - docker-compose down
   - docker-compose remove 
   - docker network prune -f
4. Check if docker-compose configuration is correct:
   - docker-compose -f docker-compose.yml config
5. Build the new docker images using the following command:
   - docker-compose build --no-cache
6. Run the new docker images using the following command:
   - docker-compose up -d

<b>New method</b> (fully automated - using Jenkins):
1. make sure the Github webhook for the repository is Active for the Jenkins URL 
   - http://ec2-3-86-65-191.compute-1.amazonaws.com:8080/github-webhook/
2. commit new code to repository
   - this triggers the Jenkins pipeline to stop, build and run the new code.


### Continuous Integration

TODO: Add automated testing for all container services from the webapp to the restapi.
