from django import forms

class ResumeUploadForm(forms.Form):
    resume = forms.FileField(label='Upload Resume', required=True, error_messages={'required': 'Please upload a resume'})
