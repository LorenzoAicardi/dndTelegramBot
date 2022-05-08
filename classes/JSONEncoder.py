from json import JSONEncoder


class MyEncoder(JSONEncoder):
    def default(self, obj):
        return obj.__dict__

    # def from_json(json_object):
    #    if 'fname' in json_object:
    #        return (json_object['fname'])