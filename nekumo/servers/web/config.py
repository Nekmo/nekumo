from nekumo.conf import Config, IntegerField, ListParser


class WebConfig(Config):
    # ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"]
    default = {
        "availability": ["0.0.0.0"],
        "port": 7070,
    }
    schema = {
        'availability': ListParser,
        'port': IntegerField(),
    }
