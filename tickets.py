#!/usr/bin/python

# Copyright (c) 2014 Nikolay Yakovlev
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from gi.repository import Gtk, Gio, GdkPixbuf, Pango
import os
import base64
import ConfigParser
from dialogs import Settings
import constants


class Tickets():
    _database = '/home/nyakovlev/.config/tododo/tododo.db'
    done = []
    active = []

    def __init__(self):
        home_path = os.getenv("HOME")
        tododo_conf_folder = os.path.join(
            home_path,
            '.config',
            'tododo'
        )
        if not os.path.exists(tododo_conf_folder):
            os.mkdir(tododo_conf_folder)

        if not os.path.exists(Settings.get_db_path()):
            open(Settings.get_db_path(), 'a').close()

    def create_ticket(self, text, is_important):
        """Append to self.active"""
        self.active.append([0, is_important, text, text.split('\n')[0]])
        
        self._save()

    def delete_ticket(self, index):
        """We can remove only from self.done list"""
        del self.done[index]

        self._save()

    def update_ticket(self, index, text, is_important):
        self.active[index][constants.TEXT_INDEX] = text
        self.active[index][constants.IMPORTANT_INDEX] = is_important
        self.active[index][constants.HEADER_INDEX] = text.split('\n')[0]

        self._save()

    def done_ticket(self, index):
        """Move ticket from self.active to self.done"""
        ticket = self.active[index][:]
        ticket[0] = True
        self.done.append(ticket)
        del self.active[index]

        self._save()

    def undone_ticket(self, index):
        """Move ticket from self.done to self.active"""
        ticket = self.done[index][:]
        ticket[0] = False
        self.active.append(ticket)
        del self.done[index]

        self._save()

    def _save(self):
        """Save to file"""
        done_lines = []
        for ticket in self.done:
            is_important = '1' if ticket[constants.IMPORTANT_INDEX] is self.important else '0' 
            ticket_value = base64.b64encode(ticket[constants.TEXT_INDEX])
            done_lines.append("%s|%s|%s" % (1, is_important, ticket_value))

        active_lines = []
        for ticket in self.active:
            is_important = '1' if ticket[constants.IMPORTANT_INDEX] is self.important else '0' 
            ticket_value = base64.b64encode(ticket[constants.TEXT_INDEX])
            active_lines.append("%s|%s|%s" % (0, is_important, ticket_value))
       
        lines = "\n".join(done_lines) + "\n" + "\n".join(active_lines)
        with open(Settings.get_db_path(), 'w') as db:
            db.write(lines)

    def _load(self, pb, npb):
        """Load from file"""
        self.important = pb
        self.nonimportant = npb

        with open(Settings.get_db_path(), 'r') as tododo_db:
            tododo_db = tododo_db.read().splitlines()

            for line in tododo_db:
                if '|' not in line:
                    continue

                ticket = line.split('|')
                if len(ticket) == 2:
                    ticket.append('0')

                if ticket[constants.IMPORTANT_INDEX] == '0':
                    important_mark = npb
                elif ticket[constants.IMPORTANT_INDEX] == '1':
                    important_mark = pb

                ticket_value = base64.b64decode(ticket[constants.TEXT_INDEX])
                ticket_head = ticket_value.split('\n')[0]
                if ticket[constants.ACTIVITY_INDEX] == '1':
                    self.done.append([True, important_mark, ticket_value, ticket_head])
                elif ticket[0] == '0':
                    self.active.append([False, important_mark, ticket_value, ticket_head])