import itertools
import typing

from hazelcast.aggregator import Aggregator
from hazelcast.config import IndexUtil, IndexType, IndexConfig
from hazelcast.core import SimpleEntryView
from hazelcast.future import combine_futures, ImmediateFuture, Future
from hazelcast.invocation import Invocation
from hazelcast.projection import Projection
from hazelcast.protocol import PagingPredicateHolder
from hazelcast.protocol.codec import (
    map_add_entry_listener_codec,
    map_add_entry_listener_to_key_codec,
    map_add_entry_listener_with_predicate_codec,
    map_add_entry_listener_to_key_with_predicate_codec,
    map_clear_codec,
    map_contains_key_codec,
    map_contains_value_codec,
    map_delete_codec,
    map_entry_set_codec,
    map_entries_with_predicate_codec,
    map_evict_codec,
    map_evict_all_codec,
    map_flush_codec,
    map_force_unlock_codec,
    map_get_codec,
    map_get_all_codec,
    map_get_entry_view_codec,
    map_is_empty_codec,
    map_is_locked_codec,
    map_key_set_codec,
    map_key_set_with_predicate_codec,
    map_load_all_codec,
    map_load_given_keys_codec,
    map_lock_codec,
    map_put_codec,
    map_put_all_codec,
    map_put_if_absent_codec,
    map_put_transient_codec,
    map_size_codec,
    map_remove_codec,
    map_remove_if_same_codec,
    map_remove_entry_listener_codec,
    map_replace_codec,
    map_replace_if_same_codec,
    map_set_codec,
    map_try_lock_codec,
    map_try_put_codec,
    map_try_remove_codec,
    map_unlock_codec,
    map_values_codec,
    map_values_with_predicate_codec,
    map_add_interceptor_codec,
    map_aggregate_codec,
    map_aggregate_with_predicate_codec,
    map_project_codec,
    map_project_with_predicate_codec,
    map_execute_on_all_keys_codec,
    map_execute_on_key_codec,
    map_execute_on_keys_codec,
    map_execute_with_predicate_codec,
    map_add_near_cache_invalidation_listener_codec,
    map_add_index_codec,
    map_set_ttl_codec,
    map_entries_with_paging_predicate_codec,
    map_key_set_with_paging_predicate_codec,
    map_values_with_paging_predicate_codec,
    map_put_with_max_idle_codec,
    map_put_if_absent_with_max_idle_codec,
    map_put_transient_with_max_idle_codec,
    map_set_with_max_idle_codec,
    map_remove_interceptor_codec,
)
from hazelcast.proxy.base import (
    Proxy,
    EntryEvent,
    EntryEventType,
    get_entry_listener_flags,
    MAX_SIZE,
)
from hazelcast.predicate import PagingPredicate, Predicate
from hazelcast.types import AggregatorResultType, KeyType, ValueType, ProjectionType
from hazelcast.util import (
    check_not_none,
    thread_id,
    to_millis,
    ImmutableLazyDataList,
    IterationType,
)


EntryEventCallable = typing.Callable[[EntryEvent[KeyType, ValueType]], None]


