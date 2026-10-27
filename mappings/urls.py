from django.urls import path

from mappings.views import MappingDetailView, MappingListCreateView

urlpatterns = [
    path("", MappingListCreateView.as_view(), name="mapping-list-create"),
    path("<int:pk>/", MappingDetailView.as_view(), name="mapping-detail"),
]
