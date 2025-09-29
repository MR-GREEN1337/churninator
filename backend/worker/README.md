## Achieve horizontal scaling elasticity by implementing auto scaling group for worker instances

```mermaid
graph TD
    subgraph GCP[Google Cloud]
        Lambda[Metric Publisher (Cloud Function / Scheduler Job)] -- Publishes Metric --> CloudMonitoring(Cloud Monitoring: QueueLength)
        CloudMonitoring -- Triggers Policy --> CloudRun(Cloud Run Service: Worker)
    end

    subgraph Your VPC
        Redis(Redis Instance)
    end

    Lambda -- "LLEN default" --> Redis
    CloudRun --> Redis
```

This captures the **Cloud Run flow**:

1. A Cloud Function (or Cloud Scheduler job + small function) checks Redis queue length.
2. Publishes the metric (`ChurninatorQueueLength`) to **Cloud Monitoring**.
3. **Cloud Run Service** auto-scales worker containers based on that metric.
4. Workers interact with Redis as usual.
