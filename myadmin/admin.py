from django.contrib import admin
from .models import *


admin.site.register(Plan)
admin.site.register(PayHistory)
admin.site.register(TermsHistory)
admin.site.register(LimitsHistory)
admin.site.register(DumpsHistory)
admin.site.register(Debtors)
admin.site.register(CallRequest)

