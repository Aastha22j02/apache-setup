import requests
import base64
import zipfile
import io
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

class CustomBranchNotFoundError(Exception):
    pass

@login_required
def trigger_pipeline_view(request):
    if request.method == 'POST':
        try:
            form_data = request.POST

            # Dictionary mapping tool names to their corresponding branch names
            tool_branch_mapping = {
                "Wazuh": "efk",
                "Filebeat": "filebeat",
                # "Wazuh + EFK": "efk",
                "Graylog": "graylog",
                "Splunk": "splunk",
                "WazuhIndexer": "wazuhindexer",
                "Elasticsearch": "elasticsearch",
                "Grafana": "grafana",
                "Kibana": "kibana",
                "Fluentd": "fluentd",
                "OpenCTI": "opencti",
                "MISP": "misp",
                "TheHIVE": "thehive",
                "RTIR": "rtir",
                "Shuffle": "shuffle",
                "Cortex": "cortex",
                "Velociraptor": "velociraptor",
                "OSINT": "osint",
                "InfluxDB": "influxdb",
                "Prometheus": "prometheus"
            }

            selected_tools = []

            # Identify which tools the user has selected
            for tool, branch_name in tool_branch_mapping.items():
                if form_data.get(tool):
                    selected_tools.append(branch_name)

            # Replace these variables with your actual GitLab project ID and private token
            project_id = "109"
            private_token = "Brd96ShxJsCfqZsL-3ZB"
            base_url = "https://gitlab.os3.com/api/v4/"
            headers = {"PRIVATE-TOKEN": private_token}

            pipeline_names = []

            #Trigger Infra first as a default 
            if selected_tools:
                pipeline_names.append("wazuh-s100")
                trigger_branch(base_url, project_id, headers, "wazuh-s100")
            # Trigger selected branches
            for branch_name in selected_tools:
                pipeline_names.append(branch_name)
                trigger_branch(base_url, project_id, headers, branch_name)

        except CustomBranchNotFoundError:
            return render(request, 'custom_error_page.html', {'error_message': "Specified branch does not exist."})

        return render(request, 'result.html', {'message': 'Installation in Progress', 'pipeline_names': pipeline_names})
    else:
        return render(request, 'trigger_pipeline.html')


def trigger_branch(base_url, project_id, headers, branch_name):
    data = {"ref": branch_name}
    response = requests.post(base_url + f"projects/{project_id}/pipeline", headers=headers, json=data, verify=False)

    try:
        response.raise_for_status()  # This will raise an exception if response status code is not 2xx
    except requests.exceptions.HTTPError as e:
        if response.status_code == 400 and "Reference not found" in response.json().get('message', {}).get('base', []):
            raise CustomBranchNotFoundError("The specified branch does not exist.")
        else:
            raise ValueError(f"Error triggering pipeline for branch '{branch_name}': {e}")


def get_latest_pipeline_statuses(base_url, project_id, headers, count=2):
    response = requests.get(base_url + f"projects/{project_id}/pipelines", headers=headers, verify=False)

    if response.status_code != 200:
        raise ValueError(f"Error fetching pipelines: {response.status_code}, {response.json()}")

    pipelines = response.json()
    if not pipelines:
        return []

    latest_pipelines = pipelines[:count]
    latest_statuses = []

    for pipeline in latest_pipelines:
        latest_status = pipeline['status']
        latest_statuses.append({"id": pipeline['id'], "status": latest_status})

    return latest_statuses

def get_latest_pipeline_artifacts(base_url, project_id, headers, pipeline_id):
    response = requests.get(base_url + f"projects/{project_id}/pipelines/{pipeline_id}/jobs", headers=headers, verify=False)

    if response.status_code != 200:
        raise ValueError(f"Error fetching pipeline jobs: {response.status_code}, {response.json()}")

    jobs = response.json()
    artifacts = []

    for job in jobs:
        response = requests.get(base_url + f"projects/{project_id}/jobs/{job['id']}/artifacts", headers=headers, verify=False)
        if response.status_code == 200:
            with zipfile.ZipFile(io.BytesIO(response.content), 'r') as zip_file:
                # Modify the following to fetch the required artifacts
                required_artifacts = ['ip.txt', 'elastic_creds.txt']
                for artifact_name in required_artifacts:
                    if artifact_name in zip_file.namelist():
                        content = zip_file.read(artifact_name).decode('utf-8')
                        artifacts.append({"filename": artifact_name, "content": content})

    return artifacts

def get_latest_pipeline_statuses_and_artifacts(request):
    # Replace these variables with your actual GitLab project ID and private token
    project_id = "109"
    private_token = "Brd96ShxJsCfqZsL-3ZB"
    base_url = "https://gitlab.os3.com/api/v4/"
    headers = {"PRIVATE-TOKEN": private_token}
    pipeline_count = 2

    # Get the statuses of the latest pipelines
    latest_pipeline_statuses = get_latest_pipeline_statuses(base_url, project_id, headers, pipeline_count)

    # Get the artifacts for each of the latest pipelines
    all_artifacts = []
    for pipeline_status in latest_pipeline_statuses:
        pipeline_id = pipeline_status["id"]
        artifacts = get_latest_pipeline_artifacts(base_url, project_id, headers, pipeline_id)
        all_artifacts.append({"status": pipeline_status["status"], "artifacts": artifacts})

    return JsonResponse({"pipelines": all_artifacts})
