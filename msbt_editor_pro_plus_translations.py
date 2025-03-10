from msbt import *
from util import *
import tkinter as tk
from tkinter import ttk, filedialog, simpledialog, messagebox
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

operating_system = platform.system()
script_dir = os.path.dirname(sys.argv[0])
resources_dir = os.path.join(script_dir, 'resources')
cache_file_dir = os.path.join(script_dir, "cache", "cache.txt")

# Resource dir ?
if not os.path.exists(resources_dir):
    os.makedirs(resources_dir)

# Theme colors
DARK_BG = "#1E1E1E"
DARKER_BG = "#121212"
ACCENT_COLOR = "#0095AC"
TEXT_COLOR = "#F0F0F0"
SECONDARY_TEXT = "#BBBBBB"
BORDER_COLOR = "#333333"
BUTTON_BG = "#2A2A2A"
BUTTON_ACTIVE = "#3D3D3D"
ENTRY_BG = "#2D2D2D"
HIGHLIGHT_COLOR = "#0095AC"

class FlatButton(tk.Button):
    def __init__(self, master=None, **kwargs):
        kwargs.setdefault('relief', tk.FLAT)
        kwargs.setdefault('bg', BUTTON_BG)
        kwargs.setdefault('fg', TEXT_COLOR)
        kwargs.setdefault('activebackground', BUTTON_ACTIVE)
        kwargs.setdefault('activeforeground', TEXT_COLOR)
        kwargs.setdefault('bd', 0)
        kwargs.setdefault('padx', 10)
        kwargs.setdefault('pady', 5)
        super().__init__(master, **kwargs)
        
    def disable(self):
        self.config(state='disabled', bg=DARKER_BG, fg=SECONDARY_TEXT)
        
    def enable(self):
        self.config(state='normal', bg=BUTTON_BG, fg=TEXT_COLOR)

class FlatStyle:
    @staticmethod
    def configure_ttk_styles():
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure TButton
        style.configure("TButton", 
                        background=BUTTON_BG, 
                        foreground=TEXT_COLOR, 
                        borderwidth=0,
                        focusthickness=0,
                        padding=(10, 5))
                        
        style.map("TButton",
                 background=[('active', BUTTON_ACTIVE), ('disabled', DARKER_BG)],
                 foreground=[('disabled', SECONDARY_TEXT)])
                 
        # Configure TEntry
        style.configure("TEntry", 
                        fieldbackground=ENTRY_BG,
                        background=ENTRY_BG,
                        foreground=TEXT_COLOR,
                        borderwidth=0,
                        padding=5)
                        
        # Configure TCombobox
        style.configure("TCombobox",
                        fieldbackground=ENTRY_BG,
                        background=ENTRY_BG,
                        foreground=TEXT_COLOR,
                        arrowcolor=TEXT_COLOR,
                        borderwidth=0)
                        
        style.map("TCombobox",
                 fieldbackground=[('readonly', ENTRY_BG)],
                 selectbackground=[('readonly', ACCENT_COLOR)])
                 
        # Configure TProgressbar
        style.configure("TProgressbar",
                        background=ACCENT_COLOR,
                        troughcolor=ENTRY_BG,
                        borderwidth=0)
                        
        # Configure TFrame
        style.configure("TFrame", background=DARK_BG)
        
        # Configure TLabelframe
        style.configure("TLabelframe", background=DARK_BG, foreground=TEXT_COLOR)
        style.configure("TLabelframe.Label", background=DARK_BG, foreground=TEXT_COLOR)

class FlatListbox(tk.Listbox):
    def __init__(self, master=None, **kwargs):
        kwargs.setdefault('bg', ENTRY_BG)
        kwargs.setdefault('fg', TEXT_COLOR)
        kwargs.setdefault('selectbackground', ACCENT_COLOR)
        kwargs.setdefault('selectforeground', TEXT_COLOR)
        kwargs.setdefault('borderwidth', 0)
        kwargs.setdefault('highlightthickness', 0)
        super().__init__(master, **kwargs)

