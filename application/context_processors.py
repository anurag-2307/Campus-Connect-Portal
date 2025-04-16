# application/context_processors.py

from .models import ClubAdmin

def club_info(request):
    if request.user.is_authenticated:
        try:
            club_admin = ClubAdmin.objects.select_related('club').get(user=request.user)
            return {
                'is_club_admin': True,
                'user_club': club_admin.club
            }
        except ClubAdmin.DoesNotExist:
            pass
    return {
        'is_club_admin': False,
        'user_club': None
    }
