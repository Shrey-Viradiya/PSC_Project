from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.decorators import login_required
from users.models import Member
from django.contrib import messages
from django.views.generic import DetailView
from .models import Book, BookCopy, BookHold, BookBorrowed, UserHistory, ReviewRequest, ReviewRecord
from .forms import AuthorUpdateForm, PublisherUpdateForm, AddBookForm, GiveBookForm, ReturnBookForm, Review
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from .tasks import SendEmails
from textblob import TextBlob
from random import randint
from models.BooksData import BooksData
from surprise import KNNBasic, SVD
import numpy as np
import heapq
from collections import defaultdict
from operator import itemgetter

# Create your views here.

@login_required
def StartBackgroundProcess(request):
    if not request.user.is_staff:
        messages.warning(request, 'You are not authorised to requested page.')
        return redirect('Member-dashboard')
    else:
        full_url = ''.join(['http://', get_current_site(request).domain])
        SendEmails(full_url, repeat=86400, schedule=timedelta(minutes=1))
        messages.info(request,'Background Process Start')
        return redirect('Member-dashboard')


@login_required
def dashboard(request):
    if Member.objects.filter(user=request.user).first() is None:
        messages.warning(request, 'You Need to first Update your profile.')
        return redirect('profile')
    else:
        H_books = BookHold.objects.filter(holder=request.user).order_by('-res_date')
        H_books = [(x.book, x.res_date) for x in H_books]

        B_books = BookBorrowed.objects.filter(borrower=request.user).order_by('-res_date')
        B_books = [(x.book, x.res_date, x.due_date) for x in B_books]

        history = UserHistory.objects.filter(reader = request.user)
        history = [(x.book.title, x.book.ISBN) for x in history]

        pending_reviews = ReviewRequest.objects.filter(user = request.user)
        pending_reviews = [(x.book.title, x.book.ISBN) for x in pending_reviews]

        context = {
            'H_books': H_books,
            'B_books': B_books,
            'history': history,
            'prs' : pending_reviews
        }
        return render(request, 'LibraryMS/dashboard.html', context=context)


@login_required
def add_author(request):
    if Member.objects.filter(user=request.user).first() is None:
        messages.warning(request, 'You Need to first Update your profile.')
        return redirect('profile')
    if not request.user.is_staff:
        messages.warning(request, 'You are not authorised to requested page.')
        return redirect('Member-dashboard')
    else:
        if request.method == 'POST':
            form = AuthorUpdateForm(request.POST)
            if form.is_valid():
                form.cleaned_data['name'] = form.cleaned_data['name'].title()
                form.save()
                author = form.cleaned_data.get('name')
                messages.success(request, f'Author entry created successfully for {author}!')
                return redirect('add-author')
        else:
            form = AuthorUpdateForm()
        return render(request, 'LibraryMS/AddAuthor.html', {'form': form})


@login_required
def add_book(request):
    if Member.objects.filter(user=request.user).first() is None:
        messages.warning(request, 'You Need to first Update your profile.')
        return redirect('profile')
    if not request.user.is_staff:
        messages.warning(request, 'You are not authorised to requested page.')
        return redirect('Member-dashboard')
    else:
        if request.method == 'POST':
            form = AddBookForm(request.POST)
            if form.is_valid():
                ISBN = form.cleaned_data['ISBN']
                title = form.cleaned_data['title']
                price = form.cleaned_data['price']
                authors = form.cleaned_data['authors']
                publisher = form.cleaned_data['publishers']
                availability = form.cleaned_data['availability']

                avb = Book.objects.create(ISBN=ISBN, availability=availability, title=title, price=price,
                                          publisher=publisher)
                avb.save()

                for author in authors:
                    avb.authors.add(author)

                for _ in range(availability):
                    bk = BookCopy.objects.create(ISBN=avb)
                    bk.save()

                messages.success(request, f'Book entry created successfully for {title} !')
                return redirect('add-book')
        else:
            form = AddBookForm()

        return render(request, 'LibraryMS/AddBook.html', {'form': form})


@login_required
def add_publisher(request):
    if Member.objects.filter(user=request.user).first() is None:
        messages.warning(request, 'You Need to first Update your profile.')
        return redirect('profile')
    if not request.user.is_staff:
        messages.warning(request, 'You are not authorised to requested page.')
        return redirect('Member-dashboard')
    else:
        if request.method == 'POST':
            form = PublisherUpdateForm(request.POST)
            if form.is_valid():
                form.save()
                name = form.cleaned_data.get('name')
                messages.success(request, f'Publisher entry created successfully for {name}!')
                return redirect('add-publisher')
        else:
            form = PublisherUpdateForm()
        return render(request, 'LibraryMS/AddPub.html', {'form': form})


