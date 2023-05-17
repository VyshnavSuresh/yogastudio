from django.shortcuts import redirect


class User_Authentication:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response
    def process_view(self,request,view_fun,view_args,view_kwargs):
        print(view_fun.__name__)
        views=["index","Login","Register","insrtructorregistration","Studentregistration","activate","login","Password_reset","forgotpassword","Passwdemail"]
        if view_fun.__name__ in views:
            pass
        else:
            if request.user.is_authenticated==False:
                return redirect('yogaapp:login')
        if request.user.is_authenticated:
            if view_fun.__name__ in ["Studentregistration","Login","insrtructorregistration"]:
                return redirect("/")

