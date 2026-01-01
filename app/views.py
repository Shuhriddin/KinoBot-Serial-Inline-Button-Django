from django.shortcuts import render
# Create your views here.
from rest_framework.viewsets import ModelViewSet
from .serializer import BotUserSerializer, TelegramChannelSerializer, MovieSerializer, SeriesSerializer, EpisodeSerializer
from .models import BotUserModel, TelegramChannelModel, Movie, Series, Episode
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Max
import re

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.http import JsonResponse
from django.views import View

class BotUserViewset(ModelViewSet):
    queryset = BotUserModel.objects.all()
    serializer_class = BotUserSerializer
class GetUser(APIView):
    def post(self,request):
        data = request.data
        data = data.dict()
        if data.get('telegram_id',None):
            try:
                user = BotUserModel.objects.get(telegram_id=data['telegram_id'])
                serializer = BotUserSerializer(user, partial=True)
                return Response(serializer.data, status=status.HTTP_206_PARTIAL_CONTENT)
            except BotUserModel.DoesNotExist:
                return Response({'error': 'Not found'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'error':'Not found'},status=status.HTTP_204_NO_CONTENT)
class ChangeUserLanguage(APIView):
    def post(self,request):
        data = request.data
        data = data.dict()
        if data.get('telegram_id',None):
            try:
                user = BotUserModel.objects.get(telegram_id=data['telegram_id'])
                user.language = data['language']
                user.save()
                serializer = BotUserSerializer(user, partial=True)
                return Response(serializer.data, status=status.HTTP_206_PARTIAL_CONTENT)
            except BotUserModel.DoesNotExist:
                return Response({'error': 'Not found'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'error':'Not found'},status=status.HTTP_204_NO_CONTENT)
class TelegramChannelViewset(ModelViewSet):
    queryset = TelegramChannelModel.objects.all()
    serializer_class = TelegramChannelSerializer
class DeleteTelegramChannel(APIView):
    def post(self,request):
        data = request.data
        data = data.dict()
        if data.get('channel_id', None):
            try:
                user = TelegramChannelModel.objects.get(channel_id=data['channel_id'])
                user.delete()
                return Response({'status':"Deleted"},status=status.HTTP_200_OK)
            except TelegramChannelModel.DoesNotExist:
                return Response({'error': 'Not found'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'error': 'Not found'}, status=status.HTTP_204_NO_CONTENT)
class GetTelegramChannel(APIView):
    def post(self,request):
        data = request.data
        data = data.dict()
        if data.get('channel_id',None):
            try:
                channel = TelegramChannelModel.objects.get(channel_id=data['channel_id'])
                serializer = TelegramChannelSerializer(channel, partial=True)
                return Response(serializer.data, status=status.HTTP_206_PARTIAL_CONTENT)
            except TelegramChannelModel.DoesNotExist:
                return Response({'error': 'Not found'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'error':'Not found'},status=status.HTTP_204_NO_CONTENT)


