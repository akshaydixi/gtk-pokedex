# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
# This file is in the public domain
### END LICENSE
import sqlite3,os
import gettext
from gettext import gettext as _
gettext.textdomain('myapp')

from gi.repository import Gtk,Gdk # pylint: disable=E0611
import logging
logger = logging.getLogger('myapp')

from myapp_lib import Window
from myapp.AboutMyappDialog import AboutMyappDialog
from myapp.PreferencesMyappDialog import PreferencesMyappDialog

# See myapp_lib.Window.py for more details about how this class works
class MyappWindow(Window):
    __gtype_name__ = "MyappWindow"
    
    def finish_initializing(self, builder): # pylint: disable=E1002
        """Set up the main window"""
        super(MyappWindow, self).finish_initializing(builder)

        self.AboutDialog = AboutMyappDialog
        self.PreferencesDialog = PreferencesMyappDialog
        # Code for other initialization actions should be added here.
        self.directory = os.getcwd()
        self.scrolled_window = builder.get_object('scrolled_window')
        self.main_image = builder.get_object('main_image')
        self.entry = builder.get_object('query_entry')
        tree = builder.get_object('tree')
        self.select = builder.get_object('select')
        self.label_name = builder.get_object('label_name')
        self.label_desc = builder.get_object('label_desc')
        self.label_genus = builder.get_object('label_genus')
        self.image_type1 = builder.get_object('image_type1')
        self.image_type2 = builder.get_object('image_type2')
        self.label_ability = builder.get_object('label_ability')
        self.label_hp = builder.get_object('label_hp')
        self.entry_hp = builder.get_object('entry_hp')
        self.label_attack = builder.get_object('label_attack')
        self.entry_attack = builder.get_object('entry_attack')
        self.label_defense = builder.get_object('label_defense')
        self.label_special_attack = builder.get_object('label_special_attack')
        self.label_special_defense = builder.get_object('label_special_defense')
        self.label_speed = builder.get_object('label_speed')
        self.entry_defense = builder.get_object('entry_defense')
        self.entry_special_attack = builder.get_object('entry_special_attack')
        self.entry_special_defense = builder.get_object('entry_special_defense')
        self.entry_speed = builder.get_object('entry_speed')
        self.label_height = builder.get_object('label_height')
        self.label_weight = builder.get_object('label_weight')
        
        #Basic touches
        self.label_hp.set_markup('<span weight="bold" size = "large" >HP</span>')
        self.entry_hp.set_can_focus(False)
        self.label_attack.set_markup('<span weight="bold" size = "large" >Attack</span>')
        self.entry_attack.set_can_focus(False)
        self.label_defense.set_markup('<span weight="bold" size = "large" >Defense</span>')
        self.entry_defense.set_can_focus(False)
        self.label_special_attack.set_markup('<span weight="bold" size = "large" >Special Attack</span>')
        self.entry_special_attack.set_can_focus(False)
        self.label_special_defense.set_markup('<span weight="bold" size = "large" >Special Defense</span>')
        self.entry_special_defense.set_can_focus(False)
        self.label_speed.set_markup('<span weight="bold" size = "large" >Speed</span>')
        self.entry_speed.set_can_focus(False)
        
        
        # Retrieving data from database
        connection = sqlite3.connect(self.directory+'/data/pokedex.db')
        self.cursor = connection.cursor()
        self.cursor.execute('SELECT pokemon_species_id,name,genus FROM pokemon_species_names WHERE local_language_id = 9')
        self.result1 = self.cursor.fetchall() 
        
        # Creating TreeList and ListStore
        
        
        store = Gtk.ListStore (int,str,str)
        for i in range ( len(self.result1) ):
            treeiter = store.append(self.result1[i])
        
        # Creating filter for queried searches    
        self.filter = store.filter_new()
        self.filter.set_visible_func(self.filter_function , data=None)
        self.storesort = Gtk.TreeModelSort(model = self.filter)
        
        tree.set_model(self.storesort)
        self.model = tree.get_model()
        
        # Creating CellRenders 
        
        renderer_serialno = Gtk.CellRendererText()
        renderer_name = Gtk.CellRendererText()
        
        # Creating columns
        
        column_serialno = Gtk.TreeViewColumn('S.No',renderer_serialno,text=0)
        column_name = Gtk.TreeViewColumn('Name',renderer_name,text=1)
        
        # Appending columns to tree
        
        tree.append_column(column_serialno)
        tree.append_column(column_name)
        
        # Creating TreeViewSelection
        
        self.select = tree.get_selection()
        self.select.connect('changed',self.on_tree_selection_changed)
        
        # Building GUI
        self.scrolled_window.set_hexpand(True)
        self.scrolled_window.set_vexpand(True)
        self.on_query_entry_activate(self.entry)
                
        
    def on_tree_selection_changed(self,select):
        model,treeiter = select.get_selected()
        image_name = str(model[treeiter][0])
        
        # Setting up labels for Pokemon name and Genus
        self.label_name.set_markup('<span font_weight = "heavy" font_size="xx-large" >'+str(model[treeiter][1])+'</span>')
        self.label_genus.set_markup('<span size="large">'+str(model[treeiter][2])+'</span>'+'<span font_weight = "bold"> Pok'+unicode(unichr(233))+'mon</span>')
        
        # Retrieving data for Type and Description
        self.cursor.execute('SELECT * FROM main_pokemon_table WHERE pokemon_id = '+image_name )
        
        result = self.cursor.fetchall()        
        self.label_desc.set_markup('<span weight = "bold" size = "x-large">Description</span><span size="medium">\n'+result[0][11]+'</span>')
        self.image_type1.set_from_file(self.directory+'/data/media/types/'+result[0][9]+'.png')
        self.image_type2.set_from_file(self.directory+'/data/media/types/'+result[0][10]+'.png')
        
        
        # Retrieving data for Abilities    
        self.cursor.execute('SELECT ability_names.name FROM pokemon_abilities,ability_names WHERE pokemon_abilities.ability_id = ability_names.ability_id  AND local_language_id = 9 AND pokemon_id = '+str(eval(image_name[0:3])))
        abilities = ''
        for ability in self.cursor.fetchall():
            abilities = str(ability[0])+'\n'+abilities
        
        self.label_ability.set_markup('<span weight = "bold" size = "x-large">Abilities\n</span>'+abilities)
        
        # Setting height and weight
        self.label_weight.set_markup('<span size = "large" >Weight : '+ str(result[0][8])+'</span>')
        self.label_height.set_markup('<span size = "large" >Height : '+ str(result[0][7])+'</span>')
        
        
        # Setting stat bars
        self.entry_hp.set_progress_fraction(result[0][1]/100)
        self.entry_attack.set_progress_fraction(result[0][2]/100)
        self.entry_defense.set_progress_fraction(result[0][3]/100)
        self.entry_special_attack.set_progress_fraction(result[0][4]/100)
        self.entry_special_defense.set_progress_fraction(result[0][5]/100)
        self.entry_speed.set_progress_fraction(result[0][6]/100)
            
        # Setting main Pokemon image
        while (len(image_name)<3):
            image_name = '0'+image_name
        image_name+='.png'        
        self.main_image.set_from_file(self.directory+'/data/media/sugimori/'+image_name)
    
    
    def filter_function(self,model,iter,query):
        if(self.entry.get_text()==''):
        
            return True
        check = model[iter][1].lower()
        if str(self.entry.get_text().lower()) not in str(check):
            return False
        return True
    
    def on_query_entry_activate(self,entry):
        self.filter.refilter()
        self.select.select_iter(self.model.get_iter_first())        
