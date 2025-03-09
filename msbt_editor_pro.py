from msbt import *
from util import *
import tkinter as tk
from tkinter import ttk, filedialog, simpledialog
from PIL import ImageTk, Image
import sys, os
import platform
import random
import time
import types
import re

cgi = types.ModuleType('cgi')
cgi.parse_header = lambda x: ('text/plain', {})
sys.modules['cgi'] = cgi

from googletrans import Translator

# Dark theme colors
BG_COLOR = "#2d2d2d"
FG_COLOR = "#ffffff"
ACCENT_COLOR = "#4a9c82"
ENTRY_BG = "#404040"
BUTTON_BG = "#3c3f41"
TEXT_BG = "#363636"
SELECT_BG = "#4a7a9c"
DISABLED_FG = "#777777"

operating_system = platform.system()
script_dir = os.path.dirname(sys.argv[0])
resources_dir = os.path.join(script_dir, 'resources')
cache_file_dir = os.path.join(script_dir, "cache", "cache.txt")

class DarkTheme:
    @staticmethod
    def configure_styles():
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('.', 
            background=BG_COLOR,
            foreground=FG_COLOR,
            fieldbackground=ENTRY_BG,
            selectbackground=SELECT_BG,
            selectforeground=FG_COLOR
        )
        
        style.configure('TFrame', background=BG_COLOR)
        style.configure('TLabel', background=BG_COLOR, foreground=FG_COLOR)
        style.configure('TButton', 
            background=BUTTON_BG,
            foreground=FG_COLOR,
            borderwidth=0,
            focuscolor=BG_COLOR
        )
        style.map('TButton',
            background=[('active', ACCENT_COLOR), ('disabled', BG_COLOR)],
            foreground=[('disabled', DISABLED_FG)]
        )
        style.configure('TEntry', 
            fieldbackground=ENTRY_BG,
            foreground=FG_COLOR,
            insertcolor=FG_COLOR
        )
        style.configure('TCombobox', 
            fieldbackground=ENTRY_BG,
            foreground=FG_COLOR
        )
        style.configure('Vertical.TScrollbar', 
            background=BUTTON_BG,
            troughcolor=BG_COLOR
        )
        style.configure('Horizontal.TScrollbar', 
            background=BUTTON_BG,
            troughcolor=BG_COLOR
        )
        style.configure('TProgressbar', 
            troughcolor=BG_COLOR,
            background=ACCENT_COLOR
        )

