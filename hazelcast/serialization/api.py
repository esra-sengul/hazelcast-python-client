"""
User API for Serialization.
"""
import typing

from hazelcast.serialization.portable.classdef import FieldType


class ObjectDataOutput:
    """ObjectDataOutput provides an interface to convert any of primitive types or arrays of them to series of bytes and
    write them on a stream.
    """

    def write_from(self, buff: bytearray, offset: int = None, length: int = None) -> None:
        """Writes the content of the buffer to this output stream.

        Args:
            buff: Input buffer.
            offset: Offset of the buffer where copy begin.
            length: Length of data to be copied from the offset into stream.
        """
        raise NotImplementedError()

    def write_boolean(self, val: bool) -> None:
        """Writes a bool value to this output stream.

        Single byte value 1 represent True, 0 represent False

        Args:
            val: The bool to be written.
        """
        raise NotImplementedError()

    def write_byte(self, val: int) -> None:
        """Writes a byte value to this output stream.

        Args:
            val: The byte value to be written.
        """
        raise NotImplementedError()

    def write_short(self, val: int) -> None:
        """Writes a short value to this output stream.

        Args:
            val: The short value to be written.
        """
        raise NotImplementedError()

    def write_char(self, val: str) -> None:
        """Writes a char value to this output stream.

        Args:
            val: The char value to be written.
        """
        raise NotImplementedError()

    def write_int(self, val: int) -> None:
        """Writes an int value to this output stream.

        Args:
            val: The int value to be written.
        """
        raise NotImplementedError()

    def write_long(self, val: int) -> None:
        """Writes a long value to this output stream.

        Args:
            val: The long value to be written.
        """
        raise NotImplementedError()

    def write_float(self, val: float) -> None:
        """Writes a float value to this output stream.

        Args:
            val: The float value to be written.
        """
        raise NotImplementedError()

    def write_double(self, val: float) -> None:
        """Writes a double value to this output stream.

        Args:
            val: The double value to be written.
        """
        raise NotImplementedError()

    def write_bytes(self, val: str) -> None:
        """Writes a string to this output stream.

        Args:
            val: The string to be written.
        """
        raise NotImplementedError()

    def write_chars(self, val: str) -> None:
        """Writes every character of string to this output stream.

        Args:
            val: The string to be written.
        """
        raise NotImplementedError()

    def write_string(self, val: str) -> None:
        """Writes UTF-8 string to this output stream.

        Args:
            val: The UTF-8 string to be written.
        """
        raise NotImplementedError()

    def write_utf(self, val: str) -> None:
        """Writes UTF-8 string to this output stream.

        .. deprecated:: 4.1
            This method is deprecated and will be removed in the
            next major version. Use :func:`write_string` instead.

        Args:
            val: The UTF-8 string to be written.
        """
        raise NotImplementedError()

    def write_byte_array(self, val: bytearray) -> None:
        """Writes a byte array to this output stream.

        Args:
            val: The byte array to be written.
        """
        raise NotImplementedError()

    def write_boolean_array(self, val: typing.Sequence[bool]) -> None:
        """Writes a bool array to this output stream.

        Args:
            val: The bool array to be written.
        """
        raise NotImplementedError()

    def write_char_array(self, val: typing.Sequence[str]) -> None:
        """Writes a char array to this output stream.

        Args:
            val: The char array to be written.
        """
        raise NotImplementedError()

    def write_int_array(self, val: typing.Sequence[int]) -> None:
        """Writes a int array to this output stream.

        Args:
            val: The int array to be written.
        """
        raise NotImplementedError()

    def write_long_array(self, val: typing.Sequence[int]) -> None:
        """Writes a long array to this output stream.

        Args:
            val: The long array to be written.
        """
        raise NotImplementedError()

    def write_double_array(self, val: typing.Sequence[float]) -> None:
        """Writes a double array to this output stream.

        Args:
            val: The double array to be written.
        """
        raise NotImplementedError()

    def write_float_array(self, val: typing.Sequence[float]) -> None:
        """Writes a float array to this output stream.

        Args:
            val: The float array to be written.
        """
        raise NotImplementedError()

    def write_short_array(self, val: typing.Sequence[int]) -> None:
        """Writes a short array to this output stream.

        Args:
            val: The short array to be written.
        """
        raise NotImplementedError()

    def write_string_array(self, val: typing.Sequence[str]) -> None:
        """Writes a UTF-8 String array to this output stream.

        Args:
            val: The UTF-8 String array to be written.
        """
        raise NotImplementedError()

    def write_utf_array(self, val: typing.Sequence[str]) -> None:
        """Writes a UTF-8 String array to this output stream.

        .. deprecated:: 4.1
            This method is deprecated and will be removed in the
            next major version. Use :func:`write_string_array` instead.

        Args:
            val: The UTF-8 String array to be written.
        """
        raise NotImplementedError()

    def write_object(self, val: typing.Any) -> None:
        """Writes an object to this output stream.

        Args:
            val: The object to be written.
        """
        raise NotImplementedError()

    def to_byte_array(self) -> bytearray:
        """Returns a copy of internal byte array.

        Returns:
            The copy of internal byte array
        """
        raise NotImplementedError()

    def get_byte_order(self) -> str:
        """Returns the order of bytes, as BIG_ENDIAN or LITTLE_ENDIAN."""
        raise NotImplementedError()


