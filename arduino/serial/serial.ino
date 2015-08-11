/*
  Vs 0.0.1
  Robot Pi
  fernando.lourenco@lourenco.eu
*/

#include <Wire.h> //I2C Arduino Library

#define address 0x1E //0011110b, I2C 7bit address of HMC5883

const int ledPin = 13;      // the pin that the LED is attached to
const int pwmPin = 2;
const int trigerPin = 3;
const int echoPin = 4;

void setup()
{
  // initialize the serial communication:
  Serial.begin(115200);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for Leonardo only
  }
  
  Serial.setTimeout(10);
  
  // initialize the ledPin as an output:
  pinMode(ledPin, OUTPUT);
  digitalWrite(trigerPin, LOW);
  pinMode(pwmPin, OUTPUT);
  pinMode(trigerPin, OUTPUT);
  digitalWrite(trigerPin, LOW);
  pinMode(echoPin, INPUT);

  Wire.begin();
  
  //Put the HMC5883 IC into the correct operating mode
  Wire.beginTransmission(address); //open communication with HMC5883
  Wire.send(0x02); //select mode register
  Wire.send(0x00); //continuous measurement mode
  Wire.endTransmission();
}

void blinkled()
{
  digitalWrite(ledPin, HIGH);   // turn the LED on (HIGH is the voltage level)
  delay(20);                    // wait 
  digitalWrite(ledPin, LOW);    // turn the LED off by making the voltage LOW
}

void loop() {
  int incomingByte;   // for incoming serial data
  String mensagem;
  int angulo;
  
  // check if data has been sent from the computer:
  if (Serial.available()) {
    mensagem = Serial.readString();
    mensagem.toUpperCase();
    
    switch (mensagem[0])
    {
        case 'A': 
                  mensagem = mensagem.substring(1);
                 
                  angulo = constrain(mensagem.toInt(), 0, 180);
                  //angulo = constrain(mensagem.toInt(), 0, 20000);
                  //Serial.println("A");
                  //Serial.println(angulo);
                  
                  float dutyOn;
                  dutyOn = map(angulo, 0, 180, 500, 2500); // in microseconds
                  //dutyOn =angulo;
                  
                  Serial.println("OK"); 
                  
                  for (float tempo = 0; tempo<2.5; tempo += 0.02)
                  {
                    digitalWrite(pwmPin, HIGH);
                    delayMicroseconds(dutyOn);
                    digitalWrite(pwmPin, LOW);
                    delayMicroseconds(20000.0-dutyOn);
                  }
                  
                  break;
        case 'D': 
                  float distance;
                  unsigned long pulse_duration;
                  char distancestr[15];
                  unsigned long pulse_start;
                  unsigned long pulse_end;
                  unsigned long timestart;
                  boolean timeout;
                  
                  do
                  {
                    digitalWrite(trigerPin, LOW);
                    delay(5);
                    digitalWrite(trigerPin, HIGH);
                    delayMicroseconds(10);
                    digitalWrite(trigerPin, LOW);
  
                    timeout = false;
                    
                    timestart = micros();
                    pulse_start = timestart;
                    while (digitalRead(echoPin) == LOW && pulse_start-timestart <25000)
                    {
                        pulse_start = micros();
                    }
                    if (pulse_start-timestart>=25000) timeout = true;
                    
                    timestart = micros();
                    pulse_end = timestart;
                    while (digitalRead(echoPin) == HIGH && pulse_end-timestart <25000)
                    {
                        pulse_end = micros();
                    }
                    if (pulse_end-timestart>=25000) timeout = true;
                  } while (pulse_end < pulse_start);
                  
                  if (timeout == false)
                  {
                    pulse_duration = pulse_end - pulse_start;
                    distance = pulse_duration * 0.0170145;
                    dtostrf(distance, 4, 2, distancestr);
                  }
                  else
                  {
                    distancestr[0] = 'E';
                    distancestr[1] = 'R';
                    distancestr[2] = 'R';
                    distancestr[3] = 'O';
                    distancestr[4] = 'R';
                    distancestr[5] = '!';
                    distancestr[6] = 0;
                  }

                  //Serial.println("D");
                  //Serial.println(pulse_start);
                  //Serial.println(pulse_end);
                  Serial.println(distancestr);
                  Serial.println("OK"); 
                  break;
        case 'C': 
                  float course;
                  char coursestr[15];
                  
                  int x,y,z; //triple axis data

                  //Tell the HMC5883 where to begin reading data
                  Wire.beginTransmission(address);
                  Wire.send(0x03); //select register 3, X MSB register
                  Wire.endTransmission();
                  
                 //Read data from each axis, 2 registers per axis
                  Wire.requestFrom(address, 6);
                  if(6<=Wire.available()){
                    x = Wire.receive()<<8; //X msb
                    x |= Wire.receive(); //X lsb
                    z = Wire.receive()<<8; //Z msb
                    z |= Wire.receive(); //Z lsb
                    y = Wire.receive()<<8; //Y msb
                    y |= Wire.receive(); //Y lsb
                  }
                  
                  course = 0.0;
                  dtostrf(course, 4, 2, coursestr);
                 
                  Serial.println(coursestr);
                  Serial.println("OK"); 
                  break;
        default:
                 Serial.println("UNKNOWN");  
                  break;
    }
    blinkled();
    
  }
}

