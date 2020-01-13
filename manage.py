#!/usr/bin/env python3
from flask_script import Manager, Server
from mnlookup import create_app, scheduler


class CustomServer(Server):
    def __call__(self, app, *args, **kwargs):
        scheduler.start()
        #Hint: Here you could manipulate app
        return Server.__call__(self, app, *args, **kwargs)


manager = Manager(create_app)
#manager.add_command('db', MigrateCommand)
manager.add_command('runserver', CustomServer())

if __name__ == '__main__':
    manager.run()
