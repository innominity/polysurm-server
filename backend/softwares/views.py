from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

from django.views.decorators.csrf import csrf_exempt
import base64
from django.contrib.auth import authenticate

from django.http import JsonResponse, HttpResponse
from .models import SoftwareApp
from .serializers import SoftwareAppSerializer, SoftwareAppTaskSerializers

import json
from .app_starter import RemoteAppSoftware

@csrf_exempt
def software_list(request):
    softwares = SoftwareApp.objects.all()
    serializer = SoftwareAppSerializer(softwares, many=True)
    return JsonResponse(serializer.data, safe=False)

@csrf_exempt
def app_main(request, app_name):
    software_app = SoftwareApp.objects.get(slug=app_name)
    if not software_app.is_public:
            if 'HTTP_AUTHORIZATION' in request.META:
                auth = request.META['HTTP_AUTHORIZATION'].split()
                if len(auth) == 2:
                    if auth[0].lower() == "basic":
                        uname, passwd = base64.b64decode(auth[1]).decode("ascii").split(':')
                        user = authenticate(username=uname, password=passwd)
                        if not (user is not None and user.is_active):
                            response = HttpResponse()
                            response.status_code = 401
                            response['WWW-Authenticate'] = 'Basic realm="%s"' % "Basci Auth Protected"
                            return response
                        
    if request.method == 'GET':
        config_params = RemoteAppSoftware.get_config_params(str(software_app.guid))
        config_files = []
        
        response = {
            "name": software_app.name,
            "version": software_app.get_version(),
            "description": software_app.description,
            "config_params": config_params,
            "config_files": config_files,
        }
        return JsonResponse(
            config_params, json_dumps_params={"ensure_ascii": False}, status=200
        )

    elif request.method == 'POST':
        # В этой ветке стартуем задачу ПО
        config_params_dict = json.loads(request.body)
        config_files = request.FILES if len(request.FILES) > 0 else []
        guid_config_files = []
        software_module_task = RemoteAppSoftware(software_app_guid=software_app.guid)
        result_data = software_module_task.run(config_params_dict['data'], guid_config_files)
        return JsonResponse({'status': result_data['status'], 'data': result_data['results']})
    else:
        return JsonResponse({})
    

@csrf_exempt
def app_info(request, app_name):
    if request.method == 'GET':
        software_app = SoftwareApp.objects.get(slug=app_name)
        
        response = {
            "name": software_app.name,
            "version": software_app.get_version(),
            "description": software_app.description,
        }
        return JsonResponse(
            response, json_dumps_params={"ensure_ascii": False}, status=200
        )
    

@csrf_exempt
def app_params(request, app_name):
    if request.method == 'GET':
        software_app = SoftwareApp.objects.get(slug=app_name)
        config_params = RemoteAppSoftware.get_config_params(str(software_app.guid))
        config_files = []
        
        response = config_params
        return JsonResponse(
            response, json_dumps_params={"ensure_ascii": False}, status=200
        )