import json

from celery import shared_task
from django.db.models import Q

import os
import tensorflow as tf
import shutil
import imghdr

from web.models import Photo, Project, PhotoProject

# change it to correct paths

path_to_media = 'C:/Users/idmit/GalleryAI/media/'
path_to_models = 'C:/Users/idmit/GalleryAI/ai/models/'


@shared_task
def start_train(project_id):
    try:
        project = Project.objects.get(id=project_id)
        if project.photos.filter(
                Q(meta__is_ai_tag=False) and Q(meta__match=True)).count() >= 20 and project.photos.filter(
            Q(meta__is_ai_tag=False) and Q(meta__match=False)).count() >= 20:

            photos = project.photos.filter(meta__is_ai_tag=False)

            model = Train(project_id, photos)
            model_delete_and_save(model, str(project.user.email), str(project_id))

            project.is_trained = True
            project.save()
        else:
            print('PROJECT CANT BE TRAINED')
    except json.decoder.JSONDecodeError:
        print('\njson error\n')


@shared_task
def start_prediction(user_id):
    try:
        projects = Project.objects.filter(user_id=user_id)
        for project in projects:
            project_id = project.id
            if project.is_trained:
                photos = project.photos.filter(meta__match=None)

                print(photos)

                if photos:
                    result = Prediction(project_id, photos, str(project.user.email), str(project_id))

                    score_list = [int(result[i] * 100) for i in range(len(result))]

                    x = 50

                    for i in range(len(score_list)):
                        score = score_list[i]
                        photo = photos[i]

                        meta = photo.meta.get(project_id=project_id)
                        meta.match = True if score >= x else False
                        meta.score = score
                        meta.is_ai_tag = True

                        meta.save()
            else:
                print('PROJECT IS NOT TRAINED ')
    except json.decoder.JSONDecodeError:
        print('\njson error\n')


def model_preparation(user_name, model_name):
    path_to_model = path_to_models + user_name + "/" + model_name
    print(path_to_model)
    try:
        model = tf.keras.models.load_model(path_to_model)
        return model
    except:
        print("Model not found")
        return None


def check_user_folder(user_name):
    user_folder = path_to_models + user_name
    try:
        os.mkdir(user_folder)
    except:
        print("user folder is already created")


def model_delete_and_save(model, user_name, model_name):
    check_user_folder(user_name)
    path_to_model = path_to_models + user_name + "/" + model_name
    try:
        path = os.path.join(os.path.dirname((__file__)), path_to_model)
        shutil.rmtree(path)
    except:
        print("directory is already empty")
    finally:
        os.mkdir(path_to_model)
        model.save(path_to_model)


def Train(project_id, photos):
    BATCH_SIZE = 32
    IMG_SIZE = (160, 160)

    photos = [photo for photo in photos if
              imghdr.what(path_to_media + str(photo.image)) in ['jpg', 'png', 'jpeg', 'gif', 'bmp']]

    train_dataset = dataset_by_filenames(project_id, photos, "train")

    # class_names = train_dataset.class_names

    AUTOTUNE = tf.data.AUTOTUNE

    train_dataset = train_dataset.prefetch(buffer_size=AUTOTUNE)

    data_augmentation = tf.keras.Sequential([
        tf.keras.layers.RandomFlip('horizontal'),
        tf.keras.layers.RandomRotation(0.2),
    ])

    preprocess_input = tf.keras.applications.mobilenet_v2.preprocess_input
    rescale = tf.keras.layers.Rescaling(1. / 127.5, offset=-1)

    IMG_SHAPE = IMG_SIZE + (3,)
    base_model = tf.keras.applications.MobileNetV2(input_shape=IMG_SHAPE,
                                                   include_top=False,
                                                   weights='imagenet')

    image_batch, label_batch = next(iter(train_dataset))
    feature_batch = base_model(image_batch)
    print(feature_batch.shape)

    base_model.trainable = False

    base_model.summary()

    global_average_layer = tf.keras.layers.GlobalAveragePooling2D()
    feature_batch_average = global_average_layer(feature_batch)
    print(feature_batch_average.shape)

    prediction_layer = tf.keras.layers.Dense(1)
    prediction_batch = prediction_layer(feature_batch_average)
    print(prediction_batch.shape)

    inputs = tf.keras.Input(shape=(160, 160, 3))
    x = data_augmentation(inputs)
    x = preprocess_input(x)
    x = base_model(x, training=False)
    x = global_average_layer(x)
    x = tf.keras.layers.Dropout(0.2)(x)
    outputs = prediction_layer(x)
    model = tf.keras.Model(inputs, outputs)

    # base_learning_rate = 0.0001
    base_learning_rate = 0.0025
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=base_learning_rate),
                  loss=tf.keras.losses.BinaryCrossentropy(from_logits=True),
                  metrics=['accuracy'])

    model.summary()

    initial_epochs = 10

    history = model.fit(train_dataset,
                        epochs=initial_epochs)

    base_model.trainable = True

    fine_tune_at = 100

    for layer in base_model.layers[:fine_tune_at]:
        layer.trainable = False

    model.summary()

    fine_tune_epochs = 10

    total_epochs = initial_epochs + fine_tune_epochs

    history_fine = model.fit(train_dataset, epochs=total_epochs, initial_epoch=history.epoch[-1])

    return model


def parse_function(filename, label):
    filename = path_to_media + filename
    image_string = tf.io.read_file(filename)
    image_decoded = tf.image.decode_jpeg(image_string, channels=3)
    image = tf.cast(image_decoded, tf.float32)
    image = tf.image.resize(image, [160, 160], preserve_aspect_ratio=False)
    return image, label


def dataset_by_filenames(project_id, photos, mode):
    filenames = list()
    labels = list()

    print(photos[0].__dict__.keys())

    if mode == "train":
        for photo in photos:
            filenames.append(str(photo.image))
            if photo.meta.get(project_id=project_id).match:
                labels.append(1)
            else:
                labels.append(0)
    elif mode == "prediction":
        for photo in photos:
            filenames.append(str(photo.image))
            labels.append(0)

    total_amount = len(labels)

    filenames = tf.constant(filenames)
    labels = tf.constant(labels)

    dataset = tf.data.Dataset.from_tensor_slices((filenames, labels))

    dataset = dataset.map(parse_function)
    dataset = dataset.batch(total_amount)

    print(type(dataset))

    return dataset


def join_prediction_dataset():
    prediction_dir = os.path.join('Onprediction')
    BATCH_SIZE = 32
    IMG_SIZE = (160, 160)
    prediction_dataset = tf.keras.utils.image_dataset_from_directory(prediction_dir,
                                                                     shuffle=True,
                                                                     batch_size=BATCH_SIZE,
                                                                     image_size=IMG_SIZE)
    return prediction_dataset


def Prediction(project_id, photos, user_name, model_name):
    photos = [photo for photo in photos if
              imghdr.what(path_to_media + str(photo.image)) in ['jpg', 'png', 'jpeg', 'gif', 'bmp']]

    model = model_preparation(user_name, model_name)
    prediction_dataset = dataset_by_filenames(project_id, photos, "prediction")
    AUTOTUNE = tf.data.AUTOTUNE

    prediction_dataset = prediction_dataset.prefetch(buffer_size=AUTOTUNE)

    image_batch, label_batch = prediction_dataset.as_numpy_iterator().next()
    predictions = model.predict_on_batch(image_batch).flatten()

    predictions = tf.nn.sigmoid(predictions)
    return predictions.numpy()
