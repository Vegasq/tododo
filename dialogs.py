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

from gi.repository import Gtk, GdkPixbuf
import os
import ConfigParser


class Settings(Gtk.Dialog):
    STORAGE = 'STORAGE'
    DB = 'db_path'
    FONT_SIZE = 'font_size'

    DB_FILENAME = 'tododo.db'

    @staticmethod
    def get_config_path():
        home_path = os.getenv("HOME")
        return os.path.join(
            home_path,
            '.config',
            'tododo',
            'tododo.conf'
        )

    @staticmethod
    def get_settings():
        config = ConfigParser.ConfigParser()
        config.read(Settings.get_config_path())

        if Settings.STORAGE not in config.sections():
            config.add_section(Settings.STORAGE)

        try:
            config.get(Settings.STORAGE, Settings.DB)
        except ConfigParser.NoOptionError:
            home_path = os.getenv("HOME")
            config.set(Settings.STORAGE, Settings.DB, os.path.join(
                home_path,
                '.config',
                'tododo',
                'tododo.db'
            ))

        try:
            config.get(Settings.STORAGE, Settings.FONT_SIZE)
        except ConfigParser.NoOptionError:
            config.set(Settings.STORAGE, Settings.FONT_SIZE, '10')

        return config

    @staticmethod
    def get_db_path():
        return Settings.get_settings().get(Settings.STORAGE,
                                           Settings.DB)

    @staticmethod
    def get_font_size():
        return int(float(Settings.get_settings().get(Settings.STORAGE,
                                             Settings.FONT_SIZE)))

    @staticmethod
    def update_db_path(a):
        settings = Settings.get_settings()
        settings.set(Settings.STORAGE, Settings.DB,
            os.path.join(a.get_filename(), Settings.DB_FILENAME))
        Settings.save_settings(settings)

    @staticmethod
    def update_font_size(a):
        settings = Settings.get_settings()
        settings.set(Settings.STORAGE, Settings.FONT_SIZE, a.get_value())
        Settings.save_settings(settings)

    @staticmethod
    def save_settings(settings):
        settings.write(open(Settings.get_config_path(), 'w'))

    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "Settings", parent, 0)

        self.set_default_size(450, 110)
        self.set_border_width(4)

        box = self.get_content_area()
        list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.add(list_box)

        select_db_dialog = Gtk.FileChooserDialog(
            'Select DB path',
            self,
            Gtk.FileChooserAction.SELECT_FOLDER,
            ("Select",
            Gtk.ResponseType.APPLY)
        )
        select_db_dialog.connect('current-folder-changed', Settings.update_db_path)
        select_db_dialog.set_default_size(350, 200)

        select_txt = Gtk.Label('Database path')
        select_txt.set_justify(Gtk.Justification.LEFT)
        select_db = Gtk.FileChooserButton.new_with_dialog(select_db_dialog)
        select_db.set_current_folder(Settings.get_db_path())
        select_db_line = Gtk.Box()
        select_db_line.pack_start(select_txt, False, False, 0)
        select_db_line.pack_end(select_db, False, False, 0)

        list_box.pack_start(select_db_line, True, True, 0)

        font_size_btn = Gtk.Label('Font size')
        font_size_btn.set_justify(Gtk.Justification.LEFT)
        spin = Gtk.SpinButton.new_with_range(8, 15, 1)
        spin.connect('value-changed', Settings.update_font_size)
        spin.set_value(Settings.get_font_size())
        spin_line = Gtk.Box()
        spin_line.pack_start(font_size_btn, False, False, 0)
        spin_line.pack_end(spin, False, False, 0)

        list_box.pack_start(spin_line, True, True, 0)

        about = Gtk.Button('About')
        about.connect('clicked', parent.show_about)
        about_line = Gtk.Box()
        about_line.pack_end(about, False, False, 0)

        list_box.pack_start(about_line, True, True, 0)

        list_box.show()

        self.show_all()


class AboutDialog(Gtk.AboutDialog):

    def __init__(self, parent):
        Gtk.AboutDialog.__init__(self)
        self.set_authors(["Nikolay Yakovlev <vegasq@gmail.com>"])
        self.set_copyright("Nikolay Yakovlev, 2014")
        self.set_program_name("ToDoDo")
        self.set_version('1.0')
        self.set_website("http://github.com/vegasq/tododo")
        pb = GdkPixbuf.Pixbuf.new_from_file(
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                 'temp-todo-icon.png'))
        self.set_logo(pb)


class CreateTicketDialog(Gtk.Dialog):

    def __init__(self, parent):
        Gtk.Dialog.use_header_bar = True
        Gtk.Dialog.__init__(self, "Create ticket", parent, 0)


        self.set_default_size(350, 200)
        self.set_border_width(4)

        self.textview = Gtk.TextView(expand=True)
        self.textview.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.textview.set_right_margin(5)
        self.textview.set_left_margin(5)
        self.textbuffer = self.textview.get_buffer()

        box = self.get_content_area()
        box.add(self.textview)

        is_important = Gtk.Box()
        self.switch = Gtk.Switch()
        self.switch.connect("notify::active", lambda a,b: 1)
        self.switch.set_active(False)
        lbl = Gtk.Label()
        lbl.set_text("Mark as important")
        is_important.pack_start(lbl, True, True, padding=1)
        is_important.pack_start(self.switch, False, False, padding=1)

        self.add_action_widget(is_important, 123)
        self.add_button('Add', Gtk.ResponseType.OK)

        self.show_all()

    def get_text(self):
        return self.textbuffer.get_text(
            self.textbuffer.get_start_iter(),
            self.textbuffer.get_end_iter(),
            True
        )

    def is_important(self):
        return self.switch.get_active()


class ShowTicketDialog(Gtk.Dialog):

    def __init__(self, parent, text, is_done, is_important):
        if is_done:
            buttons = ('Delete', Gtk.ResponseType.REJECT)
        else:
            buttons = ('Save', Gtk.ResponseType.OK)

        Gtk.Dialog.__init__(
            self, "Edit ticket", parent, 0
        )

        self.set_default_size(350, 200)
        self.set_border_width(4)

        self.textview = Gtk.TextView(expand=True)
        self.textview.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.textview.set_right_margin(5)
        self.textview.set_left_margin(5)

        if is_done:
            self.textview.set_editable(False)
        self.textbuffer = self.textview.get_buffer()
        self.textbuffer.set_text(text)

        box = self.get_content_area()
        box.add(self.textview)

        if not is_done:
            is_important_box = Gtk.Box()
            self.switch = Gtk.Switch()
            self.switch.connect("notify::active", lambda a,b: 1)
            self.switch.set_active(is_important)
            lbl = Gtk.Label()
            lbl.set_text("Mark as important")
            is_important_box.pack_start(lbl, True, True, padding=1)
            is_important_box.pack_start(self.switch, False, False, padding=1)

            self.add_action_widget(is_important_box, 123)

        self.add_button(buttons[0], buttons[1])


        self.show_all()

    def get_text(self):
        return self.textbuffer.get_text(
            self.textbuffer.get_start_iter(),
            self.textbuffer.get_end_iter(),
            True
        )

    def is_important(self):
        return self.switch.get_active()
