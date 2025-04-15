from django import forms
from .models import Event, Club ,ClubAdmin
# forms.py
from django import forms
from .models import Event, Club  # Adjust as needed

# Custom widget to allow multiple file selection
'''class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

# Custom field to handle multiple file uploads
class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        # If no data is provided, return an empty list
        if not data:
            return []
        # Ensure data is always a list or tuple
        if not isinstance(data, (list, tuple)):
            data = [data]
        # Clean each file individually
        return [super(MultipleFileField, self).clean(item, initial) for item in data]'''

# Updated EventForm using the custom MultipleFileField for image uploads
class EventForm(forms.ModelForm):
    club = forms.ModelChoiceField(queryset=Club.objects.none(), label="Select Club", required=False)
    #posts = MultipleFileField(label="Select Event Images", required=False)

    class Meta:
        model = Event
        fields = ['club', 'event_name', 'event_desc', 'event_date', 'event_location','standard_price', 'member_discount_price']
        widgets = {
            'event_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(EventForm, self).__init__(*args, **kwargs)
        if user:
            from .models import ClubAdmin
            club_ids = ClubAdmin.objects.filter(user=user).values_list('club_id', flat=True)
            self.fields['club'].queryset = Club.objects.filter(id__in=club_ids)

class ClubForm(forms.ModelForm):
    club_password = forms.CharField(
        widget=forms.PasswordInput,
        required=True,
        label="Club Password"
    )
    class Meta:
        model = Club
        fields = ['club_name' , 'club_desc' , 'club_email','membership_fee']

class ClubJoinForm(forms.Form):
    club_email = forms.EmailField(
        label="Club Email",
        required= True)
    club_password = forms.CharField(
        widget=forms.PasswordInput, 
        label="Club Password",
        required= True)

# forms.py

from django import forms
from .models import VirtualPayment

class VirtualPaymentForm(forms.ModelForm):
    class Meta:
        model = VirtualPayment
        fields = ['payment_method']
        widgets = {
            'payment_method': forms.RadioSelect
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Remove blank choice if it's being added
        self.fields['payment_method'].empty_label = None

        # Ensure only actual choices are shown
        self.fields['payment_method'].choices = [
            ('card', 'Credit/Debit Card'),
            ('upi', 'UPI'),
            ('netbanking', 'Netbanking')
        ]
