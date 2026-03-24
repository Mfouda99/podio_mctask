import os
import requests

from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from dotenv import load_dotenv
from collections import Counter
from datetime import datetime

from .models import (
    ExpaApplication, SignupPerson, Opportunity,
    OGVSignup, IGVApplication, IGTaApplication, IGTeApplication,
    IGVOpportunity, IGTaOpportunity, IGTeOpportunity, OGVApplication, OGTaApplication, OGTeApplication,
    OGTaSignup, OGTeSignup
)

load_dotenv()

EXPA_TOKEN = os.getenv('EXPA_TOKEN')
EXPA_URL = "https://gis-api.aiesec.org/graphql"
EXPA_HEADERS = {
    "Authorization": EXPA_TOKEN,
    "Content-Type": "application/json"
}


def parse_date(date_str):
    if not date_str:
        return None
    try:
        dt = parse_datetime(date_str)
        if dt and timezone.is_naive(dt):
            return timezone.make_aware(dt)
        return dt
    except Exception as e:
        print(f"Date parsing error: {e}")
        return None


def _map_status_to_podio(status_value):
    if not status_value:
        return None
    normalized = str(status_value).strip().lower()
    status_map = {
        'open': 'open',
        'applied': 'Applied',
        'accepted': 'Accepted',
        'approved': 'Approved',
        'realized': 'Realized',
        'finished': 'Finished',
        'complete': 'Complete',
        'completed': 'Complete',
    }
    return status_map.get(normalized)


def sync_signups_to_podio(request):
    query = """
    query {
      people(
        page: 1,
        per_page: 3000,
        filters: { registered: { from: "2025-02-01", to: "2026-04-01" } }
      ) {
        data {
          id
          full_name
          email
          status
          dob
          contact_detail { phone }
          created_at
          profile_photo
          home_lc { id name }
          home_mc { id name }
          person_profile {
            selected_programmes
            backgrounds { id name }
          }
        }
      }
    }
    """

    response = requests.post(EXPA_URL, json={'query': query}, headers=EXPA_HEADERS)
    if response.status_code != 200:
        return JsonResponse({"error": "Failed to fetch EXPA", "details": response.text}, status=400)

    people = response.json().get("data", {}).get("people", {}).get("data", [])

    from .podio_utils import PodioService
    podio_service = PodioService()
    if not podio_service.ensure_authenticated():
        return JsonResponse({"error": "Podio authentication failed"}, status=401)

    synced_count = 0
    errors = []

    for person in people:
        profile = person.get('person_profile') or {}
        progs = profile.get('selected_programmes') or []
        if 7 not in progs:
            continue

        dob_val = (person.get('dob') + " 00:00:00") if person.get('dob') else None
        created_at_val = person.get('created_at').replace('Z', '').replace('T', ' ') if person.get('created_at') else None
        bg_text = ", ".join(bg.get('name', '') for bg in (profile.get('backgrounds') or []) if isinstance(bg, dict))
        campus = person['home_lc']['name'] if person.get('home_lc') else ''
        phone = (person.get('contact_detail') or {}).get('phone') or ''
        mapped_status = _map_status_to_podio(person.get('status'))

        fields_data = [
            {"external_id": "ep-id", "values": [{"value": str(person.get('id'))}]},
            {"external_id": "name", "values": [{"value": person.get('full_name', '')}]},
        ]
        if phone:         fields_data.append({"external_id": "phone", "values": [{"type": "mobile", "value": phone}]})
        if mapped_status: fields_data.append({"external_id": "status", "values": [{"value": mapped_status}]})
        if dob_val:       fields_data.append({"external_id": "dob-person", "values": [{"start": dob_val}]})
        if bg_text:       fields_data.append({"external_id": "backgrounds", "values": [{"value": bg_text}]})
        if campus:        fields_data.append({"external_id": "campus", "values": [{"value": campus}]})
        if created_at_val: fields_data.append({"external_id": "signed-up-at", "values": [{"start": created_at_val[:19]}]})

        success, result = podio_service.create_item(fields_data)
        if success:
            synced_count += 1
        else:
            errors.append({"ep_id": person.get('id'), "error": result})
            if "rate_limit" in str(result):
                break

    return JsonResponse({"status": "success", "synced_to_podio": synced_count, "errors": errors})


