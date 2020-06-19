from django.db import models


class DailyStock(models.Model):
    end_price = models.SmallIntegerField()
    diff_yesterday = models.SmallIntegerField()
    current_price = models.SmallIntegerField()
    high_price = models.SmallIntegerField()
    row_price = models.SmallIntegerField()
    volume = models.IntegerField()
    year = models.SmallIntegerField()
    month = models.SmallIntegerField()
    date = models.SmallIntegerField()

    def __str__(self):
        return '{}/{:02d}/{:02d}'.format(self.year, self.month, self.date)
