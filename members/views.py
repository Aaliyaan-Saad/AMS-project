from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import MemberForm, MembershipPlanForm
from .models import Member, MembershipPlan


def member_list(request):
    members = Member.objects.select_related("plan").all()

    search = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()
    plan_id = request.GET.get("plan", "").strip()

    if search:
        members = members.filter(
            Q(member_code__icontains=search)
            | Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
            | Q(email__icontains=search)
            | Q(phone__icontains=search)
            | Q(city__icontains=search)
        )

    if plan_id:
        members = members.filter(plan_id=plan_id)

    if status == "active":
        members = [member for member in members if member.status == "Active"]
    elif status == "expired":
        members = [member for member in members if member.status == "Expired"]

    paginator = Paginator(members, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    plans = MembershipPlan.objects.filter(active=True)

    return render(request, "members/member_list.html", {
        "page_obj": page_obj,
        "plans": plans,
        "search": search,
        "status": status,
        "plan_id": plan_id,
    })


def member_add(request):
    if request.method == "POST":
        form = MemberForm(request.POST)
        if form.is_valid():
            member = form.save(commit=False)

            if not member.expiry_date:
                member.expiry_date = member.plan.expiry_date_from(member.join_date)

            member.save()

            messages.success(request, "Member added successfully.")
            return redirect("member_detail", pk=member.pk)
    else:
        form = MemberForm()

    return render(request, "members/member_form.html", {
        "form": form,
        "title": "Add Member",
    })


def member_detail(request, pk):
    member = get_object_or_404(
        Member.objects.select_related("plan"),
        pk=pk
    )

    return render(request, "members/member_detail.html", {
        "member": member,
    })


def member_edit(request, pk):
    member = get_object_or_404(Member, pk=pk)

    if request.method == "POST":
        form = MemberForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, "Member updated successfully.")
            return redirect("member_detail", pk=member.pk)
    else:
        form = MemberForm(instance=member)

    return render(request, "members/member_form.html", {
        "form": form,
        "title": "Edit Member",
        "member": member,
    })


def member_delete(request, pk):
    member = get_object_or_404(Member, pk=pk)

    if request.method == "POST":
        member.delete()
        messages.success(request, "Member deleted successfully.")
        return redirect("member_list")

    return render(request, "members/member_confirm_delete.html", {
        "member": member,
    })


def member_renew(request, pk):
    member = get_object_or_404(Member, pk=pk)

    if request.method == "POST":
        plan_id = request.POST.get("plan")
        plan = get_object_or_404(MembershipPlan, pk=plan_id, active=True)

        renewal_date = timezone.localdate()

        member.plan = plan
        member.last_renewed_date = renewal_date
        member.expiry_date = plan.expiry_date_from(renewal_date)
        member.save()

        messages.success(request, "Membership renewed successfully.")
        return redirect("member_detail", pk=member.pk)

    plans = MembershipPlan.objects.filter(active=True)

    return render(request, "members/member_renew.html", {
        "member": member,
        "plans": plans,
    })


def plan_list(request):
    plans = MembershipPlan.objects.all()

    return render(request, "members/plan_list.html", {
        "plans": plans,
    })


def plan_add(request):
    if request.method == "POST":
        form = MembershipPlanForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Membership plan created successfully.")
            return redirect("plan_list")
    else:
        form = MembershipPlanForm()

    return render(request, "members/plan_form.html", {
        "form": form,
        "title": "Create Plan",
    })


def plan_edit(request, pk):
    plan = get_object_or_404(MembershipPlan, pk=pk)

    if request.method == "POST":
        form = MembershipPlanForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
            messages.success(request, "Membership plan updated successfully.")
            return redirect("plan_list")
    else:
        form = MembershipPlanForm(instance=plan)

    return render(request, "members/plan_form.html", {
        "form": form,
        "title": "Edit Plan",
        "plan": plan,
    })


def plan_disable(request, pk):
    plan = get_object_or_404(MembershipPlan, pk=pk)

    if request.method == "POST":
        plan.active = False
        plan.save()
        messages.success(request, "Membership plan disabled successfully.")
        return redirect("plan_list")

    return render(request, "members/plan_confirm_disable.html", {
        "plan": plan,
    })
