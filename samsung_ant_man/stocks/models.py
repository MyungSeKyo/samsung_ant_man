from django.db import models


class DailyStock(models.Model):
    end_price = models.SmallIntegerField()
    diff_yesterday = models.SmallIntegerField()
    current_price = models.SmallIntegerField()
    high_price = models.SmallIntegerField()
    row_price = models.SmallIntegerField()
    volume = models.IntegerField()

    def __str__(self):
        return self.id
