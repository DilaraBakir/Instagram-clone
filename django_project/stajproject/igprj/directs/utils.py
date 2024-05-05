from django.contrib.auth.models import User
from django.db.models import Max
from .models import Message


def send_message(from_user, to_user, body):
    # sender to receiver (instance)
    message = Message(
        sender=from_user,
        receiver=to_user,
        body=body,
        is_read=True,
    )
    message.save()
    return message
    # to retrieve the latest messages for the given user, to group them by the receivers, and to calculate the number of unread messages for each user


def get_message(user):
    # .values for grouping the messages by the user who received them, aggregating to get the latest message and making it show the last
    messages = Message.objects.filter(sender=user).values("receiver").annotate(last=Max('date')).order_by("-last")
    users = [{
        'user': User.objects.get(pk=message['receiver']),
        'last': message['last'],
        'unread': Message.objects.filter(sender=user, receiver__pk=message['receiver'], is_read=False).count(),
    } for message in messages]

    return users