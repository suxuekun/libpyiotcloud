pipeline {

    agent any

    stages {

        stage("Docker-compose config") {
            steps {
                sh "docker-compose -f docker-compose.yml config"
            }
        }

        stage("Docker-compose build") {
            steps {
                sh "docker-compose build"
            }
        }

        stage("Docker-compose up -d") {
            steps {
                sh "docker-compose up -d"
            }
        }
    }

    post {
      always {
          echo "Docker-compose completed"
      }

      success {
          echo "Success"
      }

      failure {
          echo "Fail"
      }
    }
}