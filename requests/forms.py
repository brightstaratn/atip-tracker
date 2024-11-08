from django import forms
from .models import ATIPRequest, Document, ATIPRequestStatus

class ATIPRequestForm(forms.ModelForm):
    class Meta:
        model = ATIPRequest
        fields = ['institution', 'request_text', 'date_submitted']
        widgets = {
            'request_text': forms.Textarea(attrs={'rows': 4}),
            'date_submitted': forms.DateInput(attrs={'type': 'date'}),
        }

class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['file', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
        }

class StatusUpdateForm(forms.ModelForm):
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        label="Status Change Notes (Optional)"
    )

    class Meta:
        model = ATIPRequest
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_status(self):
        # Comprehensive status transition rules
        current_status = self.instance.status
        new_status = self.cleaned_data['status']

        valid_transitions = {
            ATIPRequestStatus.DRAFT: [ATIPRequestStatus.SUBMITTED],
            ATIPRequestStatus.SUBMITTED: [
                ATIPRequestStatus.RECEIVED,
                ATIPRequestStatus.REJECTED
            ],
            ATIPRequestStatus.RECEIVED: [
                ATIPRequestStatus.CLOSED_COMPLETE,
                ATIPRequestStatus.APPEALED
            ],
            ATIPRequestStatus.REJECTED: [
                ATIPRequestStatus.APPEALED,
                ATIPRequestStatus.CLOSED_COMPLETE
            ]
        }

        if new_status not in valid_transitions.get(current_status, []):
            raise forms.ValidationError(f"Invalid status transition from {current_status}")
        
        return new_status
