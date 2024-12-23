#include <SPI.h>
#include <MFRC522.h>

#define SS_PIN 5
#define RST_PIN 0

MFRC522 mfrc522(SS_PIN, RST_PIN); // Instance of the class

int errorCount = 0;
const int errorThreshold = 3;
String detected_tag = "";
MFRC522::MIFARE_Key key;  // Global key declaration

void setup() { 
  Serial.begin(9600);
  SPI.begin();
  mfrc522.PCD_Init();
  Serial.println("Reader has booted");

  // Initialize the key to 0xFFFFFFFFFFFF (default key)
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

    // Read block
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


void loop() {
  if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {
    if (detected_tag == "") { // No card present
      detected_tag = toHexString(mfrc522.uid.uidByte, mfrc522.uid.size);
      Serial.print("Tag found: ");
      Serial.println(detected_tag);
      readCardMemory(); // Read and print card memory
    }
    errorCount = 0; // Reset error counter when card is detected, even if already present
  } else {
    if (detected_tag != "") { // Card was previously there.
      errorCount++;
      if (errorCount > errorThreshold) {
        Serial.print("Tag lost: ");
        Serial.println(detected_tag);
        detected_tag = "";
        errorCount = 0; // Reset error count after detecting removal
        mfrc522.PICC_HaltA();
        mfrc522.PCD_StopCrypto1();
      }
    }
  }
}
