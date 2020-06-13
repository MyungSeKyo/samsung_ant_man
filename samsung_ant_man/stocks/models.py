from django.db import models


class DailyStock(models.Model):
    date = models.DateField()
    end_price = models.SmallIntegerField()
    diff_yesterday = models.SmallIntegerField()
    high_price = models.SmallIntegerField()
    row_price = models.SmallIntegerField()
    volume = models.IntegerField()

    def __str__(self):
        return self.date
