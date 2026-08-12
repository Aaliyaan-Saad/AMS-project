from django import forms

from .models import Member, MembershipPlan


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        exclude = ["member_code"]


class MembershipPlanForm(forms.ModelForm):
    class Meta:
        model = MembershipPlan
        fields = "__all__"
