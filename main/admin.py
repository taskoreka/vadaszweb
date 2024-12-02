from django.contrib import admin
from .models import Vadfajtak, Vadfelek, Vadaszterulet, Idopont,  Vadasztarsasag, User, UserProfil, Krotaliaszam

admin.site.register(Vadfajtak)
admin.site.register(Vadfelek)
admin.site.register(Vadaszterulet)
admin.site.register(Idopont)
admin.site.register(Krotaliaszam)
admin.site.register(UserProfil)



class VadasztarsasagAdmin(admin.ModelAdmin):
    list_display = ('vadasztarsasag', 'vad_hatosag')
    filter_horizontal = ('vadaszok',)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "vadaszok":
            kwargs["queryset"] = User.objects.filter(groups__name='vadasz')
        return super().formfield_for_manytomany(db_field, request, **kwargs)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "vad_hatosag":
            kwargs["queryset"] = User.objects.filter(groups__name='hatosag')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(Vadasztarsasag, VadasztarsasagAdmin)

class VadaszteruletAdmin(admin.ModelAdmin):
    list_display = ('vadaszterulet', 'vadasztarsasag')


class KrotaliaAdmin(admin.ModelAdmin):
    list_display = ('krotaliaszam', 'tulajdnos')