from django.db.models import Q
from django.http import HttpResponse, JsonResponse

from rest_framework.authtoken.models import Token
from app.models import MODEL
from news.models import News as NewsRequest


def check_header_token_auth(request):
    if request.user.is_authenticated:
        return request.user
    if "HTTP_AUTHORIZATION" in request.META:
        auth = request.META["HTTP_AUTHORIZATION"].split()
        if len(auth) == 2:
            if auth[0].lower() == "token":
                try:
                    token = Token.objects.select_related("user").get(key=auth[1])
                    if not token.user.is_active:
                        return False
                except:
                    return False
                return token.user
    return False


def media_access(request, path):
    """
    When trying to access :
    myproject.com/media/uploads/passport.png

    If access is authorized, the request will be redirected to
    myproject.com/protected/media/uploads/passport.png

    This special URL will be handle by nginx we the help of X-Accel
    """

    has_permission = False
    query = Q(
        Q(voice__file=path)
        | Q(photo__file=path)
        | Q(video__file=path)
        | Q(document__file=path)
    )
    news_query = Q(Q(thumbnail=path) | Q(file__file=path))

    user = check_header_token_auth(request)
    if user:
        if user.is_staff and str(path).startswith("tmp/"):
            response = HttpResponse()
            del response["Content-Type"]
            response["X-Accel-Redirect"] = "/protected/media/" + path
            return response

        if MODEL.objects.filter(query).exists():
            tmp = MODEL.objects.filter(query).last()
            if user == tmp.user:
                has_permission = True
        elif NewsRequest.objects.filter(news_query).exists():
            # Public imges
            has_permission = True
        else:
            return JsonResponse(
                status=400, data={"error": "File Not Found Or Permission Denied"}
            )

        if user.is_superuser or user.is_staff or has_permission:
            response = HttpResponse()
            del response["Content-Type"]
            response["X-Accel-Redirect"] = "/protected/media/" + path
            return response

        return JsonResponse(
            status=400, data={"error": "File Not Found Or Permission Denied"}
        )

    return JsonResponse(
        status=400, data={"error": "File Not Found Or Permission Denied"}
    )
