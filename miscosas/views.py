"""
Django views for app MisCosas
"""

from django.shortcuts import render, HttpResponse
from django.core.handlers.wsgi import WSGIRequest

def index(request: WSGIRequest):
    return HttpResponse("Página principal")

def feeds(request: WSGIRequest):
    return HttpResponse("Página de alimentadores")

def feed(request: WSGIRequest, id: str):
    return HttpResponse("Página de alimentador")

def items(request: WSGIRequest):
    return HttpResponse("Página de items")

def item(request: WSGIRequest, id: str):
    return HttpResponse("Página de item")

def users(request: WSGIRequest):
    return HttpResponse("Página de usuarios")

def user(request: WSGIRequest, id: str):
    return HttpResponse("Página de usuario")

def about(request: WSGIRequest):
    return HttpResponse("Página de información")
