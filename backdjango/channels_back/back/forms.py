from django import forms

class FileForm(forms.Form):
    """
        The model used for the form submitted when uploading a scenario
        The form should only contain one key/value: File
    """
    File=forms.FileField()