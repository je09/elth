from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from .parser import EtisTool

@csrf_exempt
def parse_session(request, session_id):
    etis_tool = EtisTool(session_id)
    etis_tool.full_parse()

    return HttpResponse("Wow, it's done!")


def return_schedule_week(request, session_id, api_key, week):
    result = {
        'error_code' : 0,
        'error_description' : 'wrong api key'
    }
    if api_key:
        etis_tool = EtisTool(session_id)
        result = etis_tool.return_week(week)
        result = {'data' : result}

    return JsonResponse(result)

def return_schedule_week_formated(request, session_id, api_key, week):
    result = {
        'error_code' : 0,
        'error_description' : 'wrong api key'
    }
    if api_key:
        etis_tool = EtisTool(session_id)
        result = etis_tool.return_week(week, True)
        result = {'data' : result}

    return JsonResponse(result)


def return_student_info(request, session_id, api_key):
    result = {
        'error_code': 0,
        'error_description': 'wrong api key'
    }
    if api_key:
        etis_tool = EtisTool(session_id)
        result = etis_tool.student_info()

    return JsonResponse(result)

def return_week_period(request, session_id, api_key):
    result = {
        'error_code': 0,
        'error_description': 'wrong api key'
    }
    if api_key:
        etis_tool = EtisTool(session_id)
        result = etis_tool.week_periods()

    return JsonResponse(result)


def return_mark_trimester(request, session_id, api_key):
    pass