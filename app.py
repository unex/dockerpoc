import os
import asyncio
import uuid

from random import randint

from fastapi import FastAPI, Request, Depends, HTTPException, status
# from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse #, JSONResponse

from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.sessions import SessionMiddleware
from starlette_wtf import StarletteForm, CSRFProtectMiddleware, csrf_protect

from itsdangerous.url_safe import URLSafeSerializer

from passlib.context import CryptContext

from docker import Client

from database import Database

# DATABASE
DATABASE_URL = 'sqlite:///./app.db' # SQLite cuz I am lazy

# APP
SECRET_KEY = os.environ.get('SECRET_KEY', 'this_should_be_configured')
SERIALIZER = URLSafeSerializer(SECRET_KEY)

db = Database(DATABASE_URL)

app = FastAPI()
# app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY, session_cookie='hi-mom')
app.add_middleware(CSRFProtectMiddleware, csrf_secret=SECRET_KEY)

docker = Client()

# This would be a db table but I cannot be fucked
AVALIABLE_CONTAINERS = [
    {
        'image': 'nginx',
        'ports': ['80/tcp']
    }
]

USED_PORTS = [] # Also should be stored in the DB but fuck you ill populate it on startup

@app.on_event("startup")
async def startup():
    await db.connect()

    for c in await docker.containers.list(all=True): # eat my ass
        for port in c.Ports:
            USED_PORTS.append(port['PublicPort'])

@app.on_event("shutdown")
async def shutdown():
    await db.disconnect()
    await docker.close()

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse("error.html", {"request": request, "message": f'{exc.status_code}: {exc.detail}'}, status_code=exc.status_code)


async def user(request: Request):
    if 'user' in request.session:
        return await db.get_user(SERIALIZER.loads(request.session['user']))

    return None

async def check_owns_container(user, container_id):
    user_containers = await db.user_containers(user)

    if not container_id in user_containers:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return True

def random_port():
    while True:
        port = randint(49152, 65535)
        if port in USED_PORTS:
            continue

        USED_PORTS.append(port)
        return port


@app.get('/')
async def root(request: Request, user = Depends(user)):
    if not user:
        return templates.TemplateResponse('login.html', {'request': request, 'user': user, 'form': StarletteForm(request)})

    user_containers = await db.user_containers(user)
    containers = [c for c in await docker.containers.list(all=True) if c.Id in user_containers]

    return templates.TemplateResponse('home.html', {'request': request, 'user': user, 'containers': containers, 'form': StarletteForm(request), 'avaliable_containers': enumerate(AVALIABLE_CONTAINERS)})

@app.post('/login')
@csrf_protect
async def login(request: Request):
    form = await request.form()
    user = await db.verify_login(form.get('username'), form.get('password'))
    if not user:
        return templates.TemplateResponse('error.html', {'request': request, 'message': 'username or password incorrect'})

    request.session['user'] = SERIALIZER.dumps(user.id)
    # RedirectResponse will try to POST you to the root page
    # https://github.com/tiangolo/fastapi/issues/1498
    return RedirectResponse(url=app.url_path_for('root'), status_code=status.HTTP_303_SEE_OTHER)

@app.get('/logout')
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(app.url_path_for('root'))


# "A" "P" "I"
# Shits a proof of concept I'm not gonna bother with XHR
@app.post('/container/create')
@csrf_protect
async def create_user_container(request: Request, user = Depends(user)):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    form = await request.form()

    c = AVALIABLE_CONTAINERS[int(form['image'])]
    container = await docker.containers.create({
        'Image': c['image'],
        'HostConfig': {
            'PortBindings': {p: [{'HostPort': str(random_port())}] for p in c['ports']}
        }
    }, name = f"{user.username}-{c['image']}-{str(uuid.uuid4()).split('-')[0]}")

    await container.start()

    await db.add_user_container(user, container.Id)

    return RedirectResponse(url=app.url_path_for('root'), status_code=status.HTTP_303_SEE_OTHER)

@app.post('/container/{id}/{action}')
@csrf_protect
async def user_container_action(request: Request, id: str, action: str, user = Depends(user)):
    if not action in ['start', 'restart', 'stop', 'kill', 'remove']:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    await check_owns_container(user, id)

    container = await docker.containers.get(id=id)
    await getattr(container, action)() # this is cheating

    if action == 'remove':
        await db.remove_user_container(container.Id)

        for port in container.Ports:
            USED_PORTS.remove(port['PublicPort'])

    return RedirectResponse(url=app.url_path_for('root'), status_code=status.HTTP_303_SEE_OTHER)
