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


import xbmcgui
import views
#import views.home
import views.newstuff
import views.album
import views.search
import views.nowplaying
import views.playlists.list
import views.playlists.detail
import views.more

import dialogs

import playback

import weakref


class MainWindow(xbmcgui.WindowXML):
    __view_manager = None
    __session = None
    __playlist_manager = None
    
    #Button id constants
    now_playing_button = 201
    new_stuff_button = 212
    playlists_button = 213
    search_button = 214
    more_button = 215
    exit_button = 216
    
    #Loading gif id
    loading_image = 50
    
    
    def __init__(self, file, script_path, skin_dir):
        self.__view_manager = views.ViewManager(self)
        
    
    def initialize(self, session, proxy_runner):
        self.__session = session
        self.__playlist_manager = playback.PlaylistManager(proxy_runner.get_port())
        
        #Shared vars with views
        self.__view_manager.set_var('playlist_manager', self.__playlist_manager)
        self.__view_manager.set_var('session', weakref.proxy(session))
        self.__view_manager.set_var('proxy_runner', weakref.proxy(proxy_runner))
    
    
    def show_loading(self):
        c = self.getControl(MainWindow.loading_image)
        c.setVisibleCondition("True")
    
    
    def hide_loading(self):
        c = self.getControl(MainWindow.loading_image)
        c.setVisibleCondition("False")


    def onInit(self):
        # Check if we already added views because after
        # exiting music vis this gets called again.  
        if self.__view_manager.num_views() == 0:
            #Start the new stuff view by default
            self.setProperty('MainActiveTab', 'newstuff')
            v = views.newstuff.NewStuffView(self.__session)
            self.__view_manager.add_view(v)
    
    
    def onAction(self, action):
        if action.getId() in [9,10,92]:
            if self.__view_manager.position() > 0:
                self.__view_manager.previous()
        
        #Noop action
        elif action.getId() in [0,999]:
            self.__view_manager.show()
    
    
    def _process_layout_click(self, control_id):
        if control_id == MainWindow.now_playing_button:
            self.setProperty('MainActiveTab', 'nowplaying')
            v = views.nowplaying.NowPlayingView()
            self.__view_manager.clear_views()
            self.__view_manager.add_view(v)
            
        elif control_id == MainWindow.playlists_button:
            self.setProperty('MainActiveTab', 'playlists')
            c = self.__session.playlistcontainer()
            pm = self.__playlist_manager
            v = views.playlists.list.PlaylistView(self.__session, c, pm)
            self.__view_manager.clear_views()
            self.__view_manager.add_view(v)
        
        elif control_id == MainWindow.new_stuff_button:
            self.setProperty('MainActiveTab', 'newstuff')
            v = views.newstuff.NewStuffView(self.__session)
            self.__view_manager.clear_views()
            self.__view_manager.add_view(v)
        
        elif control_id == MainWindow.search_button:
            term = views.search.ask_search_term()
            if term:
                self.setProperty('MainActiveTab', 'search')
                v = views.search.SearchTracksView(self.__session, term)
                self.__view_manager.clear_views()
                self.__view_manager.add_view(v)
        
        elif control_id == MainWindow.more_button:
            self.setProperty('MainActiveTab', 'more')
            v = views.more.MoreView()
            self.__view_manager.clear_views()
            self.__view_manager.add_view(v)
        
        elif control_id == MainWindow.exit_button:
            self.close()
    
    
    def onClick(self, control_id):
        #IDs lower than 1000 belong to the common layout
        if control_id < 1000:
            self._process_layout_click(control_id)
        
        #Hand the rest to the view manager
        else:
            self.__view_manager.click(control_id)
        
    
    def onFocus(self, controlID):
        pass