pipeline {

    agent any

    environment {
        AWS_ACCESS_KEY_ID = "${env.AWS_ACCESS_KEY_ID}"
    }

    stages {
        stage("Prepare") {
            steps {
                echo "AWS_ACCESS_KEY_ID=${env.AWS_ACCESS_KEY_ID}"
                echo "${env.AWS_SECRET_ACCESS_KEY}"
                echo "${env.AWS_COGNITO_CLIENT_ID}"
                echo "${env.AWS_COGNITO_USERPOOL_ID}"
                echo "${env.AWS_COGNITO_USERPOOL_REGION}"
                echo "${env.AWS_PINPOINT_ID}"
                echo "${env.AWS_PINPOINT_REGION}"
                echo "${env.AWS_PINPOINT_EMAIL}"
                echo "${env.CONFIG_USE_ECC}"
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