#include <SPI.h>
#include <MFRC522.h>

#define SS_PIN 5
#define RST_PIN 0

MFRC522 mfrc522(SS_PIN, RST_PIN); // Instance of the class
MFRC522::MIFARE_Key key;

int errorCount = 0;
const int errorThreshold = 3;
String detected_tag = "";
bool printMemory = false;
bool printCardType = true;

void setup() { 
  Serial.begin(9600);
  SPI.begin(); // Init SPI bus
  mfrc522.PCD_Init(); // Init MFRC522 
  Serial.println("Reader has booted");

  // Initialize default key
  for (byte i = 0; i < 6; i++) {
    key.keyByte[i] = 0xFF;
  }
}

String toHexString(byte *buffer, byte bufferSize) {
  String result = "";
  for (byte i = 0; i < bufferSize; i++) {
    result += buffer[i] < 0x10 ? "0" : "";
    result += String(buffer[i], HEX);
  }
  return result;
}

void printHex(byte *buffer, byte bufferSize) {
  for (byte i = 0; i < bufferSize; i++) {
    Serial.print(buffer[i] < 0x10 ? " 0" : " ");
    Serial.print(buffer[i], HEX);
  }
  Serial.println();
}

void readCardMemory() {
  byte buffer[18];
  byte size = sizeof(buffer);
  MFRC522::StatusCode status;

  for (byte block = 0; block < 64; block++) {
    // Authenticate before reading
    status = mfrc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, block, &key, &(mfrc522.uid));
    if (status != MFRC522::STATUS_OK) {
      Serial.print("Failed to authenticate block ");
      Serial.println(block);
      continue;
    }

    status = mfrc522.MIFARE_Read(block, buffer, &size);
    if (status == MFRC522::STATUS_OK) {
      Serial.print("Block ");
      Serial.print(block);
      Serial.print(": ");
      printHex(buffer, 16);
    } else {
      Serial.print("Failed to read block ");
      Serial.println(block);
    }
  }
  mfrc522.PICC_HaltA();
  mfrc522.PCD_StopCrypto1();
}

void processCommand(String command) {
  command.trim();
  if (command == "MREAD ON") {
    printMemory = true;
    Serial.println("Memory print enabled");
  } else if (command == "MREAD OFF") {
    printMemory = false;
    Serial.println("Memory print disabled");
  } else if (command.startsWith("WRITE ")) {
    String data = command.substring(6);
    writeCardMemory(data);
  } else {
    Serial.println("Unknown command");
  }
}


void writeCardMemory(String data) {
  Serial.print("Attempting to write: ");
  Serial.println(data);

}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    processCommand(command);
  }

  if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {
    if (detected_tag == "") {
      detected_tag = toHexString(mfrc522.uid.uidByte, mfrc522.uid.size);
      Serial.print("Tag found: ");
      Serial.println(detected_tag);
      if(printCardType) {
        Serial.print(F("PICC type: "));
        MFRC522::PICC_Type piccType = mfrc522.PICC_GetType(mfrc522.uid.sak);
        Serial.println(mfrc522.PICC_GetTypeName(piccType));
      }
      if (printMemory) {
        readCardMemory();
      }
    }
    errorCount = 0;
  } else {
    if (detected_tag != "") {
      errorCount++;
      if (errorCount > errorThreshold) {
        Serial.print("Tag lost: ");
        Serial.println(detected_tag);
        detected_tag = "";
        errorCount = 0;
        mfrc522.PICC_HaltA();
        mfrc522.PCD_StopCrypto1();
      }
    }
  }
}
