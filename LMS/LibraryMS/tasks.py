from django.core.mail import send_mass_mail
from background_task import background
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from LibraryMS.models import BookHold, BookBorrowed


@background()
def SendEmails(full_url):
    today = datetime.today().date()

    admin = User.objects.get(pk=1)
    admin.email_user('Testing Background Function', f'Start of the function {datetime.now()}\n\nVisit: {full_url}')

    try:
        hlds = BookHold.objects.filter(available=3)

        msgs = (('Advanced Book Due Notice',
                 f'Dear {_.holder.first_name} {_.holder.last_name},\nYour book {_.book.title} is not picked up by you. Your hold is released\n\nVisit: {full_url}',
                 'LibraryManagementSystem', [_.holder.email]) for _ in hlds)
        send_mass_mail(msgs, fail_silently=True)

        for _ in hlds:
            _.book.availability += 1
            _.book.save()
            _.delete()

        hlds = BookHold.objects.filter(available=1)

        for _ in hlds:
            _.available += 1
            _.save()

        hlds = BookHold.objects.filter(available=2)

        for _ in hlds:
            _.available += 1
            _.save()

        brd = BookBorrowed.objects.filter(due_date__date=today - timedelta(days=2))

        msgs = (('Advanced Book Due Notice',
                 f'Dear {book.borrower.first_name} {book.borrower.last_name},\nYour book {book.book.ISBN.title} will be due in 2 days\n\nVisit: {full_url}',
                 'LibraryManagementSystem', [book.borrower.email]) for book in brd)
        send_mass_mail(msgs, fail_silently=True)

        brd = BookBorrowed.objects.filter(due_date__date=today)

        msgs = (('Book Due Notice',
                 f'Dear {book.borrower.first_name} {book.borrower.last_name},\nYour book {book.book.ISBN.title} is due today. Please Return ASAP.\n\nVisit: {full_url}',
                 'LibraryManagementSystem', [book.borrower.email]) for book in brd)
        send_mass_mail(msgs, fail_silently=True)

        admin.email_user('Testing Background Function', f'End of the function {datetime.now()}\n\n\nVisit: {full_url}')
    except:
        admin.email_user('Testing Background Function', 'Some Error Occured\n\nVisit: {full_url}')
