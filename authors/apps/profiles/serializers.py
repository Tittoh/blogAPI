from rest_framework import serializers

from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    email = serializers.CharField(source='user.email')
    bio = serializers.CharField(allow_blank=True, required=False)
    image = serializers.CharField(allow_blank=True, required=False)
    follows = serializers.SerializerMethodField(method_name="follows_count")
    followers = serializers.SerializerMethodField(method_name="followers_count")

    class Meta:
        model = Profile
        fields = ('username', 'bio', 'image', 'email', 'follows', 'followers')
        read_only_fields = ('username',)

    def get_image(self, obj):
        if obj.image:
            return obj.image

        return 'https://static.productionready.io/images/smiley-cyrus.jpg'

    def follows_count(self, obj):
        return obj.follows.count()

    def followers_count(self, obj):
        return obj.get_followers(obj).count()
