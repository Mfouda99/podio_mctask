import requests
from django.conf import settings

def submit_podio_lead(data):
    # 1. Get token
    url = 'https://podio.com/oauth/token'
    auth_data = {
        'grant_type': 'app',
        'app_id': settings.PODIO_LEADS_APP_ID,
        'app_token': settings.PODIO_LEADS_APP_TOKEN,
        'client_id': settings.PODIO_CLIENT_ID,
        'client_secret': settings.PODIO_API_KEY
    }
    response = requests.post(url, data=auth_data)
    if response.status_code != 200:
        return False, f"Auth Error: {response.text}"
    
    token = response.json().get('access_token')
    
    # 2. Build items payload
    # As the only known field in the exact snapshot schema is 'title', 
    # but the user provided a full list, we will map them if we know their external_ids.
    # Because we don't have the exact external_ids (they might just be lowercased slugified versions of the names), 
    # we will dynamically pass the dictionary. 

    fields_payload = {}
    
    # Mappings based on standard Podio slugification
    mappings = {
        'name': 'title',  # fallback to title if needed, or 'name'
        'phone': 'phone',
        'email': 'email',
        'status': 'status',
        'campus': 'campus',
        'interested': 'interested',
        'comment': 'comment',
        'state': 'state',
    }
    
    for key, value in data.items():
        if not value: continue
        if key == 'csrfmiddlewaretoken': continue
        
        # Standard Podio external ID slugification
        ext_id = key.lower().replace(' ', '-').replace('\t', '')
        
        # Override specific keys based on typical standard Podio setups 
        if ext_id == 'name': ext_id = 'title'

        # Simple string for text fields
        fields_payload[ext_id] = value

    item_url = f'https://api.podio.com/item/app/{settings.PODIO_LEADS_APP_ID}/'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    item_data = {
        'fields': fields_payload
    }
    
    res = requests.post(item_url, headers=headers, json=item_data)
    if res.status_code in [200, 201]:
        return True, res.json()
    else:
        return False, f"API Error {res.status_code}: {res.text}"
