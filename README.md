# Bluetooth Heater Control

Let's you control your bluetooth heating thermostat.

## Usage

set temperature (celcius)

 ```btheatctl.py --device 00:00:10:00:20:00 --pin 000000 --set 22.5```

get temperature

  ```btheatctl.py --device 00:00:10:00:20:00 --pin 000000 --get```

## Dependencies

- [bluepy](https://github.com/IanHarvey/bluepy)
