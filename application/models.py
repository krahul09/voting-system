import flask
from application import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Document):
    user_id     =   db.IntField( unique=True )
    voterid = db.StringField(unique=True)
    first_name  =   db.StringField( max_length=50 )
    last_name   =   db.StringField( max_length=50 )
    email       =   db.StringField( max_length=30, unique=True )
    password    =   db.StringField( )

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def get_password(self, password):
        return check_password_hash(self.password, password)    


class Constituency(db.Document):
    constituencyID   =   db.StringField( max_length=10)
    constituency       =   db.StringField( max_length=100 )
    candidate =   db.StringField()
    party     =   db.StringField()
    term = db.StringField()



class BlockChain(db.Document):
    user_id = db.IntField(unique=True)
    name  =   db.StringField(max_length=50)
    candidate = db.StringField(max_length=50)
    email = db.StringField(unique=True)
    party       =   db.StringField( )
    timestamp   =   db.StringField( )
    prevhash    =   db.StringField( )
    curhash     =   db.StringField( )