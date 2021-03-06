from peewee import *

from Util import Configuration
from Util.Enums import ReminderStatus
from database.DBFields import TinyIntField

connection = MySQLDatabase(Configuration.get_master_var("DATABASE_NAME"),
                           user=Configuration.get_master_var("DATABASE_USER"),
                           password=Configuration.get_master_var("DATABASE_PASS"),
                           host=Configuration.get_master_var("DATABASE_HOST"),
                           port=Configuration.get_master_var("DATABASE_PORT"), use_unicode=True, charset="utf8mb4")


class EnumField(IntegerField):
    """This class enables an Enum field for Peewee"""

    def __init__(self, choices, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.choices = choices

    def db_value(self, value):
        return value.value

    def python_value(self, value):
        return self.choices(value)

class LoggedMessage(Model):
    messageid = BigIntegerField(primary_key=True)
    content = CharField(max_length=2000, collation="utf8mb4_general_ci", null=True)
    author = BigIntegerField()
    channel = BigIntegerField()
    server = BigIntegerField()
    type = TinyIntField(null=True)
    pinned = BooleanField(default=False)

    class Meta:
        database = connection


class LoggedAttachment(Model):
    id = BigIntegerField(primary_key=True)
    name = CharField(max_length=100)
    isImage = BooleanField()
    messageid = ForeignKeyField(LoggedMessage, backref='attachments', column_name='messageid')

    class Meta:
        database = connection


class CustomCommand(Model):
    id = PrimaryKeyField()
    serverid = BigIntegerField()
    trigger = CharField(max_length=20, collation="utf8mb4_general_ci")
    response = CharField(max_length=2000, collation="utf8mb4_general_ci")

    class Meta:
        database = connection


class Infraction(Model):
    id = PrimaryKeyField()
    guild_id = BigIntegerField()
    user_id = BigIntegerField()
    mod_id = BigIntegerField()
    type = CharField(max_length=10, collation="utf8mb4_general_ci")
    reason = CharField(max_length=2000, collation="utf8mb4_general_ci")
    start = TimestampField()
    end = TimestampField(null=True)
    active = BooleanField(default=True)

    class Meta:
        database = connection


class Reminder(Model):
    id = PrimaryKeyField()
    user_id = BigIntegerField()
    channel_id = BigIntegerField()
    guild_id = CharField(max_length=20)
    message_id = BigIntegerField()
    dm = BooleanField()
    to_remind = CharField(max_length=1800, collation="utf8mb4_general_ci")
    send = TimestampField()
    time = TimestampField()
    status = EnumField(choices=ReminderStatus)

    class Meta:
        database = connection


class Raid(Model):
    id = PrimaryKeyField()
    guild_id = BigIntegerField()
    start = TimestampField()
    end = TimestampField(null=True)

    class Meta:
        database = connection


class Raider(Model):
    id = PrimaryKeyField()
    raid = ForeignKeyField(Raid, backref="raiders", column_name="raid_id")
    user_id = BigIntegerField()
    joined_at = TimestampField()

    class Meta:
        database = connection


class RaidAction(Model):
    id = PrimaryKeyField()
    raider = ForeignKeyField(Raider, backref="actions_taken", column_name="raider_id")
    action = CharField(max_length=20)
    infraction = ForeignKeyField(Infraction, backref="RaiderAction", column_name="infraction_id", null=True)

    class Meta:
        database = connection


def init():
    global connection
    connection.connect()
    connection.create_tables([LoggedMessage, CustomCommand, LoggedAttachment, Infraction, Reminder, Raid, RaidAction, Raider])
    connection.close()
