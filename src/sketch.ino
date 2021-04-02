#include <stdio.h>
#include <string.h>
#include <math.h>
#include <stdlib.h>
#include <Wire.h>

const byte lightgatePin  = 2;
const byte stirrerPin    = 5;
const byte heaterPin     = 6;
const byte thermistorPin = A0;
const byte pHPin         = A1;

unsigned long lastCheck = millis();
unsigned long now;
double elapsed;
const int wait = 80000;

double changes = 0;
double targetRpm = 850;
double oldpH;
double measuredRpm;
double actualRpm;
int stirrerPwm = 100;

double voltage;
double targetpH = 5.0;
double measuredpH = 7.0;

double cTemp=303.15;
double pTemp=cTemp;
double nowTemp;
double temp; //used in clarissa's code
double dTemp = 303.15;

int acidOff;
int acidOn;
int baseOff;
int baseOn;

void setup() {
  Serial.begin(9600);

  pinMode(lightgatePin,  INPUT);
  pinMode(stirrerPin,    OUTPUT);
  pinMode(heaterPin,     OUTPUT);
  pinMode(thermistorPin, INPUT);
  pinMode(pHPin,         INPUT);
  
  attachInterrupt(digitalPinToInterrupt(lightgatePin), recordChange, CHANGE);  
}

void recordChange(){
  changes++;
}

double getTemperature() {
  //Temperature calculations
  double rawAdc = analogRead(thermistorPin);
  double Temp;
  //10000ohms at 298.15k (data sheet for N_06P00103)
  float Resistance = log(10000.0/(1024.0/rawAdc-1)); 
  Temp = 1 / (0.001129148 + (0.000234125 * Resistance) + (0.0000000876741 * Resistance * Resistance * Resistance));
  return Temp;
}

float getpH(double temp){
  voltage = (analogRead(pHPin) - 512) * -1;
  oldpH = measuredpH;
  measuredpH = 7 + ((-voltage + 12) * 9.6485309 * 10) / (8.314510 * temp * 2.30258509);
    
  return (oldpH + measuredpH)/2;
}

//auxillary functions for manageTemperature()
float getRpm(int wait){
  measuredRpm = (changes / 4) * (60000 / wait);
  actualRpm = (1.0364 * measuredRpm) + 0.8046;
    
  changes = 0;
  
  return actualRpm;  
}

void startHeating(){
  digitalWrite(heaterPin,HIGH);
}

void endHeating(){
  digitalWrite(heaterPin,LOW);
}

//end of auxillary functions

void manageTemperature(){
  nowTemp=(getTemperature()+getTemperature()+getTemperature()+getTemperature())/4;
  if (nowTemp<dTemp+0.5 && nowTemp>dTemp-0.5){
    cTemp=nowTemp;
  }
  while (nowTemp<dTemp){
    nowTemp=(getTemperature()+getTemperature()+getTemperature()+getTemperature())/4;
    startHeating();
    if (nowTemp<dTemp+0.5 && nowTemp>dTemp-0.5){
    cTemp=nowTemp;
    }
  }
  while (nowTemp>dTemp){
    nowTemp=(getTemperature()+getTemperature()+getTemperature()+getTemperature())/4;
    endHeating();
    if (nowTemp<dTemp+0.5 && nowTemp>dTemp-0.5){
      cTemp=nowTemp;
    }
  }
}

void managepH(double measuredpH, double targetpH){
  
    baseOn = 0x00;                           
    baseOff = 0x00;
    acidOn = 0x00;
    acidOff = 0x00;
  
  
  if (targetpH > measuredpH){
    baseOn = 0x02;
    baseOff = 0x05;
    acidOn = 0x00;
    acidOff = 0x00;
  } else if (targetpH < measuredpH-0.3) {
    acidOn = 0x02;
    acidOff = 0x05;
    baseOn = 0x00;
    baseOff = 0x00;
  }
  
  Wire.beginTransmission(0x70);
  Wire.write(0x00);                            // address of where you're writing to
  Wire.write(0b00100001);
  Wire.endTransmission();
  
  Wire.beginTransmission(0x70);
  Wire.write(0x06); 
  
  Wire.write(acidOn); // ACID_ON_L - USE
  Wire.write(0x00); // ACID_ON_H 
  
  
  Wire.write(0x00); // ACID_OFF_L
  Wire.write(acidOff); // ACID_OFF_H - USE
  
  Wire.write(baseOn); // BASE_ON_L - USE
  Wire.write(0x00); // BASE_ON_H
  
  Wire.write(0x00); // BASE_OFF_L
  Wire.write(baseOff); // BASE_OFF_H - USE
  
  Wire.endTransmission();
}

void manageRpm(int targetRpm){  
  stirrerPwm = floor((0.0817 * targetRpm) - 0.0562);
  
  if (actualRpm > (targetRpm + 5))
      stirrerPwm = stirrerPwm - floor((actualRpm - targetRpm)/3);
  else if (actualRpm < (targetRpm - 5))
      stirrerPwm = stirrerPwm + floor((targetRpm - actualRpm)/3);
  
  analogWrite(stirrerPin,stirrerPwm);
  
}

void loop() {
  if (Serial.available() > 0) {
    
    int operation = Serial.read();            // reads first letter as ASCII value
    int value = Serial.readString().toInt();  // reads digits after first character
    
    if (operation==72){        // heating operation (ASCII for H)
      dTemp = value+273;
    }
    if (operation==80){                     //pH operation (ASCII for P)
      targetpH = value;
    }
    if (operation==83){                    //stirring operation (ASCII for S)
      targetRpm = value;
    }
  }
  
  manageTemperature();
  managepH(measuredpH, targetpH);
  manageRpm(targetRpm);
  
  now = millis();
  elapsed = now - lastCheck;
  
  if(elapsed > wait){  
    lastCheck = now;
    
    Serial.print("H");
    Serial.print(cTemp-273);
    
    Serial.print("P");
    Serial.print(getpH(getTemperature()));
    
    Serial.print("S");
    Serial.println(getRpm(wait));
  }
}
