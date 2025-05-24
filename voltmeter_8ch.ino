#include <Wire.h>
#include <Adafruit_ADS1X15.h>

Adafruit_ADS1115 ads1; // First ADS1115 (ADDR connected to GND, I2C address 0x48)
Adafruit_ADS1115 ads2; // Second ADS1115 (ADDR connected to VDD, I2C address 0x49)

int16_t adc0, adc1, adc2, adc3, adc4, adc5, adc6, adc7;  // Variables to hold ADC readings
float multiplier = 0.125F;       // ADS1115  // 1x gain   +/- 4.096V  1 bit = 0.125mV
float voltage0, voltage1, voltage2, voltage3, voltage4, voltage5, voltage6, voltage7;

bool started = false; // Flag to indicate if data acquisition should run

void setup() {
  Serial.begin(9600);
  ads1.begin(0x48);  // Initialize first ADS1115 with address 0x48
  ads2.begin(0x49);  // Initialize second ADS1115 with address 0x49

  // The ADC input range (or gain) can be changed via the following
  // functions, but be careful never to exceed VDD +0.3V max, or to
  // exceed the upper and lower limits if you adjust the input range!
  // Setting these values incorrectly may destroy your ADC!

  //                                                                ADS1115
  //                                                                -------
  // ads.setGain(GAIN_TWOTHIRDS);  // 2/3x gain +/- 6.144V  1 bit = 0.1875mV (default)
     ads1.setGain(GAIN_ONE);        // 1x gain   +/- 4.096V  1 bit = 0.125mV
     ads2.setGain(GAIN_ONE);        // Set same gain for second ADC
  // ads.setGain(GAIN_TWO);        // 2x gain   +/- 2.048V  1 bit = 0.0625mV
  // ads.setGain(GAIN_FOUR);       // 4x gain   +/- 1.024V  1 bit = 0.03125mV
  // ads.setGain(GAIN_EIGHT);      // 8x gain   +/- 0.512V  1 bit = 0.015625mV
  // ads.setGain(GAIN_SIXTEEN);    // 16x gain  +/- 0.256V  1 bit = 0.0078125mV
}

void loop() {
  // Listen for serial commands from Python GUI
  if (Serial.available()) {
    char cmd = Serial.read();
    if (cmd == 'S') started = true;
    if (cmd == 'X') started = false;
  }

  if (started) {
    float time = millis() / 1000.0; // Calculate the current time in seconds

    // Read from first ADS1115 (0x48)
    adc0 = ads1.readADC_SingleEnded(0); // AIN0
    adc1 = ads1.readADC_SingleEnded(1); // AIN1
    adc2 = ads1.readADC_SingleEnded(2); // AIN2
    adc3 = ads1.readADC_SingleEnded(3); // AIN3

    // Read from second ADS1115 (0x49)
    adc4 = ads2.readADC_SingleEnded(0); // AIN0
    adc5 = ads2.readADC_SingleEnded(1); // AIN1
    adc6 = ads2.readADC_SingleEnded(2); // AIN2
    adc7 = ads2.readADC_SingleEnded(3); // AIN3

    // Convert to voltages
    voltage0 = adc0 * multiplier; 
    voltage1 = adc1 * multiplier; 
    voltage2 = adc2 * multiplier; 
    voltage3 = adc3 * multiplier; 
    voltage4 = adc4 * multiplier; 
    voltage5 = adc5 * multiplier; 
    voltage6 = adc6 * multiplier; 
    voltage7 = adc7 * multiplier; 

    // Print to Serial
    Serial.print(time, 2); Serial.print(", ");
    Serial.print(voltage0, 2); Serial.print(", ");
    Serial.print(voltage1, 2); Serial.print(", ");
    Serial.print(voltage2, 2); Serial.print(", ");
    Serial.print(voltage3, 2); Serial.print(", ");
    Serial.print(voltage4, 2); Serial.print(", ");
    Serial.print(voltage5, 2); Serial.print(", ");
    Serial.print(voltage6, 2); Serial.print(", ");
    Serial.println(voltage7, 2); // Print final channel with newline

    delay(1000);  // 1-second delay
  }
}
