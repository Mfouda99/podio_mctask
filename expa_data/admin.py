from django.contrib import admin
from django_admin_multiple_choice_list_filter.list_filters import MultipleChoiceListFilter

class StatusMultipleFilter(MultipleChoiceListFilter):
    title = 'status'
    parameter_name = 'status__in'

    def lookups(self, request, model_admin):
        return (
            ('open', 'Open'),
            ('applied', 'Applied'),
            ('accepted', 'Accepted'),
            ('approved', 'Approved'),
            ('realized', 'Realized'),
            ('finished', 'Finished'),
            ('completed', 'Completed'),
            ('rejected', 'Rejected'),
            ('withdrawn', 'Withdrawn'),
            ('declined', 'Declined')
        )


from .models import (

    OGVSignup,
    OGTaSignup, OGTeSignup,
    ExpaApplication, SignupPerson, Opportunity,
    IGVApplication, IGTaApplication, IGTeApplication,
    IGVOpportunity, IGTaOpportunity, IGTeOpportunity, OGVApplication, OGTaApplication, OGTeApplication
)

@admin.register(OGVSignup)
class OGVSignupAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'ep_id', 'home_lc', 'created_at', 'synced_to_podio')
    list_filter = ('synced_to_podio', 'home_lc')
    search_fields = ('full_name', 'ep_id', 'email')

@admin.register(OGTaSignup)
class OGTaSignupAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'ep_id', 'home_lc', 'created_at', 'synced_to_podio')
    list_filter = ('synced_to_podio', 'home_lc')
    search_fields = ('full_name', 'ep_id', 'email')

@admin.register(OGTeSignup)
class OGTeSignupAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'ep_id', 'home_lc', 'created_at', 'synced_to_podio')
    list_filter = ('synced_to_podio', 'home_lc')
    search_fields = ('full_name', 'ep_id', 'email')

@admin.register(ExpaApplication)
class ExpaApplicationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'ep_id', 'status', 'home_lc_name', 'opportunity_title')
    list_filter = (StatusMultipleFilter, 'home_lc_name')
    search_fields = ('full_name', 'ep_id', 'email', 'opportunity_title')

@admin.register(SignupPerson)
class SignupPersonAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'ep_id', 'home_lc_name', 'created_at')
    list_filter = ('home_lc_name',)
    search_fields = ('full_name', 'ep_id', 'email')

@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ('title', 'expa_id', 'status', 'programme_short_name', 'sdg_name')
    list_filter = (StatusMultipleFilter, 'programme_short_name')
    search_fields = ('title', 'expa_id')

    def sdg_name(self, obj):
        if obj.sdg_target_id:
            main_sdg = str(obj.sdg_target_id).split('.')[0]
            name = SDG_MAPPING.get(main_sdg, obj.sdg_target_id)
            return f'SDG {main_sdg}: {name}'
        return '-'
    sdg_name.short_description = 'SDG'

@admin.register(IGVApplication)
class IGVApplicationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'ep_id', 'status', 'home_lc_name')
    list_filter = (StatusMultipleFilter,)
    search_fields = ('full_name', 'ep_id', 'email')

@admin.register(IGTaApplication)
class IGTaApplicationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'ep_id', 'status', 'home_lc_name')
    list_filter = (StatusMultipleFilter,)
    search_fields = ('full_name', 'ep_id', 'email')

@admin.register(IGTeApplication)
class IGTeApplicationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'ep_id', 'status', 'home_lc_name')
    list_filter = (StatusMultipleFilter,)
    search_fields = ('full_name', 'ep_id', 'email')

SDG_MAPPING = {
    '1': 'NO POVERTY',
    '2': 'ZERO HUNGER',
    '3': 'GOOD HEALTH AND WELL-BEING',
    '4': 'QUALITY EDUCATION',
    '5': 'GENDER EQUALITY',
    '6': 'CLEAN WATER AND SANITATION',
    '7': 'AFFORDABLE AND CLEAN ENERGY',
    '8': 'DECENT WORK AND ECONOMIC GROWTH',
    '9': 'INDUSTRY, INNOVATION AND INFRASTRUCTURE',
    '10': 'REDUCED INEQUALITIES',
    '11': 'SUSTAINABLE CITIES AND COMMUNITIES',
    '12': 'RESPONSIBLE CONSUMPTION AND PRODUCTION',
    '13': 'CLIMATE ACTION',
    '14': 'LIFE BELOW WATER',
    '15': 'LIFE ON LAND',
    '16': 'PEACE, JUSTICE AND STRONG INSTITUTIONS',
    '17': 'PARTNERSHIPS FOR THE GOALS'
}

@admin.register(IGVOpportunity)
class IGVOpportunityAdmin(admin.ModelAdmin):
    list_display = ('title', 'expa_id', 'status', 'sdg_name')
    list_filter = (StatusMultipleFilter,)
    search_fields = ('title', 'expa_id')

    def sdg_name(self, obj):
        if obj.sdg_target_id:
            main_sdg = str(obj.sdg_target_id).split('.')[0]
            name = SDG_MAPPING.get(main_sdg, obj.sdg_target_id)
            return f'SDG {main_sdg}: {name}'
        return '-'
    sdg_name.short_description = 'SDG'

@admin.register(IGTaOpportunity)
class IGTaOpportunityAdmin(admin.ModelAdmin):
    list_display = ('title', 'expa_id', 'status', 'sdg_name')
    list_filter = (StatusMultipleFilter,)
    search_fields = ('title', 'expa_id')

    def sdg_name(self, obj):
        if obj.sdg_target_id:
            main_sdg = str(obj.sdg_target_id).split('.')[0]
            name = SDG_MAPPING.get(main_sdg, obj.sdg_target_id)
            return f'SDG {main_sdg}: {name}'
        return '-'
    sdg_name.short_description = 'SDG'

@admin.register(IGTeOpportunity)
class IGTeOpportunityAdmin(admin.ModelAdmin):
    list_display = ('title', 'expa_id', 'status', 'sdg_name')
    list_filter = (StatusMultipleFilter,)
    search_fields = ('title', 'expa_id')

    def sdg_name(self, obj):
        if obj.sdg_target_id:
            main_sdg = str(obj.sdg_target_id).split('.')[0]
            name = SDG_MAPPING.get(main_sdg, obj.sdg_target_id)
            return f'SDG {main_sdg}: {name}'
        return '-'
    sdg_name.short_description = 'SDG'


@admin.register(OGVApplication)
class OGVApplicationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'ep_id', 'status', 'home_lc_name', 'opportunity_title')
    list_filter = (StatusMultipleFilter, 'home_lc_name')
    search_fields = ('full_name', 'ep_id', 'email')

@admin.register(OGTaApplication)
class OGTaApplicationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'ep_id', 'status', 'home_lc_name', 'opportunity_title')
    list_filter = (StatusMultipleFilter, 'home_lc_name')
    search_fields = ('full_name', 'ep_id', 'email')

@admin.register(OGTeApplication)
class OGTeApplicationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'ep_id', 'status', 'home_lc_name', 'opportunity_title')
    list_filter = (StatusMultipleFilter, 'home_lc_name')
    search_fields = ('full_name', 'ep_id', 'email')



