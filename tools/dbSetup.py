# from https://pythonspot.com/orm-with-sqlalchemy/
# https://www.fullstackpython.com/sqlalchemy.html
# https://docs.sqlalchemy.org/en/14/orm/

from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Integer, String
from sqlalchemy import Date, Time, DateTime, TIMESTAMP

from sqlalchemy.schema import Table, MetaData
from sqlalchemy.schema import DropTable, DropConstraint

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import sessionmaker

from sqlalchemy.exc import IntegrityError

from datetime import datetime
import sys

import pandas as pd
import json

# see https://nitratine.net/blog/post/how-to-hash-passwords-in-python/
import hashlib
import os
import random
import hashlib

######### Notes #############
##Users familiar with the syntax of CREATE TABLE may notice
##that the VARCHAR columns were generated without a length;
##on SQLite and PostgreSQL, this is a valid datatype,
##but on others, it’s not allowed. So if running this tutorial
##on one of those databases, and you wish to use SQLAlchemy to
##issue CREATE TABLE, a “length” may be provided to the String type as below:
##Column(String(50))

## Tables ##
# config. for company (single row!)
# id, organisation, contact name, email, phone, www
# providers
#   id, name, info, city, plz, country, street, streetnum, geo, email, phone, www

# categories
#   id, name, color, iconUrl

# audience # zeilgruppe
#   id, type

# events
#   id, title,date,time,cost (normally 0), category, provider id, category id, audiency id

# tickets
#   id, avail, reserved, limit,  event id

# pending (unfinished reservations)
#   id, count, date, user_id, event_id

# codes
#   id, count, ticket id, user id
#   all fields => hash => qrcode => base64

# users
# 2 modes, normal and anonymous
# anon: mode = 0, pwd is totp, email is email hash, access is current timestamp
# named: mode = 1, pwd is encrypted pwd, email is plaintext email, access  is current timestamp
#   username is mailhash or random hash for client on totp challenge to improve security
# normally search user by email (hash or plaintext), only with totp search username

TABLES = [
    "config",
    "providers",
    "categories",
    "events",
    "tickets",
    "codes",
    "users"
    ]

# initialize
DROP_ALL = True
USE_SQLITE = False

MODE = 0 # anonymous
######### Part 1 ############

if USE_SQLITE:
    engine = create_engine('sqlite:///lerninseln.db', echo=False)
else:
    engine = create_engine('mysql://lerninseln:lerninseln@localhost/lerninseln', echo=True)

Base = declarative_base()

# to drop the table initially,
# check if it exists via schema metadata

if DROP_ALL:
    metadata1 = MetaData()
    metadata1.reflect(bind=engine)
    for table in reversed(metadata1.sorted_tables):
        #engine.execute(table.delete()) # deletes content, but not table
        Base.metadata.drop_all(engine, [table], checkfirst=True)
    print("All tables dropped")


metadata = MetaData()
metadata.reflect(bind=engine)

########################################################################
class Config(Base):
    """"""
    __tablename__ = "config"
 
    id = Column(Integer, primary_key=True)
    organisation = Column(String(255), nullable=False, unique=True)
    contactName = Column(String(255))
    www = Column(String(255))
    phone = Column(String(255))
    email = Column(String(255))
    mode = Column(Integer)

    #----------------------------------------------------------------------
    def __init__(self, organisation, name, www, email, phone, mode=0):
        """"""
        self.organisation = organisation
        self.contactName = name
        self.www = www
        self.email = email
        self.phone = phone
        self.mode = mode

