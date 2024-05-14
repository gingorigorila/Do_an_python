
from email import message
from django.shortcuts import render,redirect,HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.generic import View
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from .utils import TokenGenerator,generate_token
from django.utils.encoding import force_bytes,force_str,DjangoUnicodeDecodeError
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import authenticate,login,logout
# Create your views here.
def handlelogin(request):
    if request.method=="POST":

     username=request.POST['email']
     pwd=request.POST['pass1']
     myuser=authenticate(username=username,password=pwd)

     if myuser is not None:
      login(request,myuser)
      messages.success(request,"Đăng nhập thành công")
      return redirect("/")
     else:
      messages.error(request,"Tài khoản hoặc mật khẩu không đúng")
      return redirect("/auth/login")    
    return render(request,'login.html')

def signUp(request):
    if request.method=="POST":
        email=request.POST['email']
        pwd=request.POST['pass1']
        confirm_pwd=request.POST['pass2']
        if pwd != confirm_pwd:
         messages.error(request,"Mật khẩu với xác nhận mật khẩu khác nhau")
         return render(request,"signup.html") 
         
        try:  
         if User.objects.get(username=email):
          messages.info(request,"Email đã được sử dụng")
          return render(request,"signup.html")
        except Exception as identifier:
            pass
        user = User.objects.create_user(email,email,pwd)
        user.is_active=True
        user.save()
        email_subject="Kích hoạt tài khoản của bạn"
        message=render_to_string('active.html',{
            'user':user,
            'domain':'127.0.0.1:8000',
            'uid':urlsafe_base64_encode(force_bytes(user.pk)),
            'token':generate_token.make_token(user)
        })

        
        # messages.success(request,f"Kich hoat tai khoan cua ban bang cach nhan link trong email cua ban")
        return redirect('/auth/login')   
    return render(request,"signup.html")

class ActiveAccountView(View):
    def get(self,request,uidb64,token):
        try:
            uid=force_str(urlsafe_base64_decode(uidb64))
            user=User.objects.get(pk=uid)
        except Exception as identifier:
            user=None
        if user is not None and generate_token.check_token(user,token):
            user.is_active=True
            user.save()
            messages.info(request,"Tai khoan duoc kich hoac thanh cong")
            return redirect('/auth/login')
        return render(request,'activefail.html')
def logOut(request):
    logout(request)
    messages.info(request,"Đăng xuất thành công")
    return redirect('/auth/login')

class RequestResetEmailView(View):
    def get(self,request):
        return render(request,'request-reset-email.html')
    
    def post(self,request):
        email=request.POST['email']
        user=User.objects.filter(email=email)

        if user.exists():
            email_subject='[Reset your pwd]'
            message=render_to_string('reset-user-password.html',{
                'domain':'127.0.0.1:8000',
                'uid':urlsafe_base64_encode(force_bytes(user[0].pk)),
                'token':PasswordResetTokenGenerator().make_token(user[0])
            })

            messages.info(request,f"Chúng tôi đã gửi bạn email hướng dẫn reset mật khẩu {message}")
            return render(request,'request-reset-email.html')

class SetNewPasswordView(View):
    def get(self,request,uidb64,token):
        context = {
            'uidb64':uidb64,
            'token':token
        }
        try:
            user_id=force_str(urlsafe_base64_decode(uidb64))
            user=User.objects.get(pk=user_id)

            if not PasswordResetTokenGenerator().check_token(user,token):
                messages.warning(request,"Link reset password hop le")
                return render(request,'request-reset-email.html')
        
        except DjangoUnicodeDecodeError as identifier:
            pass

        return render(request,'set-new-password.html',context)
    
    def post(self,request,uidb64,token):
        context={
            'uidb64':uidb64,
            'token':token
        }
        password=request.POST['pass1']
        confirm_pwd=request.POST['pass2']
        if password!=confirm_pwd:
            messages.warning(request,"Pwd khong dung")
            return render(request,'set-new-password.html',context)
        
        try:
            user_id=force_str(urlsafe_base64_decode(uidb64))
            user=User.objects.get(pk=user_id)
            user.set_password(password)
            user.save()
            messages.success(request,"Pwd reset thanh cong")
            return redirect('/auth/login')
        
        except DjangoUnicodeDecodeError as identifier:
            messages.error(request,"Có lỗi")
            return render(request,'set-new-password.html',context)
        
        