class Map(Proxy["BlockingMap"], typing.Generic[KeyType, ValueType]):
    """Hazelcast Map client proxy to access the map on the cluster.

    Concurrent, distributed, observable and queryable map. This map can work
    both async(non-blocking) or sync(blocking). Blocking calls return the value
    of the call and block the execution until return value is calculated.
    However, async calls return ``Future`` and do not block execution. Result
    of the ``Future`` can be used whenever ready. A ``Future``'s result can be
    obtained with blocking the execution by calling ``future.result()``.

    Example:
        >>> my_map = client.get_map("my_map").blocking()  # sync map, all operations are blocking
        >>> print("map.put", my_map.put("key", "value"))
        >>> print("map.contains_key", my_map.contains_key("key"))
        >>> print("map.get", my_map.get("key"))
        >>> print("map.size", my_map.size())

    Example:
        >>> my_map = client.get_map("map")  # async map, all operations are non-blocking
        >>> def put_callback(f):
        >>>     print("map.put", f.result())
        >>> my_map.put("key", "async_val").add_done_callback(put_callback)
        >>>
        >>> print("map.size", my_map.size().result())
        >>>
        >>> def contains_key_callback(f):
        >>>     print("map.contains_key", f.result())
        >>> my_map.contains_key("key").add_done_callback(contains_key_callback)

    This class does not allow ``None`` to be used as a key or value.
    """

    def __init__(self, service_name, name, context):
        super(Map, self).__init__(service_name, name, context)
        self._reference_id_generator = context.lock_reference_id_generator

    def add_entry_listener(
        self,
        include_value: bool = False,
        key: KeyType = None,
        predicate: Predicate = None,
        added_func: EntryEventCallable = None,
        removed_func: EntryEventCallable = None,
        updated_func: EntryEventCallable = None,
        evicted_func: EntryEventCallable = None,
        evict_all_func: EntryEventCallable = None,
        clear_all_func: EntryEventCallable = None,
        merged_func: EntryEventCallable = None,
        expired_func: EntryEventCallable = None,
        loaded_func: EntryEventCallable = None,
    ) -> Future[str]:
        """Adds a continuous entry listener for this map.

        Listener will get notified for map events filtered with given
        parameters.

        Args:
            include_value: Whether received event should include the value or
                not.
            key: Key for filtering the events.
            predicate: Predicate for filtering the events.
            added_func: Function to be called when an entry is added to map.
            removed_func: Function to be called when an entry is removed from
                map.
            updated_func: Function to be called when an entry is updated.
            evicted_func: Function to be called when an entry is evicted from
                map.
            evict_all_func: Function to be called when entries are evicted
                from map.
            clear_all_func: Function to be called when entries are cleared
                from map.
            merged_func: Function to be called when WAN replicated entry is
                merged.
            expired_func: Function to be called when an entry's live time is
                expired.
            loaded_func: Function to be called when an entry is loaded from a
                map loader.

        Returns:
            A registration id which is used as a key to remove the listener.
        """
        flags = get_entry_listener_flags(
            ADDED=added_func,
            REMOVED=removed_func,
            UPDATED=updated_func,
            EVICTED=evicted_func,
            EXPIRED=expired_func,
            EVICT_ALL=evict_all_func,
            CLEAR_ALL=clear_all_func,
            MERGED=merged_func,
            LOADED=loaded_func,
        )

        if key and predicate:
            codec = map_add_entry_listener_to_key_with_predicate_codec
            key_data = self._to_data(key)
            predicate_data = self._to_data(predicate)
            request = codec.encode_request(
                self.name, key_data, predicate_data, include_value, flags, self._is_smart
            )
        elif key and not predicate:
            codec = map_add_entry_listener_to_key_codec
            key_data = self._to_data(key)
            request = codec.encode_request(
                self.name, key_data, include_value, flags, self._is_smart
            )
        elif not key and predicate:
            codec = map_add_entry_listener_with_predicate_codec
            predicate = self._to_data(predicate)
            request = codec.encode_request(
                self.name, predicate, include_value, flags, self._is_smart
            )
        else:
            codec = map_add_entry_listener_codec
            request = codec.encode_request(self.name, include_value, flags, self._is_smart)

        def handle_event_entry(
            key_, value, old_value, merging_value, event_type, uuid, number_of_affected_entries
        ):
            event = EntryEvent(
                self._to_object,
                key_,
                value,
                old_value,
                merging_value,
                event_type,
                uuid,
                number_of_affected_entries,
            )

            if event.event_type == EntryEventType.ADDED:
                added_func(event)
            elif event.event_type == EntryEventType.REMOVED:
                removed_func(event)
            elif event.event_type == EntryEventType.UPDATED:
                updated_func(event)
            elif event.event_type == EntryEventType.EVICTED:
                evicted_func(event)
            elif event.event_type == EntryEventType.EVICT_ALL:
                evict_all_func(event)
            elif event.event_type == EntryEventType.CLEAR_ALL:
                clear_all_func(event)
            elif event.event_type == EntryEventType.MERGED:
                merged_func(event)
            elif event.event_type == EntryEventType.EXPIRED:
                expired_func(event)
            elif event.event_type == EntryEventType.LOADED:
                loaded_func(event)

        return self._register_listener(
            request,
            lambda r: codec.decode_response(r),
            lambda reg_id: map_remove_entry_listener_codec.encode_request(self.name, reg_id),
            lambda m: codec.handle(m, handle_event_entry),
        )

    def add_index(
        self,
        attributes: typing.Sequence[str] = None,
        index_type: typing.Union[int, str] = IndexType.SORTED,
        name: str = None,
        bitmap_index_options: typing.Dict[str, typing.Any] = None,
    ) -> Future[None]:
        """Adds an index to this map for the specified entries so that queries
        can run faster.

        Example:
            Let's say your map values are Employee objects.

                >>> class Employee(IdentifiedDataSerializable):
                >>>     active = false
                >>>     age = None
                >>>     name = None
                >>>     #other fields
                >>>
                >>>     #methods

            If you query your values mostly based on age and active fields,
            you should consider indexing these.

                >>> employees = client.get_map("employees")
                >>> employees.add_index(attributes=["age"]) # Sorted index for range queries
                >>> employees.add_index(attributes=["active"], index_type=IndexType.HASH)) # Hash index for equality predicates

        Index attribute should either have a getter method or be public.
        You should also make sure to add the indexes before adding
        entries to this map.

        Indexing time is executed in parallel on each partition by operation
        threads. The Map is not blocked during this operation. The time taken
        in proportional to the size of the Map and the number Members.

        Until the index finishes being created, any searches for the attribute
        will use a full Map scan, thus avoiding using a partially built index
        and returning incorrect results.

        Args:
            attributes: List of indexed attributes.
            index_type: Type of the index. By default, set to ``SORTED``.
            name: Name of the index.
            bitmap_index_options: Bitmap index options.

                - **unique_key:** (str): The unique key attribute is used as a
                  source of values which uniquely identify each entry being
                  inserted into an index. Defaults to ``KEY_ATTRIBUTE_NAME``.
                  See the :class:`hazelcast.config.QueryConstants` for
                  possible values.
                - **unique_key_transformation** (int|str): The transformation
                  is applied to every value extracted from the unique key
                  attribue. Defaults to ``OBJECT``. See the
                  :class:`hazelcast.config.UniqueKeyTransformation` for
                  possible values.
        """
        d = {
            "name": name,
            "type": index_type,
            "attributes": attributes,
            "bitmap_index_options": bitmap_index_options,
        }
        config = IndexConfig.from_dict(d)
        validated = IndexUtil.validate_and_normalize(self.name, config)
        request = map_add_index_codec.encode_request(self.name, validated)
        return self._invoke(request)

    def add_interceptor(self, interceptor: typing.Any) -> Future[str]:
        """Adds an interceptor for this map.

        Added interceptor will intercept operations and execute user defined
        methods.

        Args:
            interceptor: Interceptor for the map which includes user defined
                methods.

        Returns:
            Id of registered interceptor.
        """
        interceptor_data = self._to_data(interceptor)

        request = map_add_interceptor_codec.encode_request(self.name, interceptor_data)
        return self._invoke(request, map_add_interceptor_codec.decode_response)

    def aggregate(
        self, aggregator: Aggregator[AggregatorResultType], predicate: Predicate = None
    ) -> Future[AggregatorResultType]:
        """Applies the aggregation logic on map entries and filter the result
        with the predicate, if given.

        Args:
            aggregator: Aggregator to aggregate the entries with.
            predicate: Predicate to filter the entries with.

        Returns:
            The result of the aggregation.
        """
        check_not_none(aggregator, "aggregator can't be none")
        aggregator_data = self._to_data(aggregator)

        if predicate:
            if isinstance(predicate, PagingPredicate):
                raise AssertionError("Paging predicate is not supported.")

            def handler(message):
                return self._to_object(map_aggregate_with_predicate_codec.decode_response(message))

            predicate_data = self._to_data(predicate)
            request = map_aggregate_with_predicate_codec.encode_request(
                self.name, aggregator_data, predicate_data
            )
            return self._invoke(request, handler)

        def handler(message):
            return self._to_object(map_aggregate_codec.decode_response(message))

        request = map_aggregate_codec.encode_request(self.name, aggregator_data)
        return self._invoke(request, handler)

    def clear(self) -> Future[None]:
        """Clears the map.

        The ``MAP_CLEARED`` event is fired for any registered listeners.
        """
        request = map_clear_codec.encode_request(self.name)
        return self._invoke(request)

    def contains_key(self, key: KeyType) -> Future[bool]:
        """Determines whether this map contains an entry with the key.

        Warning:
            This method uses ``__hash__`` and ``__eq__`` methods of binary form
            of the key, not the actual implementations of ``__hash__`` and
            ``__eq__`` defined in key's class.

        Args:
            key: The specified key.

        Returns:
            ``True`` if this map contains an entry for the specified key,
            ``False`` otherwise.
        """
        check_not_none(key, "key can't be None")
        key_data = self._to_data(key)
        return self._contains_key_internal(key_data)

    def contains_value(self, value: ValueType) -> Future[bool]:
        """Determines whether this map contains one or more keys for the
        specified value.

        Args:
            value: The specified value.

        Returns:
            ``True`` if this map contains an entry for the specified value,
            ``False`` otherwise.
        """
        check_not_none(value, "value can't be None")
        value_data = self._to_data(value)

        request = map_contains_value_codec.encode_request(self.name, value_data)
        return self._invoke(request, map_contains_value_codec.decode_response)

    def delete(self, key: KeyType) -> Future[None]:
        """Removes the mapping for a key from this map if it is present
        (optional operation).

        Unlike remove(object), this operation does not return the removed
        value, which avoids the serialization cost of the returned value.
        If the removed value will not be used, a delete operation is preferred
        over a remove operation for better performance.

        The map will not contain a mapping for the specified key once the call
        returns.

        Warning:
            This method breaks the contract of EntryListener.
            When an entry is removed by delete(), it fires an ``EntryEvent``
            with a ``None`` ``old_value``. Also, a listener with predicates
            will have ``None`` values, so only the keys can be queried
            via predicates.

        Args:
            key: Key of the mapping to be deleted.
        """
        check_not_none(key, "key can't be None")
        key_data = self._to_data(key)
        return self._delete_internal(key_data)

    def entry_set(
        self, predicate: Predicate = None
    ) -> Future[typing.List[typing.Tuple[KeyType, ValueType]]]:
        """Returns a list clone of the mappings contained in this map.

        Warning:
            The list is NOT backed by the map, so changes to the map are NOT
            reflected in the list, and vice-versa.

        Args:
            predicate: Predicate for the map to filter entries.

        Returns:
            The list of key-value tuples in the map.
        """
        if predicate:
            if isinstance(predicate, PagingPredicate):
                codec = map_entries_with_paging_predicate_codec

                def handler(message):
                    response = codec.decode_response(message)
                    predicate.anchor_list = response["anchor_data_list"].as_anchor_list(
                        self._to_object
                    )
                    return ImmutableLazyDataList(response["response"], self._to_object)

                predicate.iteration_type = IterationType.ENTRY
                holder = PagingPredicateHolder.of(predicate, self._to_data)
                request = codec.encode_request(self.name, holder)
            else:
                codec = map_entries_with_predicate_codec

                def handler(message):
                    return ImmutableLazyDataList(codec.decode_response(message), self._to_object)

                predicate_data = self._to_data(predicate)
                request = codec.encode_request(self.name, predicate_data)
        else:
            codec = map_entry_set_codec

            def handler(message):
                return ImmutableLazyDataList(codec.decode_response(message), self._to_object)

            request = codec.encode_request(self.name)

        return self._invoke(request, handler)

    def evict(self, key: KeyType) -> Future[bool]:
        """Evicts the specified key from this map.

        Warning:
            This method uses ``__hash__`` and ``__eq__`` methods of binary form
            of the key, not the actual implementations of ``__hash__`` and
            ``__eq__`` defined in key's class.

        Args:
            key: Key to evict.

        Returns:
            ``True`` if the key is evicted, ``False`` otherwise.
        """
        check_not_none(key, "key can't be None")
        key_data = self._to_data(key)
        return self._evict_internal(key_data)

    def evict_all(self) -> Future[None]:
        """Evicts all keys from this map except the locked ones.

        The ``EVICT_ALL`` event is fired for any registered listeners.
        """
        request = map_evict_all_codec.encode_request(self.name)
        return self._invoke(request)

    def execute_on_entries(
        self, entry_processor: typing.Any, predicate: Predicate = None
    ) -> Future[typing.List[typing.Any]]:
        """Applies the user defined EntryProcessor to all the entries in the
        map or entries in the map which satisfies the predicate if provided.
        Returns the results mapped by each key in the map.

        Args:
            entry_processor: A stateful serializable object which represents
                the EntryProcessor defined on server side. This object must
                have a serializable EntryProcessor counter part registered
                on server side with the actual
                ``com.hazelcast.map.EntryProcessor`` implementation.
            predicate: Predicate for filtering the entries.

        Returns:
            List of map entries which includes the keys and the results of the
            entry process.
        """
        if predicate:

            def handler(message):
                return ImmutableLazyDataList(
                    map_execute_with_predicate_codec.decode_response(message), self._to_object
                )

            entry_processor_data = self._to_data(entry_processor)
            predicate_data = self._to_data(predicate)
            request = map_execute_with_predicate_codec.encode_request(
                self.name, entry_processor_data, predicate_data
            )
        else:

            def handler(message):
                return ImmutableLazyDataList(
                    map_execute_on_all_keys_codec.decode_response(message), self._to_object
                )

            entry_processor_data = self._to_data(entry_processor)
            request = map_execute_on_all_keys_codec.encode_request(self.name, entry_processor_data)

        return self._invoke(request, handler)

    def execute_on_key(self, key: KeyType, entry_processor: typing.Any) -> Future[typing.Any]:
        """Applies the user defined EntryProcessor to the entry mapped by the
        key. Returns the object which is the result of EntryProcessor's
        process method.

        Args:
            key: Specified key for the entry to be processed.
            entry_processor: A stateful serializable object which represents
                the EntryProcessor defined on server side. This object must
                have a serializable EntryProcessor counter part registered on
                server side with the actual
                ``com.hazelcast.map.EntryProcessor`` implementation.

        Returns:
            Result of entry process.
        """
        check_not_none(key, "key can't be None")
        key_data = self._to_data(key)
        return self._execute_on_key_internal(key_data, entry_processor)

    def execute_on_keys(
        self, keys: typing.Sequence[KeyType], entry_processor: typing.Any
    ) -> Future[typing.List[typing.Any]]:
        """Applies the user defined EntryProcessor to the entries mapped by the
        collection of keys. Returns the results mapped by each key in the
        collection.

        Args:
            keys: Collection of the keys for the entries to be processed.
            entry_processor: A stateful serializable object which represents
                the EntryProcessor defined on server side. This object must
                have a serializable EntryProcessor counter part registered on
                server side with the actual
                ``com.hazelcast.map.EntryProcessor`` implementation.

        Returns:
            List of map entries which includes the keys and the results of the
            entry process.
        """
        key_list = []
        for key in keys:
            check_not_none(key, "key can't be None")
            key_list.append(self._to_data(key))

        if len(keys) == 0:
            return ImmediateFuture([])

        def handler(message):
            return ImmutableLazyDataList(
                map_execute_on_keys_codec.decode_response(message), self._to_object
            )

        entry_processor_data = self._to_data(entry_processor)
        request = map_execute_on_keys_codec.encode_request(
            self.name, entry_processor_data, key_list
        )
        return self._invoke(request, handler)

    def flush(self) -> Future[None]:
        """Flushes all the local dirty entries."""
        request = map_flush_codec.encode_request(self.name)
        return self._invoke(request)

    def force_unlock(self, key: KeyType) -> Future[None]:
        """Releases the lock for the specified key regardless of the lock
        owner.

        It always successfully unlocks the key, never blocks, and returns
        immediately.

        Warning:
            This method uses ``__hash__`` and ``__eq__`` methods of binary form
            of the key, not the actual implementations of ``__hash__`` and
            ``__eq__`` defined in key's class.

        Args:
            key: The key to lock.
        """
        check_not_none(key, "key can't be None")
        key_data = self._to_data(key)

        request = map_force_unlock_codec.encode_request(
            self.name, key_data, self._reference_id_generator.get_and_increment()
        )
        return self._invoke_on_key(request, key_data)

    def get(self, key: KeyType) -> Future[typing.Optional[ValueType]]:
        """Returns the value for the specified key, or ``None`` if this map
        does not contain this key.

        Warning:
            This method returns a clone of original value, modifying the
            returned value does not change the actual value in the map. One
            should put modified value back to make changes visible to all nodes.

                >>> value = my_map.get(key)
                >>> value.update_some_property()
                >>> my_map.put(key,value)

        Warning:
            This method uses ``__hash__`` and ``__eq__`` methods of binary form
            of the key, not the actual implementations of ``__hash__`` and
            ``__eq__`` defined in key's class.

        Args:
            key: The specified key.

        Returns:
            The value for the specified key.
        """
        check_not_none(key, "key can't be None")
        key_data = self._to_data(key)
        return self._get_internal(key_data)

    def get_all(self, keys: typing.Sequence[KeyType]) -> Future[typing.Dict[KeyType, ValueType]]:
        """Returns the entries for the given keys.

        Warning:
            The returned map is NOT backed by the original map, so changes to
            the original map are NOT reflected in the returned map, and
            vice-versa.

        Warning:
            This method uses ``__hash__`` and ``__eq__`` methods of binary form
            of the key, not the actual implementations of ``__hash__`` and
            ``__eq__`` defined in key's class.

        Args:
            keys: Keys to get.

        Returns:
            Dictionary of map entries.
        """
        check_not_none(keys, "keys can't be None")
        if not keys:
            return ImmediateFuture({})

        partition_service = self._context.partition_service
        partition_to_keys = {}

        for key in keys:
            check_not_none(key, "key can't be None")
            key_data = self._to_data(key)
            partition_id = partition_service.get_partition_id(key_data)
            try:
                partition_to_keys[partition_id][key] = key_data
            except KeyError:
                partition_to_keys[partition_id] = {key: key_data}

        return self._get_all_internal(partition_to_keys)

    def get_entry_view(self, key: KeyType) -> Future[SimpleEntryView[KeyType, ValueType]]:
        """Returns the EntryView for the specified key.

        Warning:
            This method returns a clone of original mapping, modifying the
            returned value does not change the actual value in the map. One
            should put modified value back to make changes visible to all
            nodes.

        Warning:
            This method uses ``__hash__`` and ``__eq__`` methods of binary form
            of the key, not the actual implementations of ``__hash__`` and
            ``__eq__`` defined in key's class.

        Args:
            key: The key of the entry.

        Returns:
            EntryView of the specified key.
        """
        check_not_none(key, "key can't be None")

        def handler(message):
            response = map_get_entry_view_codec.decode_response(message)
            entry_view = response["response"]
            if not entry_view:
                return None

            entry_view.key = self._to_object(entry_view.key)
            entry_view.value = self._to_object(entry_view.value)
            return entry_view

        key_data = self._to_data(key)
        request = map_get_entry_view_codec.encode_request(self.name, key_data, thread_id())
        return self._invoke_on_key(request, key_data, handler)

    def is_empty(self) -> Future[bool]:
        """Returns whether this map contains no key-value mappings or not.

        Returns:
            ``True`` if this map contains no key-value mappings, ``False``
            otherwise.
        """
        request = map_is_empty_codec.encode_request(self.name)
        return self._invoke(request, map_is_empty_codec.decode_response)

    def is_locked(self, key: KeyType) -> Future[bool]:
        """Checks the lock for the specified key.

        Warning:
            This method uses ``__hash__`` and ``__eq__`` methods of binary form
            of the key, not the actual implementations of ``__hash__`` and
            ``__eq__`` defined in key's class.

        Args:
            key: The key that is checked for lock

        Returns:
            ``True`` if lock is acquired, ``False`` otherwise.
        """
        check_not_none(key, "key can't be None")
        key_data = self._to_data(key)

        request = map_is_locked_codec.encode_request(self.name, key_data)
        return self._invoke_on_key(request, key_data, map_is_locked_codec.decode_response)

    def key_set(self, predicate: Predicate = None) -> Future[typing.List[ValueType]]:
        """Returns a List clone of the keys contained in this map or the keys
        of the entries filtered with the predicate if provided.

        Warning:
            The list is NOT backed by the map, so changes to the map are NOT
            reflected in the list, and vice-versa.

        Args:
            predicate: Predicate to filter the entries.

        Returns:
            A list of the clone of the keys.
        """
        if predicate:
            if isinstance(predicate, PagingPredicate):
                codec = map_key_set_with_paging_predicate_codec

                def handler(message):
                    response = codec.decode_response(message)
                    predicate.anchor_list = response["anchor_data_list"].as_anchor_list(
                        self._to_object
                    )
                    return ImmutableLazyDataList(response["response"], self._to_object)

                predicate.iteration_type = IterationType.KEY
                holder = PagingPredicateHolder.of(predicate, self._to_data)
                request = codec.encode_request(self.name, holder)
            else:
                codec = map_key_set_with_predicate_codec

                def handler(message):
                    return ImmutableLazyDataList(codec.decode_response(message), self._to_object)

                predicate_data = self._to_data(predicate)
                request = codec.encode_request(self.name, predicate_data)
        else:
            codec = map_key_set_codec

            def handler(message):
                return ImmutableLazyDataList(codec.decode_response(message), self._to_object)

            request = codec.encode_request(self.name)

        return self._invoke(request, handler)

    def load_all(
        self, keys: typing.Sequence[KeyType] = None, replace_existing_values: bool = True
    ) -> Future[None]:
        """Loads all keys from the store at server side or loads the given
        keys if provided.

        Args:
            keys: Keys of the entry values to load.
            replace_existing_values: Whether the existing values will be
                replaced or not with those loaded from the server side
                MapLoader.
        """
        if keys:
            key_data_list = list(map(self._to_data, keys))
            return self._load_all_internal(key_data_list, replace_existing_values)
        else:
            request = map_load_all_codec.encode_request(self.name, replace_existing_values)
            return self._invoke(request)

    def lock(self, key: KeyType, lease_time: float = None) -> Future[None]:
        """Acquires the lock for the specified key infinitely or for the
        specified lease time if provided.

        If the lock is not available, the current thread becomes disabled for
        thread scheduling purposes and lies dormant until the lock has been
        acquired.

        You get a lock whether the value is present in the map or not. Other
        threads (possibly on other systems) would block on their invoke of
        lock() until the non-existent key is unlocked. If the lock holder
        introduces the key to the map, the put() operation is not blocked. If
        a thread not holding a lock on the non-existent key tries to introduce
        the key while a lock exists on the non-existent key, the put()
        operation blocks until it is unlocked.

        Scope of the lock is this map only. Acquired lock is only for the key
        in this map.

        Locks are re-entrant; so, if the key is locked N times, it should be
        unlocked N times before another thread can acquire it.

        Warning:
            This method uses ``__hash__`` and ``__eq__`` methods of binary form
            of the key, not the actual implementations of ``__hash__`` and
            ``__eq__`` defined in key's class.

        Args:
            key: The key to lock.
            lease_time: Time in seconds to wait before releasing the lock.
        """
        check_not_none(key, "key can't be None")
        key_data = self._to_data(key)

        request = map_lock_codec.encode_request(
            self.name,
            key_data,
            thread_id(),
            to_millis(lease_time),
            self._reference_id_generator.get_and_increment(),
        )
        partition_id = self._context.partition_service.get_partition_id(key_data)
        invocation = Invocation(request, partition_id=partition_id, timeout=MAX_SIZE)
        self._invocation_service.invoke(invocation)
        return invocation.future

    def project(
        self, projection: Projection[ProjectionType], predicate: Predicate = None
    ) -> Future[ProjectionType]:
        """Applies the projection logic on map entries and filter the result
        with the predicate, if given.

        Args:
            projection: Projection to project the entries with.
            predicate: Predicate to filter the entries with.

        Returns:
            The result of the projection.
        """
        check_not_none(projection, "Projection can't be none")
        projection_data = self._to_data(projection)

        if predicate:
            if isinstance(predicate, PagingPredicate):
                raise AssertionError("Paging predicate is not supported.")

            def handler(message):
                return ImmutableLazyDataList(
                    map_project_with_predicate_codec.decode_response(message), self._to_object
                )

            predicate_data = self._to_data(predicate)
            request = map_project_with_predicate_codec.encode_request(
                self.name, projection_data, predicate_data
            )
            return self._invoke(request, handler)

        def handler(message):
            return ImmutableLazyDataList(
                map_project_codec.decode_response(message), self._to_object
            )

        request = map_project_codec.encode_request(self.name, projection_data)
        return self._invoke(request, handler)

    def put(
        self, key: KeyType, value: ValueType, ttl: float = None, max_idle: float = None
    ) -> Future[typing.Optional[ValueType]]:
        """Associates the specified value with the specified key in this map.

        If the map previously contained a mapping for the key, the old value is
        replaced by the specified value. If ttl is provided, entry will expire
        and get evicted after the ttl.

        Warning:
            This method returns a clone of the previous value, not the original
            (identically equal) value previously put into the map.

        Warning:
            This method uses ``__hash__`` and ``__eq__`` methods of binary form
            of the key, not the actual implementations of ``__hash__`` and
            ``__eq__`` defined in key's class.

        Args:
            key: The specified key.
            value: The value to associate with the key.
            ttl: Maximum time in seconds for this entry to stay in the map. If
                not provided, the value configured on the server side
                configuration will be used. Setting this to ``0`` means
                infinite time-to-live.
            max_idle: Maximum time in seconds for this entry to stay idle in
                the map. If not provided, the value configured on the server
                side configuration will be used. Setting this to ``0`` means
                infinite max idle time.

        Returns:
            Previous value associated with key or ``None`` if there was no
            mapping for key.
        """
        check_not_none(key, "key can't be None")
        check_not_none(value, "value can't be None")
        key_data = self._to_data(key)
        value_data = self._to_data(value)
        return self._put_internal(key_data, value_data, ttl, max_idle)

    def put_all(self, map: typing.Dict[KeyType, ValueType]) -> Future[None]:
        """Copies all the mappings from the specified map to this map.

        No atomicity guarantees are given. In the case of a failure, some
        key-value tuples may get written, while others are not.

        Args:
            map: Dictionary which includes mappings to be stored in this map.
        """
        check_not_none(map, "map can't be None")
        if not map:
            return ImmediateFuture(None)

        partition_service = self._context.partition_service
        partition_map = {}

        for key, value in map.items():
            check_not_none(key, "key can't be None")
            check_not_none(value, "value can't be None")
            entry = (self._to_data(key), self._to_data(value))
            partition_id = partition_service.get_partition_id(entry[0])
            try:
                partition_map[partition_id].append(entry)
            except KeyError:
                partition_map[partition_id] = [entry]

        futures = []
        for partition_id, entry_list in partition_map.items():
            request = map_put_all_codec.encode_request(
                self.name, entry_list, False
            )  # TODO trigger map loader
            future = self._invoke_on_partition(request, partition_id)
            futures.append(future)

        return combine_futures(futures)

    def put_if_absent(
        self, key: KeyType, value: ValueType, ttl: float = None, max_idle: float = None
    ) -> Future[typing.Optional[ValueType]]:
        """Associates the specified key with the given value if it is not
        already associated.

        If ttl is provided, entry will expire and get evicted after the ttl.

        This is equivalent to below, except that the action is performed
        atomically:

            >>> if not my_map.contains_key(key):
            >>>     return my_map.put(key,value)
            >>> else:
            >>>     return my_map.get(key)

        Warning:
            This method returns a clone of the previous value, not the original
            (identically equal) value previously put into the map.

        Warning:
            This method uses ``__hash__`` and ``__eq__`` methods of binary form
            of the key, not the actual implementations of ``__hash__`` and
            ``__eq__`` defined in key's class.

        Args:
            key: Key of the entry.
            value: Value of the entry.
            ttl: Maximum time in seconds for this entry to stay in the map. If
                not provided, the value configured on the server side
                configuration will be used. Setting this to ``0`` means
                infinite time-to-live.
            max_idle: Maximum time in seconds for this entry to stay idle in
                the map. If not provided, the value configured on the server
                side configuration will be used. Setting this to ``0`` means
                infinite max idle time.

        Returns:
            Old value of the entry.
        """
        check_not_none(key, "key can't be None")
        check_not_none(value, "value can't be None")

        key_data = self._to_data(key)
        value_data = self._to_data(value)
        return self._put_if_absent_internal(key_data, value_data, ttl, max_idle)

    def put_transient(
        self, key: KeyType, value: ValueType, ttl: float = None, max_idle: float = None
    ) -> Future[None]:
        """Same as ``put``, but MapStore defined at the server side will not
        be called.

        Warning:
            This method uses ``__hash__`` and ``__eq__`` methods of binary form
            of the key, not the actual implementations of ``__hash__`` and
            ``__eq__`` defined in key's class.

        Args:
            key: Key of the entry.
            value: Value of the entry.
            ttl: Maximum time in seconds for this entry to stay in the map. If
                not provided, the value configured on the server side
                configuration will be used. Setting this to ``0`` means
                infinite time-to-live.
            max_idle: Maximum time in seconds for this entry to stay idle in
                the map. If not provided, the value configured on the server
                side configuration will be used. Setting this to ``0`` means
                infinite max idle time.
        """
        check_not_none(key, "key can't be None")
        check_not_none(value, "value can't be None")

        key_data = self._to_data(key)
        value_data = self._to_data(value)
        return self._put_transient_internal(key_data, value_data, ttl, max_idle)

    def remove(self, key: KeyType) -> Future[typing.Optional[ValueType]]:
        """Removes the mapping for a key from this map if it is present.

        The map will not contain a mapping for the specified key once the call
        returns.

        Warning:
            This method uses ``__hash__`` and ``__eq__`` methods of binary form
            of the key, not the actual implementations of ``__hash__`` and
            ``__eq__`` defined in key's class.

        Args:
            key: Key of the mapping to be deleted.

        Returns:
            The previous value associated with key, or ``None`` if there was
            no mapping for key.
        """
        check_not_none(key, "key can't be None")
        key_data = self._to_data(key)
        return self._remove_internal(key_data)

    def remove_if_same(self, key: KeyType, value: ValueType) -> Future[bool]:
        """Removes the entry for a key only if it is currently mapped to a
        given value.

        This is equivalent to below, except that the action is performed
        atomically:

            >>> if my_map.contains_key(key) and my_map.get(key) == value:
            >>>     my_map.remove(key)
            >>>     return True
            >>> else:
            >>>     return False

        Warning:
            This method uses ``__hash__`` and ``__eq__`` methods of binary form
            of the key, not the actual implementations of ``__hash__`` and
            ``__eq__`` defined in key's class.

        Args:
            key: The specified key.
            value: Remove the key if it has this value.

        Returns:
            ``True`` if the value was removed, ``False`` otherwise.
        """
        check_not_none(key, "key can't be None")
        check_not_none(value, "value can't be None")

        key_data = self._to_data(key)
        value_data = self._to_data(value)
        return self._remove_if_same_internal_(key_data, value_data)

    def remove_entry_listener(self, registration_id: str) -> Future[bool]:
        """Removes the specified entry listener.

        Returns silently if there is no such listener added before.

        Args:
            registration_id: Id of registered listener.

        Returns:
            ``True`` if registration is removed, ``False`` otherwise.
        """
        return self._deregister_listener(registration_id)

    def remove_interceptor(self, registration_id: str) -> Future[bool]:
        """Removes the given interceptor for this map, so it will not intercept
        operations anymore.

        Args:
            registration_id: Registration ID of the map interceptor.

        Returns:
            ``True`` if the interceptor is removed, ``False`` otherwise.
        """
        check_not_none(registration_id, "Interceptor registration id should not be None")
        request = map_remove_interceptor_codec.encode_request(self.name, registration_id)
        return self._invoke(request, map_remove_interceptor_codec.decode_response)

    def replace(self, key: KeyType, value: ValueType) -> Future[typing.Optional[ValueType]]:
        """Replaces the entry for a key only if it is currently mapped to some
        value.

        This is equivalent to below, except that the action is performed
        atomically:

            >>> if my_map.contains_key(key):
            >>>     return my_map.put(key,value)
            >>> else:
            >>>     return None

        Warning:
            This method uses ``__hash__`` and ``__eq__`` methods of binary form
            of the key, not the actual implementations of ``__hash__`` and
            ``__eq__`` defined in key's class.

        Warning:
            This method returns a clone of the previous value, not the original
            (identically equal) value previously put into the map.

        Args:
            key: The specified key.
            value: The value to replace the previous value.

        Returns:
            Previous value associated with key, or ``None`` if there was no
            mapping for key.
        """
        check_not_none(key, "key can't be None")
        check_not_none(value, "value can't be None")

        key_data = self._to_data(key)
        value_data = self._to_data(value)

        return self._replace_internal(key_data, value_data)

    def replace_if_same(
        self, key: ValueType, old_value: ValueType, new_value: ValueType
    ) -> Future[bool]:
        """Replaces the entry for a key only if it is currently mapped to a
        given value.

        This is equivalent to below, except that the action is performed
        atomically:

            >>> if my_map.contains_key(key) and my_map.get(key) == old_value:
            >>>     my_map.put(key, new_value)
            >>>     return True
            >>> else:
            >>>     return False

        Warning:
            This method uses ``__hash__`` and ``__eq__`` methods of binary form
            of the key, not the actual implementations of ``__hash__`` and
            ``__eq__`` defined in key's class.

        Args:
            key: The specified key.
            old_value: Replace the key value if it is the old value.
            new_value: The new value to replace the old value.

        Returns:
            ``True`` if the value was replaced, ``False`` otherwise.
        """
        check_not_none(key, "key can't be None")
        check_not_none(old_value, "old_value can't be None")
        check_not_none(new_value, "new_value can't be None")

        key_data = self._to_data(key)
        old_value_data = self._to_data(old_value)
        new_value_data = self._to_data(new_value)

        return self._replace_if_same_internal(key_data, old_value_data, new_value_data)

    def set(
        self, key: KeyType, value: ValueType, ttl: float = None, max_idle: float = None
    ) -> Future[None]:
        """Puts an entry into this map.

        Similar to the put operation except that set doesn't return the old
        value, which is more efficient. If ttl is provided, entry will expire
        and get evicted after the ttl.

        Warning:
            This method uses ``__hash__`` and ``__eq__`` methods of binary form
            of the key, not the actual implementations of ``__hash__`` and
            ``__eq__`` defined in key's class.

        Args:
            key: Key of the entry.
            value: Value of the entry.
            ttl: Maximum time in seconds for this entry to stay in the map. If
                not provided, the value configured on the server side
                configuration will be used. Setting this to ``0`` means
                infinite time-to-live.
            max_idle: Maximum time in seconds for this entry to stay idle in
                the map. If not provided, the value configured on the server
                side configuration will be used. Setting this to ``0`` means
                infinite max idle time.
        """
        check_not_none(key, "key can't be None")
        check_not_none(value, "value can't be None")
        key_data = self._to_data(key)
        value_data = self._to_data(value)
        return self._set_internal(key_data, value_data, ttl, max_idle)

    def set_ttl(self, key: KeyType, ttl: float) -> Future[None]:
        """Updates the TTL (time to live) value of the entry specified by the
        given key with a new TTL value.

        New TTL value is valid starting from the time this operation is
        invoked, not since the time the entry was created. If the entry does
        not exist or is already expired, this call has no effect.

        Args:
            key: The key of the map entry.
            ttl: Maximum time in seconds for this entry to stay in the map.
                Setting this to ``0`` means infinite time-to-live.
        """
        check_not_none(key, "key can't be None")
        check_not_none(ttl, "ttl can't be None")
        key_data = self._to_data(key)
        return self._set_ttl_internal(key_data, ttl)

    def size(self) -> Future[int]:
        """Returns the number of entries in this map.

        Returns:
            Number of entries in this map.
        """
        request = map_size_codec.encode_request(self.name)
        return self._invoke(request, map_size_codec.decode_response)

    def try_lock(self, key: KeyType, lease_time: float = None, timeout: float = 0) -> Future[bool]:
        """Tries to acquire the lock for the specified key.

        When the lock is not available:

        - If the timeout is not provided, the current thread doesn't wait and
          returns ``False`` immediately.
        - If the timeout is provided, the current thread becomes disabled for
          thread scheduling purposes and lies dormant until one of the
          followings happens:

            - The lock is acquired by the current thread, or
            - The specified waiting time elapses.

        If the lease time is provided, lock will be released after this time
        elapses.

        Args:
            key: Key to lock in this map.
            lease_time: Time in seconds to wait before releasing the lock.
            timeout: Maximum time in seconds to wait for the lock.

        Returns:
            ``True`` if the lock was acquired, ``False`` otherwise.
        """
        check_not_none(key, "key can't be None")

        key_data = self._to_data(key)
        request = map_try_lock_codec.encode_request(
            self.name,
            key_data,
            thread_id(),
            to_millis(lease_time),
            to_millis(timeout),
            self._reference_id_generator.get_and_increment(),
        )
        partition_id = self._context.partition_service.get_partition_id(key_data)
        invocation = Invocation(
            request,
            partition_id=partition_id,
            timeout=MAX_SIZE,
            response_handler=map_try_lock_codec.decode_response,
        )
        self._invocation_service.invoke(invocation)
        return invocation.future

    def try_put(self, key: KeyType, value: ValueType, timeout: float = 0) -> Future[bool]:
        """Tries to put the given key and value into this map and returns
        immediately if timeout is not provided.

        If timeout is provided, operation waits until it is completed or
        timeout is reached.

        Args:
            key: Key of the entry.
            value: Value of the entry.
            timeout: Maximum time in seconds to wait.

        Returns:
            ``True`` if the put is successful, ``False`` otherwise.
        """
        check_not_none(key, "key can't be None")
        check_not_none(value, "value can't be None")

        key_data = self._to_data(key)
        value_data = self._to_data(value)

        return self._try_put_internal(key_data, value_data, timeout)

    def try_remove(self, key: KeyType, timeout: float = 0) -> Future[bool]:
        """Tries to remove the given key from this map and returns immediately
        if timeout is not provided.

        If timeout is provided, operation waits until it is completed or
        timeout is reached.

        Args:
            key: Key of the entry to be deleted.
            timeout: Maximum time in seconds to wait.

        Returns:
            ``True`` if the remove is successful, ``False`` otherwise.
        """
        check_not_none(key, "key can't be None")

        key_data = self._to_data(key)
        return self._try_remove_internal(key_data, timeout)

    def unlock(self, key: KeyType) -> Future[None]:
        """Releases the lock for the specified key.

        It never blocks and returns immediately. If the current thread is the
        holder of this lock, then the hold count is decremented. If the hold
        count is zero, then the lock is released.

        Args:
            key: The key to lock.
        """
        check_not_none(key, "key can't be None")

        key_data = self._to_data(key)
        request = map_unlock_codec.encode_request(
            self.name, key_data, thread_id(), self._reference_id_generator.get_and_increment()
        )
        return self._invoke_on_key(request, key_data)

    def values(self, predicate: Predicate = None) -> Future[typing.List[ValueType]]:
        """Returns a list clone of the values contained in this map or values
        of the entries which are filtered with the predicate if provided.

        Warning:
            The list is NOT backed by the map, so changes to the map are NOT
            reflected in the list, and vice-versa.

        Args:
            predicate: Predicate to filter the entries.

        Returns:
            A list of clone of the values contained in this map.
        """
        if predicate:
            if isinstance(predicate, PagingPredicate):
                codec = map_values_with_paging_predicate_codec

                def handler(message):
                    response = codec.decode_response(message)
                    predicate.anchor_list = response["anchor_data_list"].as_anchor_list(
                        self._to_object
                    )
                    return ImmutableLazyDataList(response["response"], self._to_object)

                predicate.iteration_type = IterationType.VALUE
                holder = PagingPredicateHolder.of(predicate, self._to_data)
                request = codec.encode_request(self.name, holder)
            else:
                codec = map_values_with_predicate_codec

                def handler(message):
                    return ImmutableLazyDataList(codec.decode_response(message), self._to_object)

                predicate_data = self._to_data(predicate)
                request = codec.encode_request(self.name, predicate_data)
        else:
            codec = map_values_codec

            def handler(message):
                return ImmutableLazyDataList(codec.decode_response(message), self._to_object)

            request = codec.encode_request(self.name)

        return self._invoke(request, handler)

    def blocking(self) -> "BlockingMap[KeyType, ValueType]":
        return BlockingMap(self)

    # internals
    def _contains_key_internal(self, key_data):
        request = map_contains_key_codec.encode_request(self.name, key_data, thread_id())
        return self._invoke_on_key(request, key_data, map_contains_key_codec.decode_response)

    def _get_internal(self, key_data):
        def handler(message):
            return self._to_object(map_get_codec.decode_response(message))

        request = map_get_codec.encode_request(self.name, key_data, thread_id())
        return self._invoke_on_key(request, key_data, handler)

    def _get_all_internal(self, partition_to_keys, futures=None):
        if futures is None:
            futures = []

        def handler(message):
            return ImmutableLazyDataList(
                map_get_all_codec.decode_response(message), self._to_object
            )

        for partition_id, key_dict in partition_to_keys.items():
            request = map_get_all_codec.encode_request(self.name, key_dict.values())
            future = self._invoke_on_partition(request, partition_id, handler)
            futures.append(future)

        def merge(f):
            return dict(itertools.chain(*f.result()))

        return combine_futures(futures).continue_with(merge)

    def _remove_internal(self, key_data):
        def handler(message):
            return self._to_object(map_remove_codec.decode_response(message))

        request = map_remove_codec.encode_request(self.name, key_data, thread_id())
        return self._invoke_on_key(request, key_data, handler)

    def _remove_if_same_internal_(self, key_data, value_data):
        request = map_remove_if_same_codec.encode_request(
            self.name, key_data, value_data, thread_id()
        )
        return self._invoke_on_key(
            request, key_data, response_handler=map_remove_if_same_codec.decode_response
        )

    def _delete_internal(self, key_data):
        request = map_delete_codec.encode_request(self.name, key_data, thread_id())
        return self._invoke_on_key(request, key_data)

    def _put_internal(self, key_data, value_data, ttl, max_idle):
        def handler(message):
            return self._to_object(map_put_codec.decode_response(message))

        if max_idle is not None:
            request = map_put_with_max_idle_codec.encode_request(
                self.name, key_data, value_data, thread_id(), to_millis(ttl), to_millis(max_idle)
            )
        else:
            request = map_put_codec.encode_request(
                self.name, key_data, value_data, thread_id(), to_millis(ttl)
            )
        return self._invoke_on_key(request, key_data, handler)

    def _set_internal(self, key_data, value_data, ttl, max_idle):
        if max_idle is not None:
            request = map_set_with_max_idle_codec.encode_request(
                self.name, key_data, value_data, thread_id(), to_millis(ttl), to_millis(max_idle)
            )
        else:
            request = map_set_codec.encode_request(
                self.name, key_data, value_data, thread_id(), to_millis(ttl)
            )
        return self._invoke_on_key(request, key_data)

    def _set_ttl_internal(self, key_data, ttl):
        request = map_set_ttl_codec.encode_request(self.name, key_data, to_millis(ttl))
        return self._invoke_on_key(request, key_data, map_set_ttl_codec.decode_response)

    def _try_remove_internal(self, key_data, timeout):
        request = map_try_remove_codec.encode_request(
            self.name, key_data, thread_id(), to_millis(timeout)
        )
        return self._invoke_on_key(request, key_data, map_try_remove_codec.decode_response)

    def _try_put_internal(self, key_data, value_data, timeout):
        request = map_try_put_codec.encode_request(
            self.name, key_data, value_data, thread_id(), to_millis(timeout)
        )
        return self._invoke_on_key(request, key_data, map_try_put_codec.decode_response)

    def _put_transient_internal(self, key_data, value_data, ttl, max_idle):
        if max_idle is not None:
            request = map_put_transient_with_max_idle_codec.encode_request(
                self.name, key_data, value_data, thread_id(), to_millis(ttl), to_millis(max_idle)
            )
        else:
            request = map_put_transient_codec.encode_request(
                self.name, key_data, value_data, thread_id(), to_millis(ttl)
            )
        return self._invoke_on_key(request, key_data)

    def _put_if_absent_internal(self, key_data, value_data, ttl, max_idle):
        def handler(message):
            return self._to_object(map_put_if_absent_codec.decode_response(message))

        if max_idle is not None:
            request = map_put_if_absent_with_max_idle_codec.encode_request(
                self.name, key_data, value_data, thread_id(), to_millis(ttl), to_millis(max_idle)
            )
        else:
            request = map_put_if_absent_codec.encode_request(
                self.name, key_data, value_data, thread_id(), to_millis(ttl)
            )
        return self._invoke_on_key(request, key_data, handler)

    def _replace_if_same_internal(self, key_data, old_value_data, new_value_data):
        request = map_replace_if_same_codec.encode_request(
            self.name, key_data, old_value_data, new_value_data, thread_id()
        )
        return self._invoke_on_key(request, key_data, map_replace_if_same_codec.decode_response)

    def _replace_internal(self, key_data, value_data):
        def handler(message):
            return self._to_object(map_replace_codec.decode_response(message))

        request = map_replace_codec.encode_request(self.name, key_data, value_data, thread_id())
        return self._invoke_on_key(request, key_data, handler)

    def _evict_internal(self, key_data):
        request = map_evict_codec.encode_request(self.name, key_data, thread_id())
        return self._invoke_on_key(request, key_data, map_evict_codec.decode_response)

    def _load_all_internal(self, key_data_list, replace_existing_values):
        request = map_load_given_keys_codec.encode_request(
            self.name, key_data_list, replace_existing_values
        )
        return self._invoke(request)

    def _execute_on_key_internal(self, key_data, entry_processor):
        def handler(message):
            return self._to_object(map_execute_on_key_codec.decode_response(message))

        entry_processor_data = self._to_data(entry_processor)
        request = map_execute_on_key_codec.encode_request(
            self.name, entry_processor_data, key_data, thread_id()
        )
        return self._invoke_on_key(request, key_data, handler)


