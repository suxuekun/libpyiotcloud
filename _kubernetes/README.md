# IoT Portal on Kubernetes

Kubernetes support for IoT portal is now available. It has been tested on both Minikube and Amazon EKS.


### Amazon EKS

[Amazon EKS](https://aws.amazon.com/eks/) is a service that allows users to run Kubernetes in AWS without needing to install and operate your own Kubernetes clusters.

<img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/kubernetes_eks.png" width="800"/>

<img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/kubernetes_eks_cluster.png" width="800"/>

<img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/kubernetes_eks_workernodes.png" width="800"/>


### Minikube

[Minikube](https://github.com/kubernetes/minikube) is an application that allows users to run Kubernetes locally.  

<img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/kubernetes_minikube.png" width="800"/>

<img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/kubernetes_minikube_dashboard.png" width="800"/>



### Setup:

Major differences between Minikube and Amazon EKS:

1. Amazon EKS requires creating the Kubernetes cluster using the eksctl tool.
2. Minikube only uses 1 worker node while Amazon EKS can create multiple worker nodes.
3. Minikube load balancer will assign a random port (3XXXX).


#### Minikube

         minikube start
         
         // To stop and/or delete
         minikube stop
         minikube delete

         // Limitations
         Ports for RabbitMQ and Nginx are not the usual 8883 and 443. 
         RabbitMQ can be accessed using port 30883 (MQTTS) and 30671 (AMQPS) instead of 8883 and 5671, respectively.
         Webapp can be accessed using port 30443 (HTTPS) instead of port 443.
         Note that to prevent random ports (30000-32767) getting assigned, I had to specify the port number replacements.
         Based on some forums, this behavior is specific to Minikube only.
         

#### Amazon EKS

         eksctl create cluster --name ft90xiotportal --version 1.14 --nodegroup-name ft90xiotportalgrp --node-type t3.micro --nodes 3 --nodes-min 1 --nodes-max 4
         eksctl scale nodegroup --cluster ft90xiotportal --name ft90xiotportalgrp --nodes 5  

         // To delete
         eksctl delete cluster --name ft90xiotportal 

         // Limitation
         Currently, it requires to spin up 5 EC2 instances as worker nodes. Otherwise, the deployment of containers will be stuck in PENDING (no available pods). Need to investigate since having 5 EC2 instances can be costly.
         

### Instructions:

1. Make sure docker images are committed to the docker repository. As the Kubernetes files will fetch the docker images from the specified container registry.

        docker-compose build --no-cache
        docker push richmondu/iotmongodb
        docker push richmondu/iotrabbitmq
        docker push richmondu/iothistory
        docker push richmondu/iotnotification
        docker push richmondu/iotrestapi
        docker push richmondu/iotwebapp
        docker push richmondu/iotnginx


2. Set docker-registry (one-time only)

        kubectl create secret docker-registry regcred --docker-server=docker.io 
         --docker-username=USERNAME --docker-password=PASSWORD --docker-email=EMAIL


3. Fill-up environment.yaml. Then run below.  (one-time only)

        kubectl apply -f environment.yaml


4. Run MongoDB

        kubectl apply -f iotmongodb-persistentvolumeclaim.yaml
        kubectl apply -f iotmongodb-deployment.yaml
        kubectl apply -f iotmongodb-service.yaml


5. Run RabbitMQ

        kubectl apply -f iotrabbitmq-deployment.yaml
        kubectl apply -f iotrabbitmq-service.yaml


6. Run history manager and notification manager

        kubectl apply -f iothistory-deployment.yaml
        kubectl apply -f iotnotification-deployment.yaml


7. Run RESTAPI

        kubectl apply -f iotrestapi-deployment.yaml
        kubectl apply -f iotrestapi-service.yaml


8. Run Webapp

        kubectl apply -f iotwebapp-deployment.yaml
        kubectl apply -f iotwebapp-service.yaml


9. Run Nginx

        kubectl apply -f iotnginx-deployment.yaml
        kubectl apply -f iotnginx-service.yaml


10. Test web app

        https://MINIKUBE_IP:30443


11. Delete all

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
        
        
12. Delete secrets (not really needed if you want to run again)
        
        kubectl delete secret environment
        kubectl delete secret regcred


### Notes:

         minikube ip
         minikube start
         minikube stop
         minikube delete
         minikube service SERVICENAME --url

         kubectl get secrets
         kubectl get deployments
         kubectl get pods
         kubectl get svc
         kubectl get persistentvolumeclaim

         kubectl get nodes
         kubectl logs PODNAME
         kubectl describe pod PODNAME
         
         kubectl delete secret SECRETNAME
         kubectl delete deployment DEPLOYMENTNAME
         kubectl delete service SERVICENAME
         kubectl delete persistentvolumeclaim PERSISTENTVOLUMENAME
