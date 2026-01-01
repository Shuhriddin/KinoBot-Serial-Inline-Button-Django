import os
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from app.models import Series, Episode, Movie
from app.serializer import SeriesSerializer, EpisodeSerializer

def debug_code(code):
    print(f"--- Debugging Code {code} ---")
    
    # Check Movie
    try:
        movie = Movie.objects.get(code=code)
        print(f"Found Movie: {movie}")
    except Movie.DoesNotExist:
        print("Movie not found")
        
    # Check Series
    try:
        series = Series.objects.get(code=code)
        print(f"Found Series: {series}")
        print(f"Episodes count: {series.episodes.count()}")
        for ep in series.episodes.all():
            print(f" - Ep {ep.episode_number}: {ep.description}")
            print(f"   File ID ({len(ep.file_id)} chars): {ep.file_id}")
            
        # Try Serialization
        try:
            serialized_series = SeriesSerializer(series).data
            print("Series Serialization: Success")
            serialized_episodes = EpisodeSerializer(series.episodes.all().order_by('episode_number'), many=True).data
            print("Episodes Serialization: Success")
            print("Serialized Data Sample:", serialized_episodes)
        except Exception as e:
            print(f"Serialization FAILED: {e}")
            
    except Series.DoesNotExist:
        print("Series not found")

if __name__ == "__main__":
    debug_code(3)
