from django import forms
from .models import Author, Publisher, ReviewRecord


class AuthorUpdateForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['name']

    def clean_name(self):
        return self.cleaned_data['name'].title()


class PublisherUpdateForm(forms.ModelForm):
    class Meta:
        model = Publisher
        fields = ['name', 'address']

    def clean_name(self):
        return self.cleaned_data['name'].title()


class AddBookForm(forms.Form):
    ISBN = forms.IntegerField(label='ISBN', min_value=0, max_value=9999999999999)
    title = forms.CharField(label='Title', max_length=255)
    price = forms.IntegerField(label = 'Price', min_value=0)
    authors = forms.ModelMultipleChoiceField(label='Authors', queryset=Author.objects.all())
    publishers = forms.ModelChoiceField(label='Publishers', queryset=Publisher.objects.all())
    availability = forms.IntegerField(label = 'Availability', min_value=0)


class GiveBookForm(forms.Form):
    book_id = forms.IntegerField(label='Book ID', min_value=0, max_value=9999999999999)
    user_id = forms.IntegerField(label='User ID', min_value=0, max_value=9999999999999)


class ReturnBookForm(forms.Form):
    book_id = forms.IntegerField(label='Book ID', min_value=0, max_value=9999999999999)


class Review(forms.ModelForm):
    class Meta:
        model = ReviewRecord
        fields = ['review']
