import random
import re


def roll(roll_string):
    """roll dice
    Args:
        (str) dice_string (example: "1d20+4")
    Return:
        (tuple)
            - (int) sum - final result of rolls and modifier
            - (list of int) rolls - dice roll results
            - (str) modifier - parsed modifier
    """
    matched_groups = re.match("(\d+)d(\d+)([\+|\-]\d+)?", roll_string)
    dice_count = matched_groups.groups()[0]
    dice_type = matched_groups.groups()[1]
    dice_modifier = matched_groups.groups('+0')[2]  # use "+0" in default if not matched
    dice_results = []
    for _ in range(int(dice_count)):
        dice_results.append(random.randint(1, int(dice_type)))
    dice_sum = sum(dice_results) + int(dice_modifier)
    return (dice_sum, dice_results, dice_modifier)
