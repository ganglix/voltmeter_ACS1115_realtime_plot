#include <Adafruit_ADS1X15.h>

Adafruit_ADS1115 ads; // Instantiate ADS1115. Default I2C address 0x48 is used.

int16_t adc0, adc1, adc2, adc3;  // Variables to hold ADC reading for each channel
float multiplier = 0.125F;       // ADS1115  // 1x gain   +/- 4.096V  1 bit = 0.125mV
float voltage0, voltage1, voltage2, voltage3; // Variables for voltage readings for each channel


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
  float time = millis() / 1000.0; // Calculate the current time using millis() and convert it to seconds for time stamping

  // Read from ADS1115 channels
  adc0 = ads.readADC_SingleEnded(0); // Read AIN0
  adc1 = ads.readADC_SingleEnded(1); // Read AIN1
  adc2 = ads.readADC_SingleEnded(2); // Read AIN2
  adc3 = ads.readADC_SingleEnded(3); // Read AIN3

  // Convert ADC readings to voltages
  voltage0 = adc0 * multiplier; 
  voltage1 = adc1 * multiplier; 
  voltage2 = adc2 * multiplier; 
  voltage3 = adc3 * multiplier; 

  // Print the current time and voltage readings to Serial
  Serial.print(time);
  Serial.print(", ");
  
  Serial.print(voltage0);
  Serial.print(", ");

  Serial.print(voltage1);
  Serial.print(", ");

  Serial.print(voltage2);
  Serial.print(", ");

  Serial.println(voltage3);

  delay(5000);  // Delay for 5 seconds before next reading
}
