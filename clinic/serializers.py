from rest_framework import serializers
from .models import ClinicUser, Record


class ClinicUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ClinicUser
        fields = ('url', 'username', 'id', 'is_staff',
                  'school', 'campus', 'realname', 'phone_num',
                  'work_mon', 'work_tue', 'work_wedn', 'work_thu',
                  'work_sat', 'work_sun')
        read_only_fields = ('is_staff', )


class RecordSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Record
        fields = '__all__'


class RecordSerializerWechat(serializers.HyperlinkedModelSerializer):
    user = serializers.RelatedField(read_only=True, source="username")

    class Meta:
        model = Record
        fields = ('url', 'user', 'status', 'realname', 'phone_num', 'campus',
                  'appointment_time', 'description', 'worker_description',
                  'model', 'reject_reason')
