from marshmallow import *
from typing import List, Mapping, Any
from marshmallow.exceptions import ValidationError
from marshmallow.validate import OneOf, Range
import ipaddress

class UnionField(fields.Field):
    """Field that deserializes multi-type input data to app-level objects."""

    def __init__(self, val_types: List[fields.Field]):
        self.valid_types = val_types
        super().__init__()

    def _deserialize(
        self, value: Any, attr: str = None, data: Mapping[str, Any] = None, **kwargs
    ):
        """
        _deserialize defines a custom Marshmallow Schema Field that takes in mutli-type input data to
        app-level objects.

        Parameters
        ----------
        value : {Any}
            The value to be deserialized.

        Keyword Parameters
        ----------
        attr : {str} [Optional]
            The attribute/key in data to be deserialized. (default: {None})
        data : {Optional[Mapping[str, Any]]}
            The raw input data passed to the Schema.load. (default: {None})

        Raises
        ----------
        ValidationError : Exception
            Raised when the validation fails on a field or schema.
        """
        errors = []
        # iterate through the types being passed into UnionField via val_types
        for field in self.valid_types:
            try:
                # inherit deserialize method from Fields class
                return field.deserialize(value, attr, data, **kwargs)
            # if error, add error message to error list
            except ValidationError as error:
                errors.append(error.messages)
        raise ValidationError(errors)

class IPv4Str(fields.IP):
    default_error_messages = {"invalid_ip": "Not a valid IPv4 address."}
    DESERIALIZATION_CLASS = ipaddress.IPv4Address

    def _deserialize(
        self, value, attr, data, **kwargs
    ) -> str | None:
        if value is None:
            return None
        try:
            return ipaddress.IPv4Address(
                fields.ensure_text_type(value)
            ).__str__()
        except (ValueError, TypeError) as error:
            raise self.make_error("invalid_ip") from error

class ExposeConfig(Schema):
    validate = []
    """Generic configuration related to an exposed port or host"""

    """
    Protocol used to expose the service, can be either
    tcp: expose a tcp port
    udp: expose a udp port
    icmp: expose all icmp traffic
    any: expose any traffic
    """
    protocol = fields.String(
        required=True,
        validate=OneOf(["tcp", "udp", "icmp", "any"]),
    )

    port = UnionField(
        [
            fields.Integer(validate=Range(0, 65535)),
            fields.List(fields.Integer(validate=Range(0, 65535))),
        ],
    )
    address = IPv4Str(
        required=True,
    )
    redirectAddress = IPv4Str(
        required=True,
    )
    redirectPort = UnionField(
        [
            fields.Integer(validate=Range(0, 65535)),
            fields.List(fields.Integer(validate=Range(0, 65535))),
        ],
    )
    masquerade = fields.Boolean(missing=False)

    @validates_schema
    def validate_ports_property(self, data, **kwargs):
        errors = {}

        # Check that, if the port property presences is consistent
        if ('redirectPort' in data) != ('port' in data):
            errors["redirectPort"] = errors["port"] = ValidationError(
                "inconsistent 'port' or 'redirectPort' property, both of them must either be there of missing"
            )
            raise ValidationError(errors)
        
        has_ports = 'port' in data
        is_port_protocol = data["protocol"] in ["tcp", "udp"]
        
        # Check that the ports values are no null if the protocol is tcp or udp
        if is_port_protocol and not has_ports:
            errors["redirectPort"] = errors["port"] = ValidationError(
                "this value must not be null since the protocol is udp or tcp"
            )
            raise ValidationError(errors)
        
        if has_ports:
            # Check that the ports values are null if the protocol is not tcp or udp
            if not is_port_protocol:
                errors["redirectPort"] = errors["port"] = ValidationError(
                    "this value must be null since the protocol is not tcp or udp"
                )
                raise ValidationError(errors)
            
            # We check that the datatypes are the same
            if type(data["redirectPort"]) != type(data["port"]):
                errors["redirectPort"] = errors["port"] = ValidationError(
                    "the redirectPort and port field must be of the same datatype"
                )
                raise ValidationError(errors)
            is_using_arrays = type(data["redirectPort"]) == type([])
            
            if (
                is_port_protocol
                and is_using_arrays
                and len(data["port"]) != len(data["redirectPort"])
            ):
                errors["redirectPort"] = errors["port"] = ValidationError(
                    "this length of the ports array must be equal"
                )
                raise ValidationError(errors)

class FirewallConfig(Schema):
    overrideMemberId = fields.Integer(allow_none=True)
    expose = fields.List(fields.Nested(ExposeConfig))
