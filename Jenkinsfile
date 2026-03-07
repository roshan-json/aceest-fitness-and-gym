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
    // VERSION will be set at runtime in the Checkout stage
    VERSION = "unset"
  }

  stages {
    stage('Checkout & Versioning') {
      steps {
        checkout scm
        script {
          // Fetch tags then determine version: increment patch of latest tag or start at 0.1.0
          sh 'git fetch --tags --force'
          def latestTag = sh(script: "git describe --tags --abbrev=0 2>/dev/null || echo ''", returnStdout: true).trim()
          if (!latestTag) {
            // No tags found -> start a new sequence
            env.VERSION = '0.1.0'
          } else {
            // Normalize tag (strip leading v if present)
            def t = latestTag.replaceFirst(/^v/, '')
            def parts = t.tokenize('.')
            if (parts.size() < 3) {
              // If tag not semver, fallback
              env.VERSION = '0.1.0'
            } else {
              def major = parts[0].toInteger()
              def minor = parts[1].toInteger()
              def patch = parts[2].toInteger() + 1
              env.VERSION = "${major}.${minor}.${patch}"
            }
          }
          echo "Computed VERSION=${env.VERSION} (based on latest tag: ${latestTag})"
        }
      }
    }

    stage('Build & Test (docker test target)') {
      steps {
        script {
          def testTag = "${env.VERSION}-test"
          // Build the test target which runs pytest during image build
          sh "docker build --progress=plain --target test -f ${DOCKERFILE} -t ${IMAGE_NAME}:${testTag} ."
        }
      }
    }

    stage('Build Runtime Image') {
      steps {
        script {
          def runtimeTag = "${env.VERSION}"
          sh "docker build --progress=plain -f ${DOCKERFILE} -t ${IMAGE_NAME}:${runtimeTag} ."
        }
      }
    }

    stage('Push Images') {
      steps {
        // Use a stored Jenkins credential (username/password) for GHCR
        withCredentials([usernamePassword(credentialsId: 'ghcr-creds', usernameVariable: 'GHCR_USER', passwordVariable: 'GHCR_TOKEN')]) {
          sh 'echo $GHCR_TOKEN | docker login ghcr.io -u $GHCR_USER --password-stdin'
          sh "docker push ${IMAGE_NAME}:${env.VERSION}"
          sh "docker push ${IMAGE_NAME}:${env.VERSION}-test"
        }
      }
    }
  }

  post {
    always {
      cleanWs()
    }
    success {
      echo "Build, test and push completed: ${IMAGE_NAME}:${env.VERSION}"
    }
    failure {
      echo 'Pipeline failed - inspect logs.'
    }
  }
}
