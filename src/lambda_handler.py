from mangum import Mangum

from the_spymaster.asgi import application

handler = Mangum(application, lifespan="off")
