from mangum import Mangum

from the_spymaster.asgi import application

handle = Mangum(application, lifespan="off")
