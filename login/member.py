# Generated People CSV Export Code - Python
# Generated from URL: https://expa.aiesec.org/people/{id}/membership

import requests
import csv
from datetime import datetime

GIS_GRAPHQL_URL = 'https://gis-api.aiesec.org/graphql'
AIESEC_TOKEN = 'Yeo1G9atXNbLdGEBqDIwzbEfB9eHm_K7Qiw08O0jcLg'  # Automatically provided by authentication

def get_people_data():
    query = '''
    query PeopleIndexQuery(
        $name: Boolean!, 
        $managers: Boolean!, 
        $date_of_birth: Boolean!, 
        $status: Boolean!, 
        $tags: Boolean!, 
        $home_lc: Boolean!, 
        $referral: Boolean!, 
        $first_contacted: Boolean!, 
        $home_mc: Boolean!, 
        $contacted_by: Boolean!, 
        $followed_up_at: Boolean!, 
        $follow_up: Boolean!, 
        $phone_number: Boolean!, 
        $page: Int, 
        $count: Int, 
        $filters: PeopleFilter, 
        $q: String, 
        $sort: String
    ) {
        people(
            page: $page
            per_page: $count
            q: $q
            filters: $filters
            sort: $sort
        ) {
            ...PeopleList
            __typename
        }
    }

    fragment PeopleList on PersonList {
        data {
            id
            full_name @include(if: $name)
            profile_photo @include(if: $name)
            status @include(if: $status)
            created_at
            gender
            home_mc {
                id
                name
                __typename
            }
            home_lc {
                id
                name
                __typename
            }
            is_aiesecer
            updated_at
            contacted_by {
                id
                full_name
                __typename
            }
            interviewed
            last_active_at
            person_profile {
                backgrounds {
                    name
                    __typename
                }
                languages {
                    constant_name
                    __typename
                }
                skills {
                    constant_name
                    __typename
                }
                selected_programmes
                nationalities {
                    name
                    id
                    __typename
                }
                __typename
            }
            contact_detail {
                phone @include(if: $phone_number)
                country_code @include(if: $phone_number)
                __typename
            }
            employee_created_via
            managed_opportunities_count
            managed_opportunities {
                edges {
                    node {
                        id
                        title
                        status
                        programmes {
                            short_name_display
                            __typename
                        }
                        host_lc {
                            name
                            __typename
                        }
                        home_mc {
                            name
                            __typename
                        }
                        __typename
                    }
                    __typename
                }
                __typename
            }
            opportunity_applications_count
            managers @include(if: $managers) {
                full_name
                profile_photo
                id
                email
                __typename
            }
            current_experiences {
                id
                __typename
            }
            contacted_at @include(if: $first_contacted)
            contacted_by @include(if: $contacted_by) {
                full_name
                __typename
            }
            followed_up_at @include(if: $followed_up_at)
            email
            first_name
            last_name
            dob @include(if: $date_of_birth)
            permissions {
                can_update
                __typename
            }
            tag_lists @include(if: $tags) {
                id
                name
                __typename
            }
            home_lc @include(if: $home_lc) {
                name
                __typename
            }
            follow_up @include(if: $follow_up) {
                id
                name
                __typename
            }
            followed_up_at @include(if: $followed_up_at)
            home_mc @include(if: $home_mc) {
                name
                __typename
            }
            lc_alignment {
                keywords
                __typename
            }
            organisation_type {
                id
                name
                __typename
            }
            referral_type @include(if: $referral)
            campaign {
                id
                campaign_tag
                __typename
            }
            __typename
        }
        paging {
            total_pages
            current_page
            total_items
            __typename
        }
        __typename
    }
    '''

    variables = {
        "page": 1,
        "count": 1000,
        "filters": {},
        "q": "",
        "name": True,
        "managers": True,
        "date_of_birth": True,
        "status": True,
        "home_mc": True,
        "home_lc": True,
        "phone_number": True,
        "tags": False,
        "referral": False,
        "first_contacted": False,
        "contacted_by": False,
        "followed_up_at": False,
        "follow_up": False,
        "sort": ""
    }

    try:
        response = requests.post(
            GIS_GRAPHQL_URL,
            headers={
                'Content-Type': 'application/json',
                'Authorization': AIESEC_TOKEN,
            },
            json={
                'query': query,
                'variables': variables
            },
            timeout=120
        )
        response.raise_for_status()
        result = response.json()
        return result
    except requests.Timeout:
        print("Request timed out. Try reducing count value (e.g., to 500 or 250) or add pagination logic.")
        return None
    except requests.RequestException as e:
        print(f"Error occurred: {e}")
        print("If you're getting 504 Gateway Timeout, try reducing the count value in variables.")
        return None