class ObjectDataInput:
    """ObjectDataInput provides an interface to read bytes from a stream and
    reconstruct it to any of primitive types or arrays of them.
    """

    def read_into(self, buff: bytearray, offset: int = None, length: int = None) -> bytearray:
        """Reads the content of the buffer into an array of bytes.

        Args:
            buff: Input buffer.
            offset: Offset of the buffer where the read begin.
            length: Length of data to be read.

        Returns:
            The read data.
        """
        raise NotImplementedError()

    def skip_bytes(self, count: int) -> int:
        """Skips over given number of bytes from input stream.

        Args:
            count: Number of bytes to be skipped.

        Returns:
            The actual number of bytes skipped.
        """
        raise NotImplementedError()

    def read_boolean(self) -> bool:
        """Reads 1 byte from input stream and convert it to a bool value.

        Returns:
            The bool value read.
        """
        raise NotImplementedError()

    def read_byte(self) -> int:
        """Reads 1 byte from input stream and returns it.

        Returns:
            The byte value read.
        """
        raise NotImplementedError()

    def read_unsigned_byte(self) -> int:
        """Reads 1 byte from input stream, zero-extends it and returns.

        Returns:
            The unsigned byte value read.
        """
        raise NotImplementedError()

    def read_short(self) -> int:
        """Reads 2 bytes from input stream and returns a short value.

        Returns:
            The short value read.
        """
        raise NotImplementedError()

    def read_unsigned_short(self) -> int:
        """Reads 2 bytes from input stream and returns an int value.

        Returns:
            The unsigned short value read.
        """
        raise NotImplementedError()

    def read_char(self) -> str:
        """Reads 2 bytes from the input stream and returns a str value.

        Returns:
            The char value read.
        """
        raise NotImplementedError()

    def read_int(self) -> int:
        """Reads 4 bytes from input stream and returns an int value.

        Returns:
            The int value read.
        """
        raise NotImplementedError()

    def read_long(self) -> int:
        """Reads 8 bytes from input stream and returns a long value.

        Returns:
            The int value read.
        """
        raise NotImplementedError()

    def read_float(self) -> float:
        """Reads 4 bytes from input stream and returns a float value.

        Returns:
            The float value read.
        """
        raise NotImplementedError()

    def read_double(self) -> float:
        """Reads 8 bytes from input stream and returns a double value.

        Returns:
            The double value read.
        """
        raise NotImplementedError()

    def read_string(self) -> str:
        """Reads a UTF-8 string from input stream and returns it.

        Returns:
            The UTF-8 string read.
        """
        raise NotImplementedError()

    def read_utf(self) -> str:
        """Reads a UTF-8 string from input stream and returns it.

        .. deprecated:: 4.1
            This method is deprecated and will be removed in the
            next major version. Use :func:`read_string` instead.

        Returns:
            The UTF-8 string read.
        """
        raise NotImplementedError()

    def read_byte_array(self) -> bytearray:
        """Reads a byte array from input stream and returns it.

        Returns:
            The byte array read.
        """
        raise NotImplementedError()

    def read_boolean_array(self) -> typing.List[bool]:
        """Reads a bool array from input stream and returns it.

        Returns:
            The bool array read.
        """
        raise NotImplementedError()

    def read_char_array(self) -> typing.List[str]:
        """Reads a char array from input stream and returns it.

        Returns:
            The char array read.
        """
        raise NotImplementedError()

    def read_int_array(self) -> typing.List[int]:
        """Reads a int array from input stream and returns it.

        Returns:
            The int array read.
        """
        raise NotImplementedError()

    def read_long_array(self) -> typing.List[int]:
        """Reads a long array from input stream and returns it.

        Returns:
            The long array read.
        """
        raise NotImplementedError()

    def read_double_array(self) -> typing.List[float]:
        """Reads a double array from input stream and returns it.

        Returns:
            The double array read.
        """
        raise NotImplementedError()

    def read_float_array(self) -> typing.List[float]:
        """Reads a float array from input stream and returns it.

        Returns:
            The float array read.
        """
        raise NotImplementedError()

    def read_short_array(self) -> typing.List[int]:
        """Reads a short array from input stream and returns it.

        Returns:
            The short array read.
        """
        raise NotImplementedError()

    def read_string_array(self) -> typing.List[str]:
        """Reads a UTF-8 string array from input stream and returns it.

        Returns:
            The UTF-8 string array read.
        """
        raise NotImplementedError()

    def read_utf_array(self) -> typing.List[str]:
        """Reads a UTF-8 string array from input stream and returns it.

        .. deprecated:: 4.1
            This method is deprecated and will be removed in the
            next major version. Use :func:`read_string_array` instead.

        Returns:
            The UTF-8 string array read.
        """
        raise NotImplementedError()

    def read_object(self) -> typing.Any:
        """Reads an object from input stream and returns it.

        Returns:
            The object read.
        """
        raise NotImplementedError()

    def get_byte_order(self) -> str:
        """Returns the order of bytes, as BIG_ENDIAN or LITTLE_ENDIAN."""
        raise NotImplementedError()

    def position(self) -> int:
        """Returns current position in buffer.

        Returns:
            Current position in buffer.
        """
        raise NotImplementedError()

    def size(self) -> int:
        """Returns size of buffer.

        Returns:
            Size of buffer.
        """
        raise NotImplementedError()


