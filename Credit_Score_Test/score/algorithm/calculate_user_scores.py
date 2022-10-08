from . import scoring


def calculate_user_scores(user_index: dict):
    try:
        result = scoring.get_result(user_index)
    except Exception as e:
        print(e)
        # TODO raise exception
        return 0
    return result
