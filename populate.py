#!/user/bin/python
# -*- coding: utf-8 -*-

from time import sleep
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.functions import current_date, current_time, now
from database_setup import Base, Catalog, Item, User

engine = create_engine('sqlite:///catlog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create an special user
user1 = User(name="admin",
             picture='https://lh3.googleusercontent.com/-v_3iOVC5VI0/AAAAAAAAAAI/AAAAAAAAAAA/ye0_gnqSwI4/s120-c/photo.jpg',
             last_login = now())
session.add(user1)
session.commit()
sleep(2)

meat = Catalog(name = "Meat",
               last_edit = now(),
               user = user1,)
session.add(meat)
session.commit()
sleep(2)
beef = Item(name = "Beef",
            catalog = meat,
            picture = "https://upload.wikimedia.org/wikipedia/commons/6/60/Standing-rib-roast.jpg",
            description = '''Beef muscle meat can be cut into roasts, short ribs or steak (filet mignon, sirloin steak, rump steak, rib steak, rib eye steak, hanger steak, etc.). Some cuts are processed (corned beef or beef jerky), and trimmings, usually mixed with meat from older, leaner cattle, are ground, minced or used in sausages.''',
            user = user1)
session.add(beef)
session.commit()
sleep(2)

chicken = Item(name = "Chicken",
            catalog = meat,
            picture = "https://upload.wikimedia.org/wikipedia/commons/8/80/Rosemary_chicken.jpg",
            description = '''Breast: These are white meat and are relatively dry. Leg: Comprises two segments: the "drumstick" and the "thigh"; Wing: Often served as a light meal or bar food. Buffalo wings are a typical example. Comprises three segments: the "drumette", the middle "flat" segment, and the tip.''',
            user = user1)
session.add(chicken)
session.commit()
sleep(2)

pork = Item(name = "Pork",
            catalog = meat,
            picture = "https://upload.wikimedia.org/wikipedia/commons/4/49/Schweinebauch-2.jpg",
            description = '''Pork is eaten both freshly cooked and preserved. Curing extends the shelf life of the pork products. Ham, smoked pork, gammon, bacon and sausage are examples of preserved pork. ''',
            user = user1)
session.add(pork)
session.commit()
sleep(2)

lamb = Item(name = "Lamb",
            catalog = meat,
            picture = "https://upload.wikimedia.org/wikipedia/commons/8/8c/Lamb_meat_%281%29.jpg",
            description = '''Lamb is often sorted into three kinds of meat: forequarter, loin, and hindquarter. The forequarter includes the neck, shoulder, front legs, and the ribs up to the shoulder blade. The hindquarter includes the rear legs and hip. The loin includes the ribs between the two.Lamb chops are cut from the rib, loin, and shoulder areas. The rib chops include a rib bone; the loin chops include only a chine bone. Shoulder chops are usually considered inferior to loin chops; both kinds of chops are usually grilled. Breast of lamb (baby chops) can be cooked in an oven. ''',
            user = user1)
session.add(lamb)
session.commit()
sleep(2)


veg = Catalog(name = "Vegetable",
               last_edit = now(),
               user = user1,)
session.add(veg)
session.commit()
sleep(2)

tomato = Item(name = "Tomato",
            catalog = veg,
            picture = "https://upload.wikimedia.org/wikipedia/commons/8/88/Bright_red_tomato_and_cross_section02.jpg",
            description = '''The tomato is consumed in diverse ways, including raw, as an ingredient in many dishes, sauces, salads, and drinks. While it is botanically a berry fruit, it is considered a vegetable for culinary purposes, which has caused some confusion. ''',
            user = user1)
session.add(tomato)
session.commit()
sleep(2)

potato = Item(name = "Potato",
            catalog = veg,
            picture = "https://upload.wikimedia.org/wikipedia/commons/a/ab/Patates.jpg",
            description = u'''The potato was originally believed to have been domesticated independently in multiple locations, but later genetic testing of the wide variety of cultivars and wild species proved a single origin for potatoes in the area of present-day southern Peru and extreme northwestern Bolivia (from a species in the Solanum brevicaule complex), where they were domesticated approximately 7,000–10,000 years ago. Following centuries of selective breeding, there are now over a thousand different types of potatoes. ''',
            user = user1)
session.add(potato)
session.commit()
sleep(2)

lettuce = Item(name = "Lettuce",
            catalog = veg,
            picture = "https://upload.wikimedia.org/wikipedia/commons/d/da/Iceberg_lettuce_in_SB.jpg",
            description = '''Lettuce is most often used for salads, although it is also seen in other kinds of food, such as soups, sandwiches and wraps; it can also be grilled. One variety, the Woju or asparagus lettuce, is grown for its stems, which are eaten either raw or cooked. Lettuce is a rich source of vitamin K and vitamin A, and is a moderate source of folate and iron. Contaminated lettuce is often a source of bacterial, viral and parasitic outbreaks in humans, including E. coli and Salmonella. In addition to its main use as a leafy green, it has also gathered religious and medicinal significance over centuries of human consumption. ''',
            user = user1)
session.add(lettuce)
session.commit()
sleep(2)

fruit = Catalog(name = "Fruit",
               last_edit = now(),
               user = user1,)
session.add(fruit)
session.commit()
sleep(2)

apple = Item(name = "Apple",
            catalog = fruit,
            picture = "https://upload.wikimedia.org/wikipedia/commons/1/15/Red_Apple.jpg",
            description = '''Apples are an important ingredient in many desserts, such as apple pie, apple crumble, apple crisp and apple cake. They are often eaten baked or stewed, and they can also be dried and eaten or reconstituted (soaked in water, alcohol or some other liquid) for later use. When cooked, some apple varieties easily form a puree known as apple sauce. Apples are also made into apple butter and apple jelly. They are also used (cooked) in meat dishes. ''',
            user = user1)
session.add(apple)
session.commit()
sleep(2)

banana = Item(name = "Banana",
            catalog = fruit,
            picture = "https://upload.wikimedia.org/wikipedia/commons/d/de/Bananavarieties.jpg",
            description = '''Bananas are a staple starch for many tropical populations. Depending upon cultivar and ripeness, the flesh can vary in taste from starchy to sweet, and texture from firm to mushy. Both the skin and inner part can be eaten raw or cooked. The primary component of the aroma of fresh bananas is isoamyl acetate (also known as banana oil), which, along with several other compounds such as butyl acetate and isobutyl acetate, is a significant contributor to banana flavor. ''',
            user = user1)
session.add(banana)
session.commit()
sleep(2)

orange = Item(name = "Orange",
            catalog = fruit,
            picture = "https://upload.wikimedia.org/wikipedia/commons/7/7b/Orange-Whole-%26-Split.jpg",
            description = '''As with other citrus fruits, orange pulp is an excellent source of vitamin C, providing 64% of the Daily Value in a 100 g serving. Numerous other essential nutrients are present in low amounts. Oranges contain diverse phytochemicals, including carotenoids (beta-carotene, lutein and beta-cryptoxanthin), flavonoids (e.g. naringenin) and numerous volatile organic compounds producing orange aroma, including aldehydes, esters, terpenes, alcohols, and ketones. ''',
            user = user1)
session.add(orange)
session.commit()
sleep(2)

pear = Item(name = "Pear",
            catalog = fruit,
            picture = "https://upload.wikimedia.org/wikipedia/commons/c/cf/Pears.jpg",
            description = '''Pears are consumed fresh, canned, as juice, and dried. The juice can also be used in jellies and jams, usually in combination with other fruits or berries. Fermented pear juice is called perry or pear cider.''',
            user = user1)
session.add(lettuce)
session.commit()
sleep(2)

seafood = Catalog(name = "Seafood",
               last_edit = now(),
               user = user1,)
session.add(seafood)
session.commit()
sleep(2)

shrimp = Item(name = "Shrimp",
            catalog = seafood,
            picture = "https://upload.wikimedia.org/wikipedia/commons/e/e9/Camaron.jpg",
            description = '''As with other seafood, shrimp is high in calcium, iodine and protein but low in food energy. A shrimp-based meal is also a significant source of cholesterol, from 122 mg to 251 mg per 100 g of shrimp, depending on the method of preparation.''',
            user = user1)
session.add(shrimp)
session.commit()
sleep(2)

crab = Item(name = "Crab",
            catalog = seafood,
            picture = "https://upload.wikimedia.org/wikipedia/commons/8/8a/Gecarcinus_quadratus_%28Nosara%29.jpg",
            description = '''Crabs are prepared and eaten as a dish in several different ways all over the world. Some species are eaten whole, including the shell, such as soft-shell crab; with other species just the claws and/or legs are eaten. The latter is particularly common for larger crabs, such as the snow crab. Mostly in East Asian cultures, the roe of the female crab is also eaten, which usually appears orange or yellow in colour in fertile crabs.''',
            user = user1)
session.add(crab)
session.commit()
sleep(2)

pop = Catalog(name = "Pop",
               last_edit = now(),
               user = user1,)
session.add(pop)
session.commit()
sleep(2)

canadadry = Item(name = "Canada Dry Ginger Ale",
            catalog = pop,
            picture = "https://upload.wikimedia.org/wikipedia/commons/4/49/Canada_dry_crop.jpg",
            description = '''In 1904, McLaughlin created "Canada Dry Pale Ginger Ale"; three years later the drink was appointed to the Royal Household of the Governor General of Canada, and the label featuring a beaver atop a map of Canada was replaced with the present Crown and shield.''',
            user = user1)
session.add(canadadry)
session.commit()
sleep(2)

