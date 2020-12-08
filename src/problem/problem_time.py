def convert_hhmm_to_seconds(hhmm):
    time_arr = hhmm.split(':')
    seconds = (int(time_arr[0]) * 3600) + (int(time_arr[1]) * 60)
    return seconds


class ProblemTime:
    def __init__(self, hhmm: str, default_hhmm: str = '00:00'):
        time_str = hhmm
        if hhmm is None:
            time_str = default_hhmm
        self.hhmm = time_str
        self.seconds = convert_hhmm_to_seconds(time_str)
