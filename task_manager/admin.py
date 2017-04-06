import os
from django.contrib import admin
from django.utils.translation import ugettext as _


# models and fields
from .models import Client, Server, Playbook, ActionHistory, Project, BuildTarget, BuildGroup

# widgets and styling
from adminsortable2.admin import SortableInlineAdminMixin

# templates
from django.template.loader import render_to_string

# i18n
from django.utils.translation import ugettext_lazy as _


class BuildTargetPlaybooksTabularInline(SortableInlineAdminMixin, admin.TabularInline):
    model = BuildTarget.pipeline.through
    extra = 0


class BuildGroupTargetsTabularInline(SortableInlineAdminMixin, admin.TabularInline):
    model = BuildGroup.builds.through
    extra = 0


class ServerAdmin(admin.ModelAdmin):
    list_display = ('name', 'domain', 'ip_v4', 'ip_v6', 'invalidate')
    exclude = ['private_key']
    readonly_fields = ['public_key']

    def invalidate(self, obj):
        return render_to_string(os.path.join('admin', 'invalidate_button.jinja'), {'id':obj.id})

    invalidate.short_description = _('Invalidate')
    invalidate.allow_tags = True

    class Media:
        js = ('js/Helpers.js', 'js/admin/Invalidate/Invalidate.js',)
        css = {'all': ('css/longpadmin.css', 'css/bootstrap_button.css')}


class BuildTargetAdmin(admin.ModelAdmin):
    inlines = (BuildTargetPlaybooksTabularInline, )
    list_filter = ('project__title', 'server__name')
    list_display = ('name', 'deploy')

    def deploy(self, obj):
        return render_to_string(os.path.join('admin', 'deploy_button.jinja'), {'id':obj.id})

    deploy.short_description = _('Execute')
    deploy.allow_tags = True

    class Media:
        js = ('js/Helpers.js', 'js/admin/Deploy/Deploy.js',)
        css = {'all': ('css/longpadmin.css', 'css/bootstrap_button.css')}


class BuildGroupAdmin(admin.ModelAdmin):
    inlines = (BuildGroupTargetsTabularInline,)
    list_display = ('name', 'deploy')

    def deploy(self, obj):
        return render_to_string(os.path.join('admin', 'group_deploy_button.jinja'), {'id':obj.id})

    deploy.short_description = _('Execute')
    deploy.allow_tags = True

    class Media:
        js = ('js/Helpers.js', 'js/admin/GroupDeploy/GroupDeploy.js',)
        css = {'all': ('css/longpadmin.css', 'css/bootstrap_button.css')}


admin.site.register(Client)
admin.site.register(Project)

admin.site.register(Server, ServerAdmin)
admin.site.register(Playbook)
admin.site.register(ActionHistory)
admin.site.register(BuildTarget, BuildTargetAdmin)
admin.site.register(BuildGroup, BuildGroupAdmin)


admin.site.site_header = _("RedCap Administration")
admin.site.index_title = _("RedCap")