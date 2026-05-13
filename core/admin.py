from django.contrib import admin
from .models import User, LostItem, FoundItem, Claim, AdminLog, Notification

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'campus_id', 'role')
    search_fields = ('email', 'full_name', 'campus_id')
    list_filter = ('role',)

@admin.register(LostItem)
class LostItemAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'user', 'category', 'date_lost', 'location')
    search_fields = ('item_name', 'description', 'location')
    list_filter = ('category', 'date_lost')

@admin.register(FoundItem)
class FoundItemAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'user', 'category', 'status', 'date_found')
    search_fields = ('item_name', 'description', 'location')
    list_filter = ('status', 'category', 'date_found')

@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ('found_item', 'user', 'status', 'claim_token', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('found_item__item_name', 'user__email', 'claim_token')
    readonly_fields = ('claim_token',)
    
    actions = ['approve_claims', 'reject_claims']

    def approve_claims(self, request, queryset):
        for claim in queryset:
            claim.status = 'approved'
            claim.save() # This triggers the notification now
            AdminLog.objects.create(
                admin=request.user,
                action='approve_claim',
                target_type='Claim',
                target_id=claim.id,
            )
        self.message_user(request, f"{queryset.count()} claims were approved and notifications sent.")
    approve_claims.short_description = "Approve selected claims"

    def reject_claims(self, request, queryset):
        for claim in queryset:
            claim.status = 'rejected'
            claim.save() # This triggers the notification now
            AdminLog.objects.create(
                admin=request.user,
                action='reject_claim',
                target_type='Claim',
                target_id=claim.id,
            )
        self.message_user(request, f"{queryset.count()} claims were rejected and notifications sent.")
    reject_claims.short_description = "Reject selected claims"

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__email', 'title', 'message')

@admin.register(AdminLog)
class AdminLogAdmin(admin.ModelAdmin):
    list_display = ('admin', 'action', 'target_type', 'timestamp')
    search_fields = ('admin__email', 'action')
    list_filter = ('action', 'target_type', 'timestamp')
