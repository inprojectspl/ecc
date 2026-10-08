from django.urls import path
from rest_framework import generics, permissions, serializers
from .models import Note


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ["id", "title"]


class NoteDetail(generics.RetrieveUpdateAPIView):
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Note.objects.filter(owner=self.request.user)


urlpatterns = [path("notes/<int:pk>/", NoteDetail.as_view())]
