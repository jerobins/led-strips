"""
EffectLoop Class - define effects in a format to be ran as a separate thread.

effect ideas and logic taken from:
https://www.tweaking4all.com/hardware/arduino/adruino-led-strip-effects/

using helpers from the APA102 library:
https://github.com/tinue/APA102_Pi
"""

import time, random, math, sys

millis = lambda: int(round(time.time() * 1000))
""" Returns time integer in milliseconds. """

def randColor(): return random.randint(0,255)
""" Random number between 1 and 255, inclusive."""

class EffectLoop:
   """ Class encapsulation of all effects and the loop/thread management. """

   def loop(self, event):
      """ Entry point for effects thread.
      Does not actually loop. Each effect handles looping as needed.
      """

      self.event = event
      random.seed()

      if self.disp.effect == 'fadeInOut':
         self.fadeInOut(self.disp.red, self.disp.green, self.disp.blue,
                        loopDelay=0.1)

      if self.disp.effect == 'halloweenEyes':
         self.halloweenEyes(self.disp.red, self.disp.green, self.disp.blue,
                            eyeWidth=1, eyeSpace=4, fade=True, steps=50,
                            fadeDelay=0.01, loopDelay=0.1)

      if self.disp.effect == 'cylon':
         self.cylon(self.disp.red, self.disp.green, self.disp.blue,
                    eyeSize=4, eyeDelay=0.04, returnDelay=0.2)

      if self.disp.effect == 'twinkle':
         self.twinkle(self.disp.red, self.disp.green, self.disp.blue,
                      loopDelay=0.3)

      if self.disp.effect == 'randomTwinkle':
         self.twinkle(0, 0, 0, rand=True, loopDelay=0.3)

      if self.disp.effect == 'sparkle':
         self.twinkle(self.disp.red, self.disp.green, self.disp.blue,
                      count=1, loopDelay=0.0)

      if self.disp.effect == 'randomSparkle':
         self.twinkle(0, 0, 0, count=1, rand=True, loopDelay=0.0)

      if self.disp.effect == 'snowSparkle':
         self.snow()

      if self.disp.effect == 'running':
         self.running(self.disp.red, self.disp.green, self.disp.blue,
                      delay=0.05)

      if self.disp.effect == 'colorWipe':
         self.wipe(self.disp.red, self.disp.green, self.disp.blue,
                   loopDelay=0.05)

      if self.disp.effect == 'rainbowCycle':
         self.rainbowCycle(delay=0.1)

      if self.disp.effect == 'marquee':
         self.marquee(self.disp.red, self.disp.green, self.disp.blue,
                      delay=0.05)

      if self.disp.effect == 'marqueeRainbow':
         self.marqueeRainbow(delay=0.05)

      if self.disp.effect == 'fire':
         self.fire(cooling=150, sparking=120, delay=0.03)

      if self.disp.effect == 'bouncing':
         self.bouncing(rand=False, balls=1)

      if self.disp.effect == 'bouncingRainbow':
         self.bouncing(rand=True, balls=4)

      if self.disp.effect == 'meteorRain':
         self.meteorRain(self.disp.red, self.disp.green, self.disp.blue)

   def exitIfDone(self):
      """ Stop this thread if we are told to, or if our parent dies."""
      if self.event.is_set(): sys.exit()
      if not self.disp.is_main_thread_active(): sys.exit()

   def fadeIn(self, red, green, blue, leds=None, steps=128, fadeDelay=0.01):
      """ Helper function to fade IN LEDs. """
      for x in range(0, 256, int(round(255.0/steps))):
         r = x/255.0 * red
         g = x/255.0 * green
         b = x/255.0 * blue
         self.disp.set_leds(leds, r, g, b)
         self.disp.strip.show()
         time.sleep(fadeDelay)

   def fadeOut(self, red, green, blue, leds=None, steps=128, fadeDelay=0.01):
      """ Helper function to fade OUT LEDs. """
      for x in range(255, -1, int(round(-1*255.0/steps))):
         r = x/255.0 * red
         g = x/255.0 * green
         b = x/255.0 * blue
         self.disp.set_leds(leds, r, g, b)
         self.disp.strip.show()
         time.sleep(fadeDelay)

   def fadeInOut(self, r, g, b, leds=None, steps=128, fadeDelay=0.01, loopDelay=0.1):
      """ Pulse/Fade-In-Out effect """
      while True:
         self.fadeIn(r, g, b, leds, steps, fadeDelay)
         self.exitIfDone()
         self.fadeOut(r, g, b, leds, steps, fadeDelay)
         self.exitIfDone()
         time.sleep(loopDelay)

   def halloweenEyes(self, r, g, b, eyeWidth=1, eyeSpace=4, fade=True,
                     steps=50, fadeDelay=0.01, loopDelay=0.1):
      """ Create random pair of eyes based on parameters given. """
      while True:
         eyeOne = random.randint(0, self.disp.NUM_LEDS - (2*eyeWidth) - eyeSpace)
         eyeTwo = eyeOne + eyeWidth + eyeSpace

         pixels = []
         for x in range(eyeWidth):
            pixels.append(eyeOne + x)
            pixels.append(eyeTwo + x)

         self.disp.set_leds(pixels, r, g, b)
         self.disp.strip.show()

         if fade:
            self.fadeOut(r, g, b, pixels, steps, fadeDelay)

         self.disp.all_off()
         self.exitIfDone()
         time.sleep(loopDelay)

   def drawEye(self, curLed, r, b, g, eyeSize):
      """ Helper to draw cylon eye on strip. """
      # set all black
      self.disp.set_leds(None, 0, 0, 0)

      pixels = []
      pixels.append(curLed)
      pixels.append(curLed+eyeSize+1)
      self.disp.set_leds(pixels, r/10, g/10, b/10)

      pixels = []
      for i in range(1, eyeSize+1):
         pixels.append(curLed+i)

      self.disp.set_leds(pixels, r, g, b)
      self.disp.strip.show()

   def cylon(self, r, g, b, eyeSize=4, eyeDelay=0.1, returnDelay=0.5):
      """ Classic cyclon effect. """
      while True:
         self.disp.all_off()

         for x in range(0, self.disp.NUM_LEDS-eyeSize-2+1):
            self.drawEye(x, r, b, g, eyeSize)
            if x % 10 == 0: self.exitIfDone()
            time.sleep(eyeDelay)

         time.sleep(returnDelay)

         for x in range(self.disp.NUM_LEDS-eyeSize-2, -1, -1):
            self.drawEye(x, r, b, g, eyeSize)
            if x % 10 == 0: self.exitIfDone()
            time.sleep(eyeDelay)

         time.sleep(returnDelay)

   def twinkle(self, r, g, b, count=10, rand=False, loopDelay=0.3):
      """ Twinkle, twinkle, little star. """
      while True:
         self.disp.set_leds(None, 0, 0, 0)
         for x in range(0, count):
            pixel = random.randint(0, self.disp.NUM_LEDS)
            if rand:
               self.disp.set_leds(pixel, randColor(), randColor(), randColor())
            else:
               self.disp.set_leds(pixel, r, g, b)
            self.disp.strip.show()
            time.sleep(loopDelay)

         self.exitIfDone()
         time.sleep(loopDelay)

   def snow(self):
      """ Opposite of twinkle. Flicker snow effect. """
      while True:
         # make it white, then sleep
         self.disp.set_leds(None, 255, 255, 255)
         self.disp.strip.show()
         time.sleep(random.randint(300, 1000)/1000.0)
         # blink one pixel
         pixel = random.randint(0, self.disp.NUM_LEDS)
         self.disp.set_leds(pixel, 16, 16, 16)
         self.disp.strip.show()
         time.sleep(0.02)
         self.exitIfDone()

   def running(self, r, g, b, delay=0.05):
      while True:
         pos = 0
         for x in range(0, self.disp.NUM_LEDS*2):
            pos = pos + 1
            for i in range(0, self.disp.NUM_LEDS):
               self.disp.set_leds(i,
                                  ((math.sin(i+pos)*127+128)/255.0)*r,
                                  ((math.sin(i+pos)*127+128)/255.0)*b,
                                  ((math.sin(i+pos)*127+128)/255.0)*g)
            self.disp.strip.show()
            if x % 10 == 0: self.exitIfDone()
            time.sleep(delay)

   def colorWipe(self, r, g, b, delay=0.05):
      """ Single color wipe of entire strip. """
      for x in range(0, self.disp.NUM_LEDS):
         self.disp.set_leds(x, r, g, b)
         self.disp.strip.show()
         if x % 10 == 0: self.exitIfDone()
         time.sleep(delay)

   def wipe(self, r, g, b, loopDelay=0.05):
      """ Repeating loop of single color wipe of entire strip, alternating with black. """
      while True:
         self.colorWipe(0, 0, 0)
         self.colorWipe(self.disp.red, self.disp.green, self.disp.blue)
         self.exitIfDone()
         time.sleep(loopDelay)

   def rainbowCycle(self, delay=0.1):
      """ Rainbow color cycle of entire strip. """
      y = 1
      while True:
         for x in range(0, self.disp.NUM_LEDS):
            c = self.disp.strip.wheel(y)
            y = (y + 40) % 255
            self.disp.set_leds(x, hex=c)

         self.disp.strip.show()
         self.exitIfDone()
         time.sleep(delay)

   def marquee(self, r, g, b, delay=0.05):
      """ Go to the movies. """
      while True:
         for x in range(0, 3):
            for i in range(0, self.disp.NUM_LEDS, 3):
               self.disp.set_leds(i+x % 255, r, g, b)

            self.disp.strip.show()
            self.exitIfDone()
            time.sleep(delay)

            for i in range(0, self.disp.NUM_LEDS, 3):
               self.disp.set_leds(i+x, hex=0)
            self.exitIfDone()

   def marqueeRainbow(self, delay=0.05):
      """ Going to the movies post Y2K. """
      while True:
         y = 1
         for x in range(0, 3):
            for i in range(0, self.disp.NUM_LEDS, 3):
               c = self.disp.strip.wheel(y)
               y = (y + 40) % 255
               self.disp.set_leds(i+x, hex=c)

            self.disp.strip.show()
            self.exitIfDone()
            time.sleep(delay)

            for i in range(0, self.disp.NUM_LEDS, 3):
               self.disp.set_leds(i+x, hex=0)
            self.exitIfDone()

   def _set_pixel_heat_color(self, pixel, temp):
      """ Helper for fire effect. """
      # Scale 'heat' down from 0-255 to 0-191
      temp = int(round((temp/255.0)*191))

      # calculate ramp up from
      heatramp = temp & 0x3F # 0..63
      heatramp = heatramp << 2 # scale up to 0..252

      # based on which third of the spectrum we're in, set colors accordingly
      if temp > 0x80: # hot
         r = 255; g = 255; b = heatramp
      elif temp > 0x40: # warmer
         r = 255; g = heatramp; b = 0
      else: # coolest
         r = heatramp; g = 0; b = 0

      self.disp.set_leds(pixel, r, g, b)

   def fire(self, cooling=50, sparking=120, delay=0.2):
      """ Create a flame effect where sparks ignite, burn, then cool down as they go up. """
      # heat array - holds heat of ea. pixel
      heat = [0 for x in range(0, self.disp.NUM_LEDS)]

      while True:
         # Step 1.  Cool down every cell a little
         for i in range(0, self.disp.NUM_LEDS):
            cooldown = random.randint(0, ((cooling * 10) / self.disp.NUM_LEDS) + 2)
            if cooldown > heat[i]:
               heat[i] = 0
            else:
               heat[i] = heat[i] - cooldown

         # Step 2.  Heat from each cell drifts 'up' and diffuses a little
         for k in range(self.disp.NUM_LEDS - 1, 1, -1):
            heat[k] = (heat[k - 1] + heat[k - 2] + heat[k - 2]) / 3;

         # Step 3.  Randomly ignite new 'sparks' near the bottom
         if random.randint(0, 255) < sparking:
            y = random.randint(0, 5)
            heat[y] = heat[y] + random.randint(160, 255)

         # Step 4.  Convert heat to LED colors
         for x in range(0, self.disp.NUM_LEDS):
            self._set_pixel_heat_color(x, heat[x])

         self.disp.strip.show()
         self.exitIfDone()
         time.sleep(delay)

   def bouncing(self, rand=False, balls=4, delay=0.05):
      """ Bouncing Balls. Not happy with this implementation. """
      gravity = -9.8/2.0 # yes, gravity

      # map colors to each ball
      colors = [[0 for x in range(3)] for y in range(balls)]
      if not rand:
         for i in range(balls):
            colors[i][0] = self.disp.red
            colors[i][1] = self.disp.green
            colors[i][2] = self.disp.blue
      else:
         for i in range(balls):
            colors[i][0] = random.randint(0, 255)
            colors[i][1] = random.randint(0, 255)
            colors[i][2] = random.randint(0, 255)

      # arrays to track ball information
      height = [0 for x in range(balls)]
      velocity = [0.0 for x in range(balls)]
      tDelta = [0 for x in range(balls)]
      position = [0 for x in range(balls)]
      clockDelta = [0.0 for x in range(balls)]
      dampening = [0.0 for x in range(balls)]

      # initialize each array
      for i in range(balls):
        clockDelta[i] = millis() # start time
        height[i] = self.disp.NUM_LEDS - (2 * i)
        position[i] = 0
        velocity[i] = 0
        tDelta[i] = 0
        # adjust dampening for each ball, so they look different
        dampening[i] = -0.90 - float(i)/math.pow(balls, 2)

      while True:
         for i in range(balls):
            tDelta[i] =  millis() - clockDelta[i]
            # calc ending velocity
            velocity[i] = velocity[i] + (gravity * tDelta[i]/1000)
            # calc how far it fell x = x + vdT
            prevHeight = height[i]
            height[i] = prevHeight + (velocity[i] * tDelta[i]/1000)

            # handle hitting bottom
            if height[i] < 0:
               height[i] = 0
               velocity[i] = dampening[i] * velocity[i]
               clockDelta[i] = millis() # mark time it hit bottom
               # and if velocity gets too low, crank it back up
               if velocity[i] < 0.01:
                  velocity[i] = 2
               # if we stop bouncing, restart it
               if int(height[i]) == int(prevHeight):
                  height[i] = self.disp.NUM_LEDS
                  velocity[i] = 0

            # @TODO - this position needs work
            # position[i] = int(round(height[i] / 4 * (self.disp.NUM_LEDS-1)))
            position[i] = int(height[i])
            # original code below
            # position[i] = int(round(height[i] * (self.disp.NUM_LEDS-1) / initialHeight))

         for i in range(balls):
            self.disp.set_leds(position[i], colors[i][0], colors[i][1], colors[i][2])

         self.disp.strip.show()
         self.disp.all_off() # immediately clear the strip
         self.exitIfDone()
         time.sleep(delay)

   def meteorRain(self, r, g, b, mSize=10, trailDecay=64, mDecay=True, delay=.03):
      """ A personal favorite: Meteor's with a fiery tail. """
      self.disp.all_off() # immediately clear the strip
      pixels = [[0 for x in range(3)] for y in range(self.disp.NUM_LEDS)]

      while True:
         for i in range(0, self.disp.NUM_LEDS*2):
            # fade brightness of all LEDS by one step
            for j in range(0, self.disp.NUM_LEDS):
               if( mDecay and random.randint(0, 10) > 5):
                  pixels[j][0] = int(trailDecay/255.0 * pixels[j][0])
                  pixels[j][1] = int(trailDecay/255.0 * pixels[j][1])
                  pixels[j][2] = int(trailDecay/255.0 * pixels[j][2])
                  self.disp.set_leds(j, pixels[j][0], pixels[j][1], pixels[j][2])

            # draw meteor
            for j in range(0, mSize):
               mPix = i - j
               if mPix > -1 and mPix < self.disp.NUM_LEDS:
                  pixels[mPix][0] = r
                  pixels[mPix][1] = g
                  pixels[mPix][2] = b
                  self.disp.set_leds(mPix, r, g, b)

            self.disp.strip.show()
            self.exitIfDone()
            time.sleep(delay)

   def __init__(self, **kwargs):
      """ Effect loop vars. loopDelay can be adjusted here for all effects. """
      self.disp = None
      self.loopDelay = 0.1
      self.__dict__.update(**kwargs)
