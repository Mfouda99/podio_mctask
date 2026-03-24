import json
import secrets
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.urls import reverse

from .decorators import expa_login_required


def _get_oauth_redirect_uri(request):
	configured = (settings.AUTH_REDIRECT_URI or '').strip()
	if configured:
		return configured

	callback_uri = request.build_absolute_uri(reverse('login_callback'))
	if callback_uri.startswith('http://') and 'ngrok-free.app' in request.get_host():
		return callback_uri.replace('http://', 'https://', 1)

	return callback_uri


def home(request):
	return render(request, 'login/home.html')


def login_start(request):
	if request.method == 'GET':
		return redirect('home')

	email = (request.POST.get('email') or '').strip()
	password = request.POST.get('password') or ''

	if not email or not password:
		return render(
			request,
			'login/login_form.html',
			{'error': 'Please provide both EXPA email and password.', 'notice': ''},
		)

	if settings.AUTH_CLIENT_ID and settings.AUTH_CLIENT_SECRET:
		try:
			token_response = _post_json(
				f"{settings.GIS_AUTH_ENDPOINT}/oauth/token",
				{
					'grant_type': 'password',
					'client_id': settings.AUTH_CLIENT_ID,
					'client_secret': settings.AUTH_CLIENT_SECRET,
					'username': email,
					'password': password,
				},
			)
		except Exception:
			return render(
				request,
				'login/login_form.html',
				{
					'error': 'EXPA login failed. Check email/password and app credentials.',
					'notice': '',
				},
			)

		request.session['expa_access_token'] = token_response.get('access_token', '')
		request.session['expa_refresh_token'] = token_response.get('refresh_token', '')
		request.session['expa_token_type'] = token_response.get('token_type', 'Bearer')
		request.session['expa_email'] = email
		request.session['auth_mode'] = 'account_password'

		expires_in = token_response.get('expires_in')
		if isinstance(expires_in, int) and expires_in > 0:
			request.session.set_expiry(expires_in)

		verified_email = _extract_email_from_token(token_response.get('access_token', ''))
		if verified_email and verified_email.lower() != email.lower():
			request.session.flush()
			return render(
				request,
				'login/login_form.html',
				{
					'error': 'Logged account does not match entered EXPA email.',
					'notice': '',
				},
			)

		if verified_email:
			request.session['expa_email'] = verified_email

		return redirect('dashboard')

	if settings.EXPA_ACCESS_TOKEN:
		verified_email = _extract_email_from_token(settings.EXPA_ACCESS_TOKEN)
		if not verified_email:
			return render(
				request,
				'login/login_form.html',
				{
					'error': 'Configured EXPA token is invalid, expired, or unreadable for account verification.',
					'notice': '',
				},
			)

		if verified_email.lower() != email.lower():
			return render(
				request,
				'login/login_form.html',
				{
					'error': 'Entered email does not match the EXPA account behind the configured token.',
					'notice': '',
				},
			)

		request.session['expa_access_token'] = settings.EXPA_ACCESS_TOKEN
		request.session['expa_refresh_token'] = ''
		request.session['expa_token_type'] = 'Bearer'
		request.session['expa_email'] = verified_email
		request.session['auth_mode'] = 'token_validation'
		return redirect('dashboard')

	return render(
		request,
		'login/login_form.html',
		{
			'error': 'Missing EXPA setup. Configure AUTH_CLIENT_ID/AUTH_CLIENT_SECRET or EXPA_ACCESS_TOKEN.',
			'notice': '',
		},
	)


def oauth_redirect(request):
	if not settings.AUTH_CLIENT_ID or not settings.AUTH_CLIENT_SECRET:
		return HttpResponseBadRequest('Missing AUTH_CLIENT_ID/AUTH_CLIENT_SECRET for OAuth redirect mode.')

	state = secrets.token_urlsafe(24)
	request.session['oauth_state'] = state
	redirect_uri = _get_oauth_redirect_uri(request)
	request.session['oauth_redirect_uri'] = redirect_uri

	query = urlencode(
		{
			'response_type': 'code',
			'client_id': settings.AUTH_CLIENT_ID,
			'redirect_uri': redirect_uri,
			'state': state,
		}
	)
	authorize_url = f"{settings.GIS_AUTH_ENDPOINT}/oauth/authorize?{query}"
	return redirect(authorize_url)


