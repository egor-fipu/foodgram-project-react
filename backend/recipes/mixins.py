from rest_framework import mixins, viewsets


class ListAndRetrieveSet(mixins.ListModelMixin,
                         mixins.RetrieveModelMixin,
                         viewsets.GenericViewSet):
    pass
