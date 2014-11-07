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
        self.active[index][ToDoDo.TEXT_INDEX] = text
        self.active[index][ToDoDo.IMPORTANT_INDEX] = is_important
        self.active[index][ToDoDo.HEADER_INDEX] = text.split('\n')[0]

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
            is_important = '1' if ticket[ToDoDo.IMPORTANT_INDEX] is self.important else '0' 
            ticket_value = base64.b64encode(ticket[ToDoDo.TEXT_INDEX])
            done_lines.append("%s|%s|%s" % (1, is_important, ticket_value))

        active_lines = []
        for ticket in self.active:
            is_important = '1' if ticket[ToDoDo.IMPORTANT_INDEX] is self.important else '0' 
            ticket_value = base64.b64encode(ticket[ToDoDo.TEXT_INDEX])
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

                if ticket[ToDoDo.IMPORTANT_INDEX] == '0':
                    important_mark = npb
                elif ticket[ToDoDo.IMPORTANT_INDEX] == '1':
                    important_mark = pb

                ticket_value = base64.b64decode(ticket[ToDoDo.TEXT_INDEX])
                ticket_head = ticket_value.split('\n')[0]
                if ticket[ToDoDo.ACTIVITY_INDEX] == '1':
                    self.done.append([True, important_mark, ticket_value, ticket_head])
                elif ticket[0] == '0':
                    self.active.append([False, important_mark, ticket_value, ticket_head])


class TicketsUI():
    ACTIVE_STORE = 0
    DONE_STORE = 1

    font_size_related_items = []

    def __init__(self, tickets):
        self.tickets = tickets

        self.important_pb = '!'
        self.nonimportant_pb = ''

    def toggle_ticket(self, switcher, switcher_index):
        if switcher.get_active():
            self.tickets.undone_ticket(switcher_index)
        else:
            self.tickets.done_ticket(switcher_index)

    def row_deleted(self, widget, index):
        self.tickets._save()

    def get_tickets_stores(self, tickets):
        """Returns list of tickets stores"""
        active_ticket_store = Gtk.ListStore(bool, str, str, str)
        tickets.active = active_ticket_store

        done_ticket_store = Gtk.ListStore(bool, str, str, str)
        tickets.done = done_ticket_store

        tickets._load(self.important_pb, self.nonimportant_pb)

        active_ticket_store.connect('row-deleted', self.row_deleted)
        done_ticket_store.connect('row-deleted', self.row_deleted)

        return [active_ticket_store, done_ticket_store]

    def get_tickets_tree_views(self, tickets, show_ticket_callback):
        ticket_stores = self.get_tickets_stores(tickets)

        # large, x-large
        title = '<span foreground="#858585" size="medium"><b>%s</b></span>'
        trees = []

        for store_type, store in enumerate(ticket_stores):
            tree = Gtk.TreeView(store)
            tree.set_reorderable(True)

            column = Gtk.TreeViewColumn()
            column.set_max_width(400)

            lbl = Gtk.Label()
            lbl.set_use_markup(True)

            if store_type == self.ACTIVE_STORE:
                lbl.set_markup(title % 'Active tasks')
            elif store_type == self.DONE_STORE:
                lbl.set_markup(title % 'Done tasks')
            lbl.show()
            column.set_widget(lbl)

            tree.connect('row-activated', show_ticket_callback)

            ticket_done = Gtk.CellRendererToggle()
            ticket_done.connect("toggled", self.toggle_ticket)

            ticket_text = Gtk.CellRendererText()

            ticket_text.props.ellipsize_set = True
            ticket_text.props.ellipsize = Pango.EllipsizeMode.END

            ticket_important = Gtk.CellRendererText()
            ticket_important.props.foreground = 'red'

            ticket_important.props.size_set = True
            ticket_text.props.size_set = True

            ticket_important.props.size_points = int(Settings.get_font_size())
            ticket_text.props.size_points = int(Settings.get_font_size())
            self.font_size_related_items.append(ticket_important)
            self.font_size_related_items.append(ticket_text)

            column.pack_start(ticket_done, False)
            column.pack_start(ticket_text, True)
            column.pack_start(ticket_important, False)

            column.add_attribute(ticket_done, "active", 0)
            column.add_attribute(ticket_important, "text", 1)
            column.add_attribute(ticket_text, "text", 3)

            tree.append_column(column)
            trees.append(tree)
        return trees


class MainMenu(Gio.MenuModel):
    pass


