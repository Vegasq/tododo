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
from tickets import Tickets
import constants
import gettext

t = gettext.translation('tododo', './locale', fallback=True)
_ = t.ugettext



class ToDoDo(Gtk.Window):
    font_size_related_items = []
    column_title = '<span foreground="#858585" size="medium"><b>%s</b></span>'

    def __init__(self, tickets):
        self.tickets = tickets

        self.important_pb = '!'
        self.nonimportant_pb = ''
        self._create_window()
        self._create_ticket_views()
        self.show_all()

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
        done_ticket_store = Gtk.ListStore(bool, str, str, str)

        tickets.active = active_ticket_store
        tickets.done = done_ticket_store

        tickets._load(self.important_pb, self.nonimportant_pb)

        active_ticket_store.connect('row-deleted', self.row_deleted)
        done_ticket_store.connect('row-deleted', self.row_deleted)

        return [active_ticket_store, done_ticket_store]

    def _get_tree_columns(self, store_type):
        column = Gtk.TreeViewColumn()
        column.set_max_width(400)

        # Create column title
        column_label = Gtk.Label()
        column_label.set_use_markup(True)
        if store_type == constants.ACTIVE_STORE:
            column_label.set_markup(self.column_title % _('Active tasks'))
        elif store_type == constants.DONE_STORE:
            column_label.set_markup(self.column_title % _('Done tasks'))
        column_label.show()
        column.set_widget(column_label)

        # Create first column, with checkbox
        ticket_done = Gtk.CellRendererToggle()
        ticket_done.connect("toggled", self.toggle_ticket)

        # Second column with text
        ticket_text = Gtk.CellRendererText()
        ticket_text.props.ellipsize_set = True
        ticket_text.props.ellipsize = Pango.EllipsizeMode.END
        ticket_text.props.size_set = True
        ticket_text.props.size_points = int(Settings.get_font_size())
        self.font_size_related_items.append(ticket_text)

        # Third column with important mark
        ticket_important = Gtk.CellRendererText()
        ticket_important.props.foreground = 'red'
        ticket_important.props.size_set = True
        ticket_important.props.size_points = int(Settings.get_font_size())
        self.font_size_related_items.append(ticket_important)

        # Pack columns
        column.pack_start(ticket_done, False)
        column.pack_start(ticket_text, True)
        column.pack_start(ticket_important, False)

        # Bind with model
        column.add_attribute(ticket_done, "active", 0)
        column.add_attribute(ticket_important, "text", 1)
        column.add_attribute(ticket_text, "text", 3)

        return column

    def get_tickets_tree_views(self, tickets, show_ticket_callback):
        ticket_stores = self.get_tickets_stores(tickets)
        trees = []

        for store_type, store in enumerate(ticket_stores):
            tree = Gtk.TreeView(store)
            tree.set_reorderable(True)
            tree.connect('row-activated', show_ticket_callback)
            trees.append(tree)

            column = self._get_tree_columns(store_type)
            tree.append_column(column)
            if store_type == constants.DONE_STORE:
                self.done_tree_view = tree
            else:
                self.active_tree_view = tree

        return trees

    def _create_window(self):
        Gtk.Window.__init__(self, title="ToDoDo")
        self.set_icon_from_file('temp-todo-icon.png')

        self.set_border_width(1)
        self.set_default_size(300, 500)

        # Define window header
        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.props.title = "ToDoDo"
        self.set_titlebar(hb)

        # Create ticket button
        create_ticket_button = Gtk.Button()
        icon = Gio.ThemedIcon(name="text-editor-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        create_ticket_button.connect('clicked', self.create_ticket)
        create_ticket_button.add(image)
        hb.pack_start(create_ticket_button)

        # Create main menu
        # main_menu_button = Gtk.Button()
        # icon = Gio.ThemedIcon(name="emblem-system-symbolic")
        # image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        # main_menu_button.add(image)
        # main_menu_button.connect('clicked', self.show_menu)
        # self._create_menu_popupover(main_menu_button)
        # hb.pack_end(main_menu_button)

    def _update_font(self, widget):
        Settings.update_font_size(widget)
        for item in self.font_size_related_items:
            item.props.size_points = Settings.get_font_size()

    def _create_menu_popupover(self, app_menu_btn):
        # Create Popover and put canvas into it
        self.popover = Gtk.Popover.new(app_menu_btn)
        self.popover.set_size_request(300, -1)
        popover_botle = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.popover.add(popover_botle)

        # Font settings UI
        font_size_label = Gtk.Label('Font size')
        spin = Gtk.SpinButton.new_with_range(8, 15, 1)
        spin.connect('value-changed', self._update_font)
        spin.set_value(Settings.get_font_size())

        spin_line = Gtk.Box()
        spin_line.pack_start(font_size_label, True, True, 0)
        spin_line.pack_end(spin, False, False, 0)
        popover_botle.add(spin_line)

        # About button
        spin_about_line = Gtk.Box()
        about = Gtk.Button(_('About'))
        about.connect('clicked', self.show_about)
        about_line = Gtk.Box()
        spin_about_line.pack_end(about, False, False, 0)
        popover_botle.add(spin_about_line)

    def _create_ticket_views(self):
        trees = self.get_tickets_tree_views(self.tickets, self.show_ticket)

        scroll_canvas = Gtk.ScrolledWindow()
        scroll_canvas.set_min_content_height(400)
        self.add(scroll_canvas)

        vbox = Gtk.Box(spacing=1, orientation=Gtk.Orientation.VERTICAL)
        scroll_canvas.add(vbox)

        vbox.pack_start(trees[constants.ACTIVE_STORE], True, True, 0)
        vbox.pack_start(trees[constants.DONE_STORE], False, False, 0)

    def create_ticket(self, widget):
        self.create_ticket_dialog = CreateTicketDialog(self)
        response = self.create_ticket_dialog.run()
        if response == Gtk.ResponseType.OK:
            ticket_text = self.create_ticket_dialog.get_text()
            imp = self.create_ticket_dialog.is_important()
            if imp:
                imp = self.important_pb
            else:
                imp = self.nonimportant_pb
            self.tickets.create_ticket(ticket_text, imp)
        self.create_ticket_dialog.destroy()

    def show_ticket(self, widget, index, itemb):
        #TODO(vegasq) Refactor me please
        if not len(widget.get_selection().get_selected_rows()[0]):
            return
        is_done = widget.get_selection().get_selected_rows()[0][0][0]
        index = index.to_string()
        if is_done and len(self.tickets.done):
            store_row = self.tickets.done[index]
        elif len(self.tickets.active):
            store_row = self.tickets.active[index]

        text = store_row[constants.TEXT_INDEX]
        is_important = store_row[constants.IMPORTANT_INDEX]

        if is_important is self.important_pb:
            is_important = True
        else:
            is_important = False

        self.show_ticket_dialog = ShowTicketDialog(self, text=text, is_done=is_done,
                                                   is_important=is_important)
        result = self.show_ticket_dialog.run()
        self._show_ticket_result(self.show_ticket_dialog, result, index, is_done)

    def delete_ticket(self, label):
        selected = self.done_tree_view.get_selection()
        self.tickets.delete_ticket(selected.get_selected_rows()[1][0])
        self.show_ticket_dialog.destroy()

    def new_ticket(self, label):
        selected = self.active_tree_view.get_selection()

        ticket_text = self.create_ticket_dialog.get_text()
        imp = self.create_ticket_dialog.is_important()
        if imp:
            imp = self.important_pb
        else:
            imp = self.nonimportant_pb
        self.tickets.create_ticket(ticket_text, imp)
        self.create_ticket_dialog.destroy()

    def save_ticket(self, label):
        selected = self.active_tree_view.get_selection()
        self.tickets.update_ticket(
            selected.get_selected_rows()[1][0],
            self.show_ticket_dialog.get_text(),
            '!' if self.show_ticket_dialog.is_important() else '')
        self.show_ticket_dialog.destroy()

    def _show_ticket_result(self, dialog, result, index, is_done):
        if result == Gtk.ResponseType.REJECT and is_done:
            self.tickets.delete_ticket(index)
        elif result == Gtk.ResponseType.OK:
            self.tickets.update_ticket(
                index,
                dialog.get_text(),
                '!' if dialog.is_important() else '')

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
        Gtk.Dialog.__init__(self, _("Settings"), parent, 0)

        self.set_default_size(450, 110)
        self.set_border_width(4)

        box = self.get_content_area()
        list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.add(list_box)

        select_db_dialog = Gtk.FileChooserDialog(
            _('Select DB path'),
            self,
            Gtk.FileChooserAction.SELECT_FOLDER,
            (_("Select"),
            Gtk.ResponseType.APPLY)
        )
        select_db_dialog.connect('current-folder-changed', Settings.update_db_path)
        select_db_dialog.set_default_size(350, 200)

        select_txt = Gtk.Label(_('Database path'))
        select_txt.set_justify(Gtk.Justification.LEFT)
        select_db = Gtk.FileChooserButton.new_with_dialog(select_db_dialog)
        select_db.set_current_folder(Settings.get_db_path())
        select_db_line = Gtk.Box()
        select_db_line.pack_start(select_txt, False, False, 0)
        select_db_line.pack_end(select_db, False, False, 0)

        list_box.pack_start(select_db_line, True, True, 0)

        font_size_btn = Gtk.Label(_('Font size'))
        font_size_btn.set_justify(Gtk.Justification.LEFT)
        spin = Gtk.SpinButton.new_with_range(8, 15, 1)
        spin.connect('value-changed', Settings.update_font_size)
        spin.set_value(Settings.get_font_size())
        spin_line = Gtk.Box()
        spin_line.pack_start(font_size_btn, False, False, 0)
        spin_line.pack_end(spin, False, False, 0)

        list_box.pack_start(spin_line, True, True, 0)

        about = Gtk.Button(_('About'))
        about.connect('clicked', parent.show_about)
        about_line = Gtk.Box()
        about_line.pack_end(about, False, False, 0)

        list_box.pack_start(about_line, True, True, 0)

        list_box.show()

        self.show_all()


class AboutDialog(Gtk.AboutDialog):

    def __init__(self, parent):
        Gtk.AboutDialog.__init__(self)

        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.props.title = _('About')
        self.set_titlebar(hb)

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
        Gtk.Dialog.__init__(self, _("Create ticket"), parent, 0)

        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.props.title = _("Create ticket")
        self.set_titlebar(hb)

        create_ticket_button = Gtk.Button(_('Create'))
        create_ticket_button.connect('clicked',
                                     parent.new_ticket)
        hb.pack_start(create_ticket_button)

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
        lbl.set_text(_("Mark as important"))
        is_important.pack_start(lbl, True, True, padding=1)
        is_important.pack_start(self.switch, False, False, padding=1)

        self.add_action_widget(is_important, 123)

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
        Gtk.Dialog.__init__(
            self, _("Edit ticket"), parent, 0
        )

        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        self.set_titlebar(hb)

        if is_done:
            # Create ticket button
            delete_ticket_button = Gtk.Button(_('Delete'))
            delete_ticket_button.connect('clicked',
                                         parent.delete_ticket)
            hb.pack_start(delete_ticket_button)
            hb.props.title = _("Done ticket")
        else:
            save_ticket_button = Gtk.Button(_('Save'))
            save_ticket_button.connect('clicked',
                                       parent.save_ticket)
            hb.pack_start(save_ticket_button)
            hb.props.title = _("Update ticket")

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
            lbl.set_text(_("Mark as important"))
            is_important_box.pack_start(lbl, True, True, padding=1)
            is_important_box.pack_start(self.switch, False, False, padding=1)

            self.add_action_widget(is_important_box, 123)

        self.show_all()

    def get_text(self):
        return self.textbuffer.get_text(
            self.textbuffer.get_start_iter(),
            self.textbuffer.get_end_iter(),
            True
        )

    def is_important(self):
        return self.switch.get_active()
