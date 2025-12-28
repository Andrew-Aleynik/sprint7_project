from django.shortcuts import render


def page_not_found(request, exception=None):
    return render(request, "pages/404.html", status=404)
