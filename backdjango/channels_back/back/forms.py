from django import forms


class FileForm(forms.Form):
    """
        The model used for the form submitted when uploading a scenario
        The form should only contain one key/value: File
    """
    File1 = forms.FileField()
    File2 = forms.FileField(required=False)
    File3 = forms.FileField(required=False)
    File4 = forms.FileField(required=False)
