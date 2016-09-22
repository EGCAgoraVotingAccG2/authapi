# This file is part of authapi.
# Copyright (C) 2016  Agora Voting SL <agora@agoravoting.com>

# authapi is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License.

# authapi  is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with authapi.  If not, see <http://www.gnu.org/licenses/>.

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from .models import AuthEvent, ACL
import json

def insert_or_update(cls, kwargs):
    l = cls.objects.filter(**kwargs)
    if len(l) == 0:
        obj = ACL(**kwargs)
        obj.save()

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def add_arguments(self, parser):
        parser.add_argument(
            'usersdata',
            nargs=1,
            type=str)

    def handle(self, *args, **options):
        users_data = json.loads(open(options['usersdata'], 'r').read())

        # process each user
        for udata in users_data:
            users = User.objects.filter(username=udata['username'])

            if len(users) == 0:
                # user doesn't exist -> create it
                db_user = User.objects.create_user(
                    username=udata['username'],
                    email=udata['email'],
                    is_active=udata.get('is_active', False),
                    is_admin=udata.get('is_admin', False),
                    is_staff=udata.get('is_admin', False)
                )
            else:
                # user exists -> update it
                db_user = users[0]
                db_user.email = udata['email']
                db_user.is_active=udata.get('is_active', False)
                db_user.is_admin=udata.get('is_admin', False)
                db_user.is_staff=udata.get('is_admin', False)

            # in any of the previous cases, save to DB
            db_user.save()

            # if password is set, update it
            if 'password' in udata:
                db_user.set_password(udata['password'])
                db_user.save()

            # if tlf is set, update it
            if 'tlf' in udata:
                db_user.userdata.tlf = udata['password']
                db_user.userdata.save()

            # make sure the user has permission to login as an admin
            insert_or_update(
                ACL,
                dict(
                    user=db_user.userdata,
                    perm='edit',
                    object_type='AuthEvent',
                    object_id=1
                )
            )

            # create each permission if needed
            for el in udata['election_permissions']:
                for perm in el['permissions']:
                  insert_or_update(
                      ACL,
                      dict(
                          user=db_user.userdata,
                          perm=perm,
                          object_type='AuthEvent',
                          object_id=int(el['election_id'])
                      )
                  )
