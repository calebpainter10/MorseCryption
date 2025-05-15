# =-- Dependencies --= #
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from typing import Literal
import datetime

Base = declarative_base()

# =-- Message --= #
class Message(Base):
    __tablename__= "messages"
    id = Column(Integer, primary_key=True)
    content = Column(String, nullable=False)
    direction = Column(String, nullable=False)
    sender_id = Column(Integer, ForeignKey('client.id'))
    receiver_id = Column(Integer, ForeignKey('client.id'))
    auth_key = Column(String, nullable=False)
    iv = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.now(datetime.UTC))

    sender = relationship("Client", foreign_keys=[sender_id]) # [sender_id] due to ambiguity
    receiver = relationship("Client", foreign_keys=[receiver_id]) # [receiver_id] due to ambiguity

# =-- CRUD Operations --= #
def create_message(content: str, direction: Literal["sent", "received"], sender_id: int, receiver_id: int, auth_key: str, iv: str) -> Message:
    """
    Create a new message in the messages table given the content, direction, sender ID, and receiver ID.
    :param content: The message content.
    :param direction: The direction ("sent" or "received") of the message.
    :param sender_id: The ID of the message's sender.
    :param receiver_id: The ID of the message's receiver.
    :param auth_key: The authorization key.
    :param iv: The message initialization vector (b64).
    :return: The message object.
    """
    message = Message(
        content=content,
        direction=direction,
        sender_id=sender_id,
        receiver_id=receiver_id,
        auth_key=auth_key,
        iv=iv
    )

    # Commit to DB
    session.add(message)
    session.commit()

    return message

def get_message_by_id(message_id):
    """
    Retrieve a message object given its ID.
    :param message_id: The ID of the message to query.
    :return: The message object.
    """
    message = session.get(Message, message_id)

    # Check if message exists
    if message is None:
        return None

    return message

def update_message(message_id, content: str=None, direction: Literal["sent", "received"]=None, sender_id: int=None, receiver_id: int=None, auth_key: str=None, iv: str=None):
    """
    Update a message in the messages table given its message ID, the content, direction, sender ID, and receiver ID.
    :param message_id: The ID of the message to update.
    :param content: The new message content.
    :param direction: The new direction ("sent" or "received") of the message.
    :param sender_id: The new message's sender ID.
    :param receiver_id: The new message's receiver ID.
    :param auth_key: The new authorization key.
    :param iv: The new message initialization vector (b64).
    :return: The updated message object.
    """
    message = session.get(Message, message_id)

    # Check if message exists
    if message is None:
        raise Exception("Message not found")

    # Account for unspecified fields
    if content is not None:
        message.content = content

    if direction is not None:
        message.direction = direction

    if sender_id is not None:
        message.sender_id = sender_id

    if receiver_id is not None:
        message.receiver_id = receiver_id

    if auth_key is not None:
        message.auth_key = auth_key

    # Commit to DB
    session.commit()

    return message

def delete_message(message_id):
    """
    Delete a message in the messages table given its message ID.
    :param message_id: The ID of the message to delete.
    :return: The deleted message object
    """
    message = session.get(Message, message_id)

    # Check if book exists
    if message is None:
        raise Exception("Message not found")

    # Commit to DB
    session.delete(message)
    session.commit()

    return message

# =-- Listing --= #
def list_all_messages():
    """
    List all messages in the messages table.
    :return: A list of message objects.
    """
    messages = session.query(Message).all()
    return messages

# =-- Client --= #
class Client(Base):
    __tablename__ = 'client'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    auth_key = Column(String, nullable=False)

    sent_messages = relationship("Message", foreign_keys='Message.sender_id', back_populates="sender")
    received_messages = relationship("Message", foreign_keys='Message.receiver_id', back_populates="receiver")

# =-- DB Init --= #
engine = create_engine('sqlite:///messaging.db')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# =-- CRUD Operations --= #
def create_or_get_client(name, auth_key):
    """
    Creates a client in the clients table given a name.
    :param name: The name of the new client.
    :param auth_key: The 16-byte authorization key in B64.
    :return: The client object.
    """
    # Create new client
    existing_client = get_client_by_name(name)
    if existing_client is None:
        client = Client(name=name, auth_key=auth_key)

        # Commit client
        session.add(client)
        session.commit()

        return client
    else:
        return existing_client

def get_client_by_id(client_id):
    """
    Returns a client object given a client ID.
    :param client_id: The ID of the client to query.
    :return: The client object of the requested client.
    """
    client = session.get(Client, client_id)

    # Check if client exists
    if not client:
        return None

    return client

def get_client_by_name(client_name):
    """
    Returns a client object given a client name, or None if it does not exist.
    :param client_name: The name of the requested client.
    :return: A client object, or None if it does not exist.
    """
    client = session.query(Client).filter_by(name=client_name).first()

    if not client:
        return None

    return client

def verify_client_by_name(client_name, auth_key):
    """
    Returns True/False depending on if the auth key is the correct key tied with the client name.
    :param client_name: The name of the client to retrieve
    :param auth_key: The authentication key to verify.
    :return: True or False
    """
    client = get_client_by_name(client_name)

    if not client:
        raise Exception('Client not found')

    if auth_key == client.auth_key:
        return True
    else:
        return False

def verify_client_by_id(client_id, auth_key):
    """
     Returns True/False depending on if the auth key is the correct key tied with the client ID.
    :param client_id: The ID of the client to retrieve.
    :param auth_key: The authentication key to verify.
    :return: True or False
    """
    client = get_client_by_id(client_id)

    if not client:
        raise Exception('Client not found')

    if auth_key == client.auth_key:
        return True
    else:
        return False


def update_client(client_id, new_name: str=None, new_auth_key: str=None):
    """
    Updates a client in the clients table given a name.
    :param client_id: The ID of the client to update.
    :param new_name: The new name of the client.
    :param new_auth_key: The new authorization key in B64.
    :return: The client object.
    """
    client = session.get(Client, client_id)

    # Check if client exists
    if client is None:
        raise Exception('Client not found')

    # Account for unspecified fields
    if new_name is not None:
        client.name = new_name
    if new_auth_key is not None:
        client.auth_key = new_auth_key

    # Commit to DB
    session.commit()

    return client

def delete_client(client_id):
    """
    Deletes a client from the clients table given a client ID.
    :param client_id: The ID of the client to delete.
    :return: The deleted client object.
    """
    client = session.get(Client, client_id)

    if client is None:
        raise Exception('Client not found')

    session.delete(client)
    session.commit()

    return client

# =-- Listing --= #
def list_clients():
    """
    Returns a list of all clients in the clients table.
    :return: A list of client objects.
    """
    clients = session.query(Client).all()
    return clients

def list_clients_messages(client: Client):
    """
    List all messages in the messages table given its client name.
    :param client: An object of the client to query
    :return: A list of messages.
    """
    messages = session.query(Message).filter_by(sender_id=client.id).all()

    return messages