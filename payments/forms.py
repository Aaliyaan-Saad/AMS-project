from django import forms

from members.models import Member

from .models import Donation, Payment


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['member', 'payment_type', 'amount', 'payment_method', 'payment_date', 'status']
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['member'].queryset = Member.objects.order_by('first_name', 'last_name')
        self.fields['amount'].widget.attrs['min'] = '0'


class PublicDonateForm(forms.Form):
    member_code = forms.CharField(label='Member ID', max_length=20, help_text='e.g. MEM-0001')
    amount = forms.DecimalField(label='Donation amount', max_digits=10, decimal_places=2, min_value=0.01)
    payment_method = forms.ChoiceField(label='Payment method', choices=Donation.METHOD_CHOICES)
    message = forms.CharField(label='Note / message (optional)', required=False, widget=forms.Textarea(attrs={'rows': 3}))

    def clean_member_code(self):
        code = self.cleaned_data['member_code'].strip().upper()
        if not Member.objects.filter(member_code=code).exists():
            raise forms.ValidationError('No member found with this Member ID. Please check and try again.')
        return code


class DonationStatusForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = ['status']