class FlatText(tk.Text):
    def __init__(self, master=None, **kwargs):
        kwargs.setdefault('bg', ENTRY_BG)
        kwargs.setdefault('fg', TEXT_COLOR)
        kwargs.setdefault('insertbackground', TEXT_COLOR)
        kwargs.setdefault('selectbackground', ACCENT_COLOR)
        kwargs.setdefault('selectforeground', TEXT_COLOR)
        kwargs.setdefault('borderwidth', 0)
        kwargs.setdefault('highlightthickness', 0)
        kwargs.setdefault('padx', 5)
        kwargs.setdefault('pady', 5)
        super().__init__(master, **kwargs)

class CallbackText(FlatText):
    def __init__(self, *args, **kwargs):
        FlatText.__init__(self, *args, **kwargs)
        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)

    def _proxy(self, command, *args):
        cmd = (self._orig, command) + args
        result = self.tk.call(cmd)

        if command in ("insert", "delete", "replace"):
            self.event_generate("<<TextModified>>")

        return result

class FlatEntry(tk.Entry):
    def __init__(self, master=None, **kwargs):
        kwargs.setdefault('bg', ENTRY_BG)
        kwargs.setdefault('fg', TEXT_COLOR)
        kwargs.setdefault('insertbackground', TEXT_COLOR)
        kwargs.setdefault('selectbackground', ACCENT_COLOR)
        kwargs.setdefault('selectforeground', TEXT_COLOR)
        kwargs.setdefault('borderwidth', 0)
        kwargs.setdefault('highlightthickness', 0)
        super().__init__(master, **kwargs)

class FlatLabel(tk.Label):
    def __init__(self, master=None, **kwargs):
        kwargs.setdefault('bg', DARK_BG)
        kwargs.setdefault('fg', TEXT_COLOR)
        super().__init__(master, **kwargs)

class ConfirmationPrompt(tk.Toplevel):
    def __init__(self, parent, title, message, options=("Yes", "No"), default=0):
        tk.Toplevel.__init__(self, parent)
        self.title(title)
        self.configure(bg=DARK_BG)
        self.resizable(False, False)
        
        self.choice = default
        
        # Calculate position
        window_width = 350
        window_height = 150
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        self.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        
        # Message
        message_label = FlatLabel(self, text=message, wraplength=300, justify=tk.CENTER, pady=10)
        message_label.pack(fill=tk.X, padx=20, pady=20)
        
        # Buttons
        button_frame = tk.Frame(self, bg=DARK_BG)
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Create buttons based on options
        for i, option_text in enumerate(options):
            button = FlatButton(button_frame, text=option_text, 
                              command=lambda i=i: self.set_choice(i))
            if i == default:
                button.config(bg=ACCENT_COLOR)
            button.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        parent.wait_window(self)
    
    def set_choice(self, choice):
        self.choice = choice
        self.destroy()

