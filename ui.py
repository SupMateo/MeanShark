import curses
import time


def x_for_center_text(text, window):
    height, width = window.getmaxyx()
    text_height, text_width = 1, len(text)
    x = (width - text_width) // 2
    return x




class Toolbar():
    def __init__(self, window, items=None):
        if items is None:
            self.items = []
        else:
            self.items = items

        self.window = window
        self.size = 0

    def add_item(self, item):
        self.items.append(item)

    def draw(self):
        self.window.addstr(2, 2, '_'*(self.window.getmaxyx()[1]-4))
        self.size = 0
        for i, item in enumerate(self.items):
            if item.is_selected:
                self.window.addstr(1,2+self.size +i*3, item.label, curses.color_pair(3) | curses.A_REVERSE)
                self.size +=len(item.label)
                item.x = self.size +i*3 -3
                item.y = 0
            else:
                self.window.addstr(1, 2 + self.size + i * 3,item.label, curses.color_pair(3))
                self.size += len(item.label)
                item.x = self.size + i * 3 -3
                item.y = 0


class ClickableObject:
    def __init__(self, screen=None, x=None, y=None, width=None, height=None, action=None, next_left=None, next_up=None, next_right=None, next_down=None):
        self.screen = screen
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.is_selected = False
        self.action = action
        self.next_left = next_left
        self.next_up = next_up
        self.next_right = next_right
        self.next_down = next_down

    def draw(self):
        raise NotImplementedError("Subclasses should implement this method.")

    def handle_event(self, event):
        raise NotImplementedError("Subclasses should implement this method.")

    def is_pressed(self, x, y):
        return self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height

    def select(self):
        self.is_selected = True
        self.draw()

    def deselect(self):
        self.is_selected = False
        self.draw()

class PacketObject(ClickableObject):
    def __init__(self, index,label, screen=None, x=None, y=None, width=None, height=None, action=None):
        super().__init__(screen=screen,x=x,y=y,height=height, action=action)
        self.window = screen
        self.index = index
        self.summary = label
        pass

    def draw(self, y=None):

        self.window.addstr(y+1, 1, ("Packet "+str(self.index) + " : " +self.summary)[:80], curses.color_pair(4))

    def handle_event(self, event):
        pass


class PacketFrame():
    def __init__(self,height,width,window):
        self.height = height
        self.width = width
        self.total_packet_list = []
        self.packets_display = []
        self.window = window
        self.is_live = True

    def refresh_packets_display(self):
        self.packets_display.clear()
        self.packets_display = self.total_packet_list[-(self.height-2):]


    def add_packet(self, packet):
        self.total_packet_list.append(packet)

    def draw(self):
        for i, packet in enumerate(self.packets_display):
            packet.draw(i)


    def get_last_packet_display(self):
        try:
            return self.packets_display[-1]
        except IndexError:
            pass

    def is_empty(self):
        return len(self.packets_display) == 0

class ToolbarItem(ClickableObject):
    def __init__(self,toolbar, label, choices=None):
        super().__init__(screen=toolbar.window,width=len(label)+2,height=3)
        self.label = label
        self.choices = choices
        self.size = len(self.label)
        toolbar.add_item(self)

    def action(self):
        pass

    def draw(self):
        pass

    def handle_event(self, event):
        pass

class Menu:
    def __init__(self, screen, title, height, width, x, y):
        self.window = None
        self.screen = screen
        self.height = height
        self.width = width
        self.x = x
        self.y = y
        self.title = title
        self.normal_objects = []
        self.clickable_objects = []
        self.selected_object = None

    def draw(self):
        self.window = self.screen.derwin(self.height, self.width, self.y, self.x)
        self.window.box()
        self.center_title()
        self.draw_objects()
        self.window.refresh()

    def draw_objects(self):
        for obj in self.clickable_objects:
            obj.draw()
        for obj in self.normal_objects:
            obj.draw()

    def add_normal_object(self, toolbar):
        self.normal_objects.append(toolbar)

    def center_title(self):
        height, width = self.window.getmaxyx()
        text_height, text_width = 1, len(self.title)
        x = (width - text_width) // 2
        self.window.addstr(0, x, self.title, curses.color_pair(1))
        self.window.refresh()

    def draw_buttons(self, buttons):
        self.clickable_objects = buttons
        for button in buttons:
            button.draw()
        if self.clickable_objects:
            self.select_object(self.clickable_objects[0])

    def draw_footer(self, text):
        x = x_for_center_text(text, self.window)
        self.window.addstr(6, 1 + x, text, curses.color_pair(1))

    def handle_mouse_event(self, mouse_x, mouse_y):
        for obj in self.clickable_objects:
            if obj.is_pressed(mouse_x, mouse_y):
                self.select_object(obj)
                if obj.action:
                    obj.action()

    def handle_keyboard_event(self, event):
        next_obj = None
        if event == curses.KEY_DOWN and self.selected_object.next_down:
            next_obj = self.selected_object.next_down
        elif event == curses.KEY_UP and self.selected_object.next_up:
            next_obj = self.selected_object.next_up
        elif event == curses.KEY_LEFT and self.selected_object.next_left:
            next_obj = self.selected_object.next_left
        elif event == curses.KEY_RIGHT and self.selected_object.next_right:
            next_obj = self.selected_object.next_right
        elif event == ord('\n') and self.selected_object.action:
            self.selected_object.action()

        if next_obj:
            self.select_object(next_obj)

    def add_button(self, button):
        self.clickable_objects.append(button)

    def add_select_bar(self, select_bar):
        self.clickable_objects.append(select_bar)

    def remove_obj(self, obj):
        if obj in self.clickable_objects:
            self.clickable_objects.remove(obj)

    def select_object(self, obj):
        if self.selected_object:
            self.selected_object.deselect()
        obj.select()
        self.selected_object = obj

    def is_clickable_obj_selected(self):
        return any(obj.is_selected for obj in self.clickable_objects)

class SelectBar(ClickableObject):
    def __init__(self, screen, x, y, choices):
        super().__init__(screen, x, y, max(len(choice) for choice in choices) + 4, len(choices) + 2)
        self.choices = choices
        self.selected_index = 0

    def draw(self):
        self.window = self.screen.subwin(self.height, self.width, self.y, self.x)
        self.window.clear()
        self.window.box()
        for idx, choice in enumerate(self.choices):
            if idx == self.selected_index:
                self.window.addstr(idx + 1, 2, choice, curses.A_REVERSE)
            else:
                self.window.addstr(idx + 1, 2, choice)
        self.window.refresh()

    def handle_event(self, event):
        if event == curses.KEY_DOWN:
            self.selected_index = (self.selected_index + 1) % len(self.choices)
        elif event == curses.KEY_UP:
            self.selected_index = (self.selected_index - 1) % len(self.choices)
        self.draw()

    def get_value(self):
        return self.choices[self.selected_index]

class Button(ClickableObject):
    def __init__(self, screen, label, x, y, color, action=None, next_left=None, next_up=None, next_right=None, next_down=None):
        super().__init__(screen, x, y, len(label) + 4, 3, action, next_left, next_up, next_right, next_down)
        self.label = label
        self.color = color

    def draw(self):
        self.button_win = self.screen.subwin(self.height, self.width, self.y, self.x)
        self.button_win.box()
        color_pair = curses.color_pair(self.color)
        if self.is_selected:
            color_pair |= curses.A_REVERSE
        self.button_win.addstr(1, 2, self.label, color_pair)
        self.button_win.refresh()

    def change_color(self, color):
        self.color = color
