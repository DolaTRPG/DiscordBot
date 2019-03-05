import requests


def filter_skills(skills):
    """remove unnecessary skills and filter columns
    Args:
        (list) skills: skill list
    Return:
        (list) filtered skills
    """
    result = []
    columns = ["name", "skill_rank", "timing", "roll", "target", "range", "cost", "limit", "function"]
    for s in skills:
        if s["timing"] == "常時":
            continue
        skill = {}
        for c in columns:
            skill[c] = s[c]
        result.append(skill)
    return result


def generate_roll20_macros(skills):
    """convert skills into macros
    Args:
        (list) skills
    Return:
        (list) macros
    """
    ability_macros = []
    for skill in skills:
        tmp = "&{template:default}"
        tmp += roll20_macro_tag("name", skill["name"])

        if skill["limit"] != "－":
            skill["limit"] = skill["limit"].replace("[SR]", str(skill["skill_rank"]))
            tmp += roll20_macro_tag("限制", skill["limit"])

        tmp += roll20_macro_tag("時機", skill["timing"])

        if skill["cost"] != "－":
            skill["cost"] = skill["cost"].replace("ヘイト", "")
            tmp += roll20_macro_tag("仇恨", skill["cost"])

        if skill["range"] != "至近":
            tmp += roll20_macro_tag("射程", skill["range"])

        if skill["target"] == "単体":
            tmp += roll20_macro_tag("對象", "@{target|token_name}")
        else:
            tmp += roll20_macro_tag("對象", skill["target"])

        if skill["roll"] not in ["判定なし", "自動成功"]:
            if "命中" in skill["roll"]:
                tmp += roll20_macro_tag("命中", "[[@{selected|命中}]]")
            if "回避" in skill["roll"]:
                tmp += roll20_macro_tag("迴避", "[[@{target|迴避}]]")
            if "抵抗" in skill["roll"]:
                tmp += roll20_macro_tag("抵抗", "[[@{target|抵抗}]]")

        tmp += "\n" + skill["function"]
        ability_macros.append(tmp)
    return ability_macros


def roll20_macro_tag(key, value):
    """generate string for macro tags
    Args:
        (str) key: macro key
        (str) value: macro value
    Return:
        (str) macro string
    """
    return "{{" + str(key) + "=" + str(value) + "}}"


def get_skill_macros(player_id):
    character = requests.get("https://lhrpg.com/lhz/api/{}.json".format(player_id)).json()
    skills = filter_skills(character["skills"])
    macros = generate_roll20_macros(skills)
    response = "```"
    for macro in macros:
        response += macro + "\n\n"
    response += "```"
    return response
