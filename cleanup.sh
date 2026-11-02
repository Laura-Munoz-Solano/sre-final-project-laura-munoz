#!/bin/bash

# Removes everything installed by cluster.sh (Minikube and Colima keep running)

echo "Uninstalling the Helm release..."
helm uninstall sre-app

echo "Deleting the namespaces..."
kubectl delete ns sre-app monitoring --ignore-not-found=true

echo "Done. To stop the cluster too: minikube stop && colima stop"
