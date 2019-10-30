# IoT Portal on Kubernetes

Kubernetes support for IoT portal is now available. 

This has been tested using [Minikube](https://github.com/kubernetes/minikube), an application that allows users to run Kubernetes locally.  

<img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/kubernetes_minikube.png" width="800"/>

<img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/kubernetes_minikube_dashboard.png" width="800"/>


### Limitations:

1. Ports for RabbitMQ and Nginx are not the usual 8883 and 443. 
   RabbitMQ can be accessed using port 30883 (MQTTS) and 30671 (AMQPS) instead of 8883 and 5671, respectively.
   Webapp can be accessed using port 30443 (HTTPS) instead of port 443.
   Note that to prevent random ports getting assigned, I had to specify the port number replacements.

2. The Kubernetes configuration files fetches the docker images from Docker.io not from local machine. 
   Note that docker-compose fetches from local machine.



### Instructions:

0. Make sure docker images is committed to the docker repository. As the Kubernetes files fetches the docker images from the specified registry.

1. Set docker-registry

        kubectl create secret docker-registry regcred --docker-server=docker.io --docker-username=USERNAME --docker-password=PASSWORD --docker-email=EMAIL


2. Fill-up environment.yaml then run 

        kubectl apply -f environment.yaml


3. Run MongoDB

        kubectl apply -f iotmongodb-persistentvolumeclaim.yaml
        kubectl apply -f iotmongodb-deployment.yaml
        kubectl apply -f iotmongodb-service.yaml


4. Run RabbitMQ

        kubectl apply -f iotrabbitmq-deployment.yaml
        kubectl apply -f iotrabbitmq-service.yaml


5. Run history manager and notification manager

        kubectl apply -f iothistory-deployment.yaml
        kubectl apply -f iotnotification-deployment.yaml


6. Run RESTAPI

        kubectl apply -f iotrestapi-deployment.yaml
        kubectl apply -f iotrestapi-service.yaml


7. Run Webapp

        kubectl apply -f iotwebapp-deployment.yaml
        kubectl apply -f iotwebapp-service.yaml


8. Run Nginx

        kubectl apply -f iotnginx-deployment.yaml
        kubectl apply -f iotnginx-service.yaml


9. Stop all

        kubectl delete service nginx
        kubectl delete deployment nginx
        kubectl delete service webapp
        kubectl delete deployment webapp
        kubectl delete service restapi
        kubectl delete deployment restapi
        kubectl delete deployment history
        kubectl delete deployment notification
        kubectl delete service rabbitmq
        kubectl delete deployment rabbitmq
        kubectl delete service mongodb
        kubectl delete deployment mongodb
        kubectl delete persistentvolumeclaim mydockervol
        kubectl delete secret environment
        kubectl delete secret regcred


### Notes:

- minikube ip
- minikube start
- minikube stop
- minikube delete
- minikube service SERVICENAME --url

- kubectl get secrets
- kubectl get deployments
- kubectl get pods
- kubectl get svc
- kubectl get persistentvolumeclaim
- kubectl log PODNAME
- kubectl describe pod PODNAME
- kubectl delete secret SECRETNAME
- kubectl delete deployment DEPLOYMENTNAME
- kubectl delete service SERVICENAME
- kubectl delete persistentvolumeclaim PERSISTENTVOLUMENAME
