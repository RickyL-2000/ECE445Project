
Communication subsystem
===

## Setup develop environment
1. Download micropython image from [MicroPython - Python for microcontrollers](https://micropython.org/download/esp32/)

2. Upload micropython image
   1. Install Thonny. 
   2. Use Thonny to upload micropython image to development board. (Press `boot` button when write image)
   3. Test micropython in Thonny

3. Install plugin `pymakr` on vscode. 
   
   1. require Node.js
   2. find the **manufacturer** of development board in **device controller** and append it in pymakr global setting
   3. In you project root directory, modify the `pymakr.conf` especially the `address`
   4. details here: [Quick reference for the ESP32 — MicroPython 1.17 documentation](http://docs.micropython.org/en/latest/esp32/quickref.html)

4. Use pymakr and enjoy coding. 

## Diractory structure

```
esp32
│  boot.py           # executable script, runs only once when booted or resetted
│  main.py           # executable script, runs always runs after boot.py (go interact CLI after return)
│  readme.md         # this file
│  unittest_PC_client.py
│  unittest_PC_server.py
│
├─log       # log files
└─utils     # utils
    │  blink.py      # onboard LED utils, used for indication and debug
    │  channel.py    # communication class
    │  color.py      # pretty color for unix-like system CLI
    │  config.py     # config file for communication and other utils
    │  log.py        # unified log functions, for both CLI and logfile
    │  uart.py       # serial port communication between ESP and PC
    │  wifi.py       # basic wifi functions
    └─ __init__.py

```


## Useful Resource
### MicroPython
- [MicroPython - Python for microcontrollers](https://micropython.org/download/esp32/)
- [Quick reference for the ESP32 — MicroPython 1.17 documentation](http://docs.micropython.org/en/latest/esp32/quickref.html)

### WIFI
- [MicroPython-ESP32 WiFi创建与连接 | NW&ONE](https://zghy.xyz/2020/05/19/MicroPython_ESP32_WiFi_connection/)

### UART
- [CP210x USB to UART Bridge VCP Drivers - Silicon Labs](https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers)

### vscode extension
- [MicroPython Program ESP32/ESP8266 VS Code and Pymakr | Random Nerd Tutorials](https://randomnerdtutorials.com/micropython-esp32-esp8266-vs-code-pymakr/)
