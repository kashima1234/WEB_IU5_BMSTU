from django.conf import settings
from django.core.management.base import BaseCommand
from minio import Minio

from .utils import *
from app.models import *


def add_users():
    User.objects.create_user("user", "user@user.com", "1234", first_name="user", last_name="user")
    User.objects.create_superuser("root", "root@root.com", "1234", first_name="root", last_name="root")

    for i in range(1, 10):
        User.objects.create_user(f"user{i}", f"user{i}@user.com", "1234", first_name=f"user{i}", last_name=f"user{i}")
        User.objects.create_superuser(f"root{i}", f"root{i}@root.com", "1234", first_name=f"user{i}", last_name=f"user{i}")


def add_places():
    Place.objects.create(
        name="Ставангер (Норвегия)",
        description="Ставангер был важным торговым и кораблестроительным центром на юго-западном побережье Норвегии. Город играл ключевую роль в викингских мореплаваниях и торговле.",
        square=71,
        image="1.png"
    )

    Place.objects.create(
        name="Альта (Норвегия)",
        description="Альта, расположенная в северной части Норвегии, известна своими наскальными рисунками и служила базой для экспедиций в Арктические регионы.",
        square=500,
        image="2.png"
    )

    Place.objects.create(
        name="Бирка (Швеция)",
        description="Бирка был важным торговым центром викингов, расположенным на острове в озере Меларен. Город играл ключевую роль в торговых путях викингов.",
        square=300,
        image="3.png"
    )

    Place.objects.create(
        name="Гардарики (Россия)",
        description="Гардарики, расположенный на территории современной России, был важным торговым центром на пути викингов к Византии и Восточной Европе.",
        square=1200,
        image="4.png"
    )

    Place.objects.create(
        name="Лунд (Швеция)",
        description="Лунд был одним из первых викингских городов и важным центром вероисповедания. Город известен своими историческими памятниками и археологическими находками.",
        square=26,
        image="5.png"
    )

    Place.objects.create(
        name="Рейкьявик (Исландия)",
        description="Рейкьявик был основан викингами и со временем стал столицей Исландии. Город стал важным центром для викингов и их потомков.",
        square=275,
        image="6.png"
    )

    client = Minio(settings.MINIO_ENDPOINT,
                   settings.MINIO_ACCESS_KEY,
                   settings.MINIO_SECRET_KEY,
                   secure=settings.MINIO_USE_HTTPS)

    for i in range(1, 7):
        client.fput_object(settings.MINIO_MEDIA_FILES_BUCKET, f'{i}.png', f"app/static/images/{i}.png")

    client.fput_object(settings.MINIO_MEDIA_FILES_BUCKET, 'default.png', "app/static/images/default.png")


def add_expeditions():
    users = User.objects.filter(is_staff=False)
    moderators = User.objects.filter(is_staff=True)
    places = Place.objects.all()

    for _ in range(30):
        status = random.randint(2, 5)
        owner = random.choice(users)
        add_expedition(status, places, owner, moderators)

    add_expedition(1, places, users[0], moderators)
    add_expedition(2, places, users[0], moderators)
    add_expedition(3, places, users[0], moderators)
    add_expedition(4, places, users[0], moderators)
    add_expedition(5, places, users[0], moderators)


def add_expedition(status, places, owner, moderators):
    expedition = Expedition.objects.create()
    expedition.status = status

    if status in [3, 4]:
        expedition.moderator = random.choice(moderators)
        expedition.date_complete = random_date()
        expedition.date_formation = expedition.date_complete - random_timedelta()
        expedition.date_created = expedition.date_formation - random_timedelta()
    else:
        expedition.date_formation = random_date()
        expedition.date_created = expedition.date_formation - random_timedelta()

    if status == 3:
        expedition.date = random_date()

    expedition.viking = "Рагнар Лодброк"

    expedition.owner = owner

    i = 1
    for place in random.sample(list(places), 3):
        item = PlaceExpedition(
            expedition=expedition,
            place=place,
            order=i
        )
        i += 1
        item.save()

    expedition.save()


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        add_users()
        add_places()
        add_expeditions()
