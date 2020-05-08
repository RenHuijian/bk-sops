# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
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
from django.views.decorators.http import require_POST

from blueapps.account.decorators import login_exempt
from gcloud import err_code
from gcloud.apigw.decorators import api_verify_perms
from gcloud.apigw.decorators import mark_request_whether_is_trust
from gcloud.apigw.decorators import project_inject
from gcloud.periodictask.models import PeriodicTask
from gcloud.periodictask.permissions import periodic_task_resource

try:
    from bkoauth.decorators import apigw_required
except ImportError:
    from packages.bkoauth.decorators import apigw_required


@login_exempt
@csrf_exempt
@require_POST
@apigw_required
@mark_request_whether_is_trust
@project_inject
@api_verify_perms(
    periodic_task_resource,
    [periodic_task_resource.actions.edit],
    get_kwargs={"task_id": "id", "project_id": "project_id"},
)
def set_periodic_task_enabled(request, task_id, project_id):
    project = request.project
    try:
        params = json.loads(request.body)
    except Exception:
        return JsonResponse(
            {
                "result": False,
                "message": "invalid json format",
                "code": err_code.REQUEST_PARAM_INVALID.code,
            }
        )

    enabled = params.get("enabled", False)

    try:
        task = PeriodicTask.objects.get(id=task_id, project_id=project.id)
    except PeriodicTask.DoesNotExist:
        return JsonResponse(
            {
                "result": False,
                "message": "task(%s) does not exist" % task_id,
                "code": err_code.CONTENT_NOT_EXIST.code,
            }
        )

    task.set_enabled(enabled)
    return JsonResponse(
        {
            "result": True,
            "data": {"enabled": task.enabled},
            "code": err_code.SUCCESS.code,
        }
    )
