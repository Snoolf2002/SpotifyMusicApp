from django.db import models

class Album(models.Model):
    artist = models.ForeignKey('music.Artist', on_delete=models.CASCADE)
    title = models.CharField(max_length=150, blank=False, null=False)
    cover = models.URLField(blank=False)

    def __str__(self):
        return self.title