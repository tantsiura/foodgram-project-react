"""Module contains additional classes
to configure the main classes of the application.
"""
from core.enums import Tuples
from django.db.models import Model, Q
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.status import (HTTP_201_CREATED, HTTP_204_NO_CONTENT,
                                   HTTP_400_BAD_REQUEST)


class AddDelViewMixin:
    """
    Adds additional methods to the Viewset.

    Contains a method for adding/removing a connection object
    Many-to-Many between models.
    Requires the `add_serializer` attribute to be defined.

    Example:
        class ExampleViewSet(ModelViewSet, AddDelViewMixin)
            ...
            add_serializer = ExamplSerializer

            def example_func(self, request, **kwargs):
                ...
                obj_id = ...
                return self.add_del_obj(obj_id, relation.M2M)
    """

    add_serializer: ModelSerializer | None = None

    def _add_del_obj(
        self,
        obj_id: int | str,
        m2m_model: Model,
        q: Q
    ) -> Response:
        """Adds/removes an M2M relationship between a user and another entity.

        Args:
            obj_id (int | str):
                `id` of the object with which you want to create/delete a link.
            m2m_model (Model):
                M2M model governing the required communication.
            q (Q):
                Object filtering condition.

        Returns:
            Responce: Status confirming/rejecting the action.
        """
        obj = get_object_or_404(self.queryset, id=obj_id)
        serializer: ModelSerializer = self.add_serializer(obj)
        m2m_obj = m2m_model.objects.filter(q & Q(user=self.request.user))

        if (self.request.method in Tuples.ADD_METHODS) and not m2m_obj:
            m2m_model(None, obj.id, self.request.user.id).save()
            return Response(serializer.data, status=HTTP_201_CREATED)

        if (self.request.method in Tuples.DEL_METHODS) and m2m_obj:
            m2m_obj[0].delete()
            return Response(status=HTTP_204_NO_CONTENT)

        return Response(status=HTTP_400_BAD_REQUEST)
