pipeline {

    agent any

    environment {
        PATH = "$PATH:/usr/local/bin"
    }
    
    stages {

        stage("Copy production certificates") {
            steps {
                script {
                    echo "Copy certificates STARTED"
                    if (env.CONFIG_USE_APIURL == "richmondu.com") {
                        sh "sudo cp /home/ec2-user/certificates/cert.pem nginx/src_prod/cert/cert.pem"
                        sh "sudo cp /home/ec2-user/certificates/pkey.pem nginx/src_prod/cert/pkey.pem"
                        sh "ls -l nginx/src_prod/cert"
                    }
                    echo "Copy certificates COMPLETED"
                }
            }
        }
        
        stage("Docker-compose down") {
            steps {
                echo "STOPPING running containers"
                sh "docker-compose down"
                sh "docker-compose rm -f"
                sh "docker network prune -f"
            }
        }

        stage("Docker-compose config") {
            steps {
                echo "CHECKING configuration"
                sh "docker-compose -f docker-compose.yml config"
            }
        }

        stage("Docker-compose build") {
            steps {
                echo "BUILDING docker images"
                sh "ls -l nginx/src_prod/cert"
                sh "docker-compose build"
            }
        }

        stage("Docker-compose up") {
            steps {
                echo "RUNNING containers"
                sh "docker-compose up -d"
            }
        }


        stage("MESSAGE BROKER tester") {
            steps {
                echo "MESSAGE BROKER tester STARTED"
                // TODO
                //sh "cd _jenkins/tester"
                //sh "python -v"
                echo "MESSAGE BROKER tester COMPLETED"
            }
        }

        stage("REST API tester") {
            steps {
                echo "REST API tester STARTED"
                // TODO
                echo "REST API tester COMPLETED"
            }
        }

        stage("DATABASE tester") {
            steps {
                echo "DATABASE tester STARTED"
                // TODO
                echo "DATABASE tester COMPLETED"
            }
        }

        stage("WEB APP tester") {
            steps {
                echo "WEB APP tester STARTED"
                // TODO
                echo "WEB APP tester COMPLETED"
            }
        }
    }

    post {
        always {
            script {
                echo "Docker-compose completed"

                echo "Sending email notification.."
                if (env.CONFIG_USE_APIURL == "prod.brtchip-iotportal.com") {
                    mail to: 'richmond.umagat@brtchip.com',
                        subject: "Jenkins notification - ${currentBuild.projectName}",
                        body: "This email was generated by Jenkins server.\n\nJenkins build triggered ${env.BUILD_URL}.\nProject: ${currentBuild.projectName}\nResult: ${currentBuild.currentResult}\n\nVisit https://prod.brtchip-iotportal.com for the updated website!\n"
                }
                else {
                    mail to: 'richmond.umagat@brtchip.com',
                        subject: "Jenkins notification - ${currentBuild.projectName}",
                        body: "This email was generated by Jenkins server.\n\nJenkins build triggered ${env.BUILD_URL}.\nProject: ${currentBuild.projectName}\nResult: ${currentBuild.currentResult}\n\nVisit https://dev.brtchip-iotportal.com for the updated website!\n"
                }
                echo "Sending email notification..DONE"
            }
        }

        success {
            echo "Success"
        }

        failure {
            echo "Fail"
            sh "docker-compose down"
            sh "docker-compose rm -f"
            sh "docker network prune -f"
        }
    }
}
