from django.shortcuts import render, get_object_or_404
from django.http import Http404
from .models import Exhibit


def exhibit_list(request):
    exhibits = Exhibit.objects.filter(status="on_display").prefetch_related("images")
    return render(request, "exhibits/exhibit_list.html", {"exhibits": exhibits})


def exhibit_detail(request, pk):
    exhibit = get_object_or_404(Exhibit, pk=pk)
    if request.user and request.user.is_staff or exhibit.status == "on_display":
        return render(request, "exhibits/exhibit_detail.html", {"exhibit": exhibit})
    raise Http404()
