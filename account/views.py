from django.shortcuts import render, get_object_or_404
from django.views.generic import DetailView

from .models import User, Evaluation


class UserDetailView(DetailView):
    model = User
    template_name = "account/user_detail.html"
    context_object_name = "user"


def evaluationList(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    evaluations = Evaluation.objects.filter(user_id=user)
    context = {"user": user, "evaluations": evaluations}
    return render(request, "account/evaluation_list.html", context)
