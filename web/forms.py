from django import forms


class DataSetCreationForm(forms.Form):
    GEEKS_CHOICES = (
        ("1", "One"),
        ("2", "Two"),
        ("3", "Three"),
        ("4", "Four"),
        ("5", "Five"),
    )
    project = forms.ChoiceField(choices=GEEKS_CHOICES)
