'''
Copyright 2011 Mikel Azkolain

This file is part of Spotimc.

Spotimc is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Spotimc is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Spotimc.  If not, see <http://www.gnu.org/licenses/>.
'''


import xbmc
import xbmcgui
import weakref
from inspect import isfunction


def iif(cond, on_true, on_false):
    if cond:
        if not isfunction(on_true):
            return on_true
        else:
            return on_true()
    else:
        if not isfunction(on_false):
            return on_false
        else:
            return on_false()


class ViewManager:
    __window = None
    __view_list = None
    __position = None
    
    __vars = None
    
    
    def __init__(self, window):
        self.__window = weakref.proxy(window)
        self.__view_list = []
        self.__position = -1
        self.__vars = {}
        
    
    def num_views(self):
        return len(self.__view_list)
    
    
    def position(self):
        return self.__position
    
    
    def has_next(self):
        return(
            self.num_views() > 0
            and self.position() < self.num_views() - 1
        )
    
    
    def _show_view(self, view):
        view.show(self)
        container_id = view.get_container_id()
        if container_id is not None:
            xbmc.executebuiltin("Control.SetFocus(%d)" % container_id)
    
    
    def next(self):
        #Fail if no next window
        if not self.has_next():
            raise IndexError("No more views available")
        
        #If there's one active
        if self.__position != -1:
            self.__view_list[self.__position].hide(self)
        
        #Show the next one
        self.__position += 1
        self._show_view(self.__view_list[self.__position])
    
    
    def has_previous(self):
        return self.__position > 0
    
    
    def previous(self):
        #Fail if no previous window
        if not self.has_previous():
            raise IndexError("No previous views available")
        
        #Hide current
        self.__view_list[self.__position].hide(self)
        
        #Show previous
        self.__position -= 1
        self._show_view(self.__view_list[self.__position])
    
    
    def add_view(self, view):
        #Remove all views that come next (if any)
        del self.__view_list[self.__position+1:]
        
        #Add the new one
        self.__view_list.append(view)
        
        #Go to the next view
        self.next()
    
    
    def click(self, control_id):
        self.__view_list[self.__position].click(self, control_id)
    
    
    def action(self, action_id):
        self.__view_list[self.__position].action(self, action_id)
    
    
    def show(self, give_focus=True):
        self.__view_list[self.__position].show(self, give_focus)
    
    
    def clear_views(self):
        #Check at least if a view is visible
        if self.__position != -1:
            #Hide current
            self.__view_list[self.__position].hide(self)
            
            #Delete all views
            self.__view_list = []
            
            #And reset the position counter
            self.__position = -1
    
    
    def set_var(self, name, value):
        self.__vars[name] = value
    
    
    def get_var(self, name):
        return self.__vars[name]
    
    
    def get_window(self):
        return self.__window



class BaseView:
    __is_visible = None
    
    
    def __init__(self):
        self.__is_visible = False
    
    
    def is_visible(self):
        return self.__is_visible
    
        
    def click(self, view_manager, control_id):
        pass
    
    
    def action(self, view_manager, action_id):
        pass
    
    
    def show(self, view_manager, give_focus=True):
        self.__is_visible = True
    
    
    def hide(self, view_manager):
        self.__is_visible = False
    
    
    def back(self, view_manager):
        pass
    
    
    def get_container_id(self):
        pass



class BaseContainerView(BaseView):
    def render(self, view_manager):
        """Tell the view to render it's content.
        
        The view should return True if the content was rendered successfully,
        and False if data was not still available.
        """
        raise NotImplementedError()
    
    
    def get_container(self, view_manager):
        raise NotImplementedError()
    
    
    def show(self, view_manager, give_focus=True):
        BaseView.show(self, view_manager, give_focus)
        
        #Hide container and show loading anim.
        self.get_container(view_manager).setVisibleCondition('false')
        view_manager.get_window().show_loading()
        
        if self.render(view_manager):
            #Hide loading and show container
            view_manager.get_window().hide_loading()
            self.get_container(view_manager).setVisibleCondition('true')
            
            #And give focus if asked to do so
            if give_focus:
                view_manager.get_window().setFocus(
                    self.get_container(view_manager)
                )
    
    
    def hide(self, view_manager):
        BaseView.hide(self, view_manager)
        
        #Just hide the container
        self.get_container(view_manager).setVisibleCondition('false')



class BaseListContainerView(BaseContainerView):
    __list_position = None
    
    
    def get_list(self, view_manager):
        raise NotImplementedError()
    
    
    def has_context_menu(self):
        return False
    
    
    def action(self, view_manager, action_id):
        if action_id in [117] and self.has_context_menu():
            #if the context menu is active...
            if not xbmc.getCondVisibility('ControlGroup(5000).HasFocus()'):
                view_manager.get_window().setFocus(self.get_list(view_manager))
                xbmc.executebuiltin('Action(left)')
                print "should pop the list"
            else:
                xbmc.executebuiltin('Action(right)')
    
    
    def show(self, view_manager, give_focus=True):
        BaseView.show(self, view_manager, give_focus)
        window = view_manager.get_window()
        
        #Hide container and show loading anim.
        self.get_container(view_manager).setVisibleCondition('false')
        window.show_loading()
        
        if self.render(view_manager):
            #If we have a stored list position
            if self.__list_position is not None:
                self.get_list(view_manager).selectItem(self.__list_position)
            
            #Not list position? Set it on the start
            else:
                self.get_list(view_manager).selectItem(0)
            
            #List was rendered but with no items, add a placeholder
            if self.get_list(view_manager).size() == 0:
                window.setProperty('ListWithNoItems', 'true')
                item = xbmcgui.ListItem()
                item.setProperty('NoItems', 'true')
                self.get_list(view_manager).addItem(item)
                
            else:
                window.setProperty('ListWithNoItems', 'false')
            
            #Hide loading and show container
            window.hide_loading()
            self.get_container(view_manager).setVisibleCondition('true')
            
            #And give focus if asked to do so
            if give_focus:
                view_manager.get_window().setFocus(
                    self.get_container(view_manager)
                )
    
    
    def hide(self, view_manager):
        BaseView.hide(self, view_manager)
        
        #Keep the list position
        list_obj = self.get_list(view_manager)
        self.__list_position = list_obj.getSelectedPosition()
        
        #And call the container stuff
        BaseContainerView.hide(self, view_manager)