class gui():
    def __init__(self):
        self.msbt = None
        self.file_open = False
        self.modified = False
        self.translator = Translator()

        self.window = tk.Tk()
        self.window.title("MSBT Editor Pro + Translations")
        DarkTheme.configure_styles()
        
        # Set favicon
        try:
            favicon_path = os.path.join(resources_dir, "favicon.png")
            favicon_image = ImageTk.PhotoImage(Image.open(favicon_path))
            self.window.iconphoto(True, favicon_image)
        except Exception as e:
            print(f"Error loading favicon: {e}")

        self.window.configure(bg=BG_COLOR)
        self.window.minsize(width=864, height=550)
        self.window.geometry("864x550")
        self.window['padx'] = 5
        self.window['pady'] = 5

        # Menu bar
        menu_style = {
            'bg': BUTTON_BG,
            'fg': FG_COLOR,
            'activebackground': ACCENT_COLOR,
            'activeforeground': FG_COLOR
        }
        
        menubar = tk.Menu(self.window, **menu_style)
        
        # File menu
        filemenu = tk.Menu(menubar, tearoff=0, **menu_style)
        filemenu.add_command(label="Open", command=lambda: self.open_file())
        filemenu.add_command(label="Save", command=lambda: self.save())
        filemenu.add_command(label="Save As", command=lambda: self.save_as())
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.window.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        # Clean Text menu
        cleantextmenu = tk.Menu(menubar, tearoff=0, **menu_style)
        cleantextmenu.add_command(label="Clean Export", command=lambda: self.clean_export())
        cleantextmenu.add_command(label="Batch Clean Export", command=lambda: self.batch_clean_export())
        cleantextmenu.add_separator()
        cleantextmenu.add_command(label="Auto Import", command=lambda: self.clean_import())
        cleantextmenu.add_command(label="Batch Auto Import", command=lambda: self.batch_clean_import())
        menubar.add_cascade(label="Clean Text", menu=cleantextmenu)

        # Coded Text menu
        codedtextmenu = tk.Menu(menubar, tearoff=0, **menu_style)
        codedtextmenu.add_command(label="Coded Export", command=lambda: self.coded_export())
        codedtextmenu.add_command(label="Batch Coded Export", command=lambda: self.batch_coded_export())
        codedtextmenu.add_separator()
        codedtextmenu.add_command(label="Import", command=lambda: self.coded_import())
        codedtextmenu.add_command(label="Batch Import", command=lambda: self.batch_coded_import())
        menubar.add_cascade(label="Coded Text", menu=codedtextmenu)

        # Translate menu
        translatemenu = tk.Menu(menubar, tearoff=0, **menu_style)
        translatemenu.add_command(label="1 time", command=lambda: self.translate_text(1))
        translatemenu.add_command(label="2 times", command=lambda: self.translate_text(2))
        translatemenu.add_command(label="5 times", command=lambda: self.translate_text(5))
        translatemenu.add_command(label="10 times", command=lambda: self.translate_text(10))
        translatemenu.add_command(label="25 times", command=lambda: self.translate_text(25))
        translatemenu.add_command(label="50 times", command=lambda: self.translate_text(50))
        translatemenu.add_command(label="100 times", command=lambda: self.translate_text(100))
        translatemenu.add_command(label="150 times", command=lambda: self.translate_text(150))
        translatemenu.add_command(label="250 times", command=lambda: self.translate_text(250))
        translatemenu.add_command(label="500 times", command=lambda: self.translate_text(500))
        translatemenu.add_command(label="1000 times", command=lambda: self.translate_text(1000))
        menubar.add_cascade(label="Translate", menu=translatemenu)

        self.window.config(menu=menubar)

        # Labels List Frame
        labels_list_frame = ttk.Frame(self.window)
        labels_list_frame.grid(row=0, column=0, sticky=tk.NSEW)

        self.labels_label = ttk.Label(labels_list_frame, text="String")
        self.labels_label.grid(row=0, columnspan=4)

        labels_listbox_subframe = ttk.Frame(labels_list_frame)
        labels_listbox_subframe.grid(row=1, column=0, columnspan=4, sticky=tk.NSEW)

        self.Labels_List = []
        self.labels_listbox_value = tk.StringVar(value=self.Labels_List)
        
        scrollbar = ttk.Scrollbar(labels_listbox_subframe, style="Vertical.TScrollbar")
        self.labels_listbox = tk.Listbox(
            labels_listbox_subframe,
            listvariable=self.labels_listbox_value,
            yscrollcommand=scrollbar.set,
            bg=ENTRY_BG,
            fg=FG_COLOR,
            selectbackground=SELECT_BG,
            selectforeground=FG_COLOR,
            borderwidth=0,
            highlightthickness=0
        )
        self.labels_listbox.bind("<<ListboxSelect>>", lambda _: self.listbox_change())
        scrollbar.config(command=self.labels_listbox.yview)
        
        self.labels_listbox.grid(row=0, column=0, sticky=tk.NSEW)
        scrollbar.grid(row=0, column=1, sticky=tk.NS)

        labels_listbox_subframe.grid_rowconfigure(0, weight=1)
        labels_listbox_subframe.grid_columnconfigure(0, weight=1)
        labels_listbox_subframe.grid_columnconfigure(1, weight=0)

        # Label Entry and Buttons
        self.label_entry_var = tk.StringVar()
        label_entry = ttk.Entry(labels_list_frame, textvariable=self.label_entry_var)
        label_entry.grid(row=2, column=0, sticky=tk.EW)

        # Load white icons for dark mode
        icon_images = {
            'save': self.load_icon("save_icon.png"),
            'add': self.load_icon("add_icon.png"),
            'remove': self.load_icon("remove_icon.png")
        }

        button_style = {
            'bg': BG_COLOR,
            'activebackground': ACCENT_COLOR,
            'borderwidth': 0,
            'highlightthickness': 0
        }

        self.save_label_button = tk.Button(
            labels_list_frame,
            image=icon_images['save'],
            **button_style,
            command=lambda: self.save_label()
        )
        self.save_label_button.grid(row=2, column=1)

        self.add_label_button = tk.Button(
            labels_list_frame,
            image=icon_images['add'],
            **button_style,
            command=lambda: self.add_label()
        )
        self.add_label_button.grid(row=2, column=2)

        self.remove_label_button = tk.Button(
            labels_list_frame,
            image=icon_images['remove'],
            **button_style,
            command=lambda: self.remove_label()
        )
        self.remove_label_button.grid(row=2, column=3)

        labels_list_frame.grid_rowconfigure(0, weight=0)
        labels_list_frame.grid_rowconfigure(1, weight=1)
        labels_list_frame.grid_rowconfigure(2, weight=0)
        labels_list_frame.grid_columnconfigure(0, weight=1)

        # Current String Frame
        current_string_frame = ttk.Frame(self.window)
        current_string_frame.grid(row=0, column=1, sticky=tk.NSEW)

        edit_label = ttk.Label(current_string_frame, text="Edit")
        edit_label.grid(row=0, column=0)

        text_style = {
            'bg': TEXT_BG,
            'fg': FG_COLOR,
            'insertbackground': FG_COLOR,
            'selectbackground': SELECT_BG,
            'selectforeground': FG_COLOR,
            'borderwidth': 0,
            'highlightthickness': 0
        }

        self.edit_string_text = CallbackText(current_string_frame, **text_style)
        self.edit_string_text.bind("<<TextModified>>", lambda x: self.edit_text_change())
        self.edit_string_text.grid(row=1, column=0, sticky=tk.NSEW)

        self.restore_original_text_button = ttk.Button(
            current_string_frame,
            text="Restore Original",
            command=lambda: self.restore_original_text()
        )
        self.restore_original_text_button['state'] = 'disabled'
        self.restore_original_text_button.grid(row=2, column=0)

        self.original_string_text = tk.Text(
            current_string_frame,
            state='disabled',
            **text_style
        )
        self.original_string_text.grid(row=3, column=0, sticky=tk.EW)

        current_string_frame.grid_rowconfigure(0, weight=0)
        current_string_frame.grid_rowconfigure(1, weight=1)
        current_string_frame.grid_rowconfigure(2, weight=0)
        current_string_frame.grid_rowconfigure(3, weight=0)
        current_string_frame.grid_columnconfigure(0, weight=1)

        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=0)
        self.window.grid_columnconfigure(1, weight=1)

        self.window.mainloop()

    def load_icon(self, filename):
        path = os.path.join(resources_dir, filename)
        try:
            img = Image.open(path).convert('L').point(lambda x: 255 if x > 40 else 0)
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Error loading icon {filename}: {e}")
            return ImageTk.PhotoImage(Image.new('RGB', (16, 16)))

    def translate_text(self, iterations):
        if self.msbt is None:
            tk.messagebox.showerror("Error", "No MSBT file loaded!")
            return

        LANGUAGES = {
            'af': 'Afrikaans', 'sq': 'Albanian', 'am': 'Amharic', 'ar': 'Arabic', 'hy': 'Armenian',
            'as': 'Assamese', 'az': 'Azerbaijani', 'eu': 'Basque', 'be': 'Belarusian', 'bn': 'Bengali',
            'bs': 'Bosnian', 'bg': 'Bulgarian', 'ca': 'Catalan', 'ceb': 'Cebuano', 'ny': 'Chichewa',
            'zh-CN': 'Chinese (Simplified)', 'zh-TW': 'Chinese (Traditional)', 'co': 'Corsican',
            'hr': 'Croatian', 'cs': 'Czech', 'da': 'Danish', 'dv': 'Dhivehi', 'doi': 'Dogri',
            'nl': 'Dutch', 'en': 'English', 'eo': 'Esperanto', 'et': 'Estonian', 'ee': 'Ewe',
            'tl': 'Filipino', 'fi': 'Finnish', 'fr': 'French', 'fy': 'Frisian', 'gl': 'Galician',
            'ka': 'Georgian', 'de': 'German', 'el': 'Greek', 'gu': 'Gujarati', 'ht': 'Haitian Creole',
            'ha': 'Hausa', 'haw': 'Hawaiian', 'iw': 'Hebrew', 'hi': 'Hindi', 'hmn': 'Hmong',
            'hu': 'Hungarian', 'is': 'Icelandic', 'ig': 'Igbo', 'id': 'Indonesian', 'ga': 'Irish',
            'it': 'Italian', 'ja': 'Japanese', 'jw': 'Javanese', 'kn': 'Kannada', 'kk': 'Kazakh',
            'km': 'Khmer', 'rw': 'Kinyarwanda', 'ko': 'Korean', 'ku': 'Kurdish (Kurmanji)',
            'ky': 'Kyrgyz', 'lo': 'Lao', 'la': 'Latin', 'lv': 'Latvian', 'lt': 'Lithuanian',
            'lb': 'Luxembourgish', 'mk': 'Macedonian', 'mg': 'Malagasy', 'ms': 'Malay', 'ml': 'Malayalam',
            'mt': 'Maltese', 'mi': 'Maori', 'mr': 'Marathi', 'mn': 'Mongolian', 'my': 'Myanmar (Burmese)',
            'ne': 'Nepali', 'no': 'Norwegian', 'or': 'Odia (Oriya)', 'ps': 'Pashto', 'fa': 'Persian',
            'pl': 'Polish', 'pt': 'Portuguese', 'pa': 'Punjabi', 'ro': 'Romanian', 'ru': 'Russian',
            'sm': 'Samoan', 'gd': 'Scots Gaelic', 'sr': 'Serbian', 'st': 'Sesotho', 'sn': 'Shona',
            'sd': 'Sindhi', 'si': 'Sinhala', 'sk': 'Slovak', 'sl': 'Slovenian', 'so': 'Somali',
            'es': 'Spanish', 'su': 'Sundanese', 'sw': 'Swahili', 'sv': 'Swedish', 'tg': 'Tajik',
            'ta': 'Tamil', 'tt': 'Tatar', 'te': 'Telugu', 'th': 'Thai', 'tr': 'Turkish',
            'tk': 'Turkmen', 'uk': 'Ukrainian', 'ur': 'Urdu', 'ug': 'Uyghur', 'uz': 'Uzbek',
            'vi': 'Vietnamese', 'cy': 'Welsh', 'xh': 'Xhosa', 'yi': 'Yiddish', 'yo': 'Yoruba',
            'zu': 'Zulu'
        }

        config_window = tk.Toplevel(self.window)
        config_window.title("Translation Settings")
        config_window.geometry("320x240")

        ttk.Label(config_window, text="Source Language:").pack(pady=2)
        source_var = tk.StringVar(value='French')
        source_combo = ttk.Combobox(config_window, textvariable=source_var, 
                                    values=list(LANGUAGES.values()), state="readonly")
        source_combo.pack(pady=2)

        ttk.Label(config_window, text="Target Language:").pack(pady=2)
        target_var = tk.StringVar(value='Spanish')
        target_combo = ttk.Combobox(config_window, textvariable=target_var, 
                                    values=list(LANGUAGES.values()), state="readonly")
        target_combo.pack(pady=2)
        
        ttk.Label(config_window, text="Random Translation Iterations:").pack(pady=2)
        iterations_var = tk.IntVar(value=iterations)
        iterations_spin = ttk.Spinbox(config_window, from_=1, to=10, textvariable=iterations_var)
        iterations_spin.pack(pady=2)

        def start_translation():
            src = [k for k, v in LANGUAGES.items() if v == source_var.get()][0]
            dest = [k for k, v in LANGUAGES.items() if v == target_var.get()][0]
            iters = iterations_var.get()
            config_window.destroy()

            progress_window = tk.Toplevel(self.window)
            progress_window.title("Translation Progress")
            progress_window.geometry("500x200")
            
            progress_frame = ttk.Frame(progress_window)
            progress_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            progress_bar = ttk.Progressbar(progress_frame, maximum=100, mode="determinate")
            progress_bar.pack(fill=tk.X, pady=5)
            
            info_frame = ttk.Frame(progress_frame)
            info_frame.pack(fill=tk.X)
            
            percent_label = ttk.Label(info_frame, text="0% completed")
            percent_label.pack(side=tk.LEFT, padx=5)
            
            iter_label = ttk.Label(info_frame, text=f"String 1/{len(self.msbt.txt2.Strings)}")
            iter_label.pack(side=tk.RIGHT, padx=5)
            
            preview_frame = ttk.LabelFrame(progress_frame, text="Current Processing")
            preview_frame.pack(fill=tk.BOTH, expand=True, pady=5)
            
            original_label = ttk.Label(preview_frame, text="Original: ")
            original_label.pack(anchor=tk.W)
            
            path_label = ttk.Label(preview_frame, text="Path: ")
            path_label.pack(anchor=tk.W)
            
            translated_label = ttk.Label(preview_frame, text="Translated: ")
            translated_label.pack(anchor=tk.W)

            try:
                translator = Translator(service_urls=[
                    'translate.google.com',
                    'translate.google.co.kr',
                    'translate.google.co.jp',
                    'translate.google.fr',
                ], user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

                all_languages = list(LANGUAGES.keys())
                total = len(self.msbt.txt2.Strings)
                
                for idx, original in enumerate(self.msbt.txt2.Strings):
                    iter_label.config(text=f"String {idx+1}/{total}")
                    
                    try:
                        if isinstance(original, bytes):
                            original_clean = original.decode('utf-8', 'surrogateescape')
                        else:
                            original_clean = original
                    except:
                        if isinstance(original, bytes):
                            original_clean = original.decode('latin-1', 'surrogateescape')
                        else:
                            original_clean = original
                    
                    preview_original = original_clean[:40] + ("..." if len(original_clean) > 40 else "")
                    original_label.config(text=f"Original: {preview_original}")
                    
                    parts = re.split(r'(<[^>]+>)', original_clean)
                    current_text = original_clean
                    
                    if iters == 1:
                        path_label.config(text=f"Path: {LANGUAGES[src]} → {LANGUAGES[dest]}")
                        progress_window.update()
                        
                        translated_segments = []
                        for part in parts:
                            if not part:
                                continue
                                
                            if re.match(r'<[^>]+>', part):
                                translated_segments.append(part)
                            else:
                                try:
                                    translated = translator.translate(part, src=src, dest=dest).text
                                    translated = translated.encode('latin-1', 'replace').decode('utf-8')
                                    translated_segments.append(translated)
                                except:
                                    try:
                                        time.sleep(0.5)
                                        translated = translator.translate(part, src=src, dest=dest).text
                                        translated = translated.encode('latin-1', 'replace').decode('utf-8')
                                        translated_segments.append(translated)
                                    except:
                                        translated_segments.append(part)
                        
                        current_text = ''.join(translated_segments)
                        current_text = current_text.encode('utf-8', 'surrogateescape').decode('utf-8')
                        
                        preview_translated = current_text[:40] + ("..." if len(current_text) > 40 else "")
                        translated_label.config(text=f"Translated: {preview_translated}")
                        
                        progress = (idx + 1) / total * 100
                        progress_bar['value'] = progress
                        percent_label.config(text=f"{progress:.1f}% completed")
                        progress_window.update()
                        
                    else:
                        current_src = src
                        translation_path = [LANGUAGES[src]]
                        
                        for iteration in range(1, iters + 1):
                            if iteration < iters:
                                available_langs = [lang for lang in all_languages if lang != current_src and lang != dest]
                                if available_langs:
                                    current_dest = random.choice(available_langs)
                                else:
                                    current_dest = dest
                            else:
                                current_dest = dest
                            
                            translation_path.append(LANGUAGES[current_dest])
                            path_str = " → ".join(translation_path)
                            path_label.config(text=f"Iteration {iteration}/{iters} with {LANGUAGES[current_dest]}")
                            
                            parts = re.split(r'(<[^>]+>)', current_text)
                            translated_segments = []
                            
                            for part in parts:
                                if not part:
                                    continue
                                    
                                if re.match(r'<[^>]+>', part):
                                    translated_segments.append(part)
                                else:
                                    try:
                                        translated = translator.translate(part, src=current_src, dest=current_dest).text
                                        translated = translated.encode('latin-1', 'replace').decode('utf-8')
                                        translated_segments.append(translated)
                                    except:
                                        try:
                                            time.sleep(0.5)
                                            translated = translator.translate(part, src=current_src, dest=current_dest).text
                                            translated = translated.encode('latin-1', 'replace').decode('utf-8')
                                            translated_segments.append(translated)
                                        except:
                                            translated_segments.append(part)
                            
                            current_text = ''.join(translated_segments)
                            current_text = current_text.encode('utf-8', 'surrogateescape').decode('utf-8')
                            
                            preview_translated = current_text[:40] + ("..." if len(current_text) > 40 else "")
                            translated_label.config(text=f"Translated: {preview_translated}")
                            
                            current_src = current_dest
                            
                            progress = ((idx * iters) + iteration) / (total * iters) * 100
                            progress_bar['value'] = progress
                            percent_label.config(text=f"{progress:.1f}% completed")
                            progress_window.update()
                        
                        path_label.config(text=f"Path: {' → '.join(translation_path)}")
                        progress_window.update()
                    
                    if isinstance(self.msbt.txt2.Strings[idx], bytes):
                        self.msbt.txt2.Strings[idx] = current_text.encode('utf-8', 'surrogateescape')
                    else:
                        self.msbt.txt2.Strings[idx] = current_text
                    
                    self.modified = True
                
                self.fix_any_remaining_encoding_issues()
                
                tk.messagebox.showinfo("Success", "Translation completed successfully!\nAll characters and tags preserved.")
                
            except Exception as e:
                tk.messagebox.showerror("Error", f"Translation failure: {str(e)}")
            finally:
                progress_window.destroy()
                self.listbox_change()

        ttk.Button(config_window, text="Start", command=start_translation).pack(pady=10)

    def process_tags(self, text):
        tags = []
        modified = []
        counter = 0
        i = 0
        while i < len(text):
            if text[i] == '<':
                start = i
                while i < len(text) and text[i] != '>':
                    i += 1
                if i < len(text):
                    i += 1
                    tag = text[start:i]
                    placeholder = f"TAG_{counter}"
                    tags.append((placeholder, tag))
                    modified.append(placeholder)
                    counter += 1
                else:
                    modified.append(text[start:i])
            else:
                modified.append(text[i])
                i += 1
        return ''.join(modified), tags

    def restore_tags(self, text, tags):
        for placeholder, tag in tags:
            text = text.replace(placeholder, tag)
        return text.encode('utf-8', 'ignore').decode('utf-8')

    def open_file(self):
        if self.modified == True:
            match ConfirmationPrompt(self.window, "Msbt Editor Pro + Translations", "Would you like to save before opening another file?", ("Yes", "No", "Cancel"), 2).choice:
                case 0:
                    self.save()
                    self.open_msbt()
                case 1:
                    self.open_msbt()
                case 2:
                    pass
        else:
            self.open_msbt()

    def open_msbt(self):
        new_dir = filedialog.askopenfilename(parent=self.window,
                                initialdir=get_initial_directory(cache_file_dir),
                                title="Please select an msbt file:",
                                filetypes=[("MSBT Files", ".msbt")])
        if new_dir != '': 
            self.msbt_dir = new_dir
            self.window.title("Msbt Editor Pro v0.10.1 - "+self.msbt_dir[self.msbt_dir.rindex("/")+1:])
            cache_file = open(cache_file_dir, 'w')
            cache_file.write(self.msbt_dir[:self.msbt_dir.rindex("/")+1])
            cache_file.close()

            self.save_dir = self.msbt_dir
            self.msbt = msbt(self.msbt_dir)
            self.modified = False
            if self.msbt.has_labels:
                Label_List_Copy = self.msbt.lbl1.Labels.copy()
                Label_List_Copy.sort(key=lambda x: x.Index)
                self.Labels_List = [i.name for i in Label_List_Copy]
                self.save_label_button['state'] = 'normal'
                self.add_label_button['state'] = 'normal'
                self.remove_label_button['state'] = 'normal'
            else:
                self.Labels_List = [i for i in self.msbt.txt2.Strings]
                self.save_label_button['state'] = 'disabled'
                self.add_label_button['state'] = 'disabled'
                self.remove_label_button['state'] = 'disabled'
                
            self.labels_listbox_value.set(self.Labels_List)

            if len(self.Labels_List) > 0:
                self.labels_listbox.selection_set(0)
                self.listbox_change()
                self.restore_original_text_button['state'] = 'normal'

    def listbox_change(self):
        cur_index = self.labels_listbox.curselection()[0]
        self.labels_label.configure(text=f"String {cur_index}")
        self.label_entry_var.set(self.labels_listbox.get( cur_index ))

        self.edit_string_text.unbind("<<TextModified>>")
        self.edit_string_text.delete(1.0, tk.END)
        self.edit_string_text.insert(1.0, self.msbt.txt2.Strings[ cur_index ])
        self.edit_string_text.bind("<<TextModified>>", lambda x : self.edit_text_change())

        self.original_string_text['state'] = 'normal'
        self.original_string_text.delete(1.0, tk.END)
        self.original_string_text.insert(1.0, self.msbt.txt2.Original_Strings[ cur_index ])
        self.original_string_text['state'] = 'disabled'

    def edit_text_change(self):
        self.modified = True
        self.msbt.txt2.Strings[ self.labels_listbox.curselection()[0] ] = self.edit_string_text.get("1.0","end-1c")

    def restore_original_text(self):
        cur_index = self.labels_listbox.curselection()[0]
        self.edit_string_text.unbind("<<TextModified>>")
        self.msbt.txt2.Strings[cur_index] = self.msbt.txt2.Original_Strings[cur_index]
        
        self.edit_string_text.delete(1.0, tk.END)
        self.edit_string_text.insert(1.0, self.msbt.txt2.Strings[ cur_index ])
        self.edit_string_text.bind("<<TextModified>>", lambda x : self.edit_text_change())

    def save_label(self):
        new_label = self.label_entry_var.get()[:64]
        if new_label in self.Labels_List:
            pass
        else:
            cur_index = self.labels_listbox.curselection()[0]
            for i in range(len(self.msbt.lbl1.Labels)):
                if self.msbt.lbl1.Labels[i].name == self.Labels_List[cur_index]:
                    break
            self.msbt.rename_label(self.msbt.lbl1.Labels[i], new_label)
            self.Labels_List[cur_index] = new_label
            self.labels_listbox_value.set(self.Labels_List)
            self.modified = True

    def add_label(self):
        new_label = self.label_entry_var.get()[:64]
        if new_label in self.Labels_List:
            pass
        else:
            self.Labels_List += [new_label]
            self.labels_listbox_value.set(self.Labels_List)
            self.msbt.add_label(new_label)
            self.modified = True

    def remove_label(self):
        cur_index = self.labels_listbox.curselection()[0]
        match ConfirmationPrompt(self.window, "Msbt Editor Pro + Translations", f"Are you sure you want to delete \"{self.Labels_List[cur_index]}\"?", ("Yes", "No"), 1).choice:
            case 0:
                for i in range(len(self.msbt.lbl1.Labels)):
                    if self.msbt.lbl1.Labels[i].name == self.Labels_List[cur_index]:
                        break
                self.msbt.remove_label(self.msbt.lbl1.Labels[i])
                self.Labels_List = self.Labels_List[:cur_index] + self.Labels_List[cur_index+1:]
                self.labels_listbox_value.set(self.Labels_List)
                self.modified = True
            case 1:
                pass

    def save(self):
        self.msbt.save(self.save_dir)
        self.modified = False

        self.original_string_text['state'] = 'normal'
        self.original_string_text.delete(1.0, tk.END)
        self.original_string_text.insert(1.0, self.msbt.txt2.Original_Strings[ self.labels_listbox.curselection()[0] ])
        self.original_string_text['state'] = 'disabled'

    def save_as(self):
        new_dir = filedialog.asksaveasfilename(parent=self.window,
                                        initialdir=get_initial_directory(cache_file_dir),
                                        title="Please create a name for your msbt file:",
                                filetypes=[("MSBT Files", ".msbt")])
        if new_dir != '':
            self.save_dir = new_dir

            cache_file = open(cache_file_dir, 'w')
            cache_file.write(self.save_dir[:self.save_dir.rindex("/")+1])
            cache_file.close()

            self.save()

    def coded_export(self):
        csv_dir = filedialog.asksaveasfilename(parent=self.window,
                                        initialdir=get_initial_directory(cache_file_dir),
                                        title="Please create a name for your csv file:",
                                filetypes=[("Comma Seperated Value Files", ".csv")])
        if csv_dir != '' and self.msbt != None:
            cache_file = open(cache_file_dir, 'w')
            cache_file.write(csv_dir[:csv_dir.rindex("/")+1])
            cache_file.close()
            coded_export(self.msbt, csv_dir)

    def batch_coded_export(self):
        msg = "Please select a folder containing the msbt files:"
        msbt_folder_dir = filedialog.askdirectory(
            parent=self.window,
            initialdir=get_initial_directory(cache_file_dir),
            message=msg
            ) if operating_system == "Darwin" else filedialog.askdirectory(
            parent=self.window,
            initialdir=get_initial_directory(cache_file_dir),
            title=msg
            )

        if msbt_folder_dir != '':
            cache_file = open(cache_file_dir, 'w')
            cache_file.write(msbt_folder_dir[:msbt_folder_dir.rindex("/")+1])
            cache_file.close()

            msbt_folder_dir += "/"

            msg = "Please select a folder to export the files to:"
            csv_dir = filedialog.askdirectory(
                parent=self.window,
                initialdir=get_initial_directory(cache_file_dir),
                message=msg
                ) if operating_system == "Darwin" else filedialog.askdirectory(
                parent=self.window,
                initialdir=get_initial_directory(cache_file_dir),
                title=msg
                )

            if csv_dir != '':
                cache_file = open(cache_file_dir, 'w')
                cache_file.write(csv_dir[:csv_dir.rindex("/")+1])
                cache_file.close()

                csv_dir += "/"

                batch_coded_export(msbt_folder_dir, csv_dir)

    def coded_import(self):
        csv_dir = filedialog.askopenfilename(parent=self.window,
                                initialdir=get_initial_directory(cache_file_dir),
                                title="Please select a csv file with \"coded\" strings:",
                                filetypes=[("Comma Seperated Value Files", ".csv")])
        if csv_dir != '' and self.msbt != None:
            cache_file = open(cache_file_dir, 'w')
            cache_file.write(csv_dir[:csv_dir.rindex("/")+1])
            cache_file.close()
            coded_import(self.msbt, csv_dir, self.save_dir)
            self.modified = False
            
            cur_index = self.labels_listbox.curselection()[0]

            self.edit_string_text.unbind("<<TextModified>>")
            self.edit_string_text.delete(1.0, tk.END)
            self.edit_string_text.insert(1.0, self.msbt.txt2.Strings[ cur_index ])
            self.edit_string_text.bind("<<TextModified>>", lambda x : self.edit_text_change())

            self.original_string_text['state'] = 'normal'
            self.original_string_text.delete(1.0, tk.END)
            self.original_string_text.insert(1.0, self.msbt.txt2.Original_Strings[ cur_index ])
            self.original_string_text['state'] = 'disabled'

    def batch_coded_import(self):
        msg = "Please select a folder containing the msbt files:"
        msbt_folder_dir = filedialog.askdirectory(
            parent=self.window,
            initialdir=get_initial_directory(cache_file_dir),
            message=msg
            ) if operating_system == "Darwin" else filedialog.askdirectory(
            parent=self.window,
            initialdir=get_initial_directory(cache_file_dir),
            title=msg
            )

        if msbt_folder_dir != '':
            cache_file = open(cache_file_dir, 'w')
            cache_file.write(msbt_folder_dir[:msbt_folder_dir.rindex("/")+1])
            cache_file.close()

            msbt_folder_dir += "/"
            msg = "Please select a folder containing the csv files:"
            csv_dir = filedialog.askdirectory(
                parent=self.window,
                initialdir=get_initial_directory(cache_file_dir),
                message=msg
                ) if operating_system == "Darwin" else filedialog.askdirectory(
                parent=self.window,
                initialdir=get_initial_directory(cache_file_dir),
                title=msg
                )

            if csv_dir != '':
                cache_file = open(cache_file_dir, 'w')
                cache_file.write(csv_dir[:csv_dir.rindex("/")+1])
                cache_file.close()

                csv_dir += "/"
                msg = "Please select a folder to save the new msbt files to:"
                save_dir = filedialog.askdirectory(
                    parent=self.window,
                    initialdir=get_initial_directory(cache_file_dir),
                    message=msg
                    ) if operating_system == "Darwin" else filedialog.askdirectory(
                    parent=self.window,
                    initialdir=get_initial_directory(cache_file_dir),
                    title=msg
                    )

                if save_dir != '':
                    cache_file = open(cache_file_dir, 'w')
                    cache_file.write(save_dir[:save_dir.rindex("/")+1])
                    cache_file.close()

                    save_dir += "/"

                    batch_coded_import(msbt_folder_dir, csv_dir, save_dir)

    def clean_export(self):
        txt_dir = filedialog.asksaveasfilename(parent=self.window,
                                        initialdir=get_initial_directory(cache_file_dir),
                                        title="Please create a name for your text file:",
                                filetypes=[("Text Files", ".txt")])
        if txt_dir != '' and self.msbt != None:
            cache_file = open(cache_file_dir, 'w')
            cache_file.write(txt_dir[:txt_dir.rindex("/")+1])
            cache_file.close()
            clean_export(self.msbt, txt_dir)

    def batch_clean_export(self):
        msg = "Please select a folder containing the msbt files:"
        msbt_folder_dir = filedialog.askdirectory(
            parent=self.window,
            initialdir=get_initial_directory(cache_file_dir),
            message=msg
            ) if operating_system == "Darwin" else filedialog.askdirectory(
            parent=self.window,
            initialdir=get_initial_directory(cache_file_dir),
            title=msg
            )

        if msbt_folder_dir != '':
            cache_file = open(cache_file_dir, 'w')
            cache_file.write(msbt_folder_dir[:msbt_folder_dir.rindex("/")+1])
            cache_file.close()

            msbt_folder_dir += "/"

            msg = "Please select a folder to export the files to:"
            txt_dir = filedialog.askdirectory(
                parent=self.window,
                initialdir=get_initial_directory(cache_file_dir),
                message=msg
                ) if operating_system == "Darwin" else filedialog.askdirectory(
                parent=self.window,
                initialdir=get_initial_directory(cache_file_dir),
                title=msg
                )

            if txt_dir != '':
                cache_file = open(cache_file_dir, 'w')
                cache_file.write(txt_dir[:txt_dir.rindex("/")+1])
                cache_file.close()

                txt_dir += "/"

                batch_clean_export(msbt_folder_dir, txt_dir)

    def clean_import(self):
        txt_dir = filedialog.askopenfilename(parent=self.window,
                                initialdir=get_initial_directory(cache_file_dir),
                                title="Please select a text file with \"clean\" strings:",
                                filetypes=[("Text Files", ".txt")])
        if txt_dir != '' and self.msbt != None:
            cache_file = open(cache_file_dir, 'w')
            cache_file.write(txt_dir[:txt_dir.rindex("/")+1])
            cache_file.close()
            clean_import(self.msbt, txt_dir, self.save_dir)
            self.modified = False
            
            cur_index = self.labels_listbox.curselection()[0]

            self.edit_string_text.unbind("<<TextModified>>")
            self.edit_string_text.delete(1.0, tk.END)
            self.edit_string_text.insert(1.0, self.msbt.txt2.Strings[ cur_index ])
            self.edit_string_text.bind("<<TextModified>>", lambda x : self.edit_text_change())

            self.original_string_text['state'] = 'normal'
            self.original_string_text.delete(1.0, tk.END)
            self.original_string_text.insert(1.0, self.msbt.txt2.Original_Strings[ cur_index ])
            self.original_string_text['state'] = 'disabled'

    def batch_clean_import(self):
        msg = "Please select a folder containing the msbt files:"
        msbt_folder_dir = filedialog.askdirectory(
            parent=self.window,
            initialdir=get_initial_directory(cache_file_dir),
            message=msg
            ) if operating_system == "Darwin" else filedialog.askdirectory(
            parent=self.window,
            initialdir=get_initial_directory(cache_file_dir),
            title=msg
            )

        if msbt_folder_dir != '':
            cache_file = open(cache_file_dir, 'w')
            cache_file.write(msbt_folder_dir[:msbt_folder_dir.rindex("/")+1])
            cache_file.close()

            msbt_folder_dir += "/"
            msg = "Please select a folder containing the \"clean\" text files:"
            txt_dir = filedialog.askdirectory(
                parent=self.window,
                initialdir=get_initial_directory(cache_file_dir),
                message=msg
                ) if operating_system == "Darwin" else filedialog.askdirectory(
                parent=self.window,
                initialdir=get_initial_directory(cache_file_dir),
                title=msg
                )

            if txt_dir != '':
                cache_file = open(cache_file_dir, 'w')
                cache_file.write(txt_dir[:txt_dir.rindex("/")+1])
                cache_file.close()

                txt_dir += "/"
                msg = "Please select a folder to save the new msbt files to:"
                save_dir = filedialog.askdirectory(
                    parent=self.window,
                    initialdir=get_initial_directory(cache_file_dir),
                    message=msg
                    ) if operating_system == "Darwin" else filedialog.askdirectory(
                    parent=self.window,
                    initialdir=get_initial_directory(cache_file_dir),
                    title=msg
                    )

                if save_dir != '':
                    cache_file = open(cache_file_dir, 'w')
                    cache_file.write(save_dir[:save_dir.rindex("/")+1])
                    cache_file.close()

                    save_dir += "/"

                    batch_clean_import(msbt_folder_dir, txt_dir, save_dir)

gui()