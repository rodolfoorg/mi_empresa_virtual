from django.http import HttpResponse

def api_welcome(request):
    return HttpResponse("Bienvenido a la API") 