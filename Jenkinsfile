// Jenkins declarative pipeline with Kubernetes deployment
// - Builds the Docker "test" target to run pytest during build
// - Builds the runtime image
// - Pushes images to GitHub Container Registry (GHCR)
// - Validates Kubernetes manifests
// - Deploys to Kubernetes cluster (optional, based on environment)
//
// Prerequisites in Jenkins:
// 1) A node/agent with Docker and kubectl installed
// 2) A Jenkins credential of type "Username with password" with ID 'ghcr-creds'
//    where the username is your GH username and password is a personal access token
//    with "write:packages" and "repo" (if pushing to ghcr.io).
// 3) For Kubernetes deployment: kubeconfig credential or cluster access

pipeline {
  agent any

  environment {
    IMAGE_NAME = "ghcr.io/roshanjson/aceest-fitness-and-gym"
    DOCKERFILE = "dockerFile/Dockerfile"
    // VERSION will be set at runtime in the Checkout stage
    VERSION = "unset"
    KUBECONFIG_PATH = credentials('kubeconfig') // Optional: for cluster deployment
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

    stage('Validate Kubernetes Manifests') {
      steps {
        script {
          // Validate YAML syntax using Python (no cluster connection needed)
          sh '''
            python3 << 'EOF'
import yaml
import os
import sys

valid = True
for root, dirs, files in os.walk('k8s'):
    for file in files:
        if file.endswith(('.yaml', '.yml')):
            filepath = os.path.join(root, file)
            print(f"Validating {filepath}...")
            try:
                with open(filepath, 'r') as f:
                    yaml.safe_load(f)
                print(f"  ✓ Valid")
            except yaml.YAMLError as e:
                print(f"  ✗ Invalid: {e}")
                valid = False

if valid:
    print("\nAll Kubernetes manifests are valid!")
    sys.exit(0)
else:
    print("\nSome manifests have errors!")
    sys.exit(1)
EOF
          '''
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

    stage('Deploy to Kubernetes (Optional)') {
      when {
        expression { return env.DEPLOY_TO_K8S == 'true' }
      }
      steps {
        script {
          // Deploy using kubectl - requires kubeconfig credential
          sh '''
            set -e
            echo "Deploying to Kubernetes cluster..."

            # Update image in deployments
            sed -i "s|ghcr.io/roshanjson/aceest-fitness-and-gym:latest|${IMAGE_NAME}:${VERSION}|g" k8s/*.yaml

            # Apply Kubernetes manifests
            kubectl apply -f k8s/

            # Wait for rollout to complete
            kubectl rollout status deployment/aceest-fitness-deployment --timeout=300s

            echo "Deployment completed successfully!"
          '''
        }
      }
    }

    stage('Tag & Push Git') {
      when {
        allOf {
          branch 'main'
          expression { return env.VERSION != 'unset' }
        }
      }
      steps {
        // Create and push a git tag for the new version so next build will increment
        withCredentials([usernamePassword(credentialsId: 'ghcr-creds', usernameVariable: 'GIT_USER', passwordVariable: 'GIT_TOKEN')]) {
          script {
            def tagName = "v${env.VERSION}"
            sh '''
              set -e
              git config user.email "jenkins@localhost"
              git config user.name "${GIT_USER}"
              # Avoid failing if tag already exists
              if git rev-parse "refs/tags/${tagName}" >/dev/null 2>&dev/null; then
                echo "Tag ${tagName} already exists, skipping creation"
              else
                git tag -a "${tagName}" -m "CI: release ${tagName}"
                # Push the tag using token-authenticated URL
                git push "https://${GIT_USER}:${GIT_TOKEN}@github.com/roshanjson/aceest-fitness-and-gym.git" "${tagName}"
              fi
            '''
          }
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