from django.db import models
# Create your models here.
class BotUserModel(models.Model):
    languages = (
        ('uz', "O'zbek",),
        ('en', "English")
    )
    name = models.CharField(max_length=300,null=True,blank=True,verbose_name="Full Name",help_text="Enter full name")
    telegram_id = models.CharField(max_length=100,unique=True,verbose_name="Telegram ID",help_text="Enter telegram id")
    language = models.CharField(max_length=5,default='uz',choices=languages,verbose_name="Language",help_text="Choose language")
    added = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        if self.name:
            return f"{self.name}"
        else:
            return f"User with ID:{self.telegram_id}"
    class Meta:
        verbose_name = 'Bot User'
        verbose_name_plural='Bot Users'
class TelegramChannelModel(models.Model):
    channel_id = models.CharField(max_length=150,verbose_name="Channel ID",help_text="Enter channel id",unique=True)
    channel_name = models.CharField(max_length=300,verbose_name="Channel Name",help_text="Enter channel name",null=True,blank=True)
    channel_members_count = models.CharField(max_length=200,null=True,blank=True,verbose_name="Channel Memers Count",help_text="Enter channel members count")
    def __str__(self):
        return f"Channel: {self.channel_id}"
    class Meta:
        verbose_name = 'Telegram Channel'
        verbose_name_plural = 'Telegram Channels'


# ==========================================

class Movie(models.Model):
    description = models.TextField(null=True, blank=True)
    file_id = models.CharField(max_length=255, null=True, blank=True)
    code = models.IntegerField(unique=True, null=True, blank=True)
    rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, null=True, blank=True)
    rank = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Movie {self.id} - {self.description}"

class Series(models.Model):
    name = models.CharField(max_length=500)
    code = models.IntegerField(unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Series: {self.name} (Code: {self.code})"

class Episode(models.Model):
    series = models.ForeignKey(Series, on_delete=models.CASCADE, related_name='episodes')
    file_id = models.CharField(max_length=255)
    episode_number = models.IntegerField()
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['episode_number']

    def __str__(self):
        return f"{self.series.name} - Episode {self.episode_number}"

