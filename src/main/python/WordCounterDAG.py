import datetime
import os
from airflow.models import DAG
from airflow.models import Variable
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from airflow.utils import dates
from datetime import timedelta
from airflow.operators.python_operator import PythonOperator


ENV = os.environ['COMPOSER_ENV']
PROJECTID = os.environ['PROJECTID']
ADOPS_DAG_ARGS = {
    'start_date': dates.days_ago(1),
    'email': ['dgoyal@fubo.tv'],
    'email_on_failure': Variable.get("EMAIL_ALERT_ADOPS") == 'True',
    'email_on_success': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=15),
}

def get_last_dag_run(dag):
    last_dag_run = dag.get_last_dagrun()
    if last_dag_run is None:
        return "no prev run"
    else:
        return last_dag_run.execution_date.strftime("%Y-%m-%d")

def get_schedule_interval():
    if "prod" in PROJECTID:
        return '15 * * * *'
    elif "dev" in PROJECTID:
        return '25 * * * *'
    else:
        return '35 * * * *'


def getDefaultDagArgs(email=None):
    if email is None:
        email = ['dgoyal@fubo.tv']

    email_alert = Variable.get("EMAIL_ALERT") == 'True'
    default_dag_args = {
        'catchup': False,
        'owner': 'airflow',
        'depends_on_past': False,
        'email': email,
        'email_on_failure': email_alert,
        'email_on_retry': email_alert,
        'email_on_success': email_alert,
        'retries': 2,
        'retry_delay': timedelta(minutes=5),
        'start_date': datetime.datetime(2019, 7, 23),
    }
    return default_dag_args

def merge_dicts(x, y):
    z = x.copy()
    z.update(y)
    return z

dag = DAG(
    dag_id='wordcount-deepansh',
    default_args=merge_dicts(getDefaultDagArgs(), ADOPS_DAG_ARGS),
    schedule_interval=get_schedule_interval(),
    max_active_runs=5,
    catchup=False,
    user_defined_macros={
        'last_dag_run_execution_date': get_last_dag_run
    },
)

def getDefaultDFArgs(
        jobClass='PostgresSyncJob',
        subnetwork='{{ var.value.SUBNETWORK }}',
        dataset='dmp',
        workerMachineType='undefined',
        numWorkers=1,
        maxNumWorkers=-1):
    if workerMachineType == 'undefined':
        if PROJECTID == 'fubotv-dev':
            workerMachineType = 'n1-standard-1'
        elif PROJECTID == 'model-gearing-425':
            workerMachineType = 'n1-standard-2'
        else:
            workerMachineType = 'n1-standard-4'

    dataflow_args = [
        f'--jobClass={jobClass}',
        '--runner=DataflowRunner',
        f'--project={PROJECTID}',
        f'--projectId={PROJECTID}',
        f'--tempLocation=gs://test-bucket-deepansh/tmp/',
        f'--stagingLocation=gs://test-bucket-deepansh/staging/',
        '--workerZone=us-east4-a',
        '--region=us-east4',
        f'--workerMachineType={workerMachineType}',
        f'--numWorkers={numWorkers}',
        '--diskSize=100',
        '--env={{ var.value.DF_ENV }}',
        '--dd_api_key={{ var.value.DD_SECRET_API_KEY }}',
        '--dd_app_key={{ var.value.DD_SECRET_APP_KEY }}',
        f'--subnetwork={subnetwork}',
        '--failFast={{ var.value.DF_FAILFAST }}',
        '--nullableCoders=true'
    ]

    if maxNumWorkers != -1:
        dataflow_args.append(f'--maxNumWorkers={maxNumWorkers}')

    return dataflow_args

def create_test_word_count(dag, job_name='deepansh-devproject', job_class='WordCount'):
    final_arg_list = (getDefaultDFArgs(jobClass=job_class, maxNumWorkers=4))
    with dag:
        return createKubeJob(dag, job_name, final_arg_list)

def my_task():
    # Add logging to check the state of pod_request_obj
    print("Pod request object:")

task = PythonOperator(
    task_id='my_task',
    python_callable=my_task,
    dag=dag,
)

def createKubeJob(dag, name, arg_list, failure_callback_func=None):
    name = name.replace('_', '-')  # no underscores in names
    # Truncate naming to 63 char (label limitation)
    label_name = name[:63].lower()
    labels = [f"""--labels={{"owner":"data-engineering", "environment":"{ENV}", "data-classification":"no", "cost-allocation":"data-engineering", "criticality":"low", "web-facing":"no", "name":"{label_name}"}}"""]
    arg_list += labels

    return KubernetesPodOperator(
        is_delete_operator_pod=True,
        dag=dag,
        in_cluster=False,
        task_id='de-airflow-kube-' + name,
        name='de-sync-pod-' + name,
        namespace='{{ var.value.KUBE_NAMESPACE }}',
        image='gcr.io/' + PROJECTID + '/de-engineering/deepansh-devproject',
        arguments=arg_list,
        on_failure_callback=failure_callback_func,
        secrets=[],
        labels={'data-engineering': 'sync-user'},
        startup_timeout_seconds=300,
        get_logs=True,
        image_pull_policy='Always',
        annotations={
            'key1': 'value1'},
        do_xcom_push=False,
        volumes=[],
        volume_mounts=[],
    )

word_count = create_test_word_count(dag)
task >> word_count