class MapFeatNearCache(Map[KeyType, ValueType]):
    """Map proxy implementation featuring Near Cache"""

    def __init__(self, service_name, name, context):
        super(MapFeatNearCache, self).__init__(service_name, name, context)
        self._invalidation_listener_id = None
        self._near_cache = context.near_cache_manager.get_or_create_near_cache(name)
        if self._near_cache.invalidate_on_change:
            self._add_near_cache_invalidation_listener()

    def clear(self):
        self._near_cache._clear()
        return super(MapFeatNearCache, self).clear()

    def evict_all(self):
        self._near_cache.clear()
        return super(MapFeatNearCache, self).evict_all()

    def load_all(self, keys=None, replace_existing_values=True):
        if keys is None and replace_existing_values:
            self._near_cache.clear()
        return super(MapFeatNearCache, self).load_all(keys, replace_existing_values)

    def blocking(self) -> "BlockingMap[KeyType, ValueType]":
        return BlockingMap(self)

    def _on_destroy(self):
        self._remove_near_cache_invalidation_listener()
        self._near_cache.clear()
        super(MapFeatNearCache, self)._on_destroy()

    def _add_near_cache_invalidation_listener(self):
        codec = map_add_near_cache_invalidation_listener_codec
        request = codec.encode_request(self.name, EntryEventType.INVALIDATION, self._is_smart)
        self._invalidation_listener_id = self._register_listener(
            request,
            lambda r: codec.decode_response(r),
            lambda reg_id: map_remove_entry_listener_codec.encode_request(self.name, reg_id),
            lambda m: codec.handle(m, self._handle_invalidation, self._handle_batch_invalidation),
        ).result()

    def _remove_near_cache_invalidation_listener(self):
        if self._invalidation_listener_id:
            self.remove_entry_listener(self._invalidation_listener_id)

    def _handle_invalidation(self, key, source_uuid, partition_uuid, sequence):
        # key is always ``Data``
        # null key means near cache has to remove all entries in it.
        # see MapAddNearCacheEntryListenerMessageTask.
        if key is None:
            self._near_cache._clear()
        else:
            self._invalidate_cache(key)

    def _handle_batch_invalidation(self, keys, source_uuids, partition_uuids, sequences):
        # key_list is always list of ``Data``
        for key_data in keys:
            self._invalidate_cache(key_data)

    def _invalidate_cache(self, key_data):
        self._near_cache._invalidate(key_data)

    def _invalidate_cache_batch(self, key_data_list):
        for key_data in key_data_list:
            self._near_cache._invalidate(key_data)

    # internals
    def _contains_key_internal(self, key_data):
        try:
            return self._near_cache[key_data]
        except KeyError:
            return super(MapFeatNearCache, self)._contains_key_internal(key_data)

    def _get_internal(self, key_data):
        try:
            value = self._near_cache[key_data]
            return ImmediateFuture(value)
        except KeyError:
            future = super(MapFeatNearCache, self)._get_internal(key_data)
            return future.continue_with(self._update_cache, key_data)

    def _update_cache(self, f, key_data):
        self._near_cache.__setitem__(key_data, f.result())
        return f.result()

    def _get_all_internal(self, partition_to_keys, futures=None):
        if futures is None:
            futures = []
        for key_dic in partition_to_keys.values():
            for key in list(key_dic.keys()):
                try:
                    key_data = key_dic[key]
                    value = self._near_cache[key_data]
                    future = ImmediateFuture((key, value))
                    futures.append(future)
                    del key_dic[key]
                except KeyError:
                    pass
        return super(MapFeatNearCache, self)._get_all_internal(partition_to_keys, futures)

    def _try_remove_internal(self, key_data, timeout):
        self._invalidate_cache(key_data)
        return super(MapFeatNearCache, self)._try_remove_internal(key_data, timeout)

    def _try_put_internal(self, key_data, value_data, timeout):
        self._invalidate_cache(key_data)
        return super(MapFeatNearCache, self)._try_put_internal(key_data, value_data, timeout)

    def _set_internal(self, key_data, value_data, ttl, max_idle):
        self._invalidate_cache(key_data)
        return super(MapFeatNearCache, self)._set_internal(key_data, value_data, ttl, max_idle)

    def _set_ttl_internal(self, key_data, ttl):
        self._invalidate_cache(key_data)
        return super(MapFeatNearCache, self)._set_ttl_internal(key_data, ttl)

    def _replace_internal(self, key_data, value_data):
        self._invalidate_cache(key_data)
        return super(MapFeatNearCache, self)._replace_internal(key_data, value_data)

    def _replace_if_same_internal(self, key_data, old_value_data, new_value_data):
        self._invalidate_cache(key_data)
        return super(MapFeatNearCache, self)._replace_if_same_internal(
            key_data, old_value_data, new_value_data
        )

    def _remove_internal(self, key_data):
        self._invalidate_cache(key_data)
        return super(MapFeatNearCache, self)._remove_internal(key_data)

    def _remove_if_same_internal_(self, key_data, value_data):
        self._invalidate_cache(key_data)
        return super(MapFeatNearCache, self)._remove_if_same_internal_(key_data, value_data)

    def _put_transient_internal(self, key_data, value_data, ttl, max_idle):
        self._invalidate_cache(key_data)
        return super(MapFeatNearCache, self)._put_transient_internal(
            key_data, value_data, ttl, max_idle
        )

    def _put_internal(self, key_data, value_data, ttl, max_idle):
        self._invalidate_cache(key_data)
        return super(MapFeatNearCache, self)._put_internal(key_data, value_data, ttl, max_idle)

    def _put_if_absent_internal(self, key_data, value_data, ttl, max_idle):
        self._invalidate_cache(key_data)
        return super(MapFeatNearCache, self)._put_if_absent_internal(
            key_data, value_data, ttl, max_idle
        )

    def _load_all_internal(self, key_data_list, replace_existing_values):
        self._invalidate_cache_batch(key_data_list)
        return super(MapFeatNearCache, self)._load_all_internal(
            key_data_list, replace_existing_values
        )

    def _execute_on_key_internal(self, key_data, entry_processor):
        self._invalidate_cache(key_data)
        return super(MapFeatNearCache, self)._execute_on_key_internal(key_data, entry_processor)

    def _evict_internal(self, key_data):
        self._invalidate_cache(key_data)
        return super(MapFeatNearCache, self)._evict_internal(key_data)

    def _delete_internal(self, key_data):
        self._invalidate_cache(key_data)
        return super(MapFeatNearCache, self)._delete_internal(key_data)


