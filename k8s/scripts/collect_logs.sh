#!/bin/bash

# Collect Kubernetes logs and events for debugging
OUTPUT_FILE="k8s_debug_logs.txt"

echo "Collecting logs to $OUTPUT_FILE..."
echo "============================================" > $OUTPUT_FILE
echo "Generated at: $(date)" >> $OUTPUT_FILE
echo "============================================" >> $OUTPUT_FILE

echo "" >> $OUTPUT_FILE
echo ">>> POD STATUS <<<" >> $OUTPUT_FILE
kubectl get pods -n uber-clone -o wide >> $OUTPUT_FILE 2>&1

echo "" >> $OUTPUT_FILE
echo ">>> EVENTS <<<" >> $OUTPUT_FILE
kubectl get events -n uber-clone --sort-by='.lastTimestamp' >> $OUTPUT_FILE 2>&1

# Loop through all pods
PODS=$(kubectl get pods -n uber-clone -o jsonpath='{.items[*].metadata.name}')

for POD in $PODS; do
    echo "" >> $OUTPUT_FILE
    echo "============================================" >> $OUTPUT_FILE
    echo ">>> DESCRIBE POD: $POD <<<" >> $OUTPUT_FILE
    echo "============================================" >> $OUTPUT_FILE
    kubectl describe pod $POD -n uber-clone >> $OUTPUT_FILE 2>&1

    echo "" >> $OUTPUT_FILE
    echo "--------------------------------------------" >> $OUTPUT_FILE
    echo ">>> LOGS: $POD <<<" >> $OUTPUT_FILE
    echo "--------------------------------------------" >> $OUTPUT_FILE
    
    # Get logs (including previous instance if crashed)
    kubectl logs $POD -n uber-clone --all-containers=true --prefix=true >> $OUTPUT_FILE 2>&1
    
    echo "" >> $OUTPUT_FILE
    echo ">>> PREVIOUS LOGS (if crashed): $POD <<<" >> $OUTPUT_FILE
    kubectl logs $POD -n uber-clone --all-containers=true --prefix=true --previous >> $OUTPUT_FILE 2>&1
done

echo "Done! Logs saved to $OUTPUT_FILE"
