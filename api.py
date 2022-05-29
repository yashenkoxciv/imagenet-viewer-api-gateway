from functools import wraps
from flask import Flask, jsonify, request, abort
from flask_restful import Resource, Api
from environs import Env
from imagenetviewer import image as imnt_image
from mongoengine import connect
import pika

# inspired by https://medium.com/zmninja/building-your-own-machine-learning-api-gateway-routes-db-and-security-part-ii-bf52f690c392

env = Env()
env.read_env()

app = Flask(__name__)
api = Api(app, prefix='/api/v1')

connect(host=env('MONGODB_HOST'), uuidRepresentation='standard')

con_par = pika.ConnectionParameters(
    heartbeat=600,
    blocked_connection_timeout=300,
    host=env('RABBITMQ_HOST')
)
connection = pika.BlockingConnection(con_par)
channel = connection.channel()

channel.queue_declare(queue=env('OUTPUT_QUEUE'), durable=True)


def get_http_exception_handler(app):
    """Overrides the default http exception handler to return JSON."""
    handle_http_exception = app.handle_http_exception
    @wraps(handle_http_exception)
    def ret_val(exception):
        exc = handle_http_exception(exception)
        return jsonify({'code': exc.code, 'msg': exc.description}), exc.code
    return ret_val

# Override the HTTP exception handler.
app.handle_http_exception = get_http_exception_handler(app)


def convert_image_to_dict(image):
    image_dict = image.to_dict()
    image_dict['id'] = str(image_dict['id'])
    image_dict['status'] = imnt_image.ImageStatus(image_dict['status']).name
    return image_dict


class Image(Resource):
    def post(self):
        if not request.is_json:
            abort(400, 'Missing JSON in request')

        image_url = request.json.get('url', None)

        if not image_url:
            abort(400, 'Missing image URL')

        image = imnt_image.Image(url=image_url)

        pilimage = image.get_pil_image()
        pilimage.verify()

        image.save()

        message = f'{image.id}'
        channel.basic_publish(
            exchange='',
            routing_key=env('OUTPUT_QUEUE'),
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            )
        )

        return {'id': str(image.id)}

    def get(self):
        if not request.is_json:
            abort(400, 'Missing JSON in request')

        image_id = request.json.get('id', None)

        if not image_id:
            abort(400, 'Missing image id')

        image = imnt_image.Image.objects.get(pk=image_id)
        image_dict = convert_image_to_dict(image)
        return image_dict


class RecentImages(Resource):
    def get(self):
        if not request.is_json:
            abort(400, 'Missing JSON in request')

        n = request.json.get('n', None)

        if not n:
            #abort(400, 'Missing n, number of recent classifications')
            n = 5

        n_objects = len(imnt_image.Image.objects)
        if n > n_objects:
            n = n_objects
        images = imnt_image.Image.objects.order_by('-id').limit(n)
        images_list = []
        for image in images:
            image_dict = convert_image_to_dict(image)
            images_list.append(image_dict)
        return images_list


class Clusters(Resource):
    def get(self):
        cluster_ids = imnt_image.Image.objects.distinct(field='cluster_id')
        return cluster_ids


class Cluster(Resource):
    def get(self):
        if not request.is_json:
            abort(400, 'Missing JSON in request')

        cluster_id = request.json.get('cluster_id', None)

        if not cluster_id:
            abort(400, 'Missing cluster id')

        cluster_images = imnt_image.Image.objects(cluster_id=cluster_id)
        images_list = []
        for image in cluster_images:
            image_dict = convert_image_to_dict(image)
            images_list.append(image_dict)
        return images_list


api.add_resource(Image, '/image')
api.add_resource(RecentImages, '/images')
api.add_resource(Clusters, '/clusters')
api.add_resource(Cluster, '/cluster')

if __name__ == '__main__':
    app.run(
        host=env('HOST'),
        port=env.int('PORT'),
        debug=env.bool('DEBUG')
    )
