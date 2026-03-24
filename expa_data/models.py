from django.db import models



class OGVSignup(models.Model):
    class Meta:
        verbose_name = 'OGV Signup'
        verbose_name_plural = 'OGV Signups'

    ep_id = models.CharField(max_length=50, unique=True)

    full_name = models.CharField(max_length=255)

    email = models.EmailField(blank=True, null=True)

    phone = models.CharField(max_length=50, blank=True, null=True)

    status = models.CharField(max_length=100, blank=True, null=True)

    dob = models.DateField(blank=True, null=True)

    backgrounds = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(blank=True, null=True)

    campus = models.CharField(max_length=100, blank=True, null=True)

    home_lc = models.CharField(max_length=100, blank=True, null=True)

    home_mc = models.CharField(max_length=100, blank=True, null=True)

    selected_programmes = models.CharField(max_length=100, blank=True, null=True)

    synced_to_podio = models.BooleanField(default=False)



    def __str__(self):

        return f"{self.full_name} ({self.ep_id})"



class ExpaApplication(models.Model):

    ep_id = models.CharField(max_length=50, unique=True)

    status = models.CharField(max_length=100, blank=True, null=True)

    current_status = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(blank=True, null=True)

    signuped_at = models.DateTimeField(blank=True, null=True)

    experience_end_date = models.DateTimeField(blank=True, null=True)

    date_matched = models.DateTimeField(blank=True, null=True)

    date_approved = models.DateTimeField(blank=True, null=True)

    date_realized = models.DateTimeField(blank=True, null=True)
    date_completed = models.DateTimeField(blank=True, null=True)

    full_name = models.CharField(max_length=255, blank=True, null=True)

    email = models.EmailField(blank=True, null=True)

    profile_photo = models.URLField(max_length=1000, blank=True, null=True)

    home_lc_name = models.CharField(max_length=255, blank=True, null=True)

    home_mc_name = models.CharField(max_length=255, blank=True, null=True)

    opportunity_title = models.CharField(max_length=500, blank=True, null=True)

    opportunity_duration = models.IntegerField(blank=True, null=True)

    opportunity_earliest_start_date = models.DateField(blank=True, null=True)

    opportunity_latest_end_date = models.DateField(blank=True, null=True)

    programme_short_name = models.CharField(max_length=100, blank=True, null=True)

    programme_id = models.CharField(max_length=50, blank=True, null=True)

    home_lc_name_opportunity = models.CharField(max_length=255, blank=True, null=True)

    home_mc_name_opportunity = models.CharField(max_length=255, blank=True, null=True)

    host_lc_name = models.CharField(max_length=255, blank=True, null=True)



    def __str__(self):

        return f"{self.full_name} - {self.status}"



class SignupPerson(models.Model):

    ep_id = models.CharField(max_length=50, unique=True)

    full_name = models.CharField(max_length=255, blank=True, null=True)

    email = models.EmailField(blank=True, null=True)

    created_at = models.DateTimeField(blank=True, null=True)

    profile_photo = models.URLField(max_length=1000, blank=True, null=True)

    home_lc_name = models.CharField(max_length=255, blank=True, null=True)

    home_mc_name = models.CharField(max_length=255, blank=True, null=True)

    selected_programmes = models.CharField(max_length=255, blank=True, null=True)



    def __str__(self):

        return f"{self.full_name}"



class Opportunity(models.Model):

    expa_id = models.CharField(max_length=50, unique=True)

    title = models.CharField(max_length=500, blank=True, null=True)

    status = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(blank=True, null=True)

    date_opened = models.DateTimeField(blank=True, null=True)

    applicants_count = models.IntegerField(default=0)

    accepted_count = models.IntegerField(default=0)
    approvals_count = models.IntegerField(default=0)

    programme_short_name = models.CharField(max_length=100, blank=True, null=True)

    sub_product_name = models.CharField(max_length=255, blank=True, null=True)

    sdg_target_id = models.CharField(max_length=100, blank=True, null=True)

    slots = models.JSONField(blank=True, null=True, default=list)

    available_slots_count = models.IntegerField(default=0)



    def __str__(self):

        return f"{self.title}"




