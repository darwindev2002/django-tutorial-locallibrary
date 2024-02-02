from django.utils.translation import gettext_lazy as _
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import Author
from django.urls import reverse_lazy
from django.forms import ModelForm
from .models import BookInstance
from .forms import RenewBookForm
import datetime
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from typing import Any
from django.db.models.query import QuerySet
from django.views import generic
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

# Create your views here.

from .models import Book, Author, BookInstance, Genre


def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(
        status__exact='a').count()

    # The 'all()' is implied by default.
    num_authors = Author.objects.count()

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_visits': num_visits,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)


@login_required
def my_view(request):
    pass


@permission_required('catalog.can_mark_returned')
@permission_required('catalog.can_edit')
def my_view_2(request):
    pass


class MyView(LoginRequiredMixin, generic.GenericViewError):
    # login_url = '/login/'
    # redirect_field_name = 'redirect_to'
    pass


class AuthorListView(generic.ListView):
    model = Author


class AuthorDetailView(generic.DetailView):
    model = Author


class BookListView(LoginRequiredMixin, generic.ListView):
    model = Book
    paginate_by = 2
    # your own name for the list as a template variable
    # context_object_name = 'my_book_list'
    # Get 5 books containing the title war
    # queryset = Book.objects.filter(title__icontains='wi')[:5]
    # Specify your own template name/location
    # template_name = 'books/my_arbitrary_template_name_list.html'

    # def get_queryset(self) -> QuerySet[Any]:
    # Get 5 books containing the title war
    # return Book.objects.filter(title__icontains='wi')[:5]

    # def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
    # Call the base implementation first to get the context
    # context = super(BookListView, self).get_context_data(**kwargs)
    # Create any data and add it to the context
    # context['some_data'] = 'This is just some data'
    # return context


class BookDetailView(generic.DetailView):
    model = Book


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view lsiting books on loan to current user."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(
            status__exact='o').order_by('due_back')


class LoanedBooksAllListView(PermissionRequiredMixin, generic.ListView):
    """Generice class-based view listing all books on loan. Only visible to users with can_mark_returned permission."""
    model = BookInstance
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/bookinstance_list_borrowed_all.html'
    paginate_by = 10

    def get_queryset(self) -> QuerySet[Any]:
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')


def renew_book_librarian(request, pk):
    book_inst = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST reuqest then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # CHeck if the form is valid:
        if form.is_valid():
            # Process the data in form.cleaned_data as required
            # (here we just write it to the model due_back field)
            book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.save()

            # Redirect to a new URL
            return HttpResponseRedirect(reverse('all-borrowed'))

    # Else if this is a GET (or any other method) create the default form
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    return render(request, 'catalog/book_renew_librarian.html', {'form': form, 'bookinst': book_inst})


class RenewBookModelForm(ModelForm):
    class Meta:
        model = BookInstance
        fields = ['due_back',]
        lbels = {'due_back': _('Renewal date'), }
        help_texts = {'due_back': _(
            'Enter a date between now and 4 weeks (defualt 3).'), }

    def clean_due_back(self):
        data = self.cleaned_data['due_back']

        # Check date is not in past
        if data < datetime.date.today():
            raise ValidationError(_('Invalid date - renewal in past'))

        # Check date is in range librarian allowed to change (+4 weeks).
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(
                _('Invalid date - renewal more than 4 weeks ahead'))

        # Remeber to always reutrn the cleaned data
        return data


class AuthorCreate(CreateView):
    model = Author
    fields = '__all__'
    initial = {'date_of_death': '05/01/2018', }


class AuthorUpdate(UpdateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']


class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')


class BookCreate(CreateView):
    model = Book
    fields = '__all__'


class BookUpdate(UpdateView):
    model = Book
    fields = '__all__'


class BookDelete(DeleteView):
    model = Book
    success_url = reverse_lazy('books')
