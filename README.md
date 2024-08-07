# UdaConnect Deployment Guide

This guide explains how to deploy the UdaConnect project, including Apache Kafka and other components, on a Kubernetes cluster using Vagrant and k3s.

## Prerequisites

- Vagrant
- VirtualBox (or another supported Vagrant provider)
- Helm 3.x installed on your local machine
- `kubectl` installed on your local machine

## Step 1: Start the Vagrant Box

1. Navigate to the root of the repository containing the Vagrantfile.
2. Start the Vagrant box:
   ```bash
   vagrant up
   ```

## Step 2: Configure kubectl for k3s

1. Copy the k3s configuration file from the Vagrant box to your local machine:
   ```bash
   vagrant ssh -c "sudo cat /etc/rancher/k3s/k3s.yaml" > k3s.yaml
   ```
2. Set the `KUBECONFIG` environment variable:
   ```bash
   export KUBECONFIG=$(pwd)/k3s.yaml
   ```

## Step 3: Add the Bitnami Helm Repository

If you haven't already added the Bitnami repository to Helm, do so with these commands:

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
```

## Step 4: Deploy Dependencies (Database and Kafka)

1. Deploy PostgreSQL:
   ```bash
   kubectl apply -f postgres.yaml
   ```

2. Deploy Kafka using Helm:
   ```bash
   helm install kafka bitnami/kafka -f kafka-values.yaml
   ```

3. Apply ConfigMap and Secret for the database:
   ```bash
   kubectl apply -f db-configmap.yaml
   kubectl apply -f db-secret.yaml
   ```

## Step 5: Deploy Application Components

Deploy the main application components:

```bash
kubectl apply -f udaconnect-api.yaml
kubectl apply -f udaconnect-app.yaml
kubectl apply -f location-processor.yaml
kubectl apply -f location-ingester.yaml
```

## Step 6: Verify the Installations

Check if all pods are running:

```bash
kubectl get pods
```

You should see pods for Kafka, PostgreSQL, and all UdaConnect components.

## Step 7: Verify Kafka Topic Creation

Once the Kafka pods are running, verify that the `geolocation_topic` was created:

```bash
kubectl exec -it kafka-0 -- kafka-topics.sh --list --bootstrap-server localhost:9092
```

You should see `geolocation_topic` in the list of topics.

## Step 8: Deploy the Job

After verifying that all components are working correctly, deploy the location ingester job:

```bash
kubectl apply -f location-ingester-job.yaml
```

## Connecting to Kafka

To connect to Kafka from within the Kubernetes cluster, use the following bootstrap server address:

```
kafka.default.svc.cluster.local:9092
```

Replace `default` with your namespace if you're not using the default namespace.

## Cleanup

To remove all deployed resources:

1. Delete the job:
   ```bash
   kubectl delete -f location-ingester-job.yaml
   ```

2. Delete application components:
   ```bash
   kubectl delete -f udaconnect-api.yaml
   kubectl delete -f udaconnect-app.yaml
   kubectl delete -f location-processor.yaml
   kubectl delete -f location-ingester.yaml
   ```

3. Uninstall Kafka:
   ```bash
   helm uninstall kafka
   ```

4. Delete PostgreSQL and other resources:
   ```bash
   kubectl delete -f postgres.yaml
   kubectl delete -f db-configmap.yaml
   kubectl delete -f db-secret.yaml
   ```

5. Stop and destroy the Vagrant box:
   ```bash
   vagrant destroy
   ```

## Troubleshooting

If you encounter issues, check the logs of the respective pods:

```bash
kubectl logs <pod-name>
```

Replace `<pod-name>` with the actual name of the pod you want to investigate.

## Additional Documentation

To satisfy the project submission requirements please find the following in the `docs/

- `architecture_design.png`: A visual representation of the project's architecture.
- `architecture_decisions.txt`: Justification for the design decisions made in the architecture.
- `grpc.txt`: Documentation of the gRPC endpoint and instructions on how to make a sample request.
- `pods_screenshot.png`: A screenshot showing the output of `kubectl get pods`.
- `services_screenshot.png`: A screenshot showing the output of `kubectl get services`.
- `postman.json`: A Postman collection containing all REST API endpoints for easy testing and interaction.
- `openapi.yaml`: An OpenAPI specs for the udaconnect-api.
- `fake_event_generator.png`: Proof that the fake generator works just fine.
- `grpc_server.png`: Proof that the gRPC server writes to the Kafka topic.
- `kafka_processor.png`: Proof that the Kafka client reads from the topic and write to the db.
