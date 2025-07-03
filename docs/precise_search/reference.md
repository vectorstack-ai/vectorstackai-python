# Vector Index API Reference

## Index Management Operations

These operations are performed at the client level and don't require connecting to a specific index.

::: vectorstackai.PreciseSearch.list_indexes

::: vectorstackai.PreciseSearch.create_index

::: vectorstackai.PreciseSearch.index_info

::: vectorstackai.PreciseSearch.index_status

::: vectorstackai.PreciseSearch.connect_to_index

::: vectorstackai.PreciseSearch.delete_index

## Index Operations

These operations are performed on a specific index after connecting to it.

::: vectorstackai.objects.index.IndexObject.set_similarity_scale

::: vectorstackai.objects.index.IndexObject.upsert

::: vectorstackai.objects.index.IndexObject.search

::: vectorstackai.objects.index.IndexObject.info

::: vectorstackai.objects.index.IndexObject.delete

::: vectorstackai.objects.index.IndexObject.delete_vectors

::: vectorstackai.objects.index.IndexObject.optimize_for_latency

::: vectorstackai.objects.index.IndexObject.get_all_ids

::: vectorstackai.objects.index.IndexObject.get_metadata
