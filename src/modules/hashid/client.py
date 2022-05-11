from hashids import Hashids

from .exceptions import InvalidHash, InvalidObjectWithID


class HashidsClient:
    def __init__(self, salt: str, min_length: int = 0):
        self.hashids = Hashids(salt, min_length=min_length)

    def encode(self, num: int) -> str:
        return self.hashids.encode(num)

    def decode(self, hash_id: str) -> int:
        try:
            return self.hashids.decode(hash_id)[0]
        except IndexError:
            raise InvalidHash()

    def encode_obj(self, obj, fields: list[str] = ["id"]):
        invalid_fields = []
        try:
            for field in fields:
                setattr(obj, field, self.encode(getattr(obj, field)))
        except AttributeError:
            invalid_fields.append(field)

        if invalid_fields:
            raise InvalidObjectWithID(
                f"{obj} doesn't have required attributes to be hashed: {invalid_fields}"
            )

        return obj
