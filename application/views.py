from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import auth
from application.models import CustomUser, Event, ClubAdmin, Club, EventRegistration, EventImage
from application.forms import EventForm, ClubForm, ClubJoinForm
from django.contrib.auth.hashers import make_password, check_password

#the user will register here.
def register(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        user_name = request.POST['user_name']
        user_email = request.POST['user_email']
        user_password1 = request.POST['user_password1']
        user_password2 = request.POST['user_password2']
        is_club_admin = request.POST.get('is_club_admin', 'off') == "on"

        if user_password1 == user_password2:
            if CustomUser.objects.filter(email=user_email).exists():
                messages.error(request, 'Email already exists.')
                return redirect('register')
            elif CustomUser.objects.filter(username=user_name).exists():
                messages.error(request, 'UserName already taken.')
                return redirect('register')
            else:
                # Create the user first
                user = CustomUser.objects.create_user(
                    username=user_name,
                    email=user_email,
                    password=user_password1,
                    first_name=first_name,
                    last_name=last_name,
                    is_club_admin=is_club_admin
                )
                user.save()

                # Create a club if the user is a club admin
                if is_club_admin:
                    # Create or get the default club
                    club, created = Club.objects.get_or_create(
                        club_name=f"{user.first_name}'s Club",  # Unique name
                        defaults={
                            'club_email': user_email,
                            'club_desc': "Default Description for Club"
                        }
                    )

                    # Ensure the password is hashed
                    hashed_password = make_password(user_password1)

                    # Create the ClubAdmin record
                    club_admin = ClubAdmin.objects.create(
                        user=user,
                        club=club,
                        club_password=hashed_password
                    )
                    club_admin.delete()
                messages.success(request, "Registration successful! Please log in.")
                return redirect('login')
        else:
            messages.error(request, 'Passwords do not match')
            return redirect('register')
    else:
        return render(request, 'registration.html')

def login(request):
    if request.method == 'POST':
        user_email = request.POST['user_email']
        user_password = request.POST['user_password']

        # Use authenticate to check for the user using the email
        user = authenticate(request, username=user_email, password=user_password)

        if user is not None:
            auth_login(request, user)
            messages.success(request, 'Logged in Successfully.')
            return redirect('homePage')
        else:
            messages.error(request, 'Invalid credentials')
            return redirect('login')
    else:
        return render(request, 'login.html')


def homePage(request):
    return render(request, 'home.html')


def logout(request):
    auth.logout(request)
    return render(request, 'home.html')


def clubPage(request):
    return render(request, 'clubHome.html')


# ----- Event CRUD Views for Club Admins -----


def event_list(request):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to view events.")
        return redirect('login')

    '''try:
        club_admin = request.user.clubadmin  # May raise an error
    except ClubAdmin.DoesNotExist:
        messages.error(request, "You are not an admin of any club.")
        return redirect('homePage')'''
    registered_event_ids = EventRegistration.objects.filter(user=request.user).values_list('event_id', flat=True)
        # Exclude these events from the list
    if hasattr(request.user, 'clubadmin'):
        club_admin = request.user.clubadmin
        #events = Event.objects.filter(club=club_admin.club)
        events = Event.objects.filter(club=club_admin.club).exclude(id__in=registered_event_ids)
    else:
        # Regular users see all events
        events = Event.objects.exclude(id__in=registered_event_ids)

    #events = Event.objects.filter(club=club_admin.club)
    return render(request, 'event/event_list.html', {'events': events})

def user_events(request):
    events = Event.objects.filter(eventregistration__user=request.user)
    return render(request, 'event/user_events.html' , {'events':events})

def create_event(request):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to create an event.")
        return redirect('login')

    if not request.user.is_club_admin:
        messages.error(request, "You are not authorized to create events.")
        return redirect('clubPage')

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, user=request.user)
        images = request.FILES.getlist('posts')
        if form.is_valid():
            event = form.save(commit=False)
            event.club = request.user.clubadmin.club
            event.save()
            for event_image in images:
                 EventImage.objects.create(
                    event=event,
                    image = event_image
                )
            return redirect('event_list')
        else:
            print("Form errors:", form.errors)
    else:
        form = EventForm(user=request.user)
        print("Available clubs:", form.fields['club'].queryset)

    return render(request, 'event/create_event.html', {'form': form})

def update_event(request, event_id):
    if not request.user.is_club_admin:
        messages.error(request, "Only club admins can update events.")
        return redirect('homePage')

    user_clubs = [request.user.clubadmin.club]
    event = get_object_or_404(Event, id=event_id, club__in=user_clubs)
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event, user=request.user)
        images = request.FILES.getlist('posts')
        
        if form.is_valid():
            event = form.save(commit=False)
            event.club = request.user.clubadmin.club
            event.save()
            print("Form is valid")
            for event_image in images:
                 EventImage.objects.create(
                    event=event,
                    image = event_image
                )
            return redirect('event_list')
        else:
            print("Form errors:", form.errors)
    else:
        form = EventForm(instance=event, user=request.user)

    return render(request, 'event/update_event.html', {'form': form, 'event': event})

def delete_event(request, event_id):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to delete events.")
        return redirect('login')
    if not request.user.is_club_admin:
        messages.error(request, "Only club admins can delete events.")
        return redirect('homePage')

    club_admin = request.user.clubadmin
    if not club_admin:
        messages.error(request, "No club admin record found for your account.")
        return redirect('homePage')
    
    event = get_object_or_404(Event, id=event_id, club=club_admin.club)
    event.delete()
    messages.success(request, "Event deleted successfully!")
    return redirect('event_list')

