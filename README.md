# imagenet-viewer-api-gateway

The service allows to send image to imagenet-viewer system and track status of the image.
Also, it shows groups of images.

# Endpoints
## POST api/v1/image

Send image to recognition pipeline.

Expects JSON like these:
```json
{
    "url": "file:///path/to/image"
}
```
```json
{
    "url": "http://path/to/image.jpg"
}
```

Returns image id as JSON:
```json
{
    "id": "image_objectid"
}
```

## GET api/v1/image

Obtain image status.

Expects:
```json
{
    "id": "6293488c4cb009c4a533cc76"
}
```

Returns:

```json
{
    "id": "6293488c4cb009c4a533cc76",
    "status": "PENDING_CLASSIFICATION",
    "label": null,
    "cluster_id": null,
    "url": "url/to/image"
}
```

## GET api/v1/images

Obtain statuses of the recent images.

Expects:
```json
{}
```
or
```json
{
    "n": 2
}
```

Returns:
```json
[
    {
        "id": "6293488c4cb009c4a533cc76",
        "status": "CLASSIFIED",
        "label": "AFRICAN_ELEPHANT",
        "cluster_id": null,
        "url": "file:///path/to/Elephant_997.jpg"
    },
    {
        "id": "6293488c4cb009c4a533cc75",
        "status": "PENDING_MATCHING",
        "label": null,
        "cluster_id": null,
        "url": "file:///path/to/Elephant_284.jpg"
    }
]
```

## GET api/v1/clusters

Obtain list of all image groups (clusters).

Expects:
```json
{}
```

Returns:
```json
[
    "0c09b6fe-7f40-43c0-a791-06a9f00b6efd",
    "10b49dfa-36a3-44a7-9d81-84aad7f6f58d",
    "82957c37-eb4a-4e2f-8738-768f9645cfa0"
]
```

## GET api/v1/cluster

Obtain the cluster content by cluster id.

Expects:
```json
{
    "cluster_id": "a10a7100-e20c-466e-8718-2f0800b65a3f"
}
```

Returns:
```json
[
    {
        "id": "62934883b1a3c1ecb3140797",
        "status": "CLUSTERIZED",
        "label": null,
        "cluster_id": "a10a7100-e20c-466e-8718-2f0800b65a3f",
        "url": "file:///path/to/black-eyed susan/1253518019_1856f6a2c3_c.jpg"
    },
    {
        "id": "62934883b1a3c1ecb3140798",
        "status": "CLUSTERIZED",
        "label": null,
        "cluster_id": "a10a7100-e20c-466e-8718-2f0800b65a3f",
        "url": "file:///path/to/black-eyed susan/14772553150_2166e229c7_c.jpg"
    }
]
```

# Expected environment variables

| Name           | Description                                                               |
|----------------|:--------------------------------------------------------------------------|
| HOST           | api-gateway host                                                          |
| PORT           | api-gateway port                                                          |
| DEBUG          | flask's debug mode                                                        |
| RABBITMQ_HOST  | RabbitMQ's host                                                           |
| OUTPUT_QUEUE   | RabbitMQ's queue to push image for recognition                            |
| MONGODB_HOST   | MongoDB's connection string like this: mongodb://host:port/imagenetviewer |

