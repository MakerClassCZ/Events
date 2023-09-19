unsigned long t0;
unsigned long t1;

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  Serial.println("Start");
  t0 = micros();
  for (int i = 0; i <= 100000; i++) {
    digitalWrite(LED_BUILTIN, HIGH); 
    digitalWrite(LED_BUILTIN, LOW);
  } 
  t1 = micros();
  Serial.println(t1-t0);
  delay(1000);

}