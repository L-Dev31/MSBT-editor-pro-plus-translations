# **MSBT Editor Pro + Translations**
![image](https://github.com/user-attachments/assets/b3d79ea2-01d0-4edb-a982-55d14f4d2c6b)


A powerful and user-friendly editor for MSBT files with built-in translation capabilities. This tool allows you to edit, manage, and translate text strings in MSBT files efficiently.

![image](https://github.com/user-attachments/assets/0868b7e8-c319-4ea8-829f-5e6de66ad04c)
![image](https://github.com/user-attachments/assets/3532649b-2848-4bdc-8235-35b8dad7dd50)


---

## Features

- **MSBT File Editing**: Open, edit, and save MSBT files with ease.
- **Translation Support**: Built-in integration with Google Translate for quick translations (with controlable Iterations) perfect for creating translation/bad translations mods.
- **Export to .txt**: export and import your .msbt files with .txt files useful for very specific usages.
- **Comfortable Interface**: Sleek, modern flat dark theme for comfortable usage.
- **Tag Preservation**: Preserves special tags during translation (you can stay chill and translate, no human verification needed 👌).

---

## **Game Compatibility List**  
(if any of the informations below are uncorrect, please come let me know !)


### **🟩 Fully Working**

- Animal Crossing: New Horizons __(Switch)__
- Fire Emblem: Three Houses __(Switch)__
- Miitopia __(3DS)__
- Miitopia __(Switch)__
- Pokémon Sun/Moon __(3DS)__
- Xenoblade Chronicles 2 __(Switch)__


### **🟧 Partially Working**

- Mario Kart 8 Deluxe __(Switch)__ **(Partial: Course names only)**
- Splatoon 2 __(Switch)__ **(Partial: Basic UI only)**  
- Super Smash Bros. Ultimate __(Switch)__ **(Partial: Menus only)**  
- The Legend of Zelda: Breath of the Wild __(Switch)__ **(Partial: Simple text)** 


### **🟥 Not Working** 

- Mario Party Superstars __(Switch)__ **(Text embedded in binaries)**  
- Pokémon Scarlet/Violet __(Switch)__ **(New encryption)**  
- Splatoon 3 __(Switch)__ **(Modified MSBT structure)**  
- The Legend of Zelda: Tears of the Kingdom __(Switch)__ **(New format)**


### **⬛ (Any games that aren't present here aren't tested yet)**
  
---

## Installation

1. Download the zip file in releases.

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python msbt_editor_pro_plus_translations.py
   ```

---

## Usage

1. **Open an MSBT File**: Use the `File > Open` menu to load an MSBT file.
2. **Edit Strings**: Modify text strings directly in the editor.
3. **Translate**: Use the `Translate` menu to translate every strings change the iteration setting if you want to make "random" translations through randomly selected languages.
4. **Save**: Save your changes with `File > Save` or `File > Save As`.

---

## Requirements

- Python 3.8+
- Pillow (`pip install pillow`)
- googletrans (`pip install googletrans==4.0.0-rc1`)

---

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

---

*Made with ❤️ for the modding community by L-DEV, work based on MSBT editor pro by [Unknown Person... :sob:]*
