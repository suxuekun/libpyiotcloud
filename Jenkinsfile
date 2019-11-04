pipeline {

    agent any

    stages {

        stage("Copy production certificates") {
            steps {
                echo "Copy certificates STARTED"
                sh "cp -ar /home/ec2-user/certificates/ nginx/src_prod/cert"
                echo "Copy certificates COMPLETED"
            }
        }
        
        stage("Docker-compose down") {
            steps {
                sh "docker-compose down"
                sh "docker-compose rm -f"
                sh "docker network prune -f"
            }
        }

        stage("Docker-compose config") {
            steps {
                sh "docker-compose -f docker-compose.yml config"
            }
        }

        stage("Docker-compose build") {
            steps {
                sh "docker-compose build --no-cache"
            }
        }

        stage("Docker-compose up") {
            steps {
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
            echo "Docker-compose completed"
          
            echo "Sending email notification..."
            mail to: 'richmond.umagat@brtchip.com',
                subject: "Jenkins notification - ${currentBuild.projectName}",
                body: "Jenkins build triggered ${env.BUILD_URL}.\nProject: ${currentBuild.projectName}\nResult: ${currentBuild.currentResult}\n"
            echo "Sending email notification...DONE"
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
