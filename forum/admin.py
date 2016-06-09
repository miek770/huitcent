from django.contrib import admin
from .models import *

admin.site.register(Forum)
admin.site.register(Category)
admin.site.register(Topic)
#admin.site.register(Topic, TopicAdmin)
admin.site.register(Thread)
#admin.site.register(Thread, ThreadAdmin)
admin.site.register(Post)
admin.site.register(NewPost)
admin.site.register(Attachment)
admin.site.register(Preference)
admin.site.register(Right)
#admin.site.register(Right, RightAdmin)
admin.site.register(Avatar)
