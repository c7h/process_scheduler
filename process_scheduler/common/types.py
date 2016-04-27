__author__ = 'Christoph Gerneth'


class SingletonType(type):
    def __call__(self, *args, **kwargs):
        try:
            return self.__instance
        except AttributeError:
            self.__instance = super(SingletonType, self).__call__(*args, **kwargs)
            return self.__instance

    def _drop(self):
        """Drop the instance (for testing purposes)."""
        self.__instance = None
        del (self._SingletonType__instance)


class ProcessTerminatedMessage(Warning):
    def __init__(self, *args, **kwargs):
        self.last_section = kwargs.get("last_section")
        super(ProcessTerminatedMessage, self).__init__(*args)
