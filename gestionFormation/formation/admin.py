from django.contrib import admin
from .models import formation
# Register your models here.
class FormationAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)

admin.site.register(formation,FormationAdmin)