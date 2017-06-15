from __future__ import unicode_literals

from django.contrib import admin

from .models import (
    Workflow, State, Transition, WorkflowActivity, WorkflowHistory,
    Participant, WorkflowObjectRelation
)


@admin.register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_by', 'created_on']
    search_fields = ['name', 'description']
    save_on_top = True


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ['id', 'label', 'name', 'description', 'is_start_state', 'is_end_state', 'workflow']
    list_display_links = ['name']
    list_filter = ['workflow']
    search_fields = ['name', 'description']
    save_on_top = True


@admin.register(Transition)
class TransitionAdmin(admin.ModelAdmin):
    list_display = ['id', 'label', 'name', 'label', 'description', 'from_state', 'to_state', 'workflow']
    list_filter = ['workflow']
    search_fields = ['name', 'description']
    save_on_top = True


@admin.register(WorkflowActivity)
class WorkflowActivityAdmin(admin.ModelAdmin):
    list_display = ['id', 'workflow', 'created_by', 'created_on', 'completed_on', 'current_state']
    save_on_top = True
    search_fields = ['id']


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ['user', 'workflowactivity']


@admin.register(WorkflowHistory)
class WorkflowHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'workflowactivity', 'log_type', 'state',
        'transition', 'note', 'created_by', 'created_on'
    ]
    save_on_top = True
    search_fields = ['id']
    list_filter = ['log_type']


@admin.register(WorkflowObjectRelation)
class WorkflowObjectRelationAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'content_type', 'workflow'
    ]
