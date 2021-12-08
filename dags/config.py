"""
All dags config is located here.
"""

# PSL
from os import path
from pathlib import Path

BUCKET_NAME: str = "skills-finder-storage"

TECH_SKILLS_FILE_S3_LOC: str = "data/tech_skills.txt"
TECH_SKILLS_FILE_LOCAL_LOC: str = path.join(
    Path(__file__).parent, "data_", "tech_skills.txt"
)

PYSPARK_JOBS_S3_LOC: str = "emr/_pyspark/jobs/skills_analyzer.py"
PYSPARK_JOBS_LOCAL_LOC: str = path.join(
    Path(__file__).parent, "emr", "_pyspark", "jobs", "skills_analyzer.py"
)

PYSPARK_JOBS_SUBMIT_CONFIG = [
    {
        "Name": "skills-analyzer-job",
        "ActionOnFailure": "TERMINATE_CLUSTER",
        "HadoopJarStep": {
            "Properties": [],
            "Jar": "command-runner.jar",
            "Args": [
                "spark-submit",
                f"s3://{BUCKET_NAME}/{PYSPARK_JOBS_S3_LOC}",
            ],
        },
    },
]

EMR_JOB_FLOW = {
    "Name": "skills analyzer from airflow",
    "ReleaseLabel": "emr-5.25.0",
    "Applications": [{"Name": "Hadoop"}, {"Name": "Spark"}],
    "Configurations": [
        {
            "Classification": "spark-env",
            "Configurations": [
                {
                    "Classification": "export",
                    "Properties": {"PYSPARK_PYTHON": "/usr/bin/python3"},
                }
            ],
        }
    ],
    "Instances": {
        "InstanceGroups": [
            {
                "Name": "Master node",
                "Market": "SPOT",
                "InstanceRole": "MASTER",
                "InstanceType": "m4.xlarge",
                "InstanceCount": 1,
            },
            {
                "Name": "Core - 2",
                "Market": "SPOT",
                "InstanceRole": "CORE",
                "InstanceType": "m4.xlarge",
                "InstanceCount": 2,
            },
        ],
        "TerminationProtected": False,
        "Ec2KeyName": "skills-finder-key-pair",
        "Ec2SubnetId": "subnet-02202364546d50ad9",
        "EmrManagedMasterSecurityGroup": "sg-084e3a57ed95b63a7",
        "EmrManagedSlaveSecurityGroup": "sg-0cb737d37d30c08b2",
    },
    "JobFlowRole": "EMR_EC2_DefaultRole",
    "ServiceRole": "EMR_DefaultRole",
}