class IdentifiedDataSerializable:
    """IdentifiedDataSerializable is an alternative serialization method to
    Python pickle, which also avoids reflection during de-serialization.

    Each IdentifiedDataSerializable is created by a registered
    DataSerializableFactory.
    """

    def write_data(self, object_data_output: ObjectDataOutput) -> None:
        """Writes object fields to output stream.

        Args:
            object_data_output: The output.
        """
        raise NotImplementedError(
            "read_data must be implemented to serialize this IdentifiedDataSerializable"
        )

    def read_data(self, object_data_input: ObjectDataInput) -> None:
        """Reads fields from the input stream.

        Args:
            object_data_input: The input.
        """
        raise NotImplementedError(
            "read_data must be implemented to deserialize this IdentifiedDataSerializable"
        )

    def get_factory_id(self) -> int:
        """Returns DataSerializableFactory factory id for this class.

        Returns:
            The factory id.
        """
        raise NotImplementedError(
            "This method must return the factory ID for this IdentifiedDataSerializable"
        )

    def get_class_id(self) -> int:
        """Returns type identifier for this class. Id should be unique per
        DataSerializableFactory.

        Returns:
            The type id.
        """
        raise NotImplementedError(
            "This method must return the class ID for this IdentifiedDataSerializable"
        )


class Portable:
    """Portable provides an alternative serialization method.

    Instead of relying on reflection, each Portable is created by a registered PortableFactory.
    Portable serialization has the following advantages:

    - Support multiversion of the same object type.
    - Fetching individual fields without having to rely on reflection.
    - Querying and indexing support without de-serialization and/or reflection.
    """

    def write_portable(self, writer: "PortableWriter") -> None:
        """Serialize this portable object using given PortableWriter.

        Args:
            writer: The PortableWriter.
        """
        raise NotImplementedError()

    def read_portable(self, reader: "PortableReader") -> None:
        """Read portable fields using PortableReader.

        Args:
            reader: The PortableReader.
        """
        raise NotImplementedError()

    def get_factory_id(self) -> int:
        """Returns PortableFactory id for this portable class

        Returns:
            The factory id.
        """
        raise NotImplementedError()

    def get_class_id(self) -> int:
        """Returns class identifier for this portable class. Class id should
        be unique per PortableFactory.

        Returns:
            The class id.
        """
        raise NotImplementedError()


