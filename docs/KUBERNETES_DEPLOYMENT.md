# Kubernetes Deployment Guide

This guide covers deploying the AI Prototyping Tool to Kubernetes clusters using either raw manifests or Helm charts.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start with Helm](#quick-start-with-helm)
- [Manual Deployment with Kubectl](#manual-deployment-with-kubectl)
- [Configuration](#configuration)
- [Scaling and High Availability](#scaling-and-high-availability)
- [Monitoring and Observability](#monitoring-and-observability)
- [Security Considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)
- [Production Best Practices](#production-best-practices)

## Prerequisites

### Required Tools
- kubectl 1.24+
- Helm 3.8+ (for Helm deployment)
- Access to a Kubernetes cluster (1.24+)
- Docker registry access for container images

### Cluster Requirements
- Kubernetes 1.24 or higher
- Ingress controller (nginx recommended)
- At least 2GB RAM and 2 CPU cores available
- Storage class for persistent volumes (optional)

### Installing Prerequisites

**kubectl:**
```bash
# macOS
brew install kubectl

# Linux
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
```

**Helm:**
```bash
# macOS
brew install helm

# Linux
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

## Quick Start with Helm

### 1. Add the Helm Repository (if published)

```bash
# If the chart is published to a Helm repository
helm repo add ai-prototyping-tool https://charts.example.com/
helm repo update
```

### 2. Install from Local Chart

```bash
# Navigate to the project directory
cd AI-Prototyping-Tool

# Install the application
helm install ai-prototyping-tool ./helm/ai-prototyping-tool \
  --create-namespace \
  --namespace ai-prototyping-tool
```

### 3. Custom Configuration

```bash
# Create custom values file
cat > custom-values.yaml << EOF
web:
  replicaCount: 3
  resources:
    requests:
      memory: "512Mi"
      cpu: "200m"
    limits:
      memory: "1Gi"
      cpu: "1000m"

ingress:
  enabled: true
  hosts:
    - host: ai-prototyping.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: ai-prototyping-tls
      hosts:
        - ai-prototyping.example.com

persistence:
  enabled: true
  size: 10Gi
EOF

# Install with custom values
helm install ai-prototyping-tool ./helm/ai-prototyping-tool \
  --create-namespace \
  --namespace ai-prototyping-tool \
  --values custom-values.yaml
```

### 4. Verify Installation

```bash
# Check deployment status
helm status ai-prototyping-tool -n ai-prototyping-tool

# Check pods
kubectl get pods -n ai-prototyping-tool

# Check services
kubectl get services -n ai-prototyping-tool

# Check ingress
kubectl get ingress -n ai-prototyping-tool
```

### 5. Access the Application

```bash
# Port forward for local access
kubectl port-forward -n ai-prototyping-tool service/ai-prototyping-tool-web 8000:8000

# Access at http://localhost:8000
```

## Manual Deployment with Kubectl

### 1. Build and Push Images

```bash
# Build the web application image
docker build -t your-registry/ai-prototyping-tool:1.0.0 .

# Build the mock LM Studio service
docker build -t your-registry/lmstudio-mock:1.0.0 ./docker/lmstudio-mock/

# Push to registry
docker push your-registry/ai-prototyping-tool:1.0.0
docker push your-registry/lmstudio-mock:1.0.0
```

### 2. Update Image References

```bash
# Update image references in manifests
sed -i 's|ai-prototyping-tool:1.0.0|your-registry/ai-prototyping-tool:1.0.0|g' k8s/*.yaml
sed -i 's|lmstudio-mock:1.0.0|your-registry/lmstudio-mock:1.0.0|g' k8s/*.yaml
```

### 3. Deploy Components

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Deploy configuration
kubectl apply -f k8s/configmap.yaml

# Deploy LM Studio mock service
kubectl apply -f k8s/lmstudio-mock-deployment.yaml

# Deploy web application
kubectl apply -f k8s/web-deployment.yaml

# Create services
kubectl apply -f k8s/services.yaml

# Create ingress (optional)
kubectl apply -f k8s/ingress.yaml
```

### 4. Verify Deployment

```bash
# Check all resources
kubectl get all -n ai-prototyping-tool

# Check deployment status
kubectl rollout status deployment/ai-prototyping-web -n ai-prototyping-tool
kubectl rollout status deployment/lmstudio-mock -n ai-prototyping-tool

# Check logs
kubectl logs -f deployment/ai-prototyping-web -n ai-prototyping-tool
```

## Configuration

### Environment Variables

Key environment variables that can be configured:

```yaml
env:
  - name: AIPROTO_APP_ENVIRONMENT
    value: "production"
  - name: AIPROTO_APP_DEBUG
    value: "false"
  - name: AIPROTO_LOGGING_LEVEL
    value: "INFO"
  - name: AIPROTO_LM_STUDIO_BASE_URL
    value: "http://lmstudio-mock-service:1234"
```

### ConfigMap Configuration

The application configuration is managed via ConfigMap. To update:

```bash
# Edit the configmap
kubectl edit configmap ai-prototyping-config -n ai-prototyping-tool

# Restart deployments to pick up changes
kubectl rollout restart deployment/ai-prototyping-web -n ai-prototyping-tool
```

### Secrets Management

For sensitive data, use Kubernetes Secrets:

```bash
# Create secret for API keys or other sensitive data
kubectl create secret generic ai-prototyping-secrets \
  --from-literal=api-key="your-secret-key" \
  --namespace ai-prototyping-tool

# Reference in deployment
env:
  - name: AIPROTO_API_KEY
    valueFrom:
      secretKeyRef:
        name: ai-prototyping-secrets
        key: api-key
```

## Scaling and High Availability

### Horizontal Pod Autoscaling

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ai-prototyping-web-hpa
  namespace: ai-prototyping-tool
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ai-prototyping-web
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Pod Disruption Budget

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: ai-prototyping-web-pdb
  namespace: ai-prototyping-tool
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app.kubernetes.io/name: ai-prototyping-tool
      app.kubernetes.io/component: web
```

### Multi-AZ Deployment

```yaml
affinity:
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
    - weight: 100
      podAffinityTerm:
        labelSelector:
          matchLabels:
            app.kubernetes.io/name: ai-prototyping-tool
            app.kubernetes.io/component: web
        topologyKey: topology.kubernetes.io/zone
```

## Monitoring and Observability

### Prometheus Monitoring

The application exposes Prometheus metrics. To scrape them:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: ai-prototyping-tool
  namespace: ai-prototyping-tool
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: ai-prototyping-tool
      app.kubernetes.io/component: web
  endpoints:
  - port: http
    path: /metrics
    interval: 30s
```

### Health Checks

```bash
# Check application health
kubectl exec -n ai-prototyping-tool deployment/ai-prototyping-web -- curl http://localhost:8000/health

# Check readiness
kubectl exec -n ai-prototyping-tool deployment/ai-prototyping-web -- curl http://localhost:8000/ready
```

### Log Collection

```bash
# Stream logs from all pods
kubectl logs -f -l app.kubernetes.io/name=ai-prototyping-tool -n ai-prototyping-tool

# Get logs from specific pod
kubectl logs -f pod/ai-prototyping-web-xxx-yyy -n ai-prototyping-tool

# Export logs
kubectl logs deployment/ai-prototyping-web -n ai-prototyping-tool > app.log
```

## Security Considerations

### Network Policies

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: ai-prototyping-tool-netpol
  namespace: ai-prototyping-tool
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/name: ai-prototyping-tool
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app.kubernetes.io/component: lmstudio-mock
    ports:
    - protocol: TCP
      port: 1234
```

### RBAC Configuration

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: ai-prototyping-tool
  namespace: ai-prototyping-tool
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: ai-prototyping-tool
  namespace: ai-prototyping-tool
rules:
- apiGroups: [""]
  resources: ["configmaps"]
  verbs: ["get", "list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: ai-prototyping-tool
  namespace: ai-prototyping-tool
subjects:
- kind: ServiceAccount
  name: ai-prototyping-tool
  namespace: ai-prototyping-tool
roleRef:
  kind: Role
  name: ai-prototyping-tool
  apiGroup: rbac.authorization.k8s.io
```

### Security Contexts

Containers run with non-root user and restricted capabilities:

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  runAsGroup: 1000
  fsGroup: 1000

containerSecurityContext:
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: false  # Set to true if possible
  capabilities:
    drop:
    - ALL
```

## Troubleshooting

### Common Issues

1. **Pods stuck in Pending state:**
   ```bash
   kubectl describe pod -n ai-prototyping-tool
   # Check resource constraints, node selectors, or taints
   ```

2. **Image pull errors:**
   ```bash
   kubectl describe pod -n ai-prototyping-tool
   # Verify image names and registry access
   ```

3. **Service connectivity issues:**
   ```bash
   # Test internal connectivity
   kubectl exec -n ai-prototyping-tool deployment/ai-prototyping-web -- \
     curl http://lmstudio-mock-service:1234/health
   ```

4. **Ingress not working:**
   ```bash
   kubectl describe ingress -n ai-prototyping-tool
   kubectl get events -n ai-prototyping-tool
   ```

### Debugging Commands

```bash
# Get detailed pod information
kubectl describe pod <pod-name> -n ai-prototyping-tool

# Check events
kubectl get events -n ai-prototyping-tool --sort-by='.lastTimestamp'

# Execute commands in pod
kubectl exec -it deployment/ai-prototyping-web -n ai-prototyping-tool -- bash

# Port forward for debugging
kubectl port-forward -n ai-prototyping-tool service/ai-prototyping-web-service 8000:8000

# Check resource usage
kubectl top pods -n ai-prototyping-tool
kubectl top nodes
```

## Production Best Practices

### Resource Management

```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "100m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

### Update Strategy

```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1
    maxUnavailable: 0
```

### Health Checks

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: http
  initialDelaySeconds: 30
  periodSeconds: 30
  timeoutSeconds: 5
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /health
    port: http
  initialDelaySeconds: 5
  periodSeconds: 10
  timeoutSeconds: 3
  failureThreshold: 3
```

### Backup and Disaster Recovery

```bash
# Backup persistent volumes
kubectl get pv -o yaml > pv-backup.yaml

# Backup application manifests
helm get values ai-prototyping-tool -n ai-prototyping-tool > values-backup.yaml

# Export all resources
kubectl get all -n ai-prototyping-tool -o yaml > app-backup.yaml
```

### Monitoring Setup

1. **Install Prometheus and Grafana:**
   ```bash
   helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
   helm install prometheus prometheus-community/kube-prometheus-stack
   ```

2. **Configure ServiceMonitor:**
   ```bash
   kubectl apply -f monitoring/servicemonitor.yaml
   ```

3. **Import Grafana dashboards:**
   - Application metrics dashboard
   - Infrastructure monitoring
   - Alert rules

### Continuous Deployment

```bash
# Example GitOps workflow with ArgoCD
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: ai-prototyping-tool
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/your-org/ai-prototyping-tool
    targetRevision: HEAD
    path: helm/ai-prototyping-tool
  destination:
    server: https://kubernetes.default.svc
    namespace: ai-prototyping-tool
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

### Performance Optimization

1. **Use resource limits and requests appropriately**
2. **Enable horizontal pod autoscaling**
3. **Use persistent volumes for data that needs to survive pod restarts**
4. **Configure appropriate health check intervals**
5. **Use node affinity to optimize pod placement**
6. **Monitor and adjust based on actual usage patterns**

For additional support and advanced configurations, refer to the main project documentation or create an issue in the project repository.