class OGTaSignup(models.Model):
    class Meta:
        verbose_name = 'OGTa Signup'
        verbose_name_plural = 'OGTa Signups'
    ep_id = models.CharField(max_length=50, unique=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    backgrounds = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    campus = models.CharField(max_length=100, blank=True, null=True)
    home_lc = models.CharField(max_length=100, blank=True, null=True)
    home_mc = models.CharField(max_length=100, blank=True, null=True)
    selected_programmes = models.CharField(max_length=100, blank=True, null=True)
    synced_to_podio = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.full_name} ({self.ep_id})"

class OGTeSignup(models.Model):
    class Meta:
        verbose_name = 'OGTe Signup'
        verbose_name_plural = 'OGTe Signups'
    ep_id = models.CharField(max_length=50, unique=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    backgrounds = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    campus = models.CharField(max_length=100, blank=True, null=True)
    home_lc = models.CharField(max_length=100, blank=True, null=True)
    home_mc = models.CharField(max_length=100, blank=True, null=True)
    selected_programmes = models.CharField(max_length=100, blank=True, null=True)
    synced_to_podio = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.full_name} ({self.ep_id})"

class IGVApplication(models.Model):
    class Meta:
        verbose_name = 'IGV Application'
        verbose_name_plural = 'IGV Applications'
    ep_id = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=100, blank=True, null=True)
    current_status = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    signuped_at = models.DateTimeField(blank=True, null=True)
    experience_end_date = models.DateTimeField(blank=True, null=True)
    date_matched = models.DateTimeField(blank=True, null=True)
    date_approved = models.DateTimeField(blank=True, null=True)
    date_realized = models.DateTimeField(blank=True, null=True)
    date_completed = models.DateTimeField(blank=True, null=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    profile_photo = models.URLField(max_length=1000, blank=True, null=True)
    home_lc_name = models.CharField(max_length=255, blank=True, null=True)
    home_mc_name = models.CharField(max_length=255, blank=True, null=True)
    opportunity_title = models.CharField(max_length=500, blank=True, null=True)
    opportunity_duration = models.IntegerField(blank=True, null=True)
    opportunity_earliest_start_date = models.DateField(blank=True, null=True)
    opportunity_latest_end_date = models.DateField(blank=True, null=True)
    programme_short_name = models.CharField(max_length=100, blank=True, null=True)
    programme_id = models.CharField(max_length=50, blank=True, null=True)
    home_lc_name_opportunity = models.CharField(max_length=255, blank=True, null=True)
    home_mc_name_opportunity = models.CharField(max_length=255, blank=True, null=True)
    host_lc_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.full_name} - {self.status}"

class IGTaApplication(models.Model):
    class Meta:
        verbose_name = 'IGTa Application'
        verbose_name_plural = 'IGTa Applications'
    ep_id = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=100, blank=True, null=True)
    current_status = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    signuped_at = models.DateTimeField(blank=True, null=True)
    experience_end_date = models.DateTimeField(blank=True, null=True)
    date_matched = models.DateTimeField(blank=True, null=True)
    date_approved = models.DateTimeField(blank=True, null=True)
    date_realized = models.DateTimeField(blank=True, null=True)
    date_completed = models.DateTimeField(blank=True, null=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    profile_photo = models.URLField(max_length=1000, blank=True, null=True)
    home_lc_name = models.CharField(max_length=255, blank=True, null=True)
    home_mc_name = models.CharField(max_length=255, blank=True, null=True)
    opportunity_title = models.CharField(max_length=500, blank=True, null=True)
    opportunity_duration = models.IntegerField(blank=True, null=True)
    opportunity_earliest_start_date = models.DateField(blank=True, null=True)
    opportunity_latest_end_date = models.DateField(blank=True, null=True)
    programme_short_name = models.CharField(max_length=100, blank=True, null=True)
    programme_id = models.CharField(max_length=50, blank=True, null=True)
    home_lc_name_opportunity = models.CharField(max_length=255, blank=True, null=True)
    home_mc_name_opportunity = models.CharField(max_length=255, blank=True, null=True)
    host_lc_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.full_name} - {self.status}"

