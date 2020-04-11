from django.contrib import admin
from .models import Author, Book, Publisher, BookCopy, BookHold, BookBorrowed, UserHistory, ReviewRequest, ReviewRecord


# Register your models here.
admin.site.register(Author)
admin.site.register(Book)
admin.site.register(Publisher)
admin.site.register(BookCopy)
admin.site.register(BookHold)
admin.site.register(BookBorrowed)
admin.site.register(UserHistory)
admin.site.register(ReviewRequest)
admin.site.register(ReviewRecord)