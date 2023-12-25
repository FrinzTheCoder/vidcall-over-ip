# This file purpose is to encode/decode
import json

# function to encode payload
# return: encoded data in bytes
def encode(type, content):
    json_to_dump = {'type':type, 'content':content}
    json_string = json.dumps(json_to_dump)
    encoded_data = json_string.encode('utf-8')
    return encoded_data

# function to decode payload
# return: decoded data in 2-tuple (type, content)
def decode(encoded_data):
    json_string = encoded_data.decode('utf-8')
    decoded_data = json.loads(json_string)
    type = decoded_data['type']
    content = decoded_data['content']
    return (type, content)