class IGTeApplication(models.Model):
    class Meta:
        verbose_name = 'IGTe Application'
        verbose_name_plural = 'IGTe Applications'
    ep_id = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=100, blank=True, null=True)
    current_status = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    signuped_at = models.DateTimeField(blank=True, null=True)
    experience_end_date = models.DateTimeField(blank=True, null=True)
    date_matched = models.DateTimeField(blank=True, null=True)
    date_approved = models.DateTimeField(blank=True, null=True)
    date_realized = models.DateTimeField(blank=True, null=True)
    date_completed = models.DateTimeField(blank=True, null=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    profile_photo = models.URLField(max_length=1000, blank=True, null=True)
    home_lc_name = models.CharField(max_length=255, blank=True, null=True)
    home_mc_name = models.CharField(max_length=255, blank=True, null=True)
    opportunity_title = models.CharField(max_length=500, blank=True, null=True)
    opportunity_duration = models.IntegerField(blank=True, null=True)
    opportunity_earliest_start_date = models.DateField(blank=True, null=True)
    opportunity_latest_end_date = models.DateField(blank=True, null=True)
    programme_short_name = models.CharField(max_length=100, blank=True, null=True)
    programme_id = models.CharField(max_length=50, blank=True, null=True)
    home_lc_name_opportunity = models.CharField(max_length=255, blank=True, null=True)
    home_mc_name_opportunity = models.CharField(max_length=255, blank=True, null=True)
    host_lc_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.full_name} - {self.status}"

class IGVOpportunity(models.Model):
    class Meta:
        verbose_name = 'IGV Opportunity'
        verbose_name_plural = 'IGV Opportunities'
    expa_id = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=500, blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    date_opened = models.DateTimeField(blank=True, null=True)
    applicants_count = models.IntegerField(default=0)
    accepted_count = models.IntegerField(default=0)
    approvals_count = models.IntegerField(default=0)
    programme_short_name = models.CharField(max_length=100, blank=True, null=True)
    sub_product_name = models.CharField(max_length=255, blank=True, null=True)
    sdg_target_id = models.CharField(max_length=100, blank=True, null=True)
    slots = models.JSONField(blank=True, null=True, default=list)
    available_slots_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.title}"

class IGTaOpportunity(models.Model):
    class Meta:
        verbose_name = 'IGTa Opportunity'
        verbose_name_plural = 'IGTa Opportunities'
    expa_id = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=500, blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    date_opened = models.DateTimeField(blank=True, null=True)
    applicants_count = models.IntegerField(default=0)
    accepted_count = models.IntegerField(default=0)
    approvals_count = models.IntegerField(default=0)
    programme_short_name = models.CharField(max_length=100, blank=True, null=True)
    sub_product_name = models.CharField(max_length=255, blank=True, null=True)
    sdg_target_id = models.CharField(max_length=100, blank=True, null=True)
    slots = models.JSONField(blank=True, null=True, default=list)
    available_slots_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.title}"

class IGTeOpportunity(models.Model):
    class Meta:
        verbose_name = 'IGTe Opportunity'
        verbose_name_plural = 'IGTe Opportunities'
    expa_id = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=500, blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    date_opened = models.DateTimeField(blank=True, null=True)
    applicants_count = models.IntegerField(default=0)
    accepted_count = models.IntegerField(default=0)
    approvals_count = models.IntegerField(default=0)
    programme_short_name = models.CharField(max_length=100, blank=True, null=True)
    sub_product_name = models.CharField(max_length=255, blank=True, null=True)
    sdg_target_id = models.CharField(max_length=100, blank=True, null=True)
    slots = models.JSONField(blank=True, null=True, default=list)
    available_slots_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.title}"



