import time
from google.auth import default
from google.cloud import monitoring_v3
from googleapiclient import discovery


def fetch_gcp_resources(project_id: str) -> dict:
    """
    Fetch a subset of common GCP resources in a project.
    Requires the necessary permissions for each API.
    """
    credentials, _ = default()
    resources = {}

    # 1. GKE Clusters
    container = discovery.build("container", "v1", credentials=credentials)
    clusters = []
    parent = f"projects/{project_id}/locations/-"
    try:
        response = container.projects().locations().clusters().list(parent=parent).execute()
        clusters = response.get("clusters", [])
    except Exception as e:
        print(f"Failed to fetch GKE clusters: {e}")
    resources["gke_clusters"] = clusters

    # 2. Storage Buckets
    storage = discovery.build('storage', 'v1', credentials=credentials)
    buckets = storage.buckets().list(project=project_id).execute()
    resources['storage_buckets'] = buckets.get('items', [])
    return resources


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
if __name__ == "__main__":
    project_id = "diagram-gen-ai"
    all_resources = fetch_gcp_resources(project_id)
    for key, items in all_resources.items():
        print(f"\n--- {key.upper()} ---")
        for item in items:
            print(item['name'])
    # fetch_k8s_node_cpu_allocatable("diagram-gen-ai")
