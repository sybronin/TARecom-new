from django.db import models


class TravelInfo(models.Model):
    id = models.AutoField('id',primary_key=True)
    title = models.CharField('景区名',max_length=255,default='')
    level = models.CharField('等级', max_length=255, default='')
    discount = models.CharField('折扣', max_length=255, default='')
    province = models.CharField('省份', max_length=255, default='')
    star = models.CharField('热度', max_length=255, default='')
    saleCount = models.CharField('销量', max_length=255, default='')
    detailAddress = models.CharField('景点详情地址', max_length=2550, default='')
    shortInfo = models.CharField('短评', max_length=255, default='')
    detailUrl = models.TextField('详情地址',  default='')
    score = models.CharField('评分', max_length=255, default='')
    price = models.CharField('价格', max_length=255, default='')
    commentsLen = models.CharField('评论个数', max_length=255, default='')
    detailIntro = models.TextField('详情介绍',  default='')
    img_list = models.ImageField('图片列表', max_length=2550, default='')
    comments = models.TextField('用户评论', default='')
    cover = models.CharField('封面', max_length=2550, default='')
    createTime = models.DateTimeField('爬取时间', auto_now_add=True)

class User(models.Model):
    id = models.AutoField('id',primary_key=True)
    username = models.CharField('用户名', max_length=255, default='')
    password = models.CharField('密码', max_length=255, default='')
    sex = models.CharField('性别', max_length=255, default='')
    address = models.CharField('地址', max_length=255, default='')
    avatar = models.ImageField('头像', upload_to='avatar/', default='avatar/default.png')
    textarea = models.CharField('个人简介', max_length=255, default='')
    createTime = models.DateTimeField('创建时间', max_length=255, default='')