########################################################################
class User(Base):
    """"""
    __tablename__ = "user"
 
    id = Column(Integer, primary_key=True)
    username = Column(String(255), nullable=False, unique=True)
    firstname = Column(String(255))
    lastname = Column(String(255))
    emailOrHash = Column(String(255), nullable=False, unique=True)
    # if hash, we use something like
    # like hashlib.sha256(email.encode("utf-8")).hexdigest()
    pwdOrTotp = Column(String(255), nullable=False)
    access = Column(TIMESTAMP,default=0)
    mode = Column(Integer, default = 0) # 1: mail/pwd 0: hash/totp

    #----------------------------------------------------------------------
    def __init__(self, username, firstname, lastname, email, pwd, access, mode=0):
        """"""
        self.username = username
        self.firstname = firstname
        self.lastname = lastname
        self.emailOrHash = email
        self.pwdOrTotp = pwd
        self.access = access
        self.mode = mode

########################################################################
class Provider(Base):
    """"""
    __tablename__ = "provider"
 
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False,unique=True)
    info = Column(String(4096))
    country = Column(String(255))
    city = Column(String(255), nullable=False)
    citycode = Column(String(255), nullable=False)
    street = Column(String(255), nullable=False)
    streetnum = Column(String(255))
    latlon = Column(String(255)) # json array
    person = Column(String(255))
    email = Column(String(255), nullable=False)
    phone = Column(String(255))
    www = Column(String(255), nullable=False)


    #----------------------------------------------------------------------
    def __init__(self, name, info, country, city, citycode, street,
                 streetnum, latlon, person, email, phone, www):
        """"""
        self.name = name
        self.info = info
        self.country = country
        self.city = city
        self.citycode = citycode
        self.street = street
        self.streetnum = streetnum
        self.latlon = latlon
        self.person = person
        self.email = email
        self.phone = phone
        self.www = www


########################################################################
class Category(Base):
    """"""
    __tablename__ = "category"
 
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    color = Column(String(255), nullable=False)
    iconUrl = Column(String(255))
                            

    #----------------------------------------------------------------------
    def __init__(self, name,color, iconUrl):
        """"""
        self.name = name
        self.color = color
        self.iconUrl = iconUrl

########################################################################
class Audience(Base):
    """"""
    __tablename__ = "audience"
 
    id = Column(Integer, primary_key=True)
    description = Column(String(1024), nullable=False, unique=True)
                            

    #----------------------------------------------------------------------
    def __init__(self, description):
        """"""
        self.description = description

