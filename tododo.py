from gi.repository import Gtk, Gio
import os



class CreateTicketDialog(Gtk.Dialog):

    def __init__(self, parent):
        Gtk.Dialog.use_header_bar = True
        Gtk.Dialog.__init__(self, "Create ticket", parent, 0,
            ('Add', Gtk.ResponseType.OK))


        self.set_default_size(350, 200)

        self.textview = Gtk.TextView(expand=True)
        self.textview.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.textbuffer = self.textview.get_buffer()

        box = self.get_content_area()
        box.add(self.textview)
        self.show_all()

    def get_text(self):
        return self.textbuffer.get_text(
            self.textbuffer.get_start_iter(),
            self.textbuffer.get_end_iter(),
            True
        )


class ShowTicketDialog(Gtk.Dialog):

    def __init__(self, parent, text, is_done):
        if is_done:
            buttons = ('Delete', Gtk.ResponseType.REJECT)
        else:
            buttons = ('Save', Gtk.ResponseType.OK)

        Gtk.Dialog.__init__(
            self, "Edit ticket", parent, 0, buttons
        )

        self.set_default_size(350, 200)

        self.textview = Gtk.TextView(expand=True)
        self.textview.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        if is_done:
            self.textview.set_editable(False)
        self.textbuffer = self.textview.get_buffer()
        self.textbuffer.set_text(text)

        box = self.get_content_area()
        box.add(self.textview)
        self.show_all()

    def get_text(self):
        return self.textbuffer.get_text(
            self.textbuffer.get_start_iter(),
            self.textbuffer.get_end_iter(),
            True
        )

class Tickets():
    _database = '/home/nyakovlev/.config/tododo.conf'
    done = []
    active = []

    def __init__(self):
        if not os.path.exists(self._database):
            open(self._database, 'a').close()

    def create_ticket(self, text):
        """Append to self.active"""
        self.active.append([0, text])
        
        self._save()

    def delete_ticket(self, index):
        """We can remove only from self.done list"""
        del self.done[index]

        self._save()

    def update_ticket(self, index, text):
        self.active[index][1] = text

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
        done_lines = ["%s|%s" % (1, ticket[1]) for ticket in self.done]
        active_lines = ["%s|%s" % (0, ticket[1]) for ticket in self.active]
        
        lines = "\n".join(done_lines) + "\n" + "\n".join(active_lines)
        with open(self._database, 'w') as db:
            db.write(lines)

    def _load(self):
        """Load from file"""
        with open(self._database, 'r') as tododo_db:
            tododo_db = tododo_db.read().splitlines()

            for line in tododo_db:
                if '|' not in line:
                    continue

                ticket = line.split('|')

                if ticket[0] == '1':
                    self.done.append([True, ticket[1]])
                elif ticket[0] == '0':
                    self.active.append([False, ticket[1]])


class TicketsUI():
    ACTIVE_STORE = 0
    DONE_STORE = 1

    def __init__(self, tickets):
        self.tickets = tickets

    def toggle_ticket(self, switcher, switcher_index):
        if switcher.get_active():
            self.tickets.undone_ticket(switcher_index)
        else:
            self.tickets.done_ticket(switcher_index)

    def row_deleted(self, widget, index):
        self.tickets._save()

    def get_tickets_stores(self, tickets):
        """Returns list of tickets stores"""
        active_ticket_store = Gtk.ListStore(bool, str)
        tickets.active = active_ticket_store

        done_ticket_store = Gtk.ListStore(bool, str)
        tickets.done = done_ticket_store

        tickets._load()

        active_ticket_store.connect('row-deleted', self.row_deleted)
        done_ticket_store.connect('row-deleted', self.row_deleted)

        return [active_ticket_store, done_ticket_store]

    def get_tickets_tree_views(self, tickets, show_ticket_callback):
        ticket_stores = self.get_tickets_stores(tickets)

        trees = []

        for store_type, store in enumerate(ticket_stores):
            tree = Gtk.TreeView(store)
            tree.set_reorderable(True)

            column = Gtk.TreeViewColumn()

            lbl = Gtk.Label()
            lbl.set_use_markup(True)

            if store_type == self.ACTIVE_STORE:
                lbl.set_markup('<span foreground="#858585" size="large">'
                               '<b>Active tasks</b></span>')
            elif store_type == self.DONE_STORE:
                lbl.set_markup('<span foreground="#858585" size="large">'
                               '<b>Done tasks</b></span>')
            lbl.show()
            column.set_widget(lbl)

            tree.connect('row-activated', show_ticket_callback)

            ticket_done = Gtk.CellRendererToggle()
            ticket_done.connect("toggled", self.toggle_ticket)

            ticket_text = Gtk.CellRendererText()

            column.pack_start(ticket_done, False)
            column.pack_start(ticket_text, True)

            column.add_attribute(ticket_text, "text", 1)
            column.add_attribute(ticket_done, "active", 0)

            tree.append_column(column)
            trees.append(tree)
        return trees


class ToDoDo(Gtk.Window):

    def __init__(self, tickets):
        self.tickets = tickets
        self._create_window()
        self._create_ticket_views()

    def _create_window(self):
        Gtk.Window.__init__(self, title="ToDoDo")
        self.set_border_width(2)
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
            self.tickets.create_ticket(ticket_text)
        dialog.destroy()

    def show_ticket(self, widget, index, itemb):
        is_done = widget.get_selection().get_selected_rows()[0][0][0]

        if is_done:
            if len(self.tickets.done):
                text = self.tickets.done[index.to_string()][1]
        else:
            if len(self.tickets.active):
                text = self.tickets.active[index.to_string()][1]

        dialog = ShowTicketDialog(self, text=text, is_done=is_done)
        result = dialog.run()

        if result == Gtk.ResponseType.REJECT and is_done:
            self.tickets.delete_ticket(index.to_string())

        if result == Gtk.ResponseType.OK:
            ticket_text = dialog.get_text()
            self.tickets.update_ticket(index.to_string(), ticket_text)

        dialog.destroy()


class Do():
    def __init__(self):
        tickets = Tickets()

        main_window = ToDoDo(tickets)
        main_window.connect("delete-event", Gtk.main_quit)
        main_window.show_all()
        Gtk.main()

do = Do()