class StreamSerializer:
    """A base class for custom serialization."""

    def write(self, out: ObjectDataOutput, obj: typing.Any) -> None:
        """Writes object to ObjectDataOutput

        Args:
            out: Stream that object will be written to.
            obj: The object to be written.
        """
        raise NotImplementedError("write method must be implemented")

    def read(self, inp: ObjectDataInput) -> typing.Any:
        """Reads object from objectDataInputStream

        Args:
            inp: Stream that object will read from.

        Returns:
            The read object.
        """
        raise NotImplementedError("write method must be implemented")

    def get_type_id(self) -> int:
        """Returns typeId of serializer.

        Returns:
            The type id of the serializer.
        """
        raise NotImplementedError("get_type_id must be implemented")

    def destroy(self) -> None:
        """Called when instance is shutting down.

        It can be used to clear used resources.
        """
        raise NotImplementedError()


class PortableReader:
    """Provides a mean of reading portable fields from binary in form of
    Python primitives and arrays of these primitives, nested portable fields
    and array of portable fields.
    """

    def get_version(self) -> int:
        """Returns the global version of portable classes.

        Returns:
            Global version of portable classes.
        """
        raise NotImplementedError()

    def has_field(self, field_name: str) -> bool:
        """Determine whether the field name exists in this portable class or
        not.

        Args:
            field_name: name of the field (does not support nested paths).

        Returns:
            ``True`` if the field name exists in class, ``False`` otherwise.
        """
        raise NotImplementedError()

    def get_field_names(self) -> typing.Set[str]:
        """Returns the set of field names on this portable class.

        Returns:
            Set of field names on this portable class.
        """
        raise NotImplementedError()

    def get_field_type(self, field_name: str) -> FieldType:
        """Returns the field type of given field name.

        Args:
            field_name: Name of the field.

        Returns:
            The field type.
        """
        raise NotImplementedError()

    def get_field_class_id(self, field_name: str) -> int:
        """Returns the class id of given field.

        Args:
          field_name: Name of the field.

        Returns:
            Class id of given field.
        """
        raise NotImplementedError()

    def read_int(self, field_name: str) -> int:
        """Reads a primitive int.

        Args:
            field_name: Name of the field.

        Returns:
            The int value read.
        """
        raise NotImplementedError()

    def read_long(self, field_name: str) -> int:
        """Reads a primitive long.

        Args:
            field_name: Name of the field.

        Returns:
            The long value read.
        """
        raise NotImplementedError()

    def read_string(self, field_name: str) -> str:
        """Reads a UTF-8 String.

        Args:
            field_name: Name of the field.

        Returns:
            The UTF-8 String read.
        """
        raise NotImplementedError()

    def read_utf(self, field_name: str) -> str:
        """Reads a UTF-8 String.

        .. deprecated:: 4.1
            This method is deprecated and will be removed in the
            next major version. Use :func:`read_string` instead.

        Args:
            field_name: Name of the field.

        Returns:
            The UTF-8 String read.
        """
        raise NotImplementedError()

    def read_boolean(self, field_name: str) -> bool:
        """Reads a primitive bool.

        Args:
            field_name: Name of the field.

        Returns:
            The bool value read.
        """
        raise NotImplementedError()

    def read_byte(self, field_name: str) -> int:
        """Reads a primitive byte.

        Args:
            field_name: Name of the field.

        Returns:
            The byte value read.
        """
        raise NotImplementedError()

    def read_char(self, field_name: str) -> str:
        """Reads a primitive char.

        Args:
            field_name: Name of the field.

        Returns:
            The char value read.
        """
        raise NotImplementedError()

    def read_double(self, field_name: str) -> float:
        """Reads a primitive double.

        Args:
            field_name: Name of the field.

        Returns:
            The double value read.
        """
        raise NotImplementedError()

    def read_float(self, field_name: str) -> float:
        """Reads a primitive float.

        Args:
            field_name: Name of the field.

        Returns:
            The float value read.
        """
        raise NotImplementedError()

    def read_short(self, field_name: str) -> int:
        """Reads a primitive short.

        Args:
            field_name: Name of the field.

        Returns:
            The short value read.
        """
        raise NotImplementedError()

    def read_portable(self, field_name: str) -> Portable:
        """Reads a portable.

        Args:
            field_name: Name of the field.

        Returns:
            The portable read.
        """
        raise NotImplementedError()

    def read_byte_array(self, field_name: str) -> bytearray:
        """Reads a primitive byte array.

        Args:
            field_name: Name of the field.

        Returns:
            The byte array read.
        """
        raise NotImplementedError()

    def read_boolean_array(self, field_name: str) -> typing.List[bool]:
        """Reads a primitive bool array.

        Args:
            field_name: Name of the field.

        Returns:
            The bool array read.
        """
        raise NotImplementedError()

    def read_char_array(self, field_name: str) -> typing.List[str]:
        """Reads a primitive char array.

        Args:
            field_name: Name of the field.

        Returns:
            The char array read.
        """
        raise NotImplementedError()

    def read_int_array(self, field_name: str) -> typing.List[int]:
        """Reads a primitive int array.

        Args:
            field_name: Name of the field.

        Returns:
            The int array read.
        """
        raise NotImplementedError()

    def read_long_array(self, field_name: str) -> typing.List[int]:
        """Reads a primitive long array.

        Args:
            field_name: Name of the field.

        Returns:
            The long array read.
        """
        raise NotImplementedError()

    def read_double_array(self, field_name: str) -> typing.List[float]:
        """Reads a primitive double array.

        Args:
            field_name: Name of the field.

        Returns:
            The double array read.
        """
        raise NotImplementedError()

    def read_float_array(self, field_name: str) -> typing.List[float]:
        """Reads a primitive float array.

        Args:
            field_name: Name of the field.

        Returns:
            The float array read.
        """
        raise NotImplementedError()

    def read_short_array(self, field_name: str) -> typing.List[int]:
        """Reads a primitive short array.

        Args:
            field_name: Name of the field.

        Returns:
            The short array read.
        """
        raise NotImplementedError()

    def read_string_array(self, field_name: str) -> typing.List[str]:
        """Reads a UTF-8 String array.

        Args:
            field_name: Name of the field.

        Returns:
            The UTF-8 String array read.
        """
        raise NotImplementedError()

    def read_utf_array(self, field_name: str) -> typing.List[str]:
        """Reads a UTF-8 String array.

        .. deprecated:: 4.1
            This method is deprecated and will be removed in the
            next major version. Use :func:`read_string_array` instead.

        Args:
            field_name: Name of the field.

        Returns:
            The UTF-8 String array read.
        """
        raise NotImplementedError()

    def read_portable_array(self, field_name: str) -> typing.List[Portable]:
        """Reads a portable array.

        Args:
            field_name: Name of the field.

        Returns:
            The portable array read.
        """
        raise NotImplementedError()

    def get_raw_data_input(self) -> ObjectDataInput:
        """After reading portable fields, one can read remaining fields in
        old fashioned way consecutively from the end of stream. After
        get_raw_data_input() called, no data can be read.

        Returns:
            The input.
        """
        raise NotImplementedError()