from django.db import IntegrityError, transaction


def create_club(request):
    if not request.user.is_authenticated or not request.user.is_club_admin:
        messages.error(request, "You must be logged in as a club admin.")
        return redirect('homePage')
    if ClubAdmin.objects.filter(user=request.user).exists():
        messages.error(request, "You are already an admin of another club. Please leave your current club first.")
        return redirect('homePage')
    if request.method == "POST":
        form = ClubForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():  # Ensure atomicity
                    # Create the club
                    club = form.save()

                    # Remove any existing admin for this user
                    ClubAdmin.objects.filter(user=request.user).delete()

                    # Hash the password
                    hashed_password = make_password(form.cleaned_data["club_password"])

                    # Create new ClubAdmin
                    ClubAdmin.objects.create(user=request.user, club=club, club_password=hashed_password)

                messages.success(request, "Club created successfully!")
                return redirect('homePage')
            
            except Exception as e:
                print(f"Error: {e}")  # Debugging
                messages.error(request, "An error occurred while creating the club.")
        else:
            messages.error(request, "There were errors in the form.")
    else:
        form = ClubForm()

    return render(request, 'club/create_club.html', {'form': form})

from django.urls import reverse

def join_club(request):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to join a club.")
        return redirect('login')

    if request.method == "POST":
        form = ClubJoinForm(request.POST)
        if form.is_valid():
            club_email = form.cleaned_data["club_email"]
            club_password = form.cleaned_data["club_password"]

            # Fetch the club using the provided email
            club = Club.objects.filter(club_email=club_email).first()
            if not club:
                messages.error(request, "Club with this email does not exist.")
                return redirect("join_club")

            club_admin = ClubAdmin.objects.filter(club=club).first()
            if not club_admin:
                messages.error(request, "This club has no admin yet. Please contact the club.")
                return redirect("homePage")

            if club_admin.check_password(club_password):
                if request.user.is_club_admin:
                    # Already admin flow
                    messages.error(request, "You are already an admin of another club. Leave your current club first.")
                    return redirect('homePage')

                else:
                    # Normal user flow → Redirect to virtual payment
                    return redirect(f'{reverse("virtual_payment")}?type=club&id={club.id}')
            else:
                messages.error(request, "Invalid club password.")
        else:
            print("Form Errors:", form.errors)
            messages.error(request, "There were errors in the form.")
    
    form = ClubJoinForm()
    return render(request, 'club/join_club.html', {'form': form})


'''def register_event(request, event_id):
    if not request.user.is_authenticated:
        messages.error(request, 'You must be logged in to register for events.')
        return redirect('login')
    
    event = get_object_or_404(Event, id=event_id)

    # Prevent duplicate registration
    if EventRegistration.objects.filter(user=request.user, event=event).exists():
        messages.error(request, 'You have already registered for the event.')
        return redirect('user_events')

    # Determine if user gets discount
    is_member = request.user.clubs.exists()
    amount = event.member_discount_price if is_member else event.standard_price

    # Redirect to virtual payment with context
    return redirect(f'{reverse("virtual_payment")}?type=event&id={event.id}&amount={amount}')'''

def register_event(request, event_id):
    if not request.user.is_authenticated:
        messages.error(request, 'Club admins from the same club need not register.')
        return redirect('login')
    
    event = get_object_or_404(Event, id = event_id)
    if request.method == "POST":
        if EventRegistration.objects.filter(user=request.user, event = event).exists():
            messages.error(request, 'You have already registered for the event.')
        else:
            is_member = request.user.clubs.exists()
            amount = event.member_discount_price if is_member else event.standard_price
            return redirect(f'{reverse("virtual_payment")}?type=event&id={event.id}&amount={amount}')

    return render(request, 'event/register_event.html', {'event' : event})

def event_details(request,event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'event/event_details.html', {'event': event})

#virtual payment section
from django.shortcuts import render, get_object_or_404, redirect
from .models import Event, VirtualPayment, EventRegistration
from .forms import VirtualPaymentForm
from django.core.mail import send_mail
from django.contrib import messages

def virtual_payment(request):
    obj_type = request.GET.get('type')
    obj_id = request.GET.get('id')

    if obj_type == 'event':
        target = get_object_or_404(Event, id=obj_id)
        amount = target.registration_fee
    elif obj_type == 'club':
        target = get_object_or_404(Club, id=obj_id)
        amount = target.membership_fee
    else:
        messages.error(request, "Invalid payment target.")
        return redirect('home')

    if request.method == 'POST':
        form = VirtualPaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.user = request.user
            payment.amount = amount
            if obj_type == 'event':
                payment.event = target
                EventRegistration.objects.create(user=request.user, event=target)
            else:
                payment.club = target
                request.user.clubs.add(target)
            payment.save()

            send_mail(
                subject='Payment Confirmation',
                message=f'Hi {request.user.username},\n\nYou have successfully paid ₹{amount:.2f} for {target}.',
                from_email='noreply@campusconnect.com',
                recipient_list=[request.user.email],
                fail_silently=True,
            )

            messages.success(request, f'Payment successful for {target}!')
            return redirect('clubPage' if obj_type == 'club' else 'event_list')

    else:
        form = VirtualPaymentForm()

    return render(request, 'payment/virtual_payment.html', {
        'form': form,
        'object': target,
        'amount': amount,
        'type': obj_type,
    })
