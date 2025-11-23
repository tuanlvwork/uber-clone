#!/bin/bash

# Extract logs for each service into separate files
LOG_DIR="k8s/logs"
mkdir -p $LOG_DIR

echo "Extracting logs to $LOG_DIR/..."

# Get list of all pods
PODS=$(kubectl get pods -n uber-clone -o jsonpath='{.items[*].metadata.name}')

for POD in $PODS; do
    echo "Processing $POD..."
    
    # Save logs
    kubectl logs $POD -n uber-clone --all-containers=true > "$LOG_DIR/$POD.log" 2>&1
    
    # Save describe output (events)
    kubectl describe pod $POD -n uber-clone > "$LOG_DIR/$POD.describe.txt" 2>&1
    
    # If the pod crashed, get previous logs too
    kubectl logs $POD -n uber-clone --all-containers=true --previous > "$LOG_DIR/$POD.previous.log" 2>&1
done

echo "============================================"
echo "Logs extracted successfully!"
echo "Check the '$LOG_DIR' directory."
echo "============================================"
ls -lh $LOG_DIR
