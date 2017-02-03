from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, Item, User

engine = create_engine('sqlite:///itemcatalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy user
User1 = User(name="Robo Barista", email="tinnyTim@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

# items for Rugby
category1 = Category(user_id=1, name="Rugby")
session.add(category1)
session.commit()

Item1 = Item(user_id=1,
             name="GILBERT GRAYS OF CAM TOP 14 OFFICIAL REPLICA RUGBY BALL",
             description="Designed for rugby training and matches. This rugby ball is the official TOP 14 ball.",
             category=category1)
session.add(Item1)
session.commit()

Item2 = Item(user_id=1,
             name="CANTERBURY STAMPEDE CLUB ADULT BLACK",
             description="Designed for playing rugby. Perfect for forwards (8 studs, reinforced at heel and under arch of foot).",
             category=category1)
session.add(Item2)
session.commit()

Item3 = Item(user_id=1,
             name="ADIDAS FRANCE RUGBY AWAY SHIRT",
             description="Designed for playing rugby but also for fans. This rugby shirt is the French team's official"
                         " replica away shirt.",
             category=category1)
session.add(Item3)
session.commit()

# items for Snowboarding
category2 = Category(user_id=1, name="Snowboarding")
session.add(category2)
session.commit()


Item1 = Item(user_id=1,
             name="WED'ZE DREAMSCAPE 700 POWDER SNOWBOARD",
             description="Designed for expert snowboarders looking for a powerful and dynamic snowboard on groomed "
                         "sloped with great buoyancy on powdery snow.",
             category=category2)
session.add(Item1)
session.commit()

Item2 = Item(user_id=1,
             name="WED'ZE G-TMAX 400 ALL WEATHER SKI GOGGLES",
             description="The G-TMAX 400 allows you to ski in the sun or cloudy conditions, the lens is brown and treated"
                         " with high quality anti-fogging. In size L, corrective lens of 130 mm wide max can be used",
             category=category2)
session.add(Item2)
session.commit()

Item3 = Item(user_id=1,
             name="WED'ZE STREAM 500 ADULT SKI HELMET - RACE",
             description="Thanks to its rigid ears and head circumference adjustment system, the helmet ensures a "
                         "good hold, better protection and great warmth.",
             category=category2)
session.add(Item3)
session.commit()


# items for Boxing
category3 = Category(user_id=1, name="Boxing")
session.add(category3)
session.commit()

Item1 = Item(user_id=1,
             name="EVERLAST BOXING GLOVES",
             description="Designed for boxing training. Elasticity, comfort, and durability.",
             category=category3)
session.add(Item1)
session.commit()

Item2 = Item(user_id=1,
             name="DOMYOS BOXING FREE STANDING PUNCH BAG",
             description="Designed for punch/kick training for advanced athletes: boxing, Muay Thai, kickboxing, "
                         "full-contact karate.",
             category=category3)
session.add(Item2)
session.commit()

Item3 = Item(user_id=1,
             name="DOMYOS DOUBLE ADULT MOUTH GUARD",
             description="Designed for reducing the risk of mouth injury when doing combat sports (boxing, martial arts).",
             category=category3)
session.add(Item3)
session.commit()


# items for Surf
category4 = Category(user_id=1, name="Surf")
session.add(category4)
session.commit()

Item1 = Item(user_id=1,
             name="BIC 7'3\" DURA-TEC MINI MALIBU SURFBOARD",
             description="Designed for beginner surfers weighing less than 70 kg or intermediate level surfers seeking "
                         "versatility and an easy access board.",
             category=category4)
session.add(Item1)
session.commit()

Item2 = Item(user_id=1,
             name="TRIBORD 900 M 4/3MM FZ SURF SUIT BLACK",
             description="Designed for intensive surfers and bodyboarders in cold water, between 12C and 17C. "
                         "Session length: up to 3 hours.",
             category=category4)
session.add(Item2)
session.commit()


Item3 = Item(user_id=1,
             name="TRIBORD 100 WOMEN'S SHORTY SUIT GREEN",
             description="Designed for female surfers seeking warmth and a low price for use in water over 20C.",
             category=category4)
session.add(Item3)
session.commit()

Item4 = Item(user_id=1,
             name="TRIBORD BASIC L PRINT TOWEL - ARROW",
             description="Designed for drying yourself off and getting changed before and after surfing. "
                         "Very soft and absorbent, 100% cotton.",
             category=category4)
session.add(Item4)
session.commit()

# items for Nutrition
category5 = Category(user_id=1, name="Nutrition")
session.add(category5)
session.commit()

Item1 = Item(user_id=1,
             name="100% PURE WHEY PROTEIN - 2000G",
             description="High quality Whey Protein Complex (Isolate primary source) to support lean muscle growth.",
             category=category5)
session.add(Item1)
session.commit()

Item2 = Item(user_id=1,
             name="GREEN KICK",
             description="Pre-training caffeine-guarana drink with taurine to kick-start your training",
             category=category5)
session.add(Item2)
session.commit()

Item3 = Item(user_id=1,
             name="CREATINE CAPSULES",
             description="100% pure Creatine Monohydrate. For better performance during strength training and other "
                         "intense physical activities. Increased muscle volume due to increased water "
                         "retention in muscle cells",
             category=category5)
session.add(Item3)
session.commit()

print "added items!"


# items for Fitness
category6 = Category(user_id=1, name="Fitness")
session.add(category6)
session.commit()

Item1 = Item(user_id=1,
             name="DOMYOS 10 KG DUMBBELLS SET",
             description="Designed for weight training with dumbbells",
             category=category6)
session.add(Item1)
session.commit()


Item2 = Item(user_id=1,
             name="DOMYOS COMFORT FITNESS MAT - GREY",
             description="Designed for daily Pilates, stretching and other gentle gymnastics exercises at home.",
             category=category6)
session.add(Item2)
session.commit()


Item3 = Item(user_id=1,
             name="ADIDAS TRAINING SKIPPING ROPE",
             description="Designed for fitness and warming up before any type of sports activity.",
             category=category6)
session.add(Item3)
session.commit()