def sync_expa_data(request):
    query = """
    query {
      allOpportunityApplication(
        page: 1,
        per_page: 3000,
        filters: {
          created_at: { from: "2025-02-01", to: "2027-04-01" }
        }
      ) {
        data {
          id
          status
          current_status
          created_at
          date_matched
          date_approved
          date_realized
          experience_end_date
          person {
            id
            full_name
            email
            status
            dob
            created_at
            profile_photo
            home_lc { id name }
            home_mc { id name }
          }
          opportunity {
            id
            title
            duration
            earliest_start_date
            latest_end_date
            programme { id short_name_display }
            home_lc { id name }
            home_mc { id name }
            host_lc { id name }
          }
        }
      }
    }
    """

    response = requests.post(EXPA_URL, json={'query': query}, headers=EXPA_HEADERS)
    if response.status_code != 200:
        return JsonResponse({"error": "Failed to fetch data from EXPA", "details": response.text})

    applications = response.json().get('data', {}).get('allOpportunityApplication', {}).get('data', [])

    for app in applications:
        print("Processing Application:", app)

        created_at        = parse_date(app.get('created_at'))
        date_matched      = parse_date(app.get('date_matched'))
        date_approved     = parse_date(app.get('date_approved'))
        date_realized     = parse_date(app.get('date_realized'))
        experience_end_date = parse_date(app.get('experience_end_date'))
        date_completed    = experience_end_date  # Default to experience_end_date

        prog_id  = str(app['opportunity']['programme']['id']) if app['opportunity'].get('programme') else ''
        host_lc  = app['opportunity']['host_lc']['name'] if app['opportunity'].get('host_lc') else ''
        home_lc  = app['person']['home_lc']['name'] if app['person'].get('home_lc') else ''
        home_mc  = app['person']['home_mc']['name'] if app['person'].get('home_mc') else ''

        defaults_dict = {
            'status': app['status'],
            'current_status': app['current_status'],
            'created_at': created_at,
            'signuped_at': parse_date(app['person'].get('created_at')),
            'experience_end_date': experience_end_date,
            'date_matched': date_matched,
            'date_approved': date_approved,
            'date_realized': date_realized,
            'date_completed': date_completed,
            'full_name': app['person'].get('full_name', ''),
            'email': app['person'].get('email', ''),
            'profile_photo': app['person'].get('profile_photo', ''),
            'home_lc_name': home_lc,
            'home_mc_name': home_mc,
            'opportunity_title': app['opportunity'].get('title', ''),
            'opportunity_duration': app['opportunity'].get('duration', 0),
            'opportunity_earliest_start_date': parse_date(app['opportunity'].get('earliest_start_date')),
            'opportunity_latest_end_date': parse_date(app['opportunity'].get('latest_end_date')),
            'programme_short_name': app['opportunity'].get('programme', {}).get('short_name_display', ''),
            'programme_id': prog_id,
            'home_lc_name_opportunity': app['opportunity'].get('home_lc', {}).get('name', ''),
            'home_mc_name_opportunity': app['opportunity'].get('home_mc', {}).get('name', ''),
            'host_lc_name': host_lc,
        }

        ExpaApplication.objects.update_or_create(ep_id=app['id'], defaults=defaults_dict)

        if host_lc == 'Tanta':
            if prog_id == '7':
                IGVApplication.objects.update_or_create(ep_id=app['id'], defaults=defaults_dict)
            elif prog_id == '8':
                IGTaApplication.objects.update_or_create(ep_id=app['id'], defaults=defaults_dict)
            elif prog_id == '9':
                IGTeApplication.objects.update_or_create(ep_id=app['id'], defaults=defaults_dict)

        if home_lc == 'Tanta':
            if prog_id == '7':
                OGVApplication.objects.update_or_create(ep_id=app['id'], defaults=defaults_dict)
            elif prog_id == '8':
                OGTaApplication.objects.update_or_create(ep_id=app['id'], defaults=defaults_dict)
            elif prog_id == '9':
                OGTeApplication.objects.update_or_create(ep_id=app['id'], defaults=defaults_dict)

        print(f"Inserted/Updated: {app['id']}")

    return JsonResponse({"status": "Data synced successfully"})


def funnel_dashboard(request):
    status_counts = dict(Counter(ExpaApplication.objects.values_list("status", flat=True)))
    return render(request, "expa_data/applications_list.html", {"funnel_data": status_counts})


