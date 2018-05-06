from django.contrib import admin
from django.contrib.sites.shortcuts import get_current_site
from django.utils.translation import ugettext_lazy as _

from .backends.admin_approval.views import SupervisedRegistrationProfile
from .models import RegistrationProfile
from .users import UsernameField


class RegistrationAdmin(admin.ModelAdmin):
    actions = ['approve_users', 'resend_activation_email']
    list_display = ('user', 'get_name', 'get_is_active')
    raw_id_fields = ['user']
    search_fields = ('user__{0}'.format(UsernameField()),
                     'user__first_name', 'user__last_name')

    def get_name(self, obj):
        return obj.user.first_name
    get_name.admin_order_field = 'name'  # Allows column order sorting
    get_name.short_description = _('Name')  # Renames column head

    def get_is_active(self, obj):
        return obj.user.is_active
    get_is_active.admin_order_field = 'is_active'  # Allows column order sorting
    get_is_active.short_description = _('Is Active?')  # Renames column head

    def approve_users(self, request, queryset):
        """
        Approves the selected users.

        """

        site = get_current_site(request)
        for profile in queryset:
            SupervisedRegistrationProfile.objects.admin_approve_user(profile.id, site)
    approve_users.short_description = _("Approve users")

    def resend_activation_email(self, request, queryset):
        """
        Re-sends activation emails for the selected users.

        Note that this will *only* send activation emails for users
        who are eligible to activate; emails will not be sent to users
        whose activation keys have expired or who have already
        activated.

        """

        site = get_current_site(request)
        for profile in queryset:
            user = profile.user
            RegistrationProfile.objects.resend_activation_mail(user.email, site, request)

    resend_activation_email.short_description = _("Re-send activation emails")

    def get_actions(self, request):
        actions = super(RegistrationAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

admin.site.register(RegistrationProfile, RegistrationAdmin)
