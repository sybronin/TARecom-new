from app.models import User
from django.contrib import messages
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist, ValidationError

#修改个人信息（除密码之外的全部个人信息）
def changeSelfIndoData(username,formData,file):
    user = User.objects.get(username=username)
    user.address = formData['address']
    user.sex = formData['sex']
    #user.email = formData['email']
    if formData['textarea'] != None:
        user.textarea = formData['textarea']
    if file.get('avatar') != None:
        user.avatar = file.get('avatar')

#存储修改后的个人信息
    user.save()

#修改密码
def changePassword(userInfo, passwordInfo):
    oldPwd = passwordInfo['oldPassword']
    newPwd = passwordInfo['newPassword']
    newPwdConfirm = passwordInfo['newPasswordConfirm']
    user = User.objects.get(username=userInfo.username)

    if oldPwd != userInfo.password:
        return '原始密码不正确'

    if newPwd != newPwdConfirm:
        return '两次新密码输入不一致'

    # 存储新密码
    user.password = newPwd
    user.save()

    # 返回 None 表示成功
    return None