class BookDetailView(DetailView):
    model = Book

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['copies'] = BookCopy.objects.filter(ISBN=self.get_object().ISBN)
        return context


@login_required
def review(request, pk):
    if Member.objects.filter(user=request.user).first() is None:
        messages.warning(request, 'You Need to first Update your profile.')
        return redirect('profile')

    book = Book.objects.get(ISBN=pk)
    RevReq = get_object_or_404(ReviewRequest,user= request.user, book=book)
    if RevReq is None:
        messages.warning(request, 'Invalid Review Request')
        return redirect('Member-dashboard')

    if request.method == 'POST':
        form = Review(request.POST)
        if form.is_valid():
            rev = form.cleaned_data['review']
            rev = TextBlob(rev)

            r = book.rating
            c = book.review_count
            r = r * c
            if rev.sentiment.polarity >= 0:
                # positive review
                r += 5
                temp = randint(8,10)
            else:
                # negative review
                r += 1
                temp = randint(1,4)

            r /= c + 1
            book.review_count += 1
            book.rating = r
            book.save()

            with open('data/ratings.csv','a') as file:
                file.write(f"\n{request.user.id},{book.ISBN},{temp}")

            revRec = ReviewRecord(user=request.user, book= book, review= rev)
            revRec.save()

            RevReq.delete()
            messages.success(request, f'Review Submitted. Thank You!')
            return redirect('Member-dashboard')
    else:
        form = Review()
    return render(request, 'LibraryMS/review.html', {'form': form , 'title':book.title})


@login_required
def recommendations(request):
    testSubject = str(request.user.id)
    k = 10

    try:
        bk = BooksData('data/')
        data = bk.loadBooksData()

        trainSet = data.build_full_trainset()

        sim_options = {'name': 'cosine',
                       'user_based': True
                       }

        model = KNNBasic(sim_options=sim_options)
        model.fit(trainSet)
        simsMatrix = model.compute_similarities()
        simsMatrix = np.nan_to_num(simsMatrix)

        # print(simsMatrix)
        # print(type(simsMatrix))

        # Get top N similar users to our test subject
        testUserInnerID = trainSet.to_inner_uid(testSubject)

        if sim_options['user_based']:
            similarityRow = simsMatrix[testUserInnerID]

            similarUsers = []
            for innerID, score in enumerate(similarityRow):
                if innerID != testUserInnerID:
                    similarUsers.append((innerID, score))

            kNeighbors = heapq.nlargest(k, similarUsers, key=lambda t: t[1])

            candidates = defaultdict(float)
            for similarUser in kNeighbors:
                innerID = similarUser[0]
                userSimilarityScore = similarUser[1]
                theirRatings = trainSet.ur[innerID]
                for rating in theirRatings:
                    candidates[rating[0]] += (rating[1] / 10.0) * userSimilarityScore

        else:
            testUserRatings = trainSet.ur[testUserInnerID]
            kNeighbors = heapq.nlargest(k, testUserRatings, key=lambda t: t[1])

            candidates = defaultdict(float)
            for itemID, rating in kNeighbors:
                similarityRow = simsMatrix[itemID]
                for innerID, score in enumerate(similarityRow):
                    candidates[innerID] += score * (rating / 10.0)
        # Get the stuff they rated, and add up ratings for each item, weighted by user similarity

        # Build a dictionary of stuff the user has already read
        read = {}
        # print('\n\nBooks user already read.')
        # print("============================")
        for itemID, rating in trainSet.ur[testUserInnerID]:
            bookID = trainSet.to_raw_iid(itemID)
            # print(bk.getBookName(bookID))
            read[itemID] = 1

        # Get top-rated items from similar users:
        pos = 0
        bks2 = []
        for itemID, ratingSum in sorted(candidates.items(), key=itemgetter(1), reverse=True):
            if not itemID in read:
                bookID = trainSet.to_raw_iid(itemID)
                # print(bk.getBookName(bookID))
                bks2.append(bookID)
                pos += 1
                if (pos > 10):
                    break

        UCB = []

        for _ in bks2:
            UCB.append(Book.objects.get(ISBN=_))


        # SVD Algorithms
        def GetAntiTestSetForUser(testSubject, trainSet):
            fill = trainSet.global_mean
            anti_testset = []
            u = trainSet.to_inner_uid(str(testSubject))
            user_items = set([j for (j, _) in trainSet.ur[u]])
            anti_testset += [(trainSet.to_raw_uid(u), trainSet.to_raw_iid(i), fill) for
                             i in trainSet.all_items() if
                             i not in user_items]
            return anti_testset

        model = SVD()
        model.fit(trainSet)
        testSet = GetAntiTestSetForUser(testSubject, trainSet)
        predictions = model.test(testSet)
        recommendations = []
        for userID, ISBN, actualRating, estimatedRating, _ in predictions:
            isbn = ISBN
            recommendations.append((isbn, estimatedRating))

        recommendations.sort(key=lambda x: x[1], reverse=True)

        SVDB = []
        for ratings in recommendations[:k]:
            # print(bk.getBookName(ratings[0]))
            SVDB.append(Book.objects.get(ISBN = ratings[0]))
    except:
        UCB = []
        SVDB = []
    return render(request, 'LibraryMS/recommendations.html', {'UCB': UCB, 'SVDB': SVDB})

