from bottle import Bottle, request
from bottle.ext import sqlalchemy
from datetime import datetime, timedelta
from . import config
from . import db
from .db import CryptoKey

app = Bottle()
app.install(sqlalchemy.Plugin(
    db.engine, # SQLAlchemy engine created with create_engine function.
    db.Base.metadata, # SQLAlchemy metadata, required only if create=True.
    keyword='db', # Keyword used to inject session database in a route (default 'db').
    create=True, # If it is true, execute `metadata.create_all(engine)` when plugin is applied (default False).
    commit=True, # If it is true, plugin commit changes after route is executed (default True).
))

def validate_request(r, fields):
    message = None
    if not r:
        message = "no params given"
    if not message:
        for field in fields:
            if field not in r:
                message = "missing mandatory parameter '%s'" % field
                break
    if message:
        return {
            'result' : 'bad request',
            'message' : message,
        }

def find_key(db, id):
    return db.query(CryptoKey).filter(CryptoKey.id == id).first()

def refresh_key(ck):
    ck.attempts = config.retrieve_attempts
    ck.expires = datetime.now() + timedelta(seconds=config.expire_interval)

@app.post('/store')
def store(db):
    r = request.json
    err = validate_request(r, ['id', 'pin', 'key'])
    if err:
        return err

    ck = find_key(db, r['id']) or CryptoKey(id=r['id'])
    ck.pin = r['pin']
    ck.key = r['key']
    refresh_key(ck)

    db.add(ck)

    return {
        'result' : 'ok',
    }

@app.post('/retrieve')
def retrieve(db):
    r = request.json
    err = validate_request(r, ['id', 'pin'])
    if err:
        return err

    ck = find_key(db, r['id'])
    if not ck or datetime.now() > ck.expires:
        if ck:
            db.delete(ck)
        return { 'result' : 'not found' }

    if ck.pin != r['pin']:
        ck.attempts -= 1
        if ck.attempts < 1:
            db.delete(ck)
        return { 'result' : 'invalid pin' }

    refresh_key(ck)
    return {
        'result' : 'ok',
        'key' : ck.key,
    }
