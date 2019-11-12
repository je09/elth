from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.shortcuts import render
from .parser import EtisTool

@csrf_exempt
def parse_session(request, session_id):
    etis_tool = EtisTool(session_id)
    etis_tool.full_parse()

    return HttpResponse("Wow, it's done!")