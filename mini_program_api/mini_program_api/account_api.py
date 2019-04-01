from django.http import JsonResponse

import json
import requests
from . import util
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from dbTables.models import User
from hashlib import sha1
from .util import WXBizDataCrypt


@require_GET
def code2id(request):
    url = util.GETSESSIONKEY + request.GET["code"]
    r = requests.get(url, verify=False)
    if r.status_code == 200:
        r = r.json()
        # try:
        User.objects.get_or_create(openId=r["openid"])
        update = User.objects.get(openId=r["openid"])
        update.session_key = r["session_key"]
        update.save()
        response = JsonResponse(util.get_json_dict(data={"sessionId": update.id}), charset="utf-8")
        return response
        # except:
    response = JsonResponse(util.get_json_dict(err_code=1, message="code2id failed", data={}))
    return response


@csrf_exempt
@require_POST
def update_user(request):
    request.POST = json.loads(request.body.decode('utf-8'))
    sessionId = request.POST["sessionId"]
    # try:
    User.objects.filter(id=int(sessionId)).update(avatarUrl=request.POST["avatarUrl"], city=request.POST["city"]
                                                  , country=request.POST["country"],
                                                  province=request.POST["province"]
                                                  , gender=request.POST["gender"],
                                                  nickname=request.POST["nickName"])
    return JsonResponse(util.get_json_dict())


# except:
# return JsonResponse(util.get_json_dict(err_code=1, message="update_user failed", data={}))

@csrf_exempt
@require_POST
def check_with_session_key(request):
    request.POST = json.loads(request.body.decode('utf-8'))
    sessionId = request.POST["sessionId"]
    session_key = User.object.filter(id=int(sessionId))
    signature2 = sha1(request.POST["rawData"], session_key)
    if signature2 == request.POST["signature"]:
        return JsonResponse(util.get_json_dict(data={"valid_user": True}))
    else:
        return JsonResponse(util.get_json_dict(data={"valid_user": False}))


