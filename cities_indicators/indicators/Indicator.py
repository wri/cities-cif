from indicators.indicator_cache import IndicatorCache


class Indicator:
    def __init__(self, indicator_cache=IndicatorCache()):
        self.indicator_cache = IndicatorCache()

    def calculate(self, indicator, city):
        # TODO check if in global cache
        # else, calculate indicator
        # save to global cache and return result

        indicator.calculate(city)
