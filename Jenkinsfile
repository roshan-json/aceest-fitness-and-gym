// Jenkins declarative pipeline
// - Builds the Docker "test" target to run pytest during build
// - Builds the runtime image
// - Pushes images to GitHub Container Registry (GHCR)
//
// Prerequisites in Jenkins:
// 1) A node/agent with Docker installed and permission to run docker commands.
// 2) A Jenkins credential of type "Username with password" with ID 'ghcr-creds'
//    where the username is your GH username and password is a personal access token
//    with "write:packages" and "repo" (if pushing to ghcr.io).

pipeline {
  agent any

  environment {
    IMAGE_NAME = "ghcr.io/roshanjson/aceest-fitness-and-gym"
    DOCKERFILE = "dockerFile/Dockerfile"
    RUNTIME_TAG = "${env.BUILD_ID}"
    TEST_TAG = "${env.BUILD_ID}-test"
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Build & Test (docker test target)') {
      steps {
        script {
          // Build the test target which runs pytest during image build
          sh "docker build --progress=plain --target test -f ${DOCKERFILE} -t ${IMAGE_NAME}:${TEST_TAG} ."
        }
      }
    }

    stage('Build Runtime Image') {
      steps {
        sh "docker build --progress=plain -f ${DOCKERFILE} -t ${IMAGE_NAME}:${RUNTIME_TAG} ."
      }
    }

    stage('Push Images') {
      steps {
        // Use a stored Jenkins credential (username/password) for GHCR
        withCredentials([usernamePassword(credentialsId: 'ghcr-creds', usernameVariable: 'GHCR_USER', passwordVariable: 'GHCR_TOKEN')]) {
          sh 'echo $GHCR_TOKEN | docker login ghcr.io -u $GHCR_USER --password-stdin'
          sh "docker push ${IMAGE_NAME}:${RUNTIME_TAG}"
          sh "docker push ${IMAGE_NAME}:${TEST_TAG}"
        }
      }
    }
  }

  post {
    always {
      cleanWs()
    }
    success {
      echo "Build, test and push completed: ${IMAGE_NAME}:${RUNTIME_TAG}"
    }
    failure {
      echo 'Pipeline failed - inspect logs.'
    }
  }
}
