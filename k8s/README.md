# Kubernetes Deployment Strategies for ACEest Fitness & Gym

This directory contains Kubernetes manifests implementing various deployment strategies as required for Assignment 2.

## Available Strategies

### 1. Blue-Green Deployment
- **Files**: `blue-deployment.yaml`, `green-deployment.yaml`, `blue-green-service.yaml`
- **Description**: Two identical environments (blue and green) where one serves production traffic while the other is updated and tested.
- **Usage**:
  ```bash
  # Deploy blue environment
  kubectl apply -f blue-deployment.yaml
  kubectl apply -f blue-green-service.yaml

  # Deploy green environment (new version)
  kubectl apply -f green-deployment.yaml

  # Switch traffic to green
  kubectl patch service aceest-fitness-blue-green -p '{"spec":{"selector":{"version":"green"}}}'
  ```

### 2. Canary Deployment
- **Files**: `canary-deployment.yaml`, `canary-service.yaml`
- **Description**: Gradually roll out new version to a small subset of users before full deployment.
- **Usage**:
  ```bash
  # Deploy canary version
  kubectl apply -f canary-deployment.yaml
  kubectl apply -f canary-service.yaml

  # Gradually increase canary traffic by scaling replicas
  kubectl scale deployment aceest-fitness-canary --replicas=2
  ```

### 3. Rolling Update
- **Files**: `rolling-deployment.yaml`
- **Description**: Update pods incrementally, ensuring zero-downtime by maintaining available replicas.
- **Usage**:
  ```bash
  kubectl apply -f rolling-deployment.yaml
  # Update image
  kubectl set image deployment/aceest-fitness-rolling aceest-fitness=ghcr.io/roshanjson/aceest-fitness-and-gym:v2.0.0
  ```

### 4. A/B Testing
- **Files**: `ab-test-deployment.yaml`
- **Description**: Route traffic based on user attributes or headers to test new features with specific user groups.
- **Usage**: Requires ingress controller or service mesh for traffic splitting based on headers/cookies.

### 5. Shadow Deployment
- **Files**: `shadow-deployment.yaml`
- **Description**: Run new version alongside production without serving user traffic, for testing and monitoring.
- **Usage**:
  ```bash
  kubectl apply -f shadow-deployment.yaml
  # Monitor logs and metrics without affecting production
  kubectl logs -f deployment/aceest-fitness-shadow
  ```

## Base Deployment
- **Files**: `deployment.yaml`, `service.yaml`
- **Description**: Standard Kubernetes deployment with 2 replicas, readiness/liveness probes, and ClusterIP service.

## Rollback Procedures

For all strategies, rollback to previous version:
```bash
# Blue-Green: Switch service selector back
kubectl patch service <service-name> -p '{"spec":{"selector":{"version":"blue"}}}'

# Rolling: Update to previous image
kubectl set image deployment/<deployment-name> <container-name>=<previous-image>

# Canary/A-B/Shadow: Scale down new deployment
kubectl scale deployment <new-deployment> --replicas=0
```

## Health Checks
All deployments include:
- Readiness probe: `/clients` endpoint
- Liveness probe: `/clients` endpoint
- Initial delay: 5s (readiness), 20s (liveness)
- Check interval: 10s (readiness), 20s (liveness)