class MoviesViewset(ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer


class CreateMovieView(APIView):
    def post(self, request):
        description = request.data.get('description')
        file_id = request.data.get('file_id')
        
        if not description or not file_id:
            return Response({'error': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)

        # Detection Logic
        series_keywords = ['series', 'serial', 'qism', 'season', 'episode', 'part', 'fasl', 'bolum']
        is_series = any(keyword in description.lower() for keyword in series_keywords)

        try:
            if is_series:
                # Basic name extraction - simplified for reliability
                # Assuming format like "Series Name x-qism" or similar.
                # We'll try to find an existing series that matches the description start or create new.
                
                # Heuristic: Remove episode indicators and numbers to get "Title"
                # pattern: (.*)(episode|part|season|qism)(.*)
                # Updated regex to swallow episode number if it precedes the keyword, and removed 'series'/'serial' from split to avoid cutting title early
                match = re.search(r'(.+?)\s*(?:\d+)?\s*(-)?\s*(qism|season|episode|part|fasl|bolum)', description, re.IGNORECASE)
                if match:
                    series_name = match.group(1).strip()
                else:
                    series_name = description[:20] # Fallback

                # Clean up series name (remove markdown bolding etc)
                series_name = series_name.replace('*', '').strip()
                
                # Check for episode number
                episode_match = re.search(r'(\d+)\s*(-)?\s*(qism|bolum|episode|part)', description, re.IGNORECASE)
                if episode_match:
                    episode_number = int(episode_match.group(1))
                else:
                    # Try finding any number
                    num_match = re.search(r'(\d+)', description)
                    episode_number = int(num_match.group(1)) if num_match else 1

                # Find or Create Series
                series, created = Series.objects.get_or_create(name=series_name)
                
                if created:
                    # Assign new code
                    max_movie = Movie.objects.aggregate(Max('code'))['code__max'] or 0
                    max_series = Series.objects.aggregate(Max('code'))['code__max'] or 0
                    series.code = max(max_movie, max_series) + 1
                    series.save()
                
                # Check if episode fails (e.g. duplicate), though we don't have unique constraint on (series, episode_number) yet.
                # Just create it.
                Episode.objects.create(
                    series=series,
                    file_id=file_id,
                    episode_number=episode_number,
                    description=description
                )
                return Response({'id': series.code, 'type': 'series', 'name': series.name}, status=status.HTTP_201_CREATED)

            else:
                # It's a Movie
                max_movie = Movie.objects.aggregate(Max('code'))['code__max'] or 0
                max_series = Series.objects.aggregate(Max('code'))['code__max'] or 0
                next_code = max(max_movie, max_series) + 1
                
                movie = Movie.objects.create(description=description, file_id=file_id, code=next_code)
                serializer = MovieSerializer(movie)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class MovieCodeView(View):
    def get(self, request, *args, **kwargs):
        id = request.GET.get('id')
        if not id:
            return JsonResponse({'error': 'Code not provided'}, status=400)
            
        # Try Movie
        try:
            movie = Movie.objects.get(code=id)
            data = {
                'id': movie.id,
                'description': movie.description,
                'file_id': movie.file_id,
                'code': movie.code,
                'type': 'movie'
            }
            return JsonResponse(data)
        except Movie.DoesNotExist:
            pass
            
        # Try Series
        try:
            series = Series.objects.get(code=id)
            episodes = series.episodes.all().order_by('episode_number')
            ep_data = [{'episode': ep.episode_number, 'file_id': ep.file_id, 'description': ep.description} for ep in episodes]
            data = {
                'id': series.id,
                'name': series.name,
                'code': series.code,
                'type': 'series',
                'episodes': ep_data
            }
            return JsonResponse(data)
        except Series.DoesNotExist:
            return JsonResponse({'error': 'Not found'}, status=404)

class SearchMovieCodeView(APIView):
    def get(self, request, id):
        if not id:
            return Response({'error': 'ID not provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Try Movie
        try:
            movie = Movie.objects.get(code=id)
            serializer = MovieSerializer(movie)
            data = dict(serializer.data)
            data['type'] = 'movie'
            return Response(data, status=status.HTTP_206_PARTIAL_CONTENT)
        except (Movie.DoesNotExist, ValueError):
            pass
        
        # Try Series
        try:
            series = Series.objects.get(code=id)
            serializer = SeriesSerializer(series)
            data = dict(serializer.data)
            data['type'] = 'series'
            data['episodes'] = EpisodeSerializer(series.episodes.all().order_by('episode_number'), many=True).data
            return Response(data, status=status.HTTP_206_PARTIAL_CONTENT)
        except (Series.DoesNotExist, ValueError):
             return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
             # Catch valid crashes (like serializer errors) and return 500 so we know it's not 404
             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetFilmView(APIView):
    def get(self, request, id):
        try:
            movie = Movie.objects.get(code=id) # Changed to code based on logic requirements likely
            serializer = MovieSerializer(movie)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Movie.DoesNotExist:
             # Fallback to check if it's an episode retrieval request? 
             # For now, let's keep it simple. If valid ID is passed, it might be internal ID or Code. 
             # The previous logic used 'id' which might have been PK. 
             # If frontend sends Code, we should use Code. 
             # Let's try PK first to avoid regression if used elsewhere
             try:
                 movie = Movie.objects.get(id=id)
                 return Response(MovieSerializer(movie).data, status=status.HTTP_200_OK)
             except:
                 pass
             return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)


class MovieRateView(APIView):
    def post(self, request):
        code = request.data.get('id')
        try:
            movie = Movie.objects.get(code=code)
            movie.rate += 1
            movie.save()
            return Response(MovieSerializer(movie).data, status=status.HTTP_200_OK)
        except:
             return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    def get(self, request, id):
        # ... existing logic ...
        return Response({}, status=status.HTTP_200_OK)

class TopMoviesView(APIView):
    def get(self, request):
        top_movies = Movie.objects.all().order_by('-rate')[:5]
        serializer = MovieSerializer(top_movies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


