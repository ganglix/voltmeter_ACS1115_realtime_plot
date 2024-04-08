#include <Wire.h>
#include <Adafruit_ADS1X15.h>

Adafruit_ADS1115 ads; // Instantiate ADS1115. Default I2C address 0x48 is used.

int16_t adc0;  // variables to hold ADC reading
float multiplier = 0.125F;               // ADS1115  // 1x gain   +/- 4.096V  1 bit = 0.125mV
float voltage_read_adc; // Added variables for voltage readings


void setup() {
  Serial.begin(9600);
  ads.begin();  // init ADS1115 ADC

  // The ADC input range (or gain) can be changed via the following
  // functions, but be careful never to exceed VDD +0.3V max, or to
  // exceed the upper and lower limits if you adjust the input range!
  // Setting these values incorrectly may destroy your ADC!
  //                                                                ADS1115
  //                                                                -------
  // ads.setGain(GAIN_TWOTHIRDS);  // 2/3x gain +/- 6.144V  1 bit = 0.1875mV (default)
   ads.setGain(GAIN_ONE);        // 1x gain   +/- 4.096V  1 bit = 0.125mV
  // ads.setGain(GAIN_TWO);        // 2x gain   +/- 2.048V  1 bit = 0.0625mV
  // ads.setGain(GAIN_FOUR);       // 4x gain   +/- 1.024V  1 bit = 0.03125mV
  // ads.setGain(GAIN_EIGHT);      // 8x gain   +/- 0.512V  1 bit = 0.015625mV
  // ads.setGain(GAIN_SIXTEEN);    // 16x gain  +/- 0.256V  1 bit = 0.0078125mV
}


void loop() {
  float time = micros() /1e6; // calculate the current time using micros and convert it to seconds for time stamping

  adc0 = ads.readADC_SingleEnded(0); // Read from ADS1115 AIN0
  voltage_read_adc = adc0 * multiplier; // Convert to mV

  Serial.print(time);
  Serial.print(", ");
  Serial.println(voltage_read_adc); 
  delay(2000);

}