class gui():
    def __init__(self):
        self.msbt = None
        self.file_open = False
        self.modified = False
        self.translator = Translator()

        self.window = tk.Tk()
        self.window.title("Msbt Editor Pro + Translations")
        self.window.configure(bg=DARK_BG)
        self.window.minsize(width=864, height=550)
        self.window.geometry("864x550")
        self.window['padx'] = 10
        self.window['pady'] = 10
        
        try:
            icon_path = os.path.join(resources_dir, 'favicon.ico')
            self.window.iconbitmap(icon_path)
        except Exception as e:
            print(f"Error loading favicon: {e}")

        self.icons = {
            'save': ImageTk.PhotoImage(Image.open(os.path.join(resources_dir, 'save_icon.png')).resize((20, 20))),
            'add': ImageTk.PhotoImage(Image.open(os.path.join(resources_dir, 'add_icon.png')).resize((20, 20))),
            'remove': ImageTk.PhotoImage(Image.open(os.path.join(resources_dir, 'remove_icon.png')).resize((20, 20)))
        }

        # Apply flat style to ttk widgets
        FlatStyle.configure_ttk_styles()

        # Create menubar with dark style
        menubar = tk.Menu(self.window, bg=DARKER_BG, fg=TEXT_COLOR, activebackground=HIGHLIGHT_COLOR, 
                          activeforeground=TEXT_COLOR, borderwidth=0)
        self.window.config(menu=menubar)

        # File menu
        filemenu = tk.Menu(menubar, tearoff=0, bg=DARKER_BG, fg=TEXT_COLOR, 
                           activebackground=HIGHLIGHT_COLOR, activeforeground=TEXT_COLOR, borderwidth=0)
        filemenu.add_command(label="Open", command=lambda: self.open_file())
        filemenu.add_command(label="Save", command=lambda: self.save())
        filemenu.add_command(label="Save As", command=lambda: self.save_as())
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.window.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        # Clean Text menu
        cleantextmenu = tk.Menu(menubar, tearoff=0, bg=DARKER_BG, fg=TEXT_COLOR, 
                               activebackground=HIGHLIGHT_COLOR, activeforeground=TEXT_COLOR, borderwidth=0)
        cleantextmenu.add_command(label="Clean Export", command=lambda: self.clean_export())
        cleantextmenu.add_command(label="Batch Clean Export", command=lambda: self.batch_clean_export())
        cleantextmenu.add_separator()
        cleantextmenu.add_command(label="Auto Import", command=lambda: self.clean_import())
        cleantextmenu.add_command(label="Batch Auto Import", command=lambda: self.batch_clean_import())
        menubar.add_cascade(label="Clean Text", menu=cleantextmenu)

        # Coded Text menu
        codedtextmenu = tk.Menu(menubar, tearoff=0, bg=DARKER_BG, fg=TEXT_COLOR, 
                               activebackground=HIGHLIGHT_COLOR, activeforeground=TEXT_COLOR, borderwidth=0)
        codedtextmenu.add_command(label="Coded Export", command=lambda: self.coded_export())
        codedtextmenu.add_command(label="Batch Coded Export", command=lambda: self.batch_coded_export())
        codedtextmenu.add_separator()
        codedtextmenu.add_command(label="Import", command=lambda: self.coded_import())
        codedtextmenu.add_command(label="Batch Import", command=lambda: self.batch_coded_import())
        menubar.add_cascade(label="Coded Text", menu=codedtextmenu)

        # Translate menu
        translatemenu = tk.Menu(menubar, tearoff=0, bg=DARKER_BG, fg=TEXT_COLOR, 
                               activebackground=HIGHLIGHT_COLOR, activeforeground=TEXT_COLOR, borderwidth=0)
        translate_counts = [1, 2, 5, 10, 25, 50, 100, 150, 250, 500, 1000]
        for count in translate_counts:
            label = f"{count} time{'s' if count > 1 else ' (simple translation)'}"
            translatemenu.add_command(label=label, command=lambda c=count: self.translate_text(c))
        menubar.add_cascade(label="Translate", menu=translatemenu)

        # Main content frame
        main_frame = tk.Frame(self.window, bg=DARK_BG)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left panel - Labels list
        labels_list_frame = tk.Frame(main_frame, bg=DARK_BG, bd=0)
        labels_list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        self.labels_label = FlatLabel(labels_list_frame, text="String")
        self.labels_label.pack(fill=tk.X, pady=(0, 5))

        # Labels listbox with scrollbar
        listbox_frame = tk.Frame(labels_list_frame, bg=DARK_BG)
        listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        self.Labels_List = []
        self.labels_listbox_value = tk.StringVar(value=self.Labels_List)
        
        scrollbar = tk.Scrollbar(listbox_frame, bg=DARK_BG, troughcolor=ENTRY_BG, 
                               activebackground=ACCENT_COLOR, borderwidth=0, highlightthickness=0)
        self.labels_listbox = FlatListbox(listbox_frame, listvariable=self.labels_listbox_value, 
                                       yscrollcommand=scrollbar.set, exportselection=False, width=25)
        self.labels_listbox.bind("<<ListboxSelect>>", lambda _: self.listbox_change())
        scrollbar.config(command=self.labels_listbox.yview)
        
        self.labels_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Label entry and buttons
        label_controls_frame = tk.Frame(labels_list_frame, bg=DARK_BG, pady=10)
        label_controls_frame.pack(fill=tk.X)
        
        self.label_entry_var = tk.StringVar()
        label_entry = FlatEntry(label_controls_frame, textvariable=self.label_entry_var)
        label_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        buttons_frame = tk.Frame(label_controls_frame, bg=DARK_BG)
        buttons_frame.pack(side=tk.RIGHT)
        
        # Icon buttons
        self.save_label_button = FlatButton(buttons_frame, image=self.icons['save'], 
                                          state='disabled', command=lambda: self.save_label())
        self.save_label_button.pack(side=tk.LEFT, padx=2)
        
        self.add_label_button = FlatButton(buttons_frame, image=self.icons['add'], 
                                        state='disabled', command=lambda: self.add_label())
        self.add_label_button.pack(side=tk.LEFT, padx=2)
        
        self.remove_label_button = FlatButton(buttons_frame, image=self.icons['remove'], 
                                           state='disabled', command=lambda: self.remove_label())
        self.remove_label_button.pack(side=tk.LEFT, padx=2)

        # Right panel - String editing
        current_string_frame = tk.Frame(main_frame, bg=DARK_BG)
        current_string_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        edit_label = FlatLabel(current_string_frame, text="Edit")
        edit_label.pack(fill=tk.X, pady=(0, 5))

        # Editing text area
        self.edit_string_text = CallbackText(current_string_frame)
        self.edit_string_text.bind("<<TextModified>>", lambda x: self.edit_text_change())
        self.edit_string_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Restore button
        self.restore_original_text_button = FlatButton(current_string_frame, text="Restore Original", 
                                                    state='disabled', command=lambda: self.restore_original_text())
        self.restore_original_text_button.pack(fill=tk.X, pady=(0, 10))

        # Original text display
        original_label = FlatLabel(current_string_frame, text="Original Text")
        original_label.pack(fill=tk.X, pady=(0, 5))
        
        self.original_string_text = FlatText(current_string_frame, state='disabled', height=8)
        self.original_string_text.pack(fill=tk.X)

        # Status bar
        self.status_frame = tk.Frame(self.window, bg=DARKER_BG, height=25)
        self.status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_label = FlatLabel(self.status_frame, text="Ready", bg=DARKER_BG, anchor=tk.W, padx=10)
        self.status_label.pack(side=tk.LEFT)

        self.window.mainloop()

    def translate_text(self, iterations):
        if self.msbt is None:
            messagebox.showerror("Error", "No MSBT file loaded!", parent=self.window)
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
            'ha': 'Hausa', 'haw': 'Hawaiian', 'he': 'Hebrew', 'hi': 'Hindi', 'hmn': 'Hmong',
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

        # Create the config window
        config_window = tk.Toplevel(self.window)
        config_window.title("Translation Settings")
        config_window.geometry("320x240")
        config_window.configure(bg=DARK_BG)
        config_window.resizable(False, False)

        # Set the favicon for the config window
        try:
            icon_path = os.path.join(resources_dir, 'favicon_translation.ico')
            config_window.iconbitmap(icon_path)
        except Exception as e:
            messagebox.showwarning("Favicon Error", f"Could not load favicon: {e}")

        # Center the config window
        config_window.update_idletasks()
        width = config_window.winfo_width()
        height = config_window.winfo_height()
        x = (config_window.winfo_screenwidth() // 2) - (width // 2)
        y = (config_window.winfo_screenheight() // 2) - (height // 2)
        config_window.geometry(f'+{x}+{y}')

        # Source Language
        ttk.Label(config_window, text="Source Language:", background=DARK_BG, foreground=TEXT_COLOR).pack(pady=2)
        source_var = tk.StringVar(value='English')
        source_combo = ttk.Combobox(config_window, textvariable=source_var, values=list(LANGUAGES.values()), state="readonly")
        source_combo.pack(pady=2)

        # Target Language
        ttk.Label(config_window, text="Target Language:", background=DARK_BG, foreground=TEXT_COLOR).pack(pady=2)
        target_var = tk.StringVar(value='English')
        target_combo = ttk.Combobox(config_window, textvariable=target_var, values=list(LANGUAGES.values()), state="readonly")
        target_combo.pack(pady=2)

        # Translation Iterations
        ttk.Label(config_window, text="Random Translation Iterations:", background=DARK_BG, foreground=TEXT_COLOR).pack(pady=2)
        iterations_var = tk.IntVar(value=iterations)
        iterations_spin = ttk.Spinbox(config_window, from_=1, to=10, textvariable=iterations_var)
        iterations_spin.pack(pady=2)

        def start_translation():
            src = [k for k, v in LANGUAGES.items() if v == source_var.get()][0]
            dest = [k for k, v in LANGUAGES.items() if v == target_var.get()][0]
            iters = iterations_var.get()
            config_window.destroy()

            # Create the progress window
            progress_window = tk.Toplevel(self.window)
            progress_window.title("Translation Progress")
            progress_window.geometry("500x200")
            progress_window.configure(bg=DARK_BG)

            # Set the favicon for the progress window
            try:
                progress_window.iconbitmap(icon_path)
            except Exception as e:
                messagebox.showwarning("Favicon Error", f"Could not load favicon: {e}")

            # Center the progress window
            progress_window.update_idletasks()
            width = progress_window.winfo_width()
            height = progress_window.winfo_height()
            x = (progress_window.winfo_screenwidth() // 2) - (width // 2)
            y = (progress_window.winfo_screenheight() // 2) - (height // 2)
            progress_window.geometry(f'+{x}+{y}')

            # Progress bar and labels
            progress_frame = ttk.Frame(progress_window)
            progress_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            progress_bar = ttk.Progressbar(progress_frame, maximum=100, mode="determinate")
            progress_bar.pack(fill=tk.X, pady=5)

            info_frame = ttk.Frame(progress_frame)
            info_frame.pack(fill=tk.X)

            percent_label = ttk.Label(info_frame, text="0% completed", background=DARK_BG, foreground=TEXT_COLOR)
            percent_label.pack(side=tk.LEFT, padx=5)

            iter_label = ttk.Label(info_frame, text=f"String 1/{len(self.msbt.txt2.Strings)}", background=DARK_BG, foreground=TEXT_COLOR)
            iter_label.pack(side=tk.RIGHT, padx=5)

            preview_frame = ttk.LabelFrame(progress_frame, text="Current Processing", style='TLabelframe')
            preview_frame.pack(fill=tk.BOTH, expand=True, pady=5)

            original_label = ttk.Label(preview_frame, text="Original: ", background=DARK_BG, foreground=TEXT_COLOR)
            original_label.pack(anchor=tk.W)

            path_label = ttk.Label(preview_frame, text="Path: ", background=DARK_BG, foreground=TEXT_COLOR)
            path_label.pack(anchor=tk.W)

            translated_label = ttk.Label(preview_frame, text="Translated: ", background=DARK_BG, foreground=TEXT_COLOR)
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
                    iter_label.config(text=f"String {idx + 1}/{total}")

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
            self.window.title("Msbt Editor Pro + Translations - "+self.msbt_dir[self.msbt_dir.rindex("/")+1:])
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