def sync_signup_people(request):
    query = """
    query {
      people(page: 1, per_page: 3000, filters: { registered: { from: "2025-02-01", to: "2026-04-01" } }) {
        data {
          id
          full_name
          email
          status
          dob
          contact_detail { phone }
          created_at
          profile_photo
          home_lc { id name }
          home_mc { id name }
          person_profile { selected_programmes }
        }
      }
    }
    """

    response = requests.post(EXPA_URL, json={'query': query}, headers=EXPA_HEADERS)
    print("Status Code:", response.status_code)

    if response.status_code != 200:
        return JsonResponse({"error": "Failed to fetch signup people", "details": response.text})

    people = response.json().get("data", {}).get("people", {}).get("data", [])

    for person in people:
        created_at = None
        try:
            if person.get('created_at'):
                created_at = parse_datetime(person['created_at'])
        except Exception as e:
            print(f"[ERROR] Could not parse created_at for person ID {person['id']}: {e}")

        selected_progs = (person.get('person_profile') or {}).get('selected_programmes') or []
        defaults_dict = {
            'full_name': person.get('full_name'),
            'email': person.get('email'),
            'status': person.get('status'),
            'dob': person.get('dob'),
            'phone': (person.get('contact_detail') or {}).get('phone') or '',
            'created_at': created_at,
            'home_lc': person['home_lc']['name'] if person.get('home_lc') else '',
            'home_mc': person['home_mc']['name'] if person.get('home_mc') else '',
            'selected_programmes': ", ".join(str(p) for p in selected_progs),
        }

        if 7 in selected_progs:
            OGVSignup.objects.update_or_create(ep_id=person['id'], defaults=defaults_dict)
        if 8 in selected_progs:
            OGTaSignup.objects.update_or_create(ep_id=person['id'], defaults=defaults_dict)
        if 9 in selected_progs:
            OGTeSignup.objects.update_or_create(ep_id=person['id'], defaults=defaults_dict)

    return JsonResponse({"status": "Signup people synced successfully"})


def sync_expa_opportunities(request):
    query = """
    query {
      opportunities(
        filters: { date_opened: { from: "2025-02-01", to: "2026-04-01" } }
        per_page: 500
      ) {
        data {
          id
          title
          status
          created_at
          date_opened
          applicants_count
          accepted_count
          applications_status_count
          slots { id status }
          programme { short_name_display }
          sub_product { name }
          available_slots { id }
          sdg_info { sdg_target { target_id } }
        }
      }
    }
    """

    response = requests.post(EXPA_URL, json={'query': query}, headers=EXPA_HEADERS)
    if response.status_code != 200:
        return JsonResponse({"error": "Failed to fetch opportunities", "details": response.text})

    opportunities = response.json().get("data", {}).get("opportunities", {}).get("data", [])

    for opp in opportunities:
        prog_name_raw = opp.get('programme', {}).get('short_name_display', '')
        prog_name     = str(prog_name_raw).upper()
        sub_product   = opp.get('sub_product') or {}
        sdg_target    = (opp.get('sdg_info') or {}).get('sdg_target') or {}
        app_status_count = opp.get('applications_status_count')

        op_defaults = {
            'title': opp.get('title'),
            'status': opp.get('status'),
            'created_at': parse_date(opp.get('created_at')),
            'date_opened': parse_date(opp.get('date_opened')),
            'applicants_count': opp.get('applicants_count', 0),
            'accepted_count': opp.get('accepted_count', 0),
            'approvals_count': app_status_count.get('approved', 0) if isinstance(app_status_count, dict) else 0,
            'programme_short_name': prog_name_raw,
            'sub_product_name': sub_product.get('name', ''),
            'sdg_target_id': str(sdg_target.get('target_id', '')),
            'available_slots_count': len(opp.get('available_slots') or []),
            'slots': opp.get('available_slots') or [],
        }

        Opportunity.objects.update_or_create(expa_id=opp.get('id'), defaults=op_defaults)

        host_lc_opp = (opp.get('host_lc') or {}).get('name', '')
        if host_lc_opp == 'Tanta' or not host_lc_opp:
            if 'GV' in prog_name:
                IGVOpportunity.objects.update_or_create(expa_id=opp.get('id'), defaults=op_defaults)
            elif 'GTA' in prog_name:
                IGTaOpportunity.objects.update_or_create(expa_id=opp.get('id'), defaults=op_defaults)
            elif 'GTE' in prog_name:
                IGTeOpportunity.objects.update_or_create(expa_id=opp.get('id'), defaults=op_defaults)

    return JsonResponse({"status": "Opportunity data synced successfully."})