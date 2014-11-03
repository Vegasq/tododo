from gi.repository import Gtk, Gio
import os


class Tickets():
    _database = '/home/nyakovlev/.config/tododo.conf'
    done = []
    active = []

    def __init__(self):
        if not os.path.exists(self._database):
            open(self._database, 'a').close()

        with open(self._database, 'r') as tododo_db:
            tododo_db = tododo_db.readlines()
            for line in tododo_db:
                ticket = line.split('|')
                if ticket[0] == 1:
                    pass

    def create_ticket(self, text):
        """Append to self.active"""
        pass

    def delete_ticket(self, index):
        """We can remove only from self.done list"""
        pass

    def done_ticket(self, index):
        """Move ticket from self.active to self.done"""
        pass

    def undone_tocket(self, index):
        """Move ticket from self.done to self.active"""
        pass

    def _save(self):
        """Save to file"""
        pass

    def _load(self):
        """Load from file"""
        pass


class TicketsUI():
    ACTIVE_STORE = 0
    DONE_STORE = 1

    def show_ticket(self):
        pass

    def toggle_ticket(self):
        pass

    def get_tickets_stores(self, tickets):
        """Returns list of tickets stores"""
        active_ticket_store = Gtk.ListStore(bool, str)
        tickets.active = active_ticket_store

        done_ticket_store = Gtk.ListStore(bool, str)
        tickets.done = done_ticket_store

        for ticket in tickets.done:
            done_ticket_store.append(ticket)

        for ticket in tickets.active:
            active_ticket_store.append(ticket)

        return [active_ticket_store, done_ticket_store]

    def get_tickets_tree_views(self, tickets):
        ticket_stores = self.get_tickets_stores(tickets)
        trees = []

        for store_type, store in enumerate(ticket_stores):
            tree = Gtk.TreeView(store)
            column = Gtk.TreeViewColumn()

            lbl = Gtk.Label()
            lbl.set_use_markup(True)

            if store_type == self.ACTIVE_STORE:
                lbl.set_markup('<span foreground="#858585" size="x-large">'
                               '<b>Active tasks</b></span>')
            elif store_type == self.DONE_STORE:
                lbl.set_markup('<span foreground="#858585" size="x-large">'
                               '<b>Done tasks</b></span>')
            lbl.show()
            column.set_widget(lbl)

            tree.connect('row-activated', self.show_ticket)

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


class CreateTicketDialog(Gtk.Dialog):

    def __init__(self, parent):
        Gtk.Dialog.use_header_bar = True
        Gtk.Dialog.__init__(self, "Create ticket", parent, 0,
            ('Add', Gtk.ResponseType.OK))


        self.set_default_size(350, 200)

        self.textview = Gtk.TextView(expand=True)
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

class DialogExample(Gtk.Dialog):

    def __init__(self, parent, text):
        print(dir(Gtk.ResponseType))
        Gtk.Dialog.__init__(self, "Edit ticket", parent, 0,
            ('Delete', Gtk.ResponseType.DELETE_EVENT,
             'Save', Gtk.ResponseType.OK)
        )

        self.set_default_size(350, 200)

        self.textview = Gtk.TextView(expand=True)
        self.textbuffer = self.textview.get_buffer()
        self.textbuffer.set_text(text)

        box = self.get_content_area()
        box.add(self.textview)
        self.show_all()

