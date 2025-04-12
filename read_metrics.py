import time

from google.cloud import monitoring_v3


def fetch_k8s_node_cpu_allocatable(project_id):
    client = monitoring_v3.MetricServiceClient()
    project_name = f"projects/{project_id}"

    now = time.time()
    seconds = int(now)
    nanos = int((now - seconds) * 10 ** 9)

    interval = monitoring_v3.TimeInterval(
        {
            "end_time": {"seconds": seconds, "nanos": nanos},
            "start_time": {"seconds": seconds - 1200, "nanos": nanos},
        }
    )

    aggregation = monitoring_v3.Aggregation(
        {
            "alignment_period": {"seconds": 60},
            "per_series_aligner": monitoring_v3.Aggregation.Aligner.ALIGN_MEAN,
            "cross_series_reducer": monitoring_v3.Aggregation.Reducer.REDUCE_SUM,
            "group_by_fields": ["metadata.user_labels.node_pool"]
        }
    )

    results = client.list_time_series(
        request={
            "name": project_name,
            "filter": (
                'metric.type = "kubernetes.io/node/cpu/allocatable_cores" '
                'AND resource.type = "k8s_node" '
            ),
            "interval": interval,
            "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
            "aggregation": aggregation,
        }
    )

    for time_series in results:
        print(f"Group: {time_series.metadata}")
        for point in time_series.points:
            print(f"  {point.interval.end_time}: {point.value.double_value}")


# Replace with your actual project ID
fetch_k8s_node_cpu_allocatable("diagram-gen-ai")
