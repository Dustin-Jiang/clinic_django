from rest_framework import serializers
from .models import Announcement, ClinicUser, Date, Record, Campus


class ClinicUserSerializer(serializers.HyperlinkedModelSerializer):
    campus = serializers.SlugRelatedField(
        slug_field='name', queryset=Campus.objects.all())

    class Meta:
        model = ClinicUser
        fields = ('url', 'username', 'id', 'is_staff',
                  'school', 'campus', 'realname', 'phone_num',
                  'work_mon', 'work_tue', 'work_wedn', 'work_thu', 'work_fri',
                  'work_sat', 'work_sun')
        read_only_fields = ('is_staff', )


class RecordSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    campus = serializers.SlugRelatedField(
        slug_field="name", queryset=Campus.objects.all())
    class Meta:
        model = Record
        fields = '__all__'


class RecordSerializerWechat(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='wechat-detail')
    user = serializers.SlugRelatedField(
        queryset=ClinicUser.objects.all(), slug_field="username")
    campus = serializers.SlugRelatedField(
        slug_field="name", queryset=Campus.objects.all())

    class Meta:
        model = Record
        fields = ('url', 'user', 'status', 'realname', 'phone_num', 'campus',
                  'appointment_time', 'description', 'worker_description',
                  'model', 'reject_reason', 'password')
        read_only_fields = ('status', 'worker_description', 'reject_reason')


class DateSerializer(serializers.HyperlinkedModelSerializer):
    count = serializers.ReadOnlyField()
    finish = serializers.ReadOnlyField()
    campus = serializers.SlugRelatedField(
        slug_field="name", queryset=Campus.objects.all())

    class Meta:
        model = Date
        fields = '__all__'
        read_only_fields = ('count', 'finish')


class AnnouncementSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Announcement
        fields = '__all__'
        read_only_fields = ('createdTime',)


class CampusSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Campus
        fields = ('name', 'address')
