from django.db import models


# Create your models here.

# class UserCreditScore(models.Model):
#     uid = models.BigIntegerField('身份证号', primary_key=True, unique=True)
#     basic_info = models.IntegerField('基本信用', default=0)
#     corporate = models.IntegerField('企业法人', default=0)
#     public_welfare = models.IntegerField('公益行为', default=0)
#     law = models.IntegerField('遵纪守法', default=0)
#     economic = models.IntegerField('经济信用', default=0)
#     life = models.IntegerField('生活信用', default=0)
#     credit_socre = models.IntegerField('信用总分', default=0)
#     created_time = models.DateTimeField('创建时间', auto_now_add=True)
#     updated_time = models.DateTimeField('更新时间', auto_now=True)
#
#     class Meta:
#         db_table = 'user_credit_scores'
