class MissingRequiredConfigException(Exception):
    def __init__(self, config_arg):
        msg = f'Releasify unable to start. `{config_arg}` is not set'
        super(MissingRequiredConfigException, self).__init__(msg)