def export_to_csv(data, filename=None):
    """
    Export people data to CSV with specified columns
    """
    if not filename:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"people_export_{timestamp}.csv"
    
    headers = [
        'ID',
        'Name', 
        'Managers',
        'Email',
        'Date of Birth',
        'AIESECer',
        'Signed Up On',
        'Applications',
        'Background',
        'Home LC',
        'Home MC',
        'Phone Number',
        'Products Interested In',
        'Status'
    ]

    people = data.get('data', {}).get('people', {}).get('data', [])

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        
        for person in people:
            managers = []
            if person.get('managers'):
                managers = [manager['full_name'] for manager in person['managers']]
            managers_str = ', '.join(managers)
            
            backgrounds = []
            if person.get('person_profile', {}).get('backgrounds'):
                backgrounds = [bg['name'] for bg in person['person_profile']['backgrounds']]
            backgrounds_str = ', '.join(backgrounds)
            
            phone_number = ''
            contact_detail = person.get('contact_detail', {})
            if contact_detail and contact_detail.get('phone') and contact_detail.get('country_code'):
                phone_number = f"{contact_detail['country_code']}{contact_detail['phone']}"
            elif contact_detail and contact_detail.get('phone'):
                phone_number = contact_detail['phone']
            
            products_interested = []
            if person.get('person_profile', {}).get('selected_programmes'):
                programme_mapping = {
                    7: 'GV (new)',
                    8: 'GTa',
                    9: 'GTe', 
                    2: 'GT',
                    5: 'GE',
                    6: 'GV (old)'
                }
                
                programme_ids = person['person_profile']['selected_programmes']
                products_interested = [programme_mapping.get(pid, str(pid)) for pid in programme_ids]
            
            products_str = ', '.join(products_interested) if products_interested else ''
            
            home_lc = person.get('home_lc', {}).get('name', '') if person.get('home_lc') else ''
            home_mc = person.get('home_mc', {}).get('name', '') if person.get('home_mc') else ''
            
            row = [
                person.get('id', ''),
                person.get('full_name', ''),
                managers_str,
                person.get('email', ''),
                person.get('dob', ''),
                'Yes' if person.get('is_aiesecer') else 'No',
                person.get('created_at', ''),
                person.get('opportunity_applications_count', 0),
                backgrounds_str,
                home_lc,
                home_mc,
                phone_number,
                products_str,
                person.get('status', '')
            ]
            
            writer.writerow(row)
    
    print(f"Data exported to {filename}")
    print(f"Total people exported: {len(people)}")
    return filename


if __name__ == "__main__":
    print('Fetching people data...')
    print('Note: Maximum 1000 records will be fetched. If you get timeout errors, reduce count value.')
    data = get_people_data()
    
    if data:
        print("Successfully retrieved data")
        if 'errors' in data:
            print("GraphQL errors:", data['errors'])
        else:
            export_to_csv(data)
    else:
        print("Failed to retrieve data")
        print("Troubleshooting tips:")
        print("1. Check if the authorization token is valid")
        print("2. If getting 504 timeout, reduce count from 1000 to 500 or 250")
        print("3. Consider adding filters to reduce the dataset size")
        print("4. Implement pagination if you need more than 1000 records")
  