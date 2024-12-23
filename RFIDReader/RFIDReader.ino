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
String data_to_write = "";
byte blockData [16] = {};

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
    data_to_write = command.substring(6); // Store the data to be written, main loop will handle it
  } else {
    Serial.println("Unknown command");
  }
}

bool writeDataToBlock(int blockNum, byte blockData[]) 
{
  /* Authenticating the desired data block for write access using Key A */
  
  MFRC522::StatusCode status;
  status = mfrc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, blockNum, &key, &(mfrc522.uid));
  if (status != MFRC522::STATUS_OK) {
    Serial.print("Authentication failed for Write: ");
    Serial.println(mfrc522.GetStatusCodeName(status));
    return false;
  }

  
  /* Write data to the block */
  status = mfrc522.MIFARE_Write(blockNum, blockData, 16);
  if (status != MFRC522::STATUS_OK) {
    Serial.print("Writing to Block failed: ");
    Serial.println(mfrc522.GetStatusCodeName(status));
    return false;
  } 
   Serial.println("WRiting complete! ");
  return true;
}


void writeCardMemory(String data) {
  byte blockData[16]; // 16 bytes for the block
  data.getBytes(blockData, 16); // Copy the string to the byte array
  for (int i = data.length(); i < 16; i++) {
    blockData[i] = '\0';
  }

  Serial.print("Attempting to write: ");
  Serial.println(data);
  if(writeDataToBlock(4, blockData)){
    data_to_write = "";
  }
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
    } else {
      // So, we do this indirectly, as the card reader seems to flip between being able to do something and not being able to do something.
      // Since we *know* that we are in a situation where it can do something, it's also the moment to write it. If we don't, we get random timeout issues
      // on the writing. We couldn't just use a normal retry, as it would try the same thing without allowing the states (or whatever the fuck is causing this)
      // to change. So future me (or idk, whoever reads this), learn from my folley. That retry stuff for the newCard present is there for a reason and it also affects the writing stuff. 
      if(data_to_write != "") {
        writeCardMemory(data_to_write);
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
