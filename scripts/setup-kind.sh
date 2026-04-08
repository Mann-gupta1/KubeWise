#!/usr/bin/env bash
set -euo pipefail

echo "==> Creating kind cluster..."
kind create cluster --name kubewise-dev --wait 60s

echo "==> Installing kube-state-metrics..."
kubectl apply -f https://github.com/kubernetes/kube-state-metrics/releases/latest/download/kube-state-metrics.yaml

echo "==> Adding Prometheus Helm repo..."
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

echo "==> Installing Prometheus stack..."
helm install prometheus prometheus-community/kube-prometheus-stack \
  --set grafana.enabled=false \
  --set alertmanager.enabled=false \
  --wait

echo "==> Port-forwarding Prometheus to localhost:9090..."
echo "Run: kubectl port-forward svc/prometheus-kube-prometheus-prometheus 9090:9090"

echo ""
echo "Kind cluster is ready. Start the app with:"
echo "  MOCK_MODE=false docker compose --profile live up"
