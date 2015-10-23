__author__ = 'c7h'


class BaseState(object):
    def __repr__(self):
        return "<State %s>" % self.__class__.__name__.lower()


class Ruhend(BaseState):
    pass


class Laufend(BaseState):
    pass


class Wartend(BaseState):
    pass


class Bereit(BaseState):
    pass


class State(object):
    I = Ruhend()
    W = Wartend()
    L = Laufend()
    B = Bereit()