class ToDoDo(Gtk.Window):
    ACTIVITY_INDEX = 0
    IMPORTANT_INDEX = 1
    TEXT_INDEX = 2
    HEADER_INDEX = 3

    def __init__(self, tickets):
        self.tickets = tickets
        self._create_window()
        self._create_ticket_views()
        self.show_all()

    def _create_window(self):
        Gtk.Window.__init__(self, title="ToDoDo")
        self.set_icon_from_file('temp-todo-icon.png')

        self.set_border_width(0)
        self.set_default_size(300, 500)

        hb = Gtk.HeaderBar()

        hb.set_show_close_button(True)
        hb.props.title = "ToDoDo"
        self.set_titlebar(hb)

        button = Gtk.Button()
        icon = Gio.ThemedIcon(name="text-editor-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.connect('clicked', self.create_ticket)
        button.add(image)

        about_button = Gtk.Button()
        icon = Gio.ThemedIcon(name="emblem-system-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        about_button.connect('clicked', self.show_settings)
        about_button.add(image)
        # hb.pack_end(about_button)

        app_menu_btn = Gtk.Button()
        icon = Gio.ThemedIcon(name="emblem-system-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        app_menu_btn.add(image)
        app_menu_btn.connect('clicked', self.show_menu)

        self._create_menu_popupover(app_menu_btn)

        hb.pack_end(app_menu_btn)
        hb.pack_start(button)

    def _update_font(self, widget):
        if hasattr(self, 'ticket_ui'):
            Settings.update_font_size(widget)
            for item in self.ticket_ui.font_size_related_items:
                item.props.size_points = Settings.get_font_size()

    def _create_menu_popupover(self, app_menu_btn):
        self.popover = Gtk.Popover.new(app_menu_btn)
        self.popover.set_size_request(300, -1)
        popover_botle = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.popover.add(popover_botle)

        font_size_label = Gtk.Label('Font size')
        font_size_label.set_justify(Gtk.Justification.LEFT)
        spin = Gtk.SpinButton.new_with_range(8, 15, 1)
        spin.connect('value-changed', self._update_font)
        spin.set_value(Settings.get_font_size())
        spin_line = Gtk.Box()
        spin_line.pack_start(font_size_label, True, True, 0)
        spin_line.pack_end(spin, False, False, 0)

        spin_about_line = Gtk.Box()
        about = Gtk.Button('About')
        about.connect('clicked', self.show_about)
        about_line = Gtk.Box()
        spin_about_line.pack_end(about, False, False, 0)

        popover_botle.add(spin_line)
        popover_botle.add(spin_about_line)

    def _create_ticket_views(self):
        self.ticket_ui = TicketsUI(self.tickets)
        trees = self.ticket_ui.get_tickets_tree_views(self.tickets, self.show_ticket)

        scroll_canvas = Gtk.ScrolledWindow()
        scroll_canvas.set_min_content_height(400)
        self.add(scroll_canvas)

        vbox = Gtk.Box(spacing=1, orientation=Gtk.Orientation.VERTICAL)
        scroll_canvas.add(vbox)

        vbox.pack_start(trees[TicketsUI.ACTIVE_STORE], True, True, 0)
        vbox.pack_start(trees[TicketsUI.DONE_STORE], False, False, 0)

    def create_ticket(self, widget):
        dialog = CreateTicketDialog(self)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            ticket_text = dialog.get_text()
            imp = dialog.is_important()
            if imp:
                imp = self.ticket_ui.important_pb
            else:
                imp = self.ticket_ui.nonimportant_pb
            self.tickets.create_ticket(ticket_text, imp)
        dialog.destroy()

    def show_ticket(self, widget, index, itemb):
        if not len(widget.get_selection().get_selected_rows()[0]):
            return
        is_done = widget.get_selection().get_selected_rows()[0][0][0]
        if is_done:
            if len(self.tickets.done):
                text = self.tickets.done[index.to_string()][ToDoDo.TEXT_INDEX]
                is_important = self.tickets.done[index.to_string()][ToDoDo.IMPORTANT_INDEX]
        else:
            if len(self.tickets.active):
                text = self.tickets.active[index.to_string()][ToDoDo.TEXT_INDEX]
                is_important = self.tickets.active[index.to_string()][ToDoDo.IMPORTANT_INDEX]

        if is_important is self.ticket_ui.important_pb:
            is_important = True
        else:
            is_important = False

        dialog = ShowTicketDialog(self, text=text, is_done=is_done,
                                  is_important=is_important)
        result = dialog.run()

        if result == Gtk.ResponseType.REJECT and is_done:
            self.tickets.delete_ticket(index.to_string())

        if result == Gtk.ResponseType.OK:
            ticket_text = dialog.get_text()
            imp = dialog.is_important()
            if imp:
                imp = self.ticket_ui.important_pb
            else:
                imp = self.ticket_ui.nonimportant_pb
            self.tickets.update_ticket(index.to_string(), ticket_text, imp)

        dialog.destroy()

    def show_about(self, widget):
        dialog = AboutDialog(self)
        dialog.run()
        dialog.destroy()

    def show_settings(self, widget):
        dialog = Settings(self)
        dialog.run()
        dialog.destroy()

    def show_menu(self, widget):
        if self.popover.get_visible():
            self.popover.hide()
        else:
            self.popover.show_all()

    def show_main_menu(self, widget):
        pass


class Do():
    def __init__(self):
        tickets = Tickets()

        main_window = ToDoDo(tickets)
        main_window.connect("delete-event", Gtk.main_quit)
        main_window.show_all()
        Gtk.main()

if __name__ == '__main__':
    do = Do()
