from django.contrib import admin

# Register your models here.

from .models import *
from import_export.admin import ImportExportModelAdmin
from import_export import resources

def is_admin(user):
    try:
        AdminUser.objects.get(pk=user)
        return True
    except:
        return False

def get_admin_user(user):
    item =None
    try:
        item = AdminUser.objects.get(pk=user.id)
        return item
    except:
        return item
class UserResource(resources.ModelResource):

    class Meta:
        model = User

class UserAdmin(ImportExportModelAdmin):
    readonly_fields = ('date_joined',)
    list_display = ('email', )
    resource_class = UserResource
    
class InputFilter(admin.SimpleListFilter):
    template = 'input_filter.html'

    def lookups(self, request, model_admin):
        # Dummy, required to show the filter.
        return ((),)

    def choices(self, changelist):
        # Grab only the "all" option.
        all_choice = next(super().choices(changelist))
        all_choice['query_parts'] = (
            (k, v)
            for k, v in changelist.get_filters_params().items()
            if k != self.parameter_name
        )
        yield all_choice


admin.site.register(User)


