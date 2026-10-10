import json

import vl_convert
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from .apiViews import getExerciseSummary, getSessionSummary


@login_required
def vegaCharts(request):
    return render(request, "rehab/vegaCharts.html")


def render_chart(spec_name, values):
    with open(settings.BASE_DIR / "static" / "vega" / spec_name) as f:
        spec = json.load(f)
    spec["data"] = {"values": values}
    return HttpResponse(vl_convert.vegalite_to_png(spec, scale=2), content_type="image/png")


@login_required
def vegaChart1(request):
    return render_chart("chart1.json", getExerciseSummary())


@login_required
def vegaChart2(request):
    return render_chart("chart2.json", getSessionSummary())