def callback(request):
	code = request.GET.get('code')
	returned_state = request.GET.get('state')
	expected_state = request.session.get('oauth_state')

	if not code:
		return HttpResponseBadRequest('Authorization code not found.')

	if expected_state and returned_state != expected_state:
		return HttpResponseBadRequest('Invalid OAuth state.')

	redirect_uri = request.session.get('oauth_redirect_uri') or _get_oauth_redirect_uri(request)

	token_payload = {
		'grant_type': 'authorization_code',
		'client_id': settings.AUTH_CLIENT_ID,
		'client_secret': settings.AUTH_CLIENT_SECRET,
		'redirect_uri': redirect_uri,
		'code': code,
	}

	token_response = _post_json(
		f"{settings.GIS_AUTH_ENDPOINT}/oauth/token",
		token_payload,
	)

	access_token = token_response.get('access_token', '')
	request.session['expa_access_token'] = access_token
	request.session['expa_refresh_token'] = token_response.get('refresh_token')
	request.session['expa_token_type'] = token_response.get('token_type')
	request.session['auth_mode'] = 'oauth_redirect'
	request.session['expa_email'] = _extract_email_from_token(access_token)

	expires_in = token_response.get('expires_in')
	if isinstance(expires_in, int) and expires_in > 0:
		request.session.set_expiry(expires_in)

	request.session.pop('oauth_state', None)
	request.session.pop('oauth_redirect_uri', None)
	return render(request, 'login/popup_close.html')


@expa_login_required
def dashboard(request):
	all_crm_links = {
		'ogv': 'https://podio.com/aiesecglobal/ogv-im-task',
		'ogt': 'https://podio.com/aiesecglobal/ogtim-task',
		'igv': 'https://podio.com/aiesecglobal/igvim-task',
		'igt': 'https://podio.com/aiesecglobal/igtaim-task',
		'b2b': 'https://podio.com/aiesecglobal/b2bim-task',
	}

	user_data = request.session.get('expa_user_data')

	if not user_data or 'current_positions' not in user_data:
		access_token = request.session.get('expa_access_token')
		if access_token:
			user_data = _get_current_person_profile(access_token)
			if user_data:
				request.session['expa_user_data'] = user_data

	# Role-based CRM links filtering
	crm_links = {}
	has_all_access = False
	allowed_funcs = set()

	if user_data and 'current_positions' in user_data:
		import re
		for pos in user_data['current_positions']:
			title = str(pos.get('title') or '').lower()
			role = str((pos.get('role') or {}).get('name') or '').lower()
			func = str((pos.get('function') or {}).get('name') or '').lower()
			full_desc = f"{title} {role} {func}"

			# Extract words safely for strict matching of short words like 'tm', 'bd', 'mc'
			words = set(re.findall(r'[a-z0-9&]+', full_desc))
			func_words = set(re.findall(r'[a-z0-9&]+', func))

			# MC, LCP, Finance, F&L, MXP, TM (as function only) show all tabs
			if 'mc' in words or 'mcvp' in words or 'mcp' in words or 'lcp' in words or 'finance' in words or 'f&l' in words or 'mxp' in words:
				has_all_access = True
			if 'tm' in func_words or 'talent management' in func:
				has_all_access = True

			# Mapping logic
			if 'ogv' in full_desc: 
				allowed_funcs.add('ogv')
			if 'ogt' in full_desc or 'ogta' in full_desc or 'ogte' in full_desc or 'ogta/e' in full_desc: 
				allowed_funcs.add('ogt')
			if 'ogx' in full_desc: 
				allowed_funcs.add('ogv')
				allowed_funcs.add('ogt')
				
			if 'igv' in full_desc: 
				allowed_funcs.add('igv')
			if 'igt' in full_desc or 'igta' in full_desc or 'igte' in full_desc or 'igta/e' in full_desc: 
				allowed_funcs.add('igt')
			
			if 'b2b' in full_desc or 'bd' in words: 
				allowed_funcs.add('b2b')

	if has_all_access or not (user_data and user_data.get('current_positions')):
		crm_links = all_crm_links
	else:
		for k in ['ogv', 'ogt', 'igv', 'igt', 'b2b']:
			if k in allowed_funcs:
				crm_links[k] = all_crm_links[k]

	# Fix __typename for django templates
	if user_data and 'current_experiences' in user_data:
		for exp in user_data['current_experiences']:
			if '__typename' in exp:
				exp['type_name'] = exp['__typename']

	return render(
		request,
		'login/dashboard.html',
		{
			'expa_email': request.session.get('expa_email', ''),
			'user_data': user_data or {},
			'crm_links': crm_links,
		},
	)



