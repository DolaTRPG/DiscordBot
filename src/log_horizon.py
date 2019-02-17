import requests


def replace_full_type_word(message):
    replacement = {
        "０": "0",
        "１": "1",
        "２": "2",
        "３": "3",
        "４": "4",
        "５": "5",
        "６": "6",
        "７": "7",
        "８": "8",
        "９": "9",
        "Ｄ": "D"
    }
    for key in replacement:
        message = message.replace(key, replacement[key])
    return message


def get_skills(player_id):
    character = requests.get("https://lhrpg.com/lhz/api/{}.json".format(player_id)).json()
    skills = {}
    for skill in character['skills']:
        if skill['timing'] == "常時":
            continue
        if skill['timing'] not in skills:
            skills[skill['timing']] = []
        skills[skill['timing']].append(skill)

    response = ""
    for timing in skills:
        response += "{}\n".format(timing)
        for skill in skills[timing]:
            description = skill['function'].replace("ＳＲ", str(skill['skill_rank']))\
                                           .replace("【魔力】", str(character['magic_attack']))
            description = replace_full_type_word(description)
            response += "{}: {}: {}: {} {}\n".format(skill['id'], skill['name'], skill['cost'], skill['tags'], description)
        response += "\n"
    return response