class ToDoDo(Gtk.Window):

    def _create_window(self):
        Gtk.Window.__init__(self, title="ToDoDo")
        self.set_border_width(2)
        self.set_default_size(400, 500)

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

    def _create_ticket_views(self, tickets):
        self.ticket_ui = TicketsUI()
        trees = self.ticket_ui.get_tickets_tree_views(tickets)

        vbox = Gtk.Box(spacing=1, orientation=Gtk.Orientation.VERTICAL)
        self.add(vbox)

        vbox.pack_start(trees[TicketsUI.ACTIVE_STORE], True, True, 0)
        vbox.pack_start(trees[TicketsUI.DONE_STORE], False, False, 0)

    def __init__(self, tickets):
        self._create_window()
        self._create_ticket_views(tickets)

    # def get_undone_tree_ticket_view(self):
    #     tree = Gtk.TreeView(self.undone_ticket_store)
    #     column = Gtk.TreeViewColumn()
    #     lbl = Gtk.Label()
    #     lbl.set_use_markup(True)
    #     lbl.set_markup('<span foreground="#858585" size="x-large">'
    #                    '<b>Active tasks</b></span>')
    #     lbl.show()
    #     column.set_widget(lbl)


    #     tree.connect('row-activated', self.on_undone_show)

    #     ticket_done = Gtk.CellRendererToggle()
    #     ticket_done.connect("toggled", self.done)

    #     author = Gtk.CellRendererText()

    #     column.pack_start(ticket_done, False)
    #     column.pack_start(author, True)

    #     column.add_attribute(author, "text", 1)
    #     column.add_attribute(ticket_done, "active", 0)

    #     tree.append_column(column)
    #     return tree

    # def get_done_tree_ticket_view(self):
    #     tree = Gtk.TreeView(self.done_ticket_store)
    #     column = Gtk.TreeViewColumn()

    #     lbl = Gtk.Label()
    #     lbl.set_use_markup(True)
    #     lbl.set_markup('<span foreground="#858585" size="x-large">'
    #                    '<b>Done tasks</b></span>')
    #     lbl.show()
    #     column.set_widget(lbl)

    #     tree.connect('row-activated', self.on_done_show)

    #     ticket_done = Gtk.CellRendererToggle()
    #     ticket_done.connect("toggled", self.undone)

    #     author = Gtk.CellRendererText()
    #     # author.set_fixed_height_from_font(2)

    #     column.pack_start(ticket_done, False)
    #     column.pack_start(author, True)

    #     column.add_attribute(author, "text", 1)
    #     column.add_attribute(ticket_done, "active", 0)

    #     tree.append_column(column)

    #     return tree

    def undone_tickets_store(self):
        tickets = []
        self.undone_ticket_store = Gtk.ListStore(bool, str)
        for ticket in tickets:
            self.undone_ticket_store.append(ticket)
        self.undone_ticket_store

    def done_tickets_store(self):
        tickets = []
        self.done_ticket_store = Gtk.ListStore(bool, str)
        for ticket in tickets:
            self.done_ticket_store.append(ticket)
        self.done_ticket_store

    def mark_ticket_as_done(self, index):
        ticket = self.undone_ticket_store[index][:]
        del self.undone_ticket_store[index]
        ticket[0] = True
        self.done_ticket_store.append(ticket)

    def mark_ticket_as_undone(self, index):
        ticket = self.done_ticket_store[index][:]
        del self.done_ticket_store[index]
        ticket[0] = False
        self.undone_ticket_store.append(ticket)

    def done(self, switcher, switcher_index):
        self.mark_ticket_as_done(switcher_index)

    def undone(self, switcher, switcher_index):
        self.mark_ticket_as_undone(switcher_index)

    def on_done_show(self, widget, index, s):
        dialog = DialogExample(
            self,
            text=self.done_ticket_store[index.to_string()][1])
        dialog.run()
        dialog.destroy()

    def on_undone_show(self, widget, index, s):
        dialog = DialogExample(
            self,
            text=self.undone_ticket_store[index.to_string()][1])
        dialog.run()
        dialog.destroy()

    def create_ticket(self, widget):
        dialog = CreateTicketDialog(self)
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            ticket_text = dialog.get_text()
            self.undone_ticket_store.append([False, ticket_text])

        dialog.destroy()



class Do():
    def __init__(self):
        tickets = Tickets()

        main_window = ToDoDo(tickets)
        main_window.connect("delete-event", Gtk.main_quit)
        main_window.show_all()
        Gtk.main()

do = Do()