########################################################################
class Code(Base):
    """"""
    __tablename__ = "code"
 
    id = Column(Integer, primary_key=True)
    count = Column(Integer, nullable=False)

    
    ticket_id = Column(Integer, ForeignKey('ticket.id', ondelete="CASCADE"), nullable=False)
    ticket = relationship("Ticket", back_populates="code")
                            
    user_id = Column(Integer, ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    user = relationship("User", back_populates="code")
                            

    #----------------------------------------------------------------------
    def __init__(self, count, ticket, user):
        """"""
        self.count = count
        self.ticket_id = ticket
        self.user_id = user


########################################################################
class Event(Base):
    """"""
    __tablename__ = "event"
 
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    date = Column(String(255), nullable=False)
    time = Column(String(255), nullable=False)
    cost = Column(Integer, nullable=False)
    costinfo = Column(String(255))

    provider_id = Column(Integer, ForeignKey('provider.id', ondelete="CASCADE"), nullable=False)
    provider = relationship("Provider", back_populates="event")

    category_id = Column(Integer, ForeignKey('category.id', ondelete="CASCADE"), nullable=False)
    category = relationship("Category", back_populates="event")
                            
    audience_id = Column(Integer, ForeignKey('audience.id', ondelete="CASCADE"), nullable=False)
    audience = relationship("Audience", back_populates="event")
                            

    #----------------------------------------------------------------------
    def __init__(self, title, date, time, cost, costinfo, provider, category, audience):
        """"""
        self.title = title
        self.date = date
        self.time = time
        self.cost = cost
        self.costinfo = costinfo
        self.provider_id = provider
        self.category_id = category
        self.audience_id = audience



########################################################################
class Ticket(Base):
    """"""
    __tablename__ = "ticket"
 
    id = Column(Integer, primary_key=True)
    avail = Column(Integer, nullable=False)  # cannot use not nullable on ints from 0
    reserved = Column(Integer, nullable=False)
    limit = Column(Integer, default=1)
    event_id = Column(Integer, ForeignKey('event.id', ondelete="CASCADE"), nullable=False)
    # next one only for sqlalch orm to get access to addr.user.<key>
    event = relationship("Event", back_populates="ticket")
                            

    #----------------------------------------------------------------------
    def __init__(self, avail, reserved, event, limit=1):
        """"""
        self.avail = avail
        self.limit = limit
        self.reserved = reserved
        self.event_id = event

########################################################################
class Pending(Base):
    """"""
    __tablename__ = "pending"
 
    id = Column(Integer, primary_key=True)
    count = Column(Integer, nullable=False)  
    date = Column(DateTime, nullable=False)

    event_id = Column(Integer, ForeignKey('event.id', ondelete="CASCADE"), nullable=False)
    event = relationship("Event", back_populates="pending")
                            
    user_id = Column(Integer, ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    user = relationship("User", back_populates="pending")
                            

    #----------------------------------------------------------------------
    def __init__(self, count, date, event, user):
        """"""
        self.count = count
        self.date = date
        self.event_id = event
        self.user_id = user

########################################################################

# see above, only python
User.pending = relationship("Pending", order_by=Pending.id, \
    back_populates="user",cascade="all, delete, delete-orphan")

Event.pending = relationship("Pending", order_by=Pending.id, \
    back_populates="event",cascade="all, delete, delete-orphan")


Event.ticket = relationship("Ticket", order_by=Ticket.id, \
    back_populates="event",cascade="all, delete, delete-orphan")


Ticket.code = relationship("Code", order_by=Code.id, \
    back_populates="ticket",cascade="all, delete, delete-orphan")

User.code = relationship("Code", order_by=Code.id, \
    back_populates="user",cascade="all, delete, delete-orphan")


Provider.event = relationship("Event", order_by=Event.id, \
    back_populates="provider",cascade="all, delete, delete-orphan")

Category.event = relationship("Event", order_by=Event.id, \
    back_populates="category",cascade="all, delete, delete-orphan")

Audience.event = relationship("Event", order_by=Event.id, \
    back_populates="audience",cascade="all, delete, delete-orphan")


##############################
# create tables
Base.metadata.create_all(engine)


######### Part 2 ############
# create a Session
Session = sessionmaker(bind=engine)
session = Session()


if DROP_ALL:
    # read initial providers
    p = pd.read_csv("lernorte1.csv",encoding="utf-8")
    def geo(x):
        return json.dumps({"lat":x.lat,"lon":x.lon})
    # create geo string
    p["geo"] = p.apply(geo,axis=1)

    for r in p.itertuples():
        #print(r)
        # try catch works, but creates an id on every attempt, so
        # sequence is no longer monotoneous
##        try:
##            provider = Provider(r.Name,r.description,"Deutschland",r.Ort,r.PLZ,
##                                " ".join(r.Strasse.split(" ")[:-1]),r.Strasse.split(" ")[-1],
##                                r.geo,"","","","")
##            session.add(provider)
##            session.commit()
##            print("Provider inserted ",r.Name)
##            
##        # check for integrity error due to dupications
##        except IntegrityError:
##            print("Duplicate provider",r.Name)
##            # important to rollback, else cannot complete
##            session.rollback()
##            pass # check audience and category still ##continue
##

        if None == session.query(Provider).filter(Provider.name == r.Name).first():
            provider = Provider(r.Name,r.description,"Deutschland",r.Ort,r.PLZ,
                                " ".join(r.Strasse.split(" ")[:-1]),r.Strasse.split(" ")[-1],
                                r.geo,"","","","")
            session.add(provider)
            session.commit()
            print("Provider inserted ",r.Name)

        # alternative was to check existence
        # if OK, check category and audience
        if None == session.query(Category).filter(Category.name == r.Beschreibung).first():
            print("Insert category: ",r.Beschreibung)
            category = Category(r.Beschreibung,"#00ff00","")
            session.add(category)
            session.commit()
            
        if None == session.query(Audience).filter(Audience.description == r.Typ).first():
            print("Insert audience: ",r.Typ)
            audiency = Audience(r.Typ)
            session.add(audiency)
            session.commit()
            

######### generate config ########
config = Config("OK Lab Karlsruhe",
          "Andreas Kugel",
          "https://ok-lab-karlsruhe.de",
          "info@ok-lab-karlsruhe.de",
          "",
          MODE
          )
session.add(config)
session.commit()

######### generate some users ########

if MODE != 0:
    USERS = [
        ("user1","first1","last1","email1@nowhe.re","1234"),
        ("user2","first2","last1","email2@nowhe.re","12345"),
        ("user3","first","last2","email3@nowhe.re","123456")
        ]

    salt = os.urandom(32) # Remember this. 32 bytes

    for u in USERS:
        key = hashlib.pbkdf2_hmac(
            'sha256', # The hash digest algorithm for HMAC
            u[4].encode('utf-8'), # Convert the password to bytes
            salt, # Provide the salt
            100000 # It is recommended to use at least 100,000 iterations of SHA-256 
        )
        pwd = salt + key
        hexPwd = pwd.hex()
        user = User(*u[:-1],hexPwd,0)
        # creating timestamp like
        # datetime.datetime.timestamp(datetime.datetime.now(datetime.timezone.utc))
        try:
            session.add(user)
            session.commit()
        except IntegrityError:
            print("Duplication on user",u)
            # important to rollback, else cannot complete
            session.rollback()
            continue # check audience and category still ##continue
        print("New user: ",u[0])

        # verify pwd
        p = bytes.fromhex(hexPwd)
        s = bytes(p[:32])
        k = bytes(p[32:])
        new_key = hashlib.pbkdf2_hmac(
        'sha256',
        u[4].encode('utf-8'), # Convert the password to bytes
        s, 100000 )
        print("Pwd verified: ", new_key == k)

    

######### generate some event ########

EVENT_TITLES = ["Schach","Musik","Sport","Robots"]
for e in range(20):
    event = Event(EVENT_TITLES[random.randint(0,len(EVENT_TITLES))-1],
                  "2021-" + f'{random.randint(6,12):02}' + "-" + f'{random.randint(1,28):02}',
                  f'{random.randint(1,24):02}' + ":00",
                  0,"Kostenlos",
                  random.randint(1,50),
                  random.randint(1,3),
                  random.randint(1,3)
                  )
    session.add(event)
    session.commit()
    print("New event: ",e)

######### generate some tickets ########


for t in range(1,20):  
    ticket = Ticket(random.randint(1,30),0,random.randint(1,20))
    session.add(ticket)
    session.commit()
    print("New ticket: ",t)


######### generate some pendings ########

now = str(datetime.now()) #.strftime('%Y-%m-%d %H:%M:%S'))
# need users for pending items
if MODE != 0:
    PENDING = [
        (1,now,1,1),
        (2,now,2,3),
        (1,now,3,2)
        ]

    for p in PENDING:
        pending = Pending(*p)
        session.add(pending)
        session.commit()
        print("New pending: ",p)



######### Part 3 ############

# Read objects  
for u in session.query(User).order_by(User.id):
    print (u.firstname, u.lastname)

for p in session.query(Provider).order_by(Provider.id):
    print (p.name)
    # optional, see above
    # print (a.user.username)

sys.exit()

######### Part 4 ############

# Select objects  
for u in session.query(User).filter(User.firstname == 'Eric'):
    print (u.firstname, u.lastname)
    session.delete(u)

######### Part 5 ############
# Delete objects with cascade. should delete addr too
for u in session.query(User).filter(User.id == 1):
    print (u.firstname, u.lastname)
    session.delete(u)

# not sure if needed ...
#session.commit()

for a in session.query(Addr).order_by(Addr.id):
    print (a.addr, a.email, a.user_id)


