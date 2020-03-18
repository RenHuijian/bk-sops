# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import ujson as json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET

from blueapps.account.decorators import login_exempt
from gcloud import err_code
from gcloud.apigw.decorators import api_verify_perms
from gcloud.apigw.decorators import mark_request_whether_is_trust
from gcloud.apigw.decorators import project_inject
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.taskflow3.permissions import taskflow_resource

try:
    from bkoauth.decorators import apigw_required
except ImportError:
    from packages.bkoauth.decorators import apigw_required


@login_exempt
@csrf_exempt
@require_GET
@apigw_required
@mark_request_whether_is_trust
@project_inject
@api_verify_perms(
    taskflow_resource,
    [taskflow_resource.actions.operate],
    get_kwargs={"task_id": "id", "project_id": "project_id"},
)
def get_task_node_data(request, project_id, task_id):
    project = request.project
    task = TaskFlowInstance.objects.get(id=task_id, project_id=project.id)

    node_id = request.GET.get("node_id")
    component_code = request.GET.get("component_code")
    loop = request.GET.get("loop")

    try:
        subprocess_stack = json.loads(request.GET.get("subprocess_stack", "[]"))
    except Exception:
        return JsonResponse(
            {
                "result": False,
                "message": "subprocess_stack is not a valid array json",
                "code": err_code.REQUEST_PARAM_INVALID.code,
            }
        )

    data = task.get_node_data(
        node_id, request.user.username, component_code, subprocess_stack, loop
    )

    return JsonResponse(
        {
            "result": data["result"],
            "data": data["data"],
            "message": data["message"],
            "code": err_code.SUCCESS.code
            if data["result"]
            else err_code.UNKNOW_ERROR.code,
        }
    )
