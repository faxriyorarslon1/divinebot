#     mp = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
#     city = serializers.PrimaryKeyRelatedField(queryset=City.objects.all())
#     lpu = serializers.PrimaryKeyRelatedField(queryset=Hospital.objects.all())
#     doctor = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all())
#     comment = serializers.CharField(max_length=500)
#     preparation = serializers.IntegerField()
#     communication = serializers.IntegerField()
#     the_need = serializers.IntegerField()
#     presentation = serializers.IntegerField()
#     protest = serializers.IntegerField()
#     agreement = serializers.IntegerField()
#     analysis = serializers.IntegerField()
import json

import requests

from api.users import BASE


def check_mp_create_vizit(mp=None,
                          city=None,
                          lpu=None,
                          doctor=None,
                          comment=None,
                          preparation=None,
                          communication=None,
                          the_need=None,
                          presentation=None,
                          protest=None,
                          agreement=None,
                          analysis=None,
                          token=None):
    url = f"{BASE}/check_mp/create_vizit/"
    payload = requests.post(url=url, data=json.dumps({"mp": mp, 'city': city, 'lpu': lpu,
                                                      'doctor': doctor, 'comment': comment,
                                                      'preparation': preparation, 'communication': communication,
                                                      'the_need': the_need, 'presentation': presentation,
                                                      'protest': protest, 'agreement': agreement, 'analysis': analysis
                                                      }),
                            headers={'Content-Type': 'Application/json', "Authorization": f"Token {token}"},
                            verify=False)
    return json.loads(payload.text)


def check_mp_create_pharmacy(mp=None,
                             city=None,
                             pharmacy=None,
                             comment=None,
                             preparation=None,
                             communication=None,
                             the_need=None,
                             presentation=None,
                             protest=None,
                             agreement=None,
                             analysis=None,
                             token=None):
    url = f"{BASE}/check_mp/create_pharmacy/"
    payload = requests.post(url=url, data=json.dumps({"mp": mp, 'city': city, 'pharmacy': pharmacy, 'comment': comment,
                                                      'preparation': preparation, 'communication': communication,
                                                      'the_need': the_need, 'presentation': presentation,
                                                      'protest': protest, 'agreement': agreement, 'analysis': analysis
                                                      }),
                            headers={'Content-Type': 'Application/json', "Authorization": f"Token {token}"},
                            verify=False)
    return json.loads(payload.text)
