# Vector Index API Reference

## Index Management Operations

These operations are performed at the client level and don't require connecting to a specific index.

::: vectorstackai.client.Client.list_indexes

::: vectorstackai.client.Client.create_index

::: vectorstackai.client.Client.get_index_info

::: vectorstackai.client.Client.connect_to_index

::: vectorstackai.client.Client.delete_index

## Index Operations

These operations are performed on a specific index after connecting to it.

::: vectorstackai.objects.index.IndexObject.set_similarity_scale

::: vectorstackai.objects.index.IndexObject.upsert

::: vectorstackai.objects.index.IndexObject.search

::: vectorstackai.objects.index.IndexObject.info

::: vectorstackai.objects.index.IndexObject.delete

::: vectorstackai.objects.index.IndexObject.delete_vectors

::: vectorstackai.objects.index.IndexObject.optimize_for_latency