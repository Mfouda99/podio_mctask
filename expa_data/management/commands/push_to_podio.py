import json
import os

from django.core.management.base import BaseCommand, CommandError

from expa_data.models import (
    OGVSignup,
    OGTaSignup,
    OGTeSignup,
    OGVApplication,
    OGTaApplication,
    OGTeApplication,
    IGVOpportunity,
    IGTaOpportunity,
    IGTeOpportunity,
)
from expa_data.podio_utils import PodioService


ENTITY_FUNCTION_MODEL_MAP = {
    'signups': {
        'ogv': OGVSignup,
        'ogta': OGTaSignup,
        'ogte': OGTeSignup,
    },
    'applications': {
        'ogv': OGVApplication,
        'ogta': OGTaApplication,
        'ogte': OGTeApplication,
    },
    'opportunities': {
        'ogv': IGVOpportunity,
        'ogta': IGTaOpportunity,
        'ogte': IGTeOpportunity,
    },
}

FUNCTION_KEY_BASE = {
    'ogv': 'OGV',
    'ogta': 'OGTA',
    'ogte': 'OGTE',
}


class Command(BaseCommand):
    help = 'Preview or push signups/applications/opportunities to Podio by function and record IDs.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--entity',
            choices=['signups', 'applications', 'opportunities', 'all'],
            default='signups',
            help='Entity to process. Default: signups',
        )
        parser.add_argument(
            '--function',
            choices=['ogv', 'ogta', 'ogte', 'all'],
            default='all',
            help='Function to process. Default: all',
        )
        parser.add_argument(
            '--ids',
            nargs='+',
            help='Optional list of record IDs (ep_id/expa_id depending on entity).',
        )
        parser.add_argument(
            '--app-id',
            help='Override Podio app_id for single-function and single-entity runs.',
        )
        parser.add_argument(
            '--app-token',
            help='Override Podio app_token for single-function and single-entity runs.',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=100,
            help='Maximum rows per function to process. Default: 100',
        )
        parser.add_argument(
            '--execute',
            action='store_true',
            help='Actually push to Podio. Without this flag, command is preview-only.',
        )

    def handle(self, *args, **options):
        selected_entity = options['entity']
        selected_function = options['function']
        selected_ids = options.get('ids') or []
        limit = options['limit']
        execute = options['execute']
        override_app_id = options.get('app_id')
        override_app_token = options.get('app_token')

        entities = ['signups', 'applications', 'opportunities'] if selected_entity == 'all' else [selected_entity]
        functions = ['ogv', 'ogta', 'ogte'] if selected_function == 'all' else [selected_function]

        if (selected_function == 'all' or selected_entity == 'all') and (override_app_id or override_app_token):
            raise CommandError('--app-id/--app-token overrides can only be used with a single function and single entity.')

        if not execute:
            self.stdout.write(self.style.WARNING('Preview mode: no data will be pushed. Use --execute to push.'))

        total_selected = 0
        total_pushed = 0
        total_failed = 0

        for entity_key in entities:
            for function_key in functions:
                model_cls = ENTITY_FUNCTION_MODEL_MAP[entity_key][function_key]
                id_field = self._id_field_for_entity(entity_key)
                env_app_id_key, env_app_token_key = self._env_keys_for(entity_key, function_key)

                app_id = override_app_id or os.getenv(env_app_id_key, '')
                app_token = override_app_token or os.getenv(env_app_token_key, '')

                queryset = model_cls.objects.all().order_by('id')
                if selected_ids:
                    queryset = queryset.filter(**{f'{id_field}__in': selected_ids})
                rows = list(queryset[:limit])

                total_selected += len(rows)

                self.stdout.write(
                    f'Entity: {entity_key.upper()} | Function: {function_key.upper()} | '
                    f'Rows selected: {len(rows)} | App ID: {app_id or "<missing>"}'
                )

                if not rows:
                    continue

                preview_sample = [self._preview_row(entity_key, row) for row in rows[:3]]
                self.stdout.write('Preview sample (first 3):')
                self.stdout.write(json.dumps(preview_sample, indent=2, ensure_ascii=False))

                if not execute:
                    continue

                if not app_id:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Skipping {entity_key.upper()}-{function_key.upper()}: '
                            f'missing {env_app_id_key} and no --app-id provided.'
                        )
                    )
                    total_failed += len(rows)
                    continue

                podio = PodioService(app_id=app_id, app_token=app_token)
                if not podio.ensure_authenticated():
                    self.stdout.write(
                        self.style.ERROR(
                            f'Skipping {entity_key.upper()}-{function_key.upper()}: Podio authentication failed.'
                        )
                    )
                    total_failed += len(rows)
                    continue

                for row in rows:
                    fields_data = self._build_fields_data(entity_key, row)
                    ok, result = podio.create_item(fields_data)
                    row_id = getattr(row, id_field, '')
                    if ok:
                        total_pushed += 1
                    else:
                        total_failed += 1
                        self.stdout.write(self.style.ERROR(f'Failed {id_field}={row_id}: {result}'))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Done.'))
        self.stdout.write(f'Total selected: {total_selected}')
        self.stdout.write(f'Total pushed: {total_pushed}')
        self.stdout.write(f'Total failed: {total_failed}')

    def _id_field_for_entity(self, entity_key):
        return 'expa_id' if entity_key == 'opportunities' else 'ep_id'

    def _env_keys_for(self, entity_key, function_key):
        base = FUNCTION_KEY_BASE[function_key]
        if entity_key == 'signups':
            suffix = ''
        elif entity_key == 'applications':
            suffix = '_APPLICATIONS'
        else:
            suffix = '_OPPORTUNITIES'

        app_id_key = f'PODIO_{base}{suffix}_APP_ID'
        app_token_key = f'PODIO_{base}{suffix}_APP_TOKEN'

        if os.getenv(app_id_key) or os.getenv(app_token_key):
            return app_id_key, app_token_key

        return f'PODIO_{base}_APP_ID', f'PODIO_{base}_APP_TOKEN'

    def _preview_row(self, entity_key, row):
        if entity_key == 'signups':
            return {
                'id': row.ep_id,
                'name': row.full_name,
                'status': self._map_status_to_podio(row.status),
                'campus': row.home_lc,
            }
        if entity_key == 'applications':
            return {
                'id': row.ep_id,
                'name': row.full_name,
                'status': self._map_status_to_podio(row.status),
                'opportunity': row.opportunity_title,
                'programme': row.programme_short_name,
            }
        return {
            'id': row.expa_id,
            'title': row.title,
            'status': self._map_status_to_podio(row.status),
            'programme': row.programme_short_name,
            'sdg_target_id': row.sdg_target_id,
        }

    def _build_fields_data(self, entity_key, row):
        if entity_key == 'signups':
            return self._build_signups_fields(row)
        if entity_key == 'applications':
            return self._build_applications_fields(row)
        return self._build_opportunities_fields(row)

    def _build_signups_fields(self, row):
        fields = [
            {'external_id': 'ep-id', 'values': [{'value': str(row.ep_id)}]},
            {'external_id': 'name', 'values': [{'value': row.full_name or ''}]},
        ]

        if row.phone:
            fields.append({'external_id': 'phone', 'values': [{'type': 'mobile', 'value': row.phone}]})

        mapped_status = self._map_status_to_podio(row.status)
        if mapped_status:
            fields.append({'external_id': 'status', 'values': [{'value': mapped_status}]})

        if row.dob:
            fields.append({'external_id': 'dob-person', 'values': [{'start': f'{row.dob} 00:00:00'}]})

        if row.backgrounds:
            fields.append({'external_id': 'backgrounds', 'values': [{'value': row.backgrounds}]})

        if row.home_lc:
            fields.append({'external_id': 'campus', 'values': [{'value': row.home_lc}]})

        if row.created_at:
            fields.append({'external_id': 'signed-up-at', 'values': [{'start': row.created_at.strftime('%Y-%m-%d %H:%M:%S')}]})

        return fields

    def _build_applications_fields(self, row):
        fields = [
            {'external_id': 'ep-id', 'values': [{'value': str(row.ep_id)}]},
            {'external_id': 'name', 'values': [{'value': row.full_name or ''}]},
        ]

        mapped_status = self._map_status_to_podio(row.status)
        if mapped_status:
            fields.append({'external_id': 'status', 'values': [{'value': mapped_status}]})

        if row.current_status:
            fields.append({'external_id': 'current-status', 'values': [{'value': row.current_status}]})
        if row.email:
            fields.append({'external_id': 'email', 'values': [{'value': row.email}]})
        if row.home_lc_name:
            fields.append({'external_id': 'home-lc', 'values': [{'value': row.home_lc_name}]})
        if row.programme_short_name:
            fields.append({'external_id': 'programme', 'values': [{'value': row.programme_short_name}]})
        if row.opportunity_title:
            fields.append({'external_id': 'opportunity-title', 'values': [{'value': row.opportunity_title}]})
        if row.created_at:
            fields.append({'external_id': 'created-at', 'values': [{'start': row.created_at.strftime('%Y-%m-%d %H:%M:%S')}]})

        return fields

    def _build_opportunities_fields(self, row):
        fields = [
            {'external_id': 'opportunity-id', 'values': [{'value': str(row.expa_id)}]},
            {'external_id': 'title', 'values': [{'value': row.title or ''}]},
        ]

        mapped_status = self._map_status_to_podio(row.status)
        if mapped_status:
            fields.append({'external_id': 'status', 'values': [{'value': mapped_status}]})

        if row.programme_short_name:
            fields.append({'external_id': 'programme-short-name', 'values': [{'value': row.programme_short_name}]})
        if row.sub_product_name:
            fields.append({'external_id': 'sub-product-name', 'values': [{'value': row.sub_product_name}]})
        if row.sdg_target_id:
            fields.append({'external_id': 'sdg-target-id', 'values': [{'value': row.sdg_target_id}]})

        fields.append({'external_id': 'applicants-count', 'values': [{'value': int(row.applicants_count or 0)}]})
        fields.append({'external_id': 'accepted-count', 'values': [{'value': int(row.accepted_count or 0)}]})
        fields.append({'external_id': 'approvals-count', 'values': [{'value': int(row.approvals_count or 0)}]})
        fields.append({'external_id': 'available-slots-count', 'values': [{'value': int(row.available_slots_count or 0)}]})

        return fields

    def _map_status_to_podio(self, status_value):
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
