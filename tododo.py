#!/usr/bin/python
from gi.repository import Gtk, Gio, GdkPixbuf, Pango
import os



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
    _database = '/home/nyakovlev/.config/tododo.conf'
    done = []
    active = []

    def __init__(self):
        if not os.path.exists(self._database):
            open(self._database, 'a').close()

    def create_ticket(self, text, is_important):
        """Append to self.active"""
        self.active.append([0, text, is_important])
        
        self._save()

    def delete_ticket(self, index):
        """We can remove only from self.done list"""
        del self.done[index]

        self._save()

    def update_ticket(self, index, text, is_important):
        self.active[index][1] = text
        self.active[index][2] = is_important

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
            is_important = '1' if ticket[2] is self.important else '0' 
            done_lines.append("%s|%s|%s" % (1, ticket[1], is_important))

        active_lines = []
        for ticket in self.active:
            is_important = '1' if ticket[2] is self.important else '0' 
            active_lines.append("%s|%s|%s" % (0, ticket[1], is_important))
       
        lines = "\n".join(done_lines) + "\n" + "\n".join(active_lines)
        with open(self._database, 'w') as db:
            db.write(lines)

    def _load(self, pb, npb):
        """Load from file"""
        self.important = pb
        self.nonimportant = npb

        with open(self._database, 'r') as tododo_db:
            tododo_db = tododo_db.read().splitlines()

            for line in tododo_db:
                if '|' not in line:
                    continue

                ticket = line.split('|')
                if len(ticket) == 2:
                    ticket.append('0')

                if ticket[2] == '0':
                    important_mark = npb
                elif ticket[2] == '1':
                    important_mark = pb

                if ticket[0] == '1':
                    self.done.append([True, ticket[1], important_mark])
                elif ticket[0] == '0':
                    self.active.append([False, ticket[1], important_mark])


class TicketsUI():
    ACTIVE_STORE = 0
    DONE_STORE = 1

    def __init__(self, tickets):
        self.tickets = tickets

        self.important_pb = GdkPixbuf.Pixbuf.new_from_file(
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                 'important.png'))
        self.nonimportant_pb = GdkPixbuf.Pixbuf.new_from_file(
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                 'nonimportant.png'))

    def toggle_ticket(self, switcher, switcher_index):
        if switcher.get_active():
            self.tickets.undone_ticket(switcher_index)
        else:
            self.tickets.done_ticket(switcher_index)

    def row_deleted(self, widget, index):
        self.tickets._save()

    def get_tickets_stores(self, tickets):
        """Returns list of tickets stores"""
        active_ticket_store = Gtk.ListStore(bool, str, GdkPixbuf.Pixbuf)
        tickets.active = active_ticket_store

        done_ticket_store = Gtk.ListStore(bool, str, GdkPixbuf.Pixbuf)
        tickets.done = done_ticket_store

        tickets._load(self.important_pb, self.nonimportant_pb)

        active_ticket_store.connect('row-deleted', self.row_deleted)
        done_ticket_store.connect('row-deleted', self.row_deleted)

        return [active_ticket_store, done_ticket_store]

    def get_tickets_tree_views(self, tickets, show_ticket_callback):
        ticket_stores = self.get_tickets_stores(tickets)

        title = '<span foreground="#858585" size="large"><b>%s</b></span>'
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
            # ticket_text.props.max_width_chars = 2
            # ticket_text.props.wrap_mode = Pango.WrapMode.WORD_CHAR
            # ticket_text.props.wrap_width = 100

            ticket_important = Gtk.CellRendererPixbuf()

            column.pack_start(ticket_done, False)
            column.pack_start(ticket_text, True)
            column.pack_start(ticket_important, False)

            column.add_attribute(ticket_done, "active", 0)
            column.add_attribute(ticket_text, "text", 1)
            column.add_attribute(ticket_important, "pixbuf", 2)

            tree.append_column(column)
            trees.append(tree)
        return trees


class ToDoDo(Gtk.Window):

    def __init__(self, tickets):
        self.tickets = tickets
        self._create_window()
        self._create_ticket_views()
        self.show_all()

    def _create_window(self):
        Gtk.Window.__init__(self, title="ToDoDo")
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
        about_button.connect('clicked', self.show_about)
        about_button.add(image)

        hb.pack_end(about_button)
        hb.pack_start(button)

    def _create_ticket_views(self):
        self.ticket_ui = TicketsUI(self.tickets)
        trees = self.ticket_ui.get_tickets_tree_views(self.tickets, self.show_ticket)

        vbox = Gtk.Box(spacing=1, orientation=Gtk.Orientation.VERTICAL)
        self.add(vbox)

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
        is_done = widget.get_selection().get_selected_rows()[0][0][0]

        if is_done:
            if len(self.tickets.done):
                text = self.tickets.done[index.to_string()][1]
                is_important = self.tickets.done[index.to_string()][2]
        else:
            if len(self.tickets.active):
                text = self.tickets.active[index.to_string()][1]
                is_important = self.tickets.active[index.to_string()][2]

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

class Do():
    def __init__(self):
        tickets = Tickets()

        main_window = ToDoDo(tickets)
        main_window.connect("delete-event", Gtk.main_quit)
        main_window.show_all()
        Gtk.main()

do = Do()
