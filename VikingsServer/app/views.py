from django.shortcuts import render

places = [
    {
        "id": 1,
        "name": "Ставангер (Норвегия)",
        "description": "Ставангер был важным торговым и кораблестроительным центром на юго-западном побережье Норвегии. Город играл ключевую роль в викингских мореплаваниях и торговле.",
        "square": 71,
        "image": "http://localhost:9000/images/1.png"
    },
    {
        "id": 2,
        "name": "Альта (Норвегия)",
        "description": "Альта, расположенная в северной части Норвегии, известна своими наскальными рисунками и служила базой для экспедиций в Арктические регионы.",
        "square": 500,
        "image": "http://localhost:9000/images/2.png"
    },
    {
        "id": 3,
        "name": "Бирка (Швеция)",
        "description": "Бирка был важным торговым центром викингов, расположенным на острове в озере Меларен. Город играл ключевую роль в торговых путях викингов.",
        "square": 300,
        "image": "http://localhost:9000/images/3.png"
    },
    {
        "id": 4,
        "name": "Гардарики (Россия)",
        "description": "Гардарики, расположенный на территории современной России, был важным торговым центром на пути викингов к Византии и Восточной Европе.",
        "square": 1200,
        "image": "http://localhost:9000/images/4.png"
    },
    {
        "id": 5,
        "name": "Лунд (Швеция)",
        "description": "Лунд был одним из первых викингских городов и важным центром вероисповедания. Город известен своими историческими памятниками и археологическими находками.",
        "square": 25.75,
        "image": "http://localhost:9000/images/5.png"
    },
    {
        "id": 6,
        "name": "Рейкьявик (Исландия)",
        "description": "Рейкьявик был основан викингами и со временем стал столицей Исландии. Город стал важным центром для викингов и их потомков.",
        "square": 274.5,
        "image": "http://localhost:9000/images/6.png"
    }
]

draft_expedition = {
    "id": 123,
    "status": "Черновик",
    "date_created": "12 сентября 2024г",
    "lead": "Рагнар Лодброк",
    "places": [
        {
            "id": 1,
            "count": 2
        },
        {
            "id": 2,
            "count": 4
        },
        {
            "id": 3,
            "count": 1
        }
    ]
}


def getPlaceById(place_id):
    for place in places:
        if place["id"] == place_id:
            return place


def getPlaces():
    return places


def searchPlaces(place_name):
    res = []

    for place in places:
        if place_name.lower() in place["name"].lower():
            res.append(place)

    return res


def getDraftExpedition():
    return draft_expedition


def getExpeditionById(expedition_id):
    return draft_expedition


def index(request):
    place_name = request.GET.get("place_name", "")
    places = searchPlaces(place_name) if place_name else getPlaces()
    draft_expedition = getDraftExpedition()

    context = {
        "places": places,
        "place_name": place_name,
        "places_count": len(draft_expedition["places"]),
        "draft_expedition": draft_expedition
    }

    return render(request, "home_page.html", context)


def place(request, place_id):
    context = {
        "id": place_id,
        "place": getPlaceById(place_id),
    }

    return render(request, "place_page.html", context)


def expedition(request, expedition_id):
    expedition = getExpeditionById(expedition_id)
    places = [
        {**getPlaceById(place["id"]), "count": place["count"]}
        for place in expedition["places"]
    ]

    context = {
        "expedition": expedition,
        "places": places
    }

    return render(request, "expedition_page.html", context)