class OGVApplication(models.Model):
    class Meta:
        verbose_name = 'OGV Application'
        verbose_name_plural = 'OGV Applications'
    ep_id = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=100, blank=True, null=True)
    current_status = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    signuped_at = models.DateTimeField(blank=True, null=True)
    experience_end_date = models.DateTimeField(blank=True, null=True)
    date_matched = models.DateTimeField(blank=True, null=True)
    date_approved = models.DateTimeField(blank=True, null=True)
    date_realized = models.DateTimeField(blank=True, null=True)
    date_completed = models.DateTimeField(blank=True, null=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    profile_photo = models.URLField(max_length=1000, blank=True, null=True)
    home_lc_name = models.CharField(max_length=255, blank=True, null=True)
    home_mc_name = models.CharField(max_length=255, blank=True, null=True)
    opportunity_title = models.CharField(max_length=500, blank=True, null=True)
    opportunity_duration = models.IntegerField(blank=True, null=True)
    opportunity_earliest_start_date = models.DateField(blank=True, null=True)
    opportunity_latest_end_date = models.DateField(blank=True, null=True)
    programme_short_name = models.CharField(max_length=100, blank=True, null=True)
    programme_id = models.CharField(max_length=50, blank=True, null=True)
    home_lc_name_opportunity = models.CharField(max_length=255, blank=True, null=True)
    home_mc_name_opportunity = models.CharField(max_length=255, blank=True, null=True)
    host_lc_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.full_name} - {self.status}"


class OGTaApplication(models.Model):
    class Meta:
        verbose_name = 'OGTa Application'
        verbose_name_plural = 'OGTa Applications'
    ep_id = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=100, blank=True, null=True)
    current_status = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    signuped_at = models.DateTimeField(blank=True, null=True)
    experience_end_date = models.DateTimeField(blank=True, null=True)
    date_matched = models.DateTimeField(blank=True, null=True)
    date_approved = models.DateTimeField(blank=True, null=True)
    date_realized = models.DateTimeField(blank=True, null=True)
    date_completed = models.DateTimeField(blank=True, null=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    profile_photo = models.URLField(max_length=1000, blank=True, null=True)
    home_lc_name = models.CharField(max_length=255, blank=True, null=True)
    home_mc_name = models.CharField(max_length=255, blank=True, null=True)
    opportunity_title = models.CharField(max_length=500, blank=True, null=True)
    opportunity_duration = models.IntegerField(blank=True, null=True)
    opportunity_earliest_start_date = models.DateField(blank=True, null=True)
    opportunity_latest_end_date = models.DateField(blank=True, null=True)
    programme_short_name = models.CharField(max_length=100, blank=True, null=True)
    programme_id = models.CharField(max_length=50, blank=True, null=True)
    home_lc_name_opportunity = models.CharField(max_length=255, blank=True, null=True)
    home_mc_name_opportunity = models.CharField(max_length=255, blank=True, null=True)
    host_lc_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.full_name} - {self.status}"


class OGTeApplication(models.Model):
    class Meta:
        verbose_name = 'OGTe Application'
        verbose_name_plural = 'OGTe Applications'
    ep_id = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=100, blank=True, null=True)
    current_status = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    signuped_at = models.DateTimeField(blank=True, null=True)
    experience_end_date = models.DateTimeField(blank=True, null=True)
    date_matched = models.DateTimeField(blank=True, null=True)
    date_approved = models.DateTimeField(blank=True, null=True)
    date_realized = models.DateTimeField(blank=True, null=True)
    date_completed = models.DateTimeField(blank=True, null=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    profile_photo = models.URLField(max_length=1000, blank=True, null=True)
    home_lc_name = models.CharField(max_length=255, blank=True, null=True)
    home_mc_name = models.CharField(max_length=255, blank=True, null=True)
    opportunity_title = models.CharField(max_length=500, blank=True, null=True)
    opportunity_duration = models.IntegerField(blank=True, null=True)
    opportunity_earliest_start_date = models.DateField(blank=True, null=True)
    opportunity_latest_end_date = models.DateField(blank=True, null=True)
    programme_short_name = models.CharField(max_length=100, blank=True, null=True)
    programme_id = models.CharField(max_length=50, blank=True, null=True)
    home_lc_name_opportunity = models.CharField(max_length=255, blank=True, null=True)
    home_mc_name_opportunity = models.CharField(max_length=255, blank=True, null=True)
    host_lc_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.full_name} - {self.status}"
