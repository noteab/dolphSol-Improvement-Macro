# **TODO List**
An ***attempt*** to organize improvements and new features.



## Improvements/Fixes
* Restructure
  - Categorize functions based on purpose, usage frequency, etc
  - Optimize accessing config
    - Consider multiple configs (menu/general, auras, biomes, scheduler)
    - Compare benefits of *maintaining global "options"* vs *read/write as needed*



## Planned Features
* ? Auto update
* ? Auto start when macro opens

* Discord notifications
  - Optional display and ping for each status

* Performance monitor
  - Function completion times, times called, etc
  - PC stats - RAM, CPU, FPS
  - Network connectivity - Pause updating and reconnecting

* Discord bot for remote commands

* Configurable OCR
  - Support any OCR capable language by allowing user to translate text

* Screenshots
  - [ ] Biomes
  - [ ] Quests
  - [ ] Active buffs
  - [ ] Stats board

* Custom Keybinds

* Configurable coordinates
  - Click/Spacebar for single X,Y
  - Click and drag to draw area for TL and BR

* Biome profiles (non-OCR detection)
  - JSON of biome properties and conditions to predict with high accuracy
  - Rough process
  1. Reset to spawn
  2. Align
  3. Zoom out completely
  4. Set zones for expected constants (Jake's roof, House roof)
  5. Use zones to determine day/night
  6. Use zones & day/night to predict current biome