def logout_view(request):
	request.session.flush()
	return redirect('home')


def _post_json(url, payload):
	body = json.dumps(payload).encode('utf-8')
	req = Request(
		url,
		data=body,
		headers={'Content-Type': 'application/json'},
		method='POST',
	)
	with urlopen(req) as response:
		raw = response.read().decode('utf-8')
		return json.loads(raw)


def _verify_expa_token(token):
	request = Request(
		f"{settings.GIS_AUTH_ENDPOINT}/oauth/token/info",
		headers={'Authorization': f'Bearer {token}'},
		method='GET',
	)
	try:
		with urlopen(request) as response:
			return response.status == 200
	except (HTTPError, URLError, ValueError):
		return False


def _extract_email_from_token(token):
	if not token:
		return ''

	token_info = _get_token_info(token)
	email = _extract_email(token_info)
	if email:
		return email

	profile = _get_current_person_profile(token)
	return _extract_email(profile)


def _get_token_info(token):
	request = Request(
		f"{settings.GIS_AUTH_ENDPOINT}/oauth/token/info",
		headers={'Authorization': f'Bearer {token}'},
		method='GET',
	)
	try:
		with urlopen(request) as response:
			raw = response.read().decode('utf-8')
			return json.loads(raw)
	except (HTTPError, URLError, ValueError, json.JSONDecodeError):
		return {}


def _get_current_person_profile(token):
	query_cp = '''
	query { 
		currentPerson { 
			id 
			email 
			full_name 
			home_lc {
				id
				name
			}
			current_positions {
				id
				title
				role { name }
				function { name }
				office { name }
			}
		} 
	}
	'''
	request_body = {'query': query_cp}
	import json
	body = json.dumps(request_body).encode('utf-8')
	
	req1 = Request(
		'https://gis-api.aiesec.org/graphql',
		data=body,
		headers={
			'Content-Type': 'application/json',
			'Authorization': token,
		},
		method='POST',
	)
	
	try:
		with urlopen(req1) as response:
			raw = response.read().decode('utf-8')
			payload = json.loads(raw)
			cp_data = payload.get('data', {}).get('currentPerson', {})
	except Exception:
		return {}

	if not cp_data or not cp_data.get('id'):
		return cp_data

	query_person = '''
	query($id: ID!) { 
		person(id: $id) {
			current_experiences {
				id
				__typename
			}
		} 
	}
	'''
	req2 = Request(
		'https://gis-api.aiesec.org/graphql',
		data=json.dumps({'query': query_person, 'variables': {'id': cp_data['id']}}).encode('utf-8'),
		headers={
			'Content-Type': 'application/json',
			'Authorization': token,
		},
		method='POST',
	)
	
	try:
		with urlopen(req2) as response:
			raw2 = response.read().decode('utf-8')
			payload2 = json.loads(raw2)
			person_data = payload2.get('data', {}).get('person', {})
			if isinstance(person_data, dict) and 'current_experiences' in person_data:
				cp_data['current_experiences'] = person_data['current_experiences']
	except Exception:
		pass

	return cp_data


def _extract_email(payload):
	if not isinstance(payload, dict):
		return ''

	for key in ['email', 'user_name', 'username', 'mail']:
		value = payload.get(key)
		if isinstance(value, str) and value.strip():
			return value.strip()

	user = payload.get('user')
	if isinstance(user, dict):
		for key in ['email', 'user_name', 'username', 'mail']:
			value = user.get(key)
			if isinstance(value, str) and value.strip():
				return value.strip()

	return ''


