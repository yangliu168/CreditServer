import scoring

def caculate_user_scores(user_index:dict):
    try:
        result = scoring.get_result(user_index)
        print(result)
    except Exception as e:
        print(e)
    return result


