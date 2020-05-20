# Backend Environment Setup Guide

Below contains a step-by-step instructions on installing and setting up the backend and frontend web infrastructure of <b>IoT Portal on local machine</b>.


## Development Tools

Please install the following tools to get the IoT Portal running on your local machine.

1. Git

    A. [Windows](https://git-scm.com/download/win)

    B. [Mac OS](https://git-scm.com/download/mac)


2. (Optional) Github Desktop

    A. [Windows](https://central.github.com/deployments/desktop/desktop/latest/win32)

    B. [Mac OS](https://central.github.com/deployments/desktop/desktop/latest/darwin)


3. Docker Toolbox or Docker Desktop

    A. Windows 7 - [Docker Toolbox](https://docs.docker.com/toolbox/toolbox_install_windows/)

    B. Windows 10 Home - [Docker Toolbox](https://docs.docker.com/toolbox/toolbox_install_windows/)

    C. Windows 10 Pro - [Docker Desktop](https://docs.docker.com/docker-for-windows/) 

    D. Mac OS - [Docker Desktop](https://docs.docker.com/docker-for-mac/)

    Note that I'm using both A and B on my PC and laptop, respectively.


4. Python 3.X.X

    A. [Windows](https://www.python.org/downloads/windows/)

    B. [Mac OS](https://www.python.org/downloads/mac-osx/)   


5. NodeJS 12.X.X

    A. [Windows](https://nodejs.org/dist/v12.13.0/node-v12.13.0-x64.msi)

    B. [Mac OS](https://nodejs.org/dist/v12.13.0/node-v12.13.0.pkg)


6. (Optional) [RabbitMQ](https://www.rabbitmq.com/download.html) 

    To be used for non-Docker version.
    Note that the configuration file needs to be updated. Refer to <b>rabbitmq.config</b> and <b>cert_ecc</b> folder in libpyiotcloud/rabbitmq/src


7. (Optional) [MongoDB](https://www.mongodb.com/download-center/community)

    To be used for non-Docker version.


## Development Setup

Please follow the steps below to get the IoT Portal running on your local machine.

Having the backend running on your local machine will enable you 
to eventually do code modifications as needed while developing the mobile applications.
This means you'll be able to update or add new APIs as the mobile app requires.
Or at the least be able to experiment before proposing new or modified APIs.

1. Download the code from the repository.

		A. Run Docker Toolbox/Desktop as administrator.

		B. Type "git clone https://github.com/richmondu/libpyiotcloud/tree/dev"
		   In Mac OS, make sure the folder has permission. Refer to https://stackoverflow.com/questions/16376035/fatal-could-not-create-work-tree-dir-kivy.
		   1. Update libpyiotcloud\rabbitmq\src\rabbitmq.config
		   2. Remove libpyiotcloud\rabbitmq\src\rabbitmq-env.conf

		C. Type "docker-machine ip"
		   Take note of the value as this will be used in the next steps.


2. Set the environment system variables.

		A. In Linux/MacOS, use <b>export ENVIRONMENT_SYSTEM_VARIABLE="ENVIRONMENT_SYSTEM_VALUE"</b>

		B. In Windows, always <b>restart the Docker Toolbox/Desktop</b> after adding or updating an environment system variable.


3. Run the Docker images using the following commands.

		A. Type "cd libpyiotcloud"

		B. Type "docker-compose -f docker-compose.yml config"
		C. Type "docker-compose build" // To rebuild from scratch, add "--no-cache"
		D. Type "docker-compose up" // To run asynchronously as daemon, add "-d"

		E. Open a browser and browse https://docker-machine_ip // Refer to value of "docker-machine ip"


    <b>Note to stop the docker containers, do the following:</b>

		F. Type "Ctrl+C"

		G. Type "docker-compose down"
		H. Type "docker-compose rm"
		I. Type "docker network prune -f"


4. Run a device simulator.

		Refer to https://github.com/richmondu/libpyiotcloud/tree/dev/_device_simulator



## Docker Basic Commands

		docker-machine ip
		docker ps
		docker ps --size
		docker logs <container>

		docker-compose -f docker-compose.yml config
		docker-compose build
		docker-compose build --no-cache // build from scratch, note: takes too long
		docker-compose build <container>
		docker-compose up
		docker-compose up -d // run as daemon
		docker-compose ps
		docker-compose down
		docker-compose rm

		docker network prune -f
		docker volume prune -f
		docker system prune -f

		docker build <container>
		docker run <container>
		docker stop <container>
		docker kill <container>
		docker rm <container>
		docker image ls
		docker image rm <container>
		docker volume ls
		docker volume inspect <volume>
		docker network ls
		docker network inspect <network>
		docker system df --verbose
