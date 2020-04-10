import inspect
from typing import Dict, Any

import kopf

from benji.helpers.constants import VERSION_LABELS, LABEL_K8S_PVC_NAMESPACE
from benji.api import APIClient


def get_caller_name() -> str:
    """Returns the name of the calling function"""
    return inspect.getouterframes(inspect.currentframe())[1].function


def check_version_access(benji: APIClient, version_uid: str, crd: Dict[Any, str]) -> None:
    try:
        version = benji.core_v1_get(version_uid=version_uid)
    except KeyError as exception:
        raise kopf.PermanentError(str(exception))

    crd_namespace = crd['metadata']['namespace']
    try:
        version_namespace = version[VERSION_LABELS][LABEL_K8S_PVC_NAMESPACE]
    except KeyError:
        raise kopf.PermanentError(f'Version is missing {LABEL_K8S_PVC_NAMESPACE} label, permission denied.')

    if crd_namespace != version_namespace:
        raise kopf.PermanentError('Version namespace label does not match resource namespace, permission denied')


def cr_to_job_name(body, suffix: str):
    if 'namespace' in body['metadata']:
        return f'crd:{body["kind"]}/{body["metadata"]["namespace"]}/{body["metadata"]["name"]}-{suffix}'
    else:
        return f'crd:{body["kind"]}/{body["metadata"]["name"]}-{suffix}'
