from rest_framework.serializers import ModelSerializer
from .models import BotUserModel,TelegramChannelModel, Movie, Series, Episode
class BotUserSerializer(ModelSerializer):
    class Meta:
        model = BotUserModel
        fields = '__all__'
class TelegramChannelSerializer(ModelSerializer):
    class Meta:
        model = TelegramChannelModel
        fields = '__all__'

class MovieSerializer(ModelSerializer):
    class Meta:
        model = Movie
        fields = '__all__'

class SeriesSerializer(ModelSerializer):
    class Meta:
        model = Series
        fields = '__all__'

class EpisodeSerializer(ModelSerializer):
    class Meta:
        model = Episode
        fields = '__all__'