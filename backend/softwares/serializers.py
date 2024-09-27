from rest_framework import serializers
from .models import SoftwareApp, SoftwareAppTask


class SoftwareAppSerializer(serializers.ModelSerializer):

    class Meta:
        model = SoftwareApp
        fields = (
            'guid',
            'name',
            'description',
            'slug',
            'created_at',
            'get_version',
            'is_public'
        )


class SoftwareAppTaskSerializers(serializers.ModelSerializer):

    class Meta:
        model = SoftwareAppTask
        fields = ('guid', 'software_app', 'created_at', 'status', 'status_update')