class PortableWriter:
    """Provides a mean of writing portable fields to a binary in form of
    Python primitives and arrays of these primitives, nested portable fields
    and array of portable fields.
    """

    def write_int(self, field_name: str, value: int) -> None:
        """Writes a primitive int.

        Args:
            field_name: Name of the field.
            value: Int value to be written.
        """
        raise NotImplementedError()

    def write_long(self, field_name: str, value: int) -> None:
        """Writes a primitive long.

        Args:
            field_name: Name of the field.
            value: Long value to be written.
        """
        raise NotImplementedError()

    def write_string(self, field_name: str, value: str) -> None:
        """Writes an UTF string.

        Args:
            field_name: Name of the field.
            value: UTF string value to be written.
        """
        raise NotImplementedError()

    def write_utf(self, field_name: str, value: str) -> None:
        """Writes an UTF string.

        .. deprecated:: 4.1
            This method is deprecated and will be removed in the
            next major version. Use :func:`write_string` instead.

        Args:
            field_name: Name of the field.
            value: UTF string value to be written.
        """
        raise NotImplementedError()

    def write_boolean(self, field_name: str, value: bool) -> None:
        """Writes a primitive bool.

        Args:
            field_name: Name of the field.
            value: Bool value to be written.
        """
        raise NotImplementedError()

    def write_byte(self, field_name: str, value: int) -> None:
        """Writes a primitive byte.

        Args:
            field_name: Name of the field.
            value: Byte value to be written.
        """
        raise NotImplementedError()

    def write_char(self, field_name: str, value: str) -> None:
        """Writes a primitive char.

        Args:
            field_name: Name of the field.
            value: Char value to be written.
        """
        raise NotImplementedError()

    def write_double(self, field_name: str, value: float) -> None:
        """Writes a primitive double.

        Args:
            field_name: Name of the field.
            value: Double value to be written.
        """
        raise NotImplementedError()

    def write_float(self, field_name: str, value: float) -> None:
        """Writes a primitive float.

        Args:
            field_name: Name of the field.
            value: Float value to be written.
        """
        raise NotImplementedError()

    def write_short(self, field_name: str, value: int) -> None:
        """Writes a primitive short.

        Args:
            field_name: Name of the field.
            value: Short value to be written.
        """
        raise NotImplementedError()

    def write_portable(self, field_name: str, portable: Portable) -> None:
        """Writes a Portable.

        Args:
            field_name: Name of the field.
            portable: Portable to be written.
        """
        raise NotImplementedError()

    def write_null_portable(self, field_name: str, factory_id: int, class_id: int) -> None:
        """To write a null portable value, user needs to provide class and
        factory ids of related class.

        Args:
            field_name: Name of the field.
            factory_id: Factory id of related portable class.
            class_id: Class id of related portable class.
        """
        raise NotImplementedError()

    def write_byte_array(self, field_name: str, values: bytearray) -> None:
        """Writes a primitive byte array.

        Args:
            field_name: Name of the field.
            values: Bytearray to be written.
        """
        raise NotImplementedError()

    def write_boolean_array(self, field_name: str, values: typing.Sequence[bool]) -> None:
        """Writes a primitive bool array.

        Args:
            field_name: Name of the field.
            values: Bool array to be written.
        """
        raise NotImplementedError()

    def write_char_array(self, field_name: str, values: typing.Sequence[str]) -> None:
        """Writes a primitive char array.

        Args:
            field_name: Name of the field.
            values: Char array to be written.
        """
        raise NotImplementedError()

    def write_int_array(self, field_name: str, values: typing.Sequence[int]) -> None:
        """Writes a primitive int array.

        Args:
            field_name: Name of the field.
            values: Int array to be written.
        """
        raise NotImplementedError()

    def write_long_array(self, field_name: str, values: typing.Sequence[int]) -> None:
        """Writes a primitive long array.

        Args:
            field_name: Name of the field.
            values: Long array to be written.
        """
        raise NotImplementedError()

    def write_double_array(self, field_name: str, values: typing.Sequence[float]) -> None:
        """Writes a primitive double array.

        Args:
            field_name: Name of the field.
            values: Double array to be written.
        """
        raise NotImplementedError()

    def write_float_array(self, field_name: str, values: typing.Sequence[float]) -> None:
        """Writes a primitive float array.

        Args:
            field_name: Name of the field.
            values: Float array to be written.
        """
        raise NotImplementedError()

    def write_short_array(self, field_name: str, values: typing.Sequence[int]) -> None:
        """Writes a primitive short array.

        Args:
            field_name: Name of the field.
            values: Short array to be written.
        """
        raise NotImplementedError()

    def write_string_array(self, field_name: str, values: typing.Sequence[str]) -> None:
        """Writes a UTF-8 String array.

        Args:
            field_name: Name of the field.
            values: UTF-8 String array to be written.
        """
        raise NotImplementedError()

    def write_utf_array(self, field_name: str, values: typing.Sequence[str]) -> None:
        """Writes a UTF-8 String array.

        .. deprecated:: 4.1
            This method is deprecated and will be removed in the
            next major version. Use :func:`write_string_array` instead.

        Args:
            field_name: Name of the field.
            values: UTF-8 String array to be written.
        """
        raise NotImplementedError()

    def write_portable_array(self, field_name: str, values: typing.Sequence[Portable]) -> None:
        """Writes a portable array.

        Args:
            field_name: Name of the field.
            values: Portable array to be written.
        """
        raise NotImplementedError()

    def get_raw_data_output(self) -> ObjectDataOutput:
        """After writing portable fields, one can write remaining fields in
        old fashioned way consecutively at the end of stream. After
        get_raw_data_output() called, no data can be written.

        Returns:
            The output.
        """
        raise NotImplementedError()
