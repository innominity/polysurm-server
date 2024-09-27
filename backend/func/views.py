import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

from django.http import JsonResponse
from.apps.rozenbrock import eval_rozenbrock

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def rozenbrock(request):
    if request.method == "GET":
        return JsonResponse({
            "x1": {"label": "$x_1$", "lower": -2, "upper": 2, "sampling_input": True},
            "x2": {"label": "$x_2$", "lower": -1, "upper": 3, "sampling_input": True},
            "f(x)": {
                "label": "$f(x)$",
                "lower": -90,
                "upper": 0,
                "sampling_input": False,
            },
        })
    elif request.method == 'POST':
        data = json.loads(request.body)
        data = data['data']
        print(data)
        results = eval_rozenbrock('f(x)', data)
        return JsonResponse({'data': results})
    else:
        return JsonResponse({})
