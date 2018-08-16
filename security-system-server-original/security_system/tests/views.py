# coding=utf-8

import json

# from django.contrib.auth.models import User
from django.contrib import auth
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from tests.models import MyUser

'''
class UserForm(forms.Form):
    username = forms.CharField(label='用户�?, max_length=100)
    password1 = forms.CharField(label='密码', widget=forms.PasswordInput())
    password2 = forms.CharField(label='确认密码', widget=forms.PasswordInput())
    email = forms.EmailField(label='电子邮件')
    gender = forms.CharField(label='性别')
    contact = forms.CharField(label='联系方式')
    unit = forms.CharField(label='所在单�?)'''

'''
class UserFormLogin(forms.Form):
    username = forms.CharField(label='用户�?, max_length=100)
    password = forms.CharField(label='密码', widget=forms.PasswordInput())
    checkcode = forms.CharField(label='验证�?)'''


def check_code(request):
    import io
    from tests import check_code as CheckCode
    stream = io.BytesIO()
    img, code = CheckCode.create_validate_code()
    img.save(stream, "png")
    request.session['checkcode'] = code
    return HttpResponse(stream.getvalue(), "png")


######################################################################################################
def jsonTest(request):
    response_data = {}
    response_data['username'] = "nibaba"
    response_data['email'] = "132@163.com"
    response_data['password'] = "password"
    response_data['id_status'] = "verified"
    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def register2(request):
    r = {}
    if request.method == "POST":
        username = request.POST['username']  # password
        filterResult = MyUser.objects.filter(username=username)
        if len(filterResult) > 0:  # username already exists
            r['success'] = 0
            r['username'] = username
            response = HttpResponse(json.dumps(r), content_type="application/json")
            return response
        else:
            password = request.POST['password']
            email = request.POST['email']
            gender = request.POST['gender']
            contact = request.POST['contact']
            unit = request.POST['company']
            #
            user = MyUser.objects.create_user(username=username, email=email, password=password, gender=gender,
                                              contact=contact, unit=unit, authLevel=1)
            user.is_active = True  # ?????
            user.save()
            #
            r["success"] = 1
            r["username"] = username
            r["email"] = email
            r["password"] = password
            r["gender"] = gender
            r["contact"] = contact
            r["company"] = unit
            r["authLevel"] = 1
            response = HttpResponse(json.dumps(r), content_type="application/json")
            return response
    else:
        return "nothing happened"


@csrf_exempt
def login2(request):
    if request.method == "POST":

        # input_code = request.session['checkcode'].upper()
        username = request.POST['username']  # uf.cleaned_data['username']
        password = request.POST['password']  # uf.cleaned_data['password']
        print(username, password)
        # checkcode = uf.cleaned_data['checkcode'].upper()
        r = {}

        user = auth.authenticate(username=username, password=password)
        if user is not None and user.is_active:
            #
            auth.login(request, user)
            #
            r["username"] = username
            r["authLevel"] = user.authLevel

            # <2017-05-12>
            r["usersex"] = user.gender
            r["usermail"] = user.email
            r["userphone"] = user.contact
            r["position"] = user.unit
            # </2017-05-12>

            response = HttpResponse(json.dumps(r), content_type="application/json")
            response.set_cookie('username', username, 3600)
            return response
        else:
            r["username"] = username
            r["authLevel"] = 0
            response = HttpResponse(json.dumps(r), content_type="application/json")
            return response

    else:
        return HttpResponse("nothing happened")


def logout(request):
    nm = request.COOKIES.get('username')
    response = render_to_response('Success.html',
                                  {'operation': "退�?", 'username': nm},
                                  context_instance=RequestContext(request))
    response.delete_cookie('username')
    #
    auth.logout(request)
    #
    return response


# <2017-05-12>

@csrf_exempt
def changePwd(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['oldPsw']
        newPassword = request.POST['newPsw']

        r = {}

        user = auth.authenticate(username=username, password=password)
        if user is not None and user.is_active:

            newuser = MyUser.objects.get(username=username)
            if newuser is not None:
                newuser.set_password(newPassword)
                newuser.save()

                r["rst"] = 1

                response = HttpResponse(json.dumps(r), content_type="application/json")
                response.set_cookie('username', username, 3600)
                return response
            else:
                r["rst"] = -1

                response = HttpResponse(json.dumps(r), content_type="application/json")
                return response
        else:
            r["rst"] = 0
            response = HttpResponse(json.dumps(r), content_type="application/json")
            return response

    else:
        return HttpResponse("nothing happened")

    '''if request.method == "POST":

        username = request.POST['username']
        password = request.POST['oldPsw']
        newPassword = request.POST['newPsw']

        f = open("/usr/local/security-system-server/security_system/tests/nmb.txt", "w")
        f.write(username)
        f.write(password)
        f.write(newPassword)
        f.close()

        r = {"username": username, "oldPsw": password, "newPsw": newPassword}
        response = HttpResponse(json.dumps(r), content_type="application/json")


        #response.set_cookie('username', username, 3600)
        return response

    else:
        return HttpResponse("nothing happened")'''

    '''r = {"username": 1, "oldPsw": 2}
    response = HttpResponse(json.dumps(r), content_type="application/json")


    #response.set_cookie('username', username, 3600)
    return response'''


# </2017-05-12>

# -------------------------------------------------------------------------------------------------------------------
@csrf_exempt
def omg(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        return HttpResponse(username + password)
    else:
        return HttpResponse("nothing happened")


def addUser(request):
    user = MyUser.objects.create_user(username="aaaaaa",
                                      email="123@123.com",
                                      password="password",
                                      gender=0, contact="12345678910", unit="buaa", authLevel=1
                                      # 1 is the lowest
                                      )
    user.is_active = True  #
    user.save()

    response = HttpResponse("username aaaaaa password password")
    return response


def addUser1(request):
    user = MyUser.objects.create_user(username="bbbbbb",
                                      email="123@123.com",
                                      password="bbbbbb",
                                      gender=0, contact="12345678910", unit="buaa", authLevel=1
                                      # 1 is the lowest
                                      )
    user.is_active = True  #
    user.save()

    response = HttpResponse("username bbbbbb password bbbbbb")
    return response
    # 总结一下：第一，修改models.py, 第二，修改settings.py(末尾加的两句)�?第三，view.py中所有的User改为MyUser
