from django.db import models


class DailyStock(models.Model):
    end_price = models.SmallIntegerField()
    diff_yesterday = models.SmallIntegerField(db_index=True)
    current_price = models.SmallIntegerField()
    high_price = models.SmallIntegerField()
    row_price = models.SmallIntegerField()
    volume = models.IntegerField()
    year = models.SmallIntegerField()
    month = models.SmallIntegerField()
    date = models.SmallIntegerField()

    # 크롤링 하는 페이지에서 몇번째 로우인지
    index_in_page = models.SmallIntegerField(db_index=True)

    def __str__(self):
        return '{}/{:02d}/{:02d}'.format(self.year, self.month, self.date)


class DailyDocument(models.Model):
    doc = models.TextField()
    is_up = models.BooleanField()

    def __str__(self):
        return str(self.is_up)
