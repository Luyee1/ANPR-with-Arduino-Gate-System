#include <Servo.h>

Servo gateServo;

// Pin definitions
const int trigPin = 2;
const int echoPin = 3;
const int servoPin = 9;

// Gate angles
const int openAngle = 90;   // Gate "open" angle
const int closeAngle = 0;   // Gate "closed" angle

// Ultrasonic sensor threshold (in cm)
const int vehicleThreshold = 10;

// Timing for sensor check
unsigned long vehicleClearTime = 0;
const unsigned long waitAfterVehicle = 2000; // 2 seconds

void setup() {
  Serial.begin(9600);
  gateServo.attach(servoPin);
  gateServo.write(closeAngle); // Start with the gate closed

  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
}

void loop() {
  if (Serial.available() > 0) {
     // Read a line from serial (until newline) and trim whitespace
    String input = Serial.readStringUntil('\n');
    input.trim();
    if (input.length() == 0) return; // Skip if empty

    // Open the gate
    Serial.println("Opening gate...");
    gateServo.write(openAngle);

    // Wait for the vehicle to pass
    waitForVehicleToPass();
  }
}

void waitForVehicleToPass() {
  bool vehicleDetected = true;
  while (vehicleDetected) {
    long distance = measureDistance();
    if (distance < vehicleThreshold && distance > 0) {
      Serial.println("Vehicle detected. Gate remains open.");
      vehicleClearTime = millis(); // Reset timer when vehicle is detected
    } else {
      if (millis() - vehicleClearTime > waitAfterVehicle) {
        Serial.println("Vehicle passed. Closing gate...");
        gateServo.write(closeAngle);
        vehicleDetected = false;
      }
    }
    delay(200);
  }
}



long measureDistance() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long duration = pulseIn(echoPin, HIGH, 30000); // Timeout after 30ms
  if (duration == 0) {
    return -1;
  }
  long distance = duration * 0.034 / 2;
  return distance;
}
