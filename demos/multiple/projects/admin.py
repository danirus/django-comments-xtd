from django.contrib import admin

from multiple.projects.models import Project, Release


class ReleaseInline(admin.StackedInline):
    model = Release
    extra = 1
    prepopulated_fields = {'slug': ('release_name',)}

class ProjectAdmin(admin.ModelAdmin):
    list_display  = ('project_name', 'is_active')
    search_fields = ('project_name', 'short_description')
    prepopulated_fields = {'slug': ('project_name',)}
    fieldsets = ((None, 
                  {'fields': ('project_name', 'slug',
                              'short_description',
                              'is_active',)}),)
    inlines = [ReleaseInline]

admin.site.register(Project, ProjectAdmin)
