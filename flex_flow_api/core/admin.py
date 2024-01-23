from django.contrib import admin
from core.models import (
    User,
    Workflow,
    Node,
    Edge,
)

admin.site.register(User)
admin.site.register(Workflow)
admin.site.register(Node)
admin.site.register(Edge)
