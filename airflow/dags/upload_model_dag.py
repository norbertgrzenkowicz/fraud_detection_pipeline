from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator

# from airflow.providers.cncf.kubernetes.operators.kubernetes import KubernetesOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from kubernetes import client, config
import docker
import os
import shutil
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "/app/model/src"))
)
import train

DOCKER_REGISTRY = "docker.io"
MODEL_SERVICE_IMAGE = "fraud-api"
MODEL_SERVICE_IMAGE_PUSH = "norbertgrzenkowicz/fraud-api"
NAMESPACE = "default"


def train_model():
    train.main()


def copy_model_to_service():
    """Copy the newly trained model.pkl to the model service directory"""
    try:
        # source_model = os.getenv("MODEL_PATH")
        source_model = "/opt/airflow/lr_model.pkl"

        # dest_model = os.path.join(os.getenv("MODEL_SERVICE_PATH"), "lr_model.pkl")
        dest_model = "/app/api/lr_model.pkl"
        shutil.copy2(source_model, dest_model)
        # shutil.copy2(source_model, dest_model)
        return True
    except Exception as e:
        print(f"Error copying model: {str(e)}")
        raise


def build_and_push_image():
    """Build and push the Docker image with the new model"""
    try:
        client = docker.from_env()

        # Build the new image
        tag = datetime.now().strftime("%Y%m%d_%H%M%S")
        full_image_name = f"{MODEL_SERVICE_IMAGE_PUSH}:{tag}"

        # Build the Docker image
        client.images.build(
            path=os.getenv("MODEL_SERVICE_PATH"),
            tag=full_image_name,
            dockerfile="/app/api/Dockerfile",
        )

        # Push the image
        client.images.push(MODEL_SERVICE_IMAGE_PUSH, tag=tag)

        return full_image_name
    except Exception as e:
        print(f"Error building/pushing image: {str(e)}")
        raise


def update_k8s_deployment(image_name):
    """Update the Kubernetes deployment with the new image"""
    try:
        config.load_incluster_config()

        api = client.AppsV1Api()

        deployment = api.read_namespaced_deployment(
            name="fraud-api", namespace=NAMESPACE
        )
        api.read_
        deployment.spec.template.spec.containers[0].image = image_name

        api.patch_namespaced_deployment(
            name="fraud-api", namespace=NAMESPACE, body=deployment
        )

        return True
    except Exception as e:
        print(f"Error updating deployment: {str(e)}")
        raise


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "model_service_update",
    default_args=default_args,
    description="Update model service with new model",
    schedule_interval=None,
    catchup=False,
)


new_model = PythonOperator(task_id="train_model", python_callable=train_model, dag=dag)

copy_model = PythonOperator(
    task_id="copy_model", python_callable=copy_model_to_service, dag=dag
)

build_image = PythonOperator(
    task_id="build_image", python_callable=build_and_push_image, dag=dag
)

# update_deployment = PythonOperator(
#     task_id="update_deployment",
#     python_callable=update_k8s_deployment,
#     op_args=["{{ task_instance.xcom_pull(task_ids='build_image') }}"],
#     dag=dag,
# )

new_model >> copy_model >> build_image
# train_model >> copy_model >> build_image >> update_deployment
