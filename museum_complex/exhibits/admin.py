from django.contrib import admin
from .models import Floor, Hall, Exhibit, ExhibitImage, Movement


@admin.register(Floor)
class FloorAdmin(admin.ModelAdmin):
    list_display = ("number", "name")
    list_editable = ("name",)


class HallInline(admin.TabularInline):
    model = Hall
    extra = 1


@admin.register(Hall)
class HallAdmin(admin.ModelAdmin):
    list_display = ("name", "floor")
    list_filter = ("floor",)
    search_fields = ("name",)


class ExhibitImageInline(admin.TabularInline):
    model = ExhibitImage
    extra = 1


class MovementInline(admin.TabularInline):
    model = Movement
    extra = 0
    readonly_fields = ("timestamp",)
    can_delete = False


@admin.register(Exhibit)
class ExhibitAdmin(admin.ModelAdmin):
    list_display = ("name", "status", "hall", "last_movement_time")
    list_filter = ("status", "hall__floor", "hall")
    search_fields = ("name", "description")
    readonly_fields = ("last_movement_time",)
    inlines = [ExhibitImageInline, MovementInline]
    fieldsets = (
        (None, {"fields": ("name", "description", "status", "hall")}),
        (
            "Системная информация",
            {"fields": ("last_movement_time",), "classes": ("collapse",)},
        ),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Ограничиваем выбор зала только если статус "on_display"
        if "hall" in form.base_fields:
            if obj and obj.status == "on_display":
                form.base_fields["hall"].required = True
            else:
                form.base_fields["hall"].required = False
        return form


@admin.register(Movement)
class MovementAdmin(admin.ModelAdmin):
    list_display = ("exhibit", "action", "from_location", "to_location", "timestamp")
    list_filter = ("action", "timestamp")
    search_fields = ("exhibit__name", "comment")
    readonly_fields = ("timestamp",)
