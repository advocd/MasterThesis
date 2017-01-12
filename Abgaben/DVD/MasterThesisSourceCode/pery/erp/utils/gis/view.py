
from django.http import HttpResponse

def update_profile_map_data(request, *args, **kwargs):
    map_state  = request.POST.get('mapstate')
    if 'lat' in map_state and 'lng' in map_state and 'zoom' in map_state:
            request.user.profile.pery_map_data = map_state
            request.user.profile.save()
    return HttpResponse()