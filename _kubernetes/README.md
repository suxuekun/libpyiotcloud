# IoT Portal on Kubernetes

Support for IoT portal is now available. This has been tested using Minikube. 


### Instructions:

1. Set docker-registry
kubectl create secret docker-registry regcred --docker-server=docker.io --docker-username=<USERNAME> --docker-password=<PASSWORD> --docker-email=<EMAIL>

2. Fill-up environment.yaml then run 
kubectl apply -f environment.yaml

3. Run RabbitMQ
kubectl apply -f iotrabbitmq-deployment.yaml
kubectl apply -f iotrabbitmq-service.yaml

4. Run history manager and notification manager
kubectl apply -f iothistory-deployment.yaml
kubectl apply -f iotnotification-deployment.yaml

5. Run MongoDB
kubectl apply -f iotmongodb-persistentvolumeclaim.yaml
kubectl apply -f iotmongodb-deployment.yaml
kubectl apply -f iotmongodb-service.yaml

6. Run RESTAPI
kubectl apply -f iotrestapi-deployment.yaml
kubectl apply -f iotrestapi-service.yaml

7. Run Webapp
kubectl apply -f iotwebapp-deployment.yaml
kubectl apply -f iotwebapp-service.yaml

8. Run Nginx
kubectl apply -f iotnginx-deployment.yaml
kubectl apply -f iotnginx-service.yaml

X. Stop all
kubectl delete service nginx
kubectl delete deployment nginx
kubectl delete service webapp
kubectl delete deployment webapp
kubectl delete service restapi
kubectl delete deployment restapi
kubectl delete service mongodb
kubectl delete deployment mongodb
kubectl delete persistentvolumeclaim mydockervol
kubectl delete deployment history
kubectl delete deployment notification
kubectl delete service rabbitmq
kubectl delete deployment rabbitmq
kubectl delete secret environment
kubectl delete secret regcred


### Notes:

minikube ip
minikube start
minikube stop
minikube delete
minikube service <SERVICENAME> --url

kubectl get secrets
kubectl get deployments
kubectl get pods
kubectl get svc
kubectl get persistentvolumeclaim
kubectl log <PODNAME>
kubectl describe pod <PODNAME>
kubectl delete secret <SECRETNAME>
kubectl delete deployment <DEPLOYMENTNAME>
kubectl delete service <SERVICENAME>
kubectl delete persistentvolumeclaim <PERSISTENTVOLUMENAME>
