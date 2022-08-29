from app.models import Client, MailingCampaign, Message, MobileOperator, Tag, Timezone
from django.contrib import admin

# Register your models here.

admin.site.register(Timezone)
admin.site.register(MailingCampaign)
admin.site.register(MobileOperator)
admin.site.register(Tag)
admin.site.register(Client)
admin.site.register(Message)