@login_required
def HoldBook(request, pk):
    book = Book.objects.get(ISBN=pk)
    if book.availability > 0:
        messages.warning(request, 'You can not hold the book which are all ready available in the shelf!')
        return redirect('book-detail', pk=pk)
    else:
        # book_copies = BookCopy.objects.filter(ISBN=book)
        #
        # reserved_book = BookHold.objects.all()
        # reserved_book_id = []
        #
        # for _ in reserved_book:
        #     reserved_book_id.append(_.book.book_id)
        #
        # for bc in book_copies:
        #     if bc.book_id not in reserved_book_id:
        #         hld = BookHold.objects.create(book_id= bc.book_id, holder = request.user, res_date=datetime.now(), priority=abs(book.availability))
        #         hld.save()
        #         book.availability -= 1
        #         book.save()
        #         break

        holds = BookHold.objects.filter(holder=request.user, book=book).first()
        if holds is not None:
            messages.info(request, 'Can not hold the same book again!')
            return redirect('book-detail', pk=pk)

        full_url = ''.join(['http://', get_current_site(request).domain])
        borrowed = BookBorrowed.objects.filter(borrower=request.user)
        if borrowed:
            for _ in borrowed:
                if _.book.ISBN == book:
                    messages.info(request, 'Can not hold the borrowed book again!')
                    return redirect('book-detail', pk=pk)

        pr = book.availability.__abs__()
        hld = BookHold.objects.create(book=book, holder=request.user, res_date=datetime.now(), priority=pr)
        hld.save()
        book.availability -= 1
        book.save()

        message = f'Dear {request.user.first_name} {request.user.last_name},\nBook {book.title} has been issued today to you.\n\nVisit: {full_url}'
        # send_mail(
        #     f'Material Hold {datetime.today()}',
        #     message,
        #     'LibraryManagementSystem',
        #     [str(request.user.email)],
        #     fail_silently=True,
        # )
        request.user.email_user(f'Material Hold {datetime.today()}', message)
        messages.info(request, 'Book Reserved!')
        return redirect('book-detail', pk=pk)


@login_required
def GiveBook(request):
    if not request.user.is_staff:
        messages.warning(request, 'You are not authorised to requested page.')
        return redirect('Member-dashboard')
    else:
        if request.method == 'POST':
            form = GiveBookForm(request.POST)
            if form.is_valid():
                full_url = ''.join(['http://', get_current_site(request).domain])
                book_id = form.cleaned_data['book_id']
                user = form.cleaned_data['user_id']

                book_copy = get_object_or_404(BookCopy, book_id=book_id)
                usr = get_object_or_404(User, id=user)
                book = book_copy.ISBN

                if BookBorrowed.objects.filter(book=book_copy).first():
                    messages.warning(request, 'Book Already Borrowed! Something is wrong !Do not give the book...')
                    return redirect('give-book')

                if book.availability <= 0:
                    check = BookHold.objects.filter(holder=usr)
                    for _ in check:
                        if _.book == book:
                            bb = BookBorrowed.objects.create(borrower=usr, book=book_copy, res_date=datetime.now(),
                                                             due_date=datetime.now() + timedelta(days=14))
                            bb.save()

                            # book.availability -= 1
                            # book.save()

                            _.delete()

                            other_holds = BookHold.objects.filter(book=book)
                            for x in other_holds:
                                x.priority -= 1
                                x.save()

                            message = f'Dear {usr.first_name} {usr.last_name},\nBook {book.title} has been issued today to you.\n\nVisit: {full_url}'
                            # send_mail(
                            #     f'Material CheckOut {datetime.today()}',
                            #     message,
                            #     'LibraryManagementSystem',
                            #     [str(usr.email)],
                            #     fail_silently=True,
                            # )
                            usr.email_user(f'Material CheckOut {datetime.today()}', message)

                            messages.success(request, 'Book Given!')
                            return redirect('give-book')
                    else:
                        messages.warning(request, 'Book Not Available!')
                        return redirect('give-book')
                else:
                    # book_copies = BookCopy.objects.filter(ISBN=book)
                    #
                    # reserved_book = BookHold.objects.all()
                    # reserved_book_id = []
                    #
                    # for _ in reserved_book:
                    #     reserved_book_id.append(_.book)
                    #
                    # for bc in book_copies:
                    #     if bc not in reserved_book_id:
                    #         bb = BookBorrowed.objects.create(borrower=usr, book=bc, res_date=datetime.now(),
                    #                                          due_date=datetime.now() + timedelta(days=14))
                    #         bb.save()
                    #         book.availability -= 1
                    #         book.save()
                    #         break

                    bb = BookBorrowed.objects.create(borrower=usr, book=book_copy, res_date=datetime.now(),
                                                     due_date=datetime.now() + timedelta(days=14))
                    bb.save()
                    book.availability -= 1
                    book.save()

                    message = f'Dear {usr.first_name} {usr.last_name},\nBook {book.title} has been issued today to you.\n\nVisit: {full_url}'
                    # send_mail(
                    #     f'Material CheckOut {datetime.today()}',
                    #     message,
                    #     'LibraryManagementSystem',
                    #     [str(usr.email)],
                    #     fail_silently=True,
                    # )
                    usr.email_user(f'Material CheckOut {datetime.today()}', message)

                    messages.success(request, 'Book Given!')
                    return redirect('give-book')
        else:
            form = GiveBookForm()
        return render(request, 'LibraryMS/GiveBook.html', {'form': form})


