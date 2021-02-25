#!/usr/bin/python3

import configparser, socket, threading
import simplejson as json
import lib.mymqtt as mymqtt
import apa102, effects, sys, time

def clamp(n, smallest=0, largest=255):
   """ Clamp integer (n) values between a range - inclusive """
   return max(smallest, min(int(n), largest))

def rgbtohex(r, g, b):
   """ Convert r,g,b integers to a hex value. """
   hexstr = "0x{0:02x}{1:02x}{2:02x}".format(clamp(r), clamp(g), clamp(b))
   return int(hexstr, 16)

class Control:
   """ Control Class for this device. """

   def is_main_thread_active(self):
      """ Check if the mian thread is still running. """
      return any((i.name == "MainThread") and i.is_alive() for i in threading.enumerate())

   def all_off(self):
      """ Reset the LED strip. """
      self.strip.clear_strip()
      self.LEDS = [0] * self.NUM_LEDS # this is done here to keep consistent state
      return

   def all_on(self):
      """ Sets all LEDs to a single color and renders it. """
      self.set_leds(None, self.red, self.green, self.blue)
      self.strip.show()
      return

   def set_leds(self, pixel, r=0, g=0, b=0, hex=None):
      """ Set individual or all the LEDs - DOES NOT RENDER
   
            pixel - None => set all NUM_LEDS the same color
                  - List => set the LEDs in the list the same color
                  - int  => set individual pixel a color
      """
      if hex is not None:
         hexcolor = hex
      else:
         hexcolor = rgbtohex(r,g,b)

      if pixel is None:
         for x in range(self.NUM_LEDS):
            self.strip.set_pixel_rgb(x, hexcolor, self.brightness)
      elif type(pixel) is list:
         for x in pixel:
            self.strip.set_pixel_rgb(x, hexcolor, self.brightness)
      else:
         self.strip.set_pixel_rgb(pixel, hexcolor, self.brightness)
      
      return

   def stop_effect(self):
      """ Stop the effect; signal the thread to exit, if running. """
      # we always have 2 threads: main and stats, then any effects threads
      if threading.active_count() > 2:
         # stop current effect
         self.done.set()
         self.active.join()
         self.done.clear()
      return

   def start_effect(self):
      """ Start the effect thread. """
      # create our loop object
      effect = effects.EffectLoop(disp=self)
      self.active = threading.Thread(target=effect.loop, args=(self.done,))
      self.active.start() # kick our thread off
      return

   def on_message(self, client, message):
      """ Callback for MQTT messages. """

      params = json.loads(message.payload.decode('utf-8'))
      status = {}
      pixel = None

      self.stop_effect() # stop any running effects
      self.effect = ''

      if ('effect' in params):
         self.effect = params['effect']
         self.start_effect()
         status['effect'] = self.effect

      if ('brightness' in params):
         self.brightness = clamp(int(params['brightness']), largest=31)

      if ('color' in params):
         self.effect = None
         self.red = clamp(int(params['color']['r']))
         self.green = clamp(int(params['color']['g']))
         self.blue = clamp(int(params['color']['b']))

      if ('led' in params):
         pixel = int(params['led'])

      if ('state' in params):
         if params['state'] == 'ON':
            self.state = 'ON'
            if pixel is not None:
               self.LEDS[pixel] = 1
               self.set_leds(pixel, self.red, self.green, self.blue)
               self.strip.show()

            else:
               self.all_on()
         else:
            if pixel is not None:
               self.LEDS[pixel] = 0
               self.set_leds(pixel, hex=0) # use black to turn off
               if len([i for i, e in enumerate(self.LEDS) if e ]):
                  self.state = 'ON' # off may not mean all off
               else:
                  self.state = 'OFF'
               self.strip.show()

            else:
               self.state = 'OFF'
               self.all_off()
      
      # @TODO this is a hack for python3 to force render by calling it twice.
      self.strip.show()

      # always report back our current state
      status['brightness'] = self.brightness
      status['color'] = {}
      status['color']['r'] = self.red
      status['color']['g'] = self.green
      status['color']['b'] = self.blue
      status['effect'] = self.effect
      status['state'] = self.state

      # Send the message back
      client.update(status, fmt='json', retain=True)
      return

   def __init__(self, leds):
      """ Initialize all object vars. """

      self.state = "OFF"
      self.effect = None
      self.brightness = 15
      self.red = self.blue = self.green = 255
      self.NUM_LEDS = int(leds)
      self.done = threading.Event()
      self.LEDS = [0] * self.NUM_LEDS

      # init our smart strip
      # Blinkt! uses BCM 23 and 24 for data and clock
      # initial prototype used BCM 10 and 11 (defaults for APA lib)
      self.strip = apa102.APA102(num_led=self.NUM_LEDS, 
                                 global_brightness=self.brightness,
                                 mosi = 23, sclk = 24,
                                 order='rgb')
      self.all_off()
      return

def main():
   """ Entry point. """

   if len(sys.argv) > 1:
      cmd = sys.argv[1]

      # Initialize the library and the strip - BCM 10 and 11
      # Blinkt! uses pins BCM 23 and 24 for its data and clock respectively
      strip = apa102.APA102(num_led=8, global_brightness=20, mosi = 23, sclk = 24,
                            order='rgb')

      # Turn off all pixels (sometimes a few light up when the strip gets power)
      strip.clear_strip()

      if cmd == 'test':
         # Prepare a few individual pixels
         strip.set_pixel_rgb(1, 0xFF0000) # Red
         strip.set_pixel_rgb(4, 0xFFFFFF) # White
         strip.set_pixel_rgb(6, 0x00FF00) # Green

         # Copy the buffer to the Strip (i.e. show the prepared pixels)
         strip.show()

         # Wait a few Seconds, to check the result
         time.sleep(10)
   
      strip.clear_strip()
      strip.cleanup()

   else:
      # load the device config
      config = configparser.ConfigParser()
      config.read('../config/config.ini')

      # initialization
      client_id = socket.gethostname()

      myDisp = Control(config[client_id]['NumLEDS']) # my display object

      client = mymqtt.mymqtt(config, userdata=myDisp)

      # Wait forever for msgs
      client.loop_forever()
   return
   
if __name__ == '__main__':
   main()
