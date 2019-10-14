pipeline {

    agent any

    environment {
        AWS_ACCESS_KEY_ID2 = "${env.AWS_ACCESS_KEY_ID}"
    }

    stages {
        stage("Prepare") {
            steps {
                sh "docker-compose -f docker-compose.yml config"
            }
        }
    }

    post {
      always {
          sh "Post"
      }

      success {
          sh "Success"
      }

      failure {
          sh "Fail"
      }
    }
}