pipeline {

    agent any

    environment {
        AWS_ACCESS_KEY_ID = "${env.AWS_ACCESS_KEY_ID}"
        AWS_SECRET_ACCESS_KEY = "${env.AWS_SECRET_ACCESS_KEY}"
        AWS_COGNITO_CLIENT_ID = "${env.AWS_COGNITO_CLIENT_ID}"
        AWS_COGNITO_USERPOOL_ID = "${env.AWS_COGNITO_USERPOOL_ID}"
        AWS_COGNITO_USERPOOL_REGION = "${env.AWS_COGNITO_USERPOOL_REGION}"
        AWS_PINPOINT_ID = "${env.AWS_PINPOINT_ID}"
        AWS_PINPOINT_REGION = "${env.AWS_PINPOINT_REGION}"
        AWS_PINPOINT_EMAIL = "${env.AWS_PINPOINT_EMAIL}"
        CONFIG_USE_ECC = "${env.CONFIG_USE_ECC}"
    }

    stages {
        stage("Prepare") {
            steps {
                withEnv(["PATH=$PATH:~/.local/bin"]){
                    echo $AWS_ACCESS_KEY_ID
                    echo $AWS_SECRET_ACCESS_KEY
                    echo $AWS_COGNITO_CLIENT_ID
                    echo $AWS_COGNITO_USERPOOL_ID
                    echo $AWS_COGNITO_USERPOOL_REGION
                    echo $AWS_PINPOINT_ID
                    echo $AWS_PINPOINT_REGION
                    echo $AWS_PINPOINT_EMAIL
                    echo $CONFIG_USE_ECC
                    sh "docker-compose -f docker-compose.yml config"
                }
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