class BlockingMap(Map[KeyType, ValueType]):
    __slots__ = ("_wrapped", "name", "service_name")

    def __init__(
        self, wrapped: typing.Union[Map[KeyType, ValueType], MapFeatNearCache[KeyType, ValueType]]
    ):
        self.name = wrapped.name
        self.service_name = wrapped.service_name
        self._wrapped = wrapped

    def add_entry_listener(  # type: ignore[override]
        self,
        include_value: bool = False,
        key: KeyType = None,
        predicate: Predicate = None,
        added_func: EntryEventCallable = None,
        removed_func: EntryEventCallable = None,
        updated_func: EntryEventCallable = None,
        evicted_func: EntryEventCallable = None,
        evict_all_func: EntryEventCallable = None,
        clear_all_func: EntryEventCallable = None,
        merged_func: EntryEventCallable = None,
        expired_func: EntryEventCallable = None,
        loaded_func: EntryEventCallable = None,
    ) -> str:
        return self._wrapped.add_entry_listener(
            include_value,
            key,
            predicate,
            added_func,
            removed_func,
            updated_func,
            evicted_func,
            evict_all_func,
            clear_all_func,
            merged_func,
            expired_func,
            loaded_func,
        ).result()

    def add_index(  # type: ignore[override]
        self,
        attributes: typing.Sequence[str] = None,
        index_type: typing.Union[int, str] = IndexType.SORTED,
        name: str = None,
        bitmap_index_options: typing.Dict[str, typing.Any] = None,
    ) -> None:
        return self._wrapped.add_index(attributes, index_type, name, bitmap_index_options).result()

    def add_interceptor(  # type: ignore[override]
        self,
        interceptor: typing.Any,
    ) -> str:
        return self._wrapped.add_interceptor(interceptor).result()

    def aggregate(  # type: ignore[override]
        self,
        aggregator: Aggregator[AggregatorResultType],
        predicate: Predicate = None,
    ) -> AggregatorResultType:
        return self._wrapped.aggregate(aggregator, predicate).result()

    def clear(  # type: ignore[override]
        self,
    ) -> None:
        return self._wrapped.clear().result()

    def contains_key(  # type: ignore[override]
        self,
        key: KeyType,
    ) -> bool:
        return self._wrapped.contains_key(key).result()

    def contains_value(  # type: ignore[override]
        self,
        value: ValueType,
    ) -> bool:
        return self._wrapped.contains_value(value).result()

    def delete(  # type: ignore[override]
        self,
        key: KeyType,
    ) -> None:
        return self._wrapped.delete(key).result()

    def entry_set(  # type: ignore[override]
        self,
        predicate: Predicate = None,
    ) -> typing.List[typing.Tuple[KeyType, ValueType]]:
        return self._wrapped.entry_set(predicate).result()

    def evict(  # type: ignore[override]
        self,
        key: KeyType,
    ) -> bool:
        return self._wrapped.evict(key).result()

    def evict_all(  # type: ignore[override]
        self,
    ) -> None:
        return self._wrapped.evict_all().result()

    def execute_on_entries(  # type: ignore[override]
        self,
        entry_processor: typing.Any,
        predicate: Predicate = None,
    ) -> typing.List[typing.Any]:
        return self._wrapped.execute_on_entries(entry_processor, predicate).result()

    def execute_on_key(  # type: ignore[override]
        self,
        key: KeyType,
        entry_processor: typing.Any,
    ) -> typing.Any:
        return self._wrapped.execute_on_key(key, entry_processor).result()

    def execute_on_keys(  # type: ignore[override]
        self,
        keys: typing.Sequence[KeyType],
        entry_processor: typing.Any,
    ) -> typing.List[typing.Any]:
        return self._wrapped.execute_on_keys(keys, entry_processor).result()

    def flush(  # type: ignore[override]
        self,
    ) -> None:
        return self._wrapped.flush().result()

    def force_unlock(  # type: ignore[override]
        self,
        key: KeyType,
    ) -> None:
        return self._wrapped.force_unlock(key).result()

    def get(  # type: ignore[override]
        self,
        key: KeyType,
    ) -> typing.Optional[ValueType]:
        return self._wrapped.get(key).result()

    def get_all(  # type: ignore[override]
        self,
        keys: typing.Sequence[KeyType],
    ) -> typing.Dict[KeyType, ValueType]:
        return self._wrapped.get_all(keys).result()

    def get_entry_view(  # type: ignore[override]
        self,
        key: KeyType,
    ) -> SimpleEntryView[KeyType, ValueType]:
        return self._wrapped.get_entry_view(key).result()

    def is_empty(  # type: ignore[override]
        self,
    ) -> bool:
        return self._wrapped.is_empty().result()

    def is_locked(  # type: ignore[override]
        self,
        key: KeyType,
    ) -> bool:
        return self._wrapped.is_locked(key).result()

    def key_set(  # type: ignore[override]
        self,
        predicate: Predicate = None,
    ) -> typing.List[ValueType]:
        return self._wrapped.key_set(predicate).result()

    def load_all(  # type: ignore[override]
        self,
        keys: typing.Sequence[KeyType] = None,
        replace_existing_values: bool = True,
    ) -> None:
        return self._wrapped.load_all(keys, replace_existing_values).result()

    def lock(  # type: ignore[override]
        self,
        key: KeyType,
        lease_time: float = None,
    ) -> None:
        return self._wrapped.lock(key, lease_time).result()

    def project(  # type: ignore[override]
        self,
        projection: Projection[ProjectionType],
        predicate: Predicate = None,
    ) -> ProjectionType:
        return self._wrapped.project(projection, predicate).result()

    def put(  # type: ignore[override]
        self,
        key: KeyType,
        value: ValueType,
        ttl: float = None,
        max_idle: float = None,
    ) -> typing.Optional[ValueType]:
        return self._wrapped.put(key, value, ttl, max_idle).result()

    def put_all(  # type: ignore[override]
        self,
        map: typing.Dict[KeyType, ValueType],
    ) -> None:
        return self._wrapped.put_all(map).result()

    def put_if_absent(  # type: ignore[override]
        self,
        key: KeyType,
        value: ValueType,
        ttl: float = None,
        max_idle: float = None,
    ) -> typing.Optional[ValueType]:
        return self._wrapped.put_if_absent(key, value, ttl, max_idle).result()

    def put_transient(  # type: ignore[override]
        self,
        key: KeyType,
        value: ValueType,
        ttl: float = None,
        max_idle: float = None,
    ) -> None:
        return self._wrapped.put_transient(key, value, ttl, max_idle).result()

    def remove(  # type: ignore[override]
        self,
        key: KeyType,
    ) -> typing.Optional[ValueType]:
        return self._wrapped.remove(key).result()

    def remove_if_same(  # type: ignore[override]
        self,
        key: KeyType,
        value: ValueType,
    ) -> bool:
        return self._wrapped.remove_if_same(key, value).result()

    def remove_entry_listener(  # type: ignore[override]
        self,
        registration_id: str,
    ) -> bool:
        return self._wrapped.remove_entry_listener(registration_id).result()

    def remove_interceptor(  # type: ignore[override]
        self,
        registration_id: str,
    ) -> bool:
        return self._wrapped.remove_interceptor(registration_id).result()

    def replace(  # type: ignore[override]
        self,
        key: KeyType,
        value: ValueType,
    ) -> typing.Optional[ValueType]:
        return self._wrapped.replace(key, value).result()

    def replace_if_same(  # type: ignore[override]
        self,
        key: ValueType,
        old_value: ValueType,
        new_value: ValueType,
    ) -> bool:
        return self._wrapped.replace_if_same(key, old_value, new_value).result()

    def set(  # type: ignore[override]
        self,
        key: KeyType,
        value: ValueType,
        ttl: float = None,
        max_idle: float = None,
    ) -> None:
        return self._wrapped.set(key, value, ttl, max_idle).result()

    def set_ttl(  # type: ignore[override]
        self,
        key: KeyType,
        ttl: float,
    ) -> None:
        return self._wrapped.set_ttl(key, ttl).result()

    def size(  # type: ignore[override]
        self,
    ) -> int:
        return self._wrapped.size().result()

    def try_lock(  # type: ignore[override]
        self,
        key: KeyType,
        lease_time: float = None,
        timeout: float = 0,
    ) -> bool:
        return self._wrapped.try_lock(key, lease_time, timeout).result()

    def try_put(  # type: ignore[override]
        self,
        key: KeyType,
        value: ValueType,
        timeout: float = 0,
    ) -> bool:
        return self._wrapped.try_put(key, value, timeout).result()

    def try_remove(  # type: ignore[override]
        self,
        key: KeyType,
        timeout: float = 0,
    ) -> bool:
        return self._wrapped.try_remove(key, timeout).result()

    def unlock(  # type: ignore[override]
        self,
        key: KeyType,
    ) -> None:
        return self._wrapped.unlock(key).result()

    def values(  # type: ignore[override]
        self,
        predicate: Predicate = None,
    ) -> typing.List[ValueType]:
        return self._wrapped.values(predicate).result()

    def blocking(self) -> "BlockingMap[KeyType, ValueType]":
        return self

    def destroy(self) -> bool:
        return self._wrapped.destroy()

    def __repr__(self) -> str:
        return self._wrapped.__repr__()


def create_map_proxy(service_name, name, context):
    near_cache_config = context.config.near_caches.get(name, None)
    if near_cache_config is None:
        return Map(service_name, name, context)
    else:
        return MapFeatNearCache(service_name, name, context)
