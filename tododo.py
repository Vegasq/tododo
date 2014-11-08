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
from dialogs import *
from tickets import Tickets
import constants


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
            column_label.set_markup(self.column_title % 'Active tasks')
        elif store_type == constants.DONE_STORE:
            column_label.set_markup(self.column_title % 'Done tasks')
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
        about = Gtk.Button('About')
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

