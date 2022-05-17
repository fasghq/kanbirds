from marshmallow import fields, Schema
import datetime
from . import db, bcrypt
from marshmallow import fields, Schema

class BirdModel(db.Model):
  __tablename__ = 'kanbirds_full'

  bird_id = db.Column(db.Integer, primary_key=True)
  theme = db.Column(db.String(128))
  head = db.Column(db.String(128))
  eyes = db.Column(db.String(128))
  body = db.Column(db.String(128))
  tail = db.Column(db.String(128))
  wingLeft = db.Column(db.String(128))
  wingRight = db.Column(db.String(128))
  feet = db.Column(db.String(128))
  beak = db.Column(db.String(128))
  trait_score = db.Column(db.Float)
  trait_rank = db.Column(db.Integer)
  set_score = db.Column(db.Float)
  set_rank = db.Column(db.Integer)
  edition_score = db.Column(db.Float)
  edition_rank = db.Column(db.Integer)
  weighted_score = db.Column(db.Float)
  weighted_rank = db.Column(db.Integer)
  birds_weighted_normalized_scores = db.Column(db.Float)
  week_trade_score = db.Column(db.Float)

  def __init__(self, data):
    self.bird_id = data.get('bird_id')
    self.theme = data.get('theme')
    self.head = data.get('head')
    self.eyes = data.get('eyes')
    self.body = data.get('body')
    self.tail = data.get('tail')
    self.wingLeft = data.get('wingLeft')
    self.wingRight = data.get('wingRight')
    self.feet = data.get('feet')
    self.beak = data.get('beak')
    self.trait_score = data.get('trait_score')
    self.trait_rank = data.get('trait_rank')
    self.set_score = data.get('set_score')
    self.set_rank = data.get('set_rank')
    self.edition_score = data.get('edition_score')
    self.edition_rank = data.get('edition_rank')
    self.weighted_score = data.get('weighted_score')
    self.weighted_rank = data.get('weighted_rank')
    self.birds_weighted_normalized_scores = data.get('birds_weighted_normalized_scores')
    self.week_trade_score = data.get('week_trade_score')

  def save(self):
    db.session.add(self)
    db.session.commit()

  def update(self, data):
    for key, item in data.items():
      setattr(self, key, item)
    #self.modified_at = datetime.datetime.utcnow()
    db.session.commit()

  def delete(self):
    db.session.delete(self)
    db.session.commit()

  @staticmethod
  def get_all_birds():
    return BirdModel.query.all()

  @staticmethod
  def get_one_bird(id):
    return BirdModel.query.get(id)

  
  def __repr(self):
    return '<id {}>'.format(self.id)

  def __generate_hash(self, password):
    return bcrypt.generate_password_hash(password, rounds=10).decode("utf-8")
  
  def check_hash(self, password):
    return bcrypt.check_password_hash(self.password, password)

class BirdSchema(Schema):
  bird_id = fields.Int(required=True)
  theme = fields.Str(dump_only=True)
  head = fields.Str(dump_only=True)
  eyes = fields.Str(dump_only=True)
  body = fields.Str(dump_only=True)
  tail = fields.Str(dump_only=True)
  wingLeft = fields.Str(dump_only=True)
  wingRight = fields.Str(dump_only=True)
  feet = fields.Str(dump_only=True)
  beak = fields.Str(dump_only=True)
  trait_score = fields.Float(dump_only=True)
  trait_rank = fields.Int(dump_only=True)
  set_score = fields.Float(dump_only=True)
  set_rank = fields.Int(dump_only=True)
  edition_score = fields.Float(dump_only=True)
  edition_rank = fields.Int(dump_only=True)
  weighted_score = fields.Float(dump_only=True)
  weighted_rank = fields.Int(dump_only=True)
  birds_weighted_normalized_scores = fields.Float(dump_only=True)
  week_trade_score = fields.Float(dump_only=True)