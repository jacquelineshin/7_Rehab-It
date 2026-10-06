import json

import vl_convert
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render

from .apiViews import getExerciseSummary, getSessionSummary


def vegaCharts(request):
    return render(request, "rehab/vegaCharts.html")


def vegaChart1(request):
    specFile = open(settings.BASE_DIR / "static" / "vega" / "chart1.json")
    spec = json.load(specFile)
    specFile.close()

    spec["data"] = {"values": getExerciseSummary()}
    png = vl_convert.vegalite_to_png(spec, scale=2)

    return HttpResponse(png, content_type="image/png")


def vegaChart2(request):
    specFile = open(settings.BASE_DIR / "static" / "vega" / "chart2.json")
    spec = json.load(specFile)
    specFile.close()

    spec["data"] = {"values": getSessionSummary()}
    png = vl_convert.vegalite_to_png(spec, scale=2)

    return HttpResponse(png, content_type="image/png")
