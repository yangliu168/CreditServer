import json
from .config import Config


map_value = Config.map_value
value_dict = Config.value_dict
d_index = Config.d_index
d_info = Config.d_info
raw_value = Config.raw_value
# para_dic = Config.para_dic

score_dict = {}
sub_score = {}
scoreNew = {}
final = {}
k_dic = {}


# Scoring sub_index according to the return_value.
def get_score(key1, key2):
    score = value_dict.get(key1).get(key2)
    score_dict[key1] = score
    return score_dict


# Calculating total scores for each dimension.
def dimension_sum(input_dict):
    for key in d_index.keys():
        total = 0
        for m in d_index.get(key):
            total += input_dict.get(m)
            sub_score[key] = total
            sub_score['life'] = raw_value

    return sub_score


# Using Min-Max Normalization scale the data between 0 and 1000.
def map_score(input_dict):
    for key in input_dict.keys():
        score = input_dict.get(key)
        max_value = d_info.get(key)['max']
        score_new = score * map_value / max_value
        scoreNew[key] = score_new
    return scoreNew


# Calculating the final score.
def get_final(input_dict):
    total = 0
    for key, value in input_dict.items():
        weight = d_info.get(key)['weight']
        total += value * weight
        final[key] = value
        final['credit_score'] = total
        final['corporate'] = 0
    return final


# Reformat output data.
def format_data(input_dict):
    for name in input_dict.keys():
        # k_dic = {'name': name, 'data': int(input_dict.get(name))}
        k_dic[name] = int(input_dict.get(name))
        # output.append(k_dic)
    result = json.dumps(k_dic, ensure_ascii=False)
    return result


# From request parameter to final output, main function.
def get_result(input_dict):
    global score_dict
    for key, value in input_dict.items():
        score_dict = get_score(key, value)
    dimension_sum(score_dict)
    map_score(sub_score)
    get_final(scoreNew)
    return format_data(final)