@login_required
def AddMaterial(request):
    if not request.user.is_staff:
        messages.warning(request, 'You are not authorised to requested page.')
        return redirect('Member-dashboard')
    return render(request,'LibraryMS/addmaterial.html')


@login_required
def ReturnBook(request):
    if not request.user.is_staff:
        messages.warning(request, 'You are not authorised to requested page.')
        return redirect('Member-dashboard')
    else:
        if request.method == 'POST':
            form = ReturnBookForm(request.POST)
            if form.is_valid():
                full_url = ''.join(['http://', get_current_site(request).domain])
                id_got = form.cleaned_data['book_id']

                bc = get_object_or_404(BookCopy, book_id=id_got)
                book = bc.ISBN
                book.availability += 1
                book.save()
                temp = get_object_or_404(BookBorrowed, book=bc)
                usr = User.objects.get(email=temp.borrower.email)

                days_past = temp.due_date - datetime.today()
                if days_past.days < 0:
                    m = Member.objects.get(user = usr)
                    m.fine += days_past.days.__abs__() * 3
                    m.save()

                temp.delete()



                record = UserHistory.objects.create(book = book, reader = usr)
                record.save()

                req = ReviewRequest.objects.create(book = book, user = usr)
                req.save()


                person = BookHold.objects.filter(book=book, available=0).order_by('priority').first()

                if person:
                    message = f'Dear {person.holder.first_name} {person.holder.last_name},\nYour held book {book.title} is available. Your hold will be available for 3 days only. Please collect the book ASAP.\n\nVisit: {full_url}'
                    # send_mail(
                    #     'Hold Available for pickup',
                    #     message,
                    #     'LibraryManagementSystem',
                    #     [str(person.holder.email)],
                    #     fail_silently=True,
                    # )
                    person.holder.email_user('Hold available for pickup', message)
                    person.available = 1
                    person.save()

                message = f'Dear {usr.first_name} {usr.last_name},\nBook {book.title} has been returned to library by you.\n\nVisit: {full_url}'
                usr.email_user(f'Material Return {datetime.today()}', message)

                # send_mail(
                #     f'Material Return {datetime.today()}',
                #     message,
                #     'LibraryManagementSystem',
                #     [str(usr.email)],
                #     fail_silently=True,
                # )

                messages.success(request, 'Book Returned!')
                return redirect('return-book')

        else:
            form = ReturnBookForm()
        return render(request, 'LibraryMS/ReturnBook.html', {'form': form})


def home(request):
    if request.method == 'GET':
        query = request.GET.get('q')

        submitbutton = request.GET.get('submit')

        if query is not None:
            query = query.title()
            lookups = Q(title__icontains=query) | Q(authors__name__icontains=query) | Q(
                publisher__name__icontains=query) | Q(ISBN__icontains=query)

            results = Book.objects.filter(lookups).distinct()

            context = {'results': results,
                       'submitbutton': submitbutton,
                       'count': len(results)
                       }
            return render(request, 'LibraryMS/home.html', context)

        else:
            return render(request, 'LibraryMS/home.html')

    else:
        return render(request, 'LibraryMS/home.html')
