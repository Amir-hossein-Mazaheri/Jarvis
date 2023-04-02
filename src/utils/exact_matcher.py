def exact_matcher(data: str):
    def exact_matcher_action(callback_data: str):
        return data == callback_data

    return exact_matcher_action
