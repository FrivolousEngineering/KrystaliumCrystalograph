#include <SPI.h>
#include <MFRC522.h>
#include <EEPROM.h>

#define SS_PIN 5
#define RST_PIN 0

MFRC522 mfrc522(SS_PIN, RST_PIN); // Instance of the class
MFRC522::MIFARE_Key key;
MFRC522::StatusCode status;

int errorCount = 0;
const int errorThreshold = 3;
String detected_tag = "";
bool printMemory = false;
bool printCardType = true;
String data_to_write = "";
byte blockData [16] = {};
byte buffer[18]; // To hold the read data
int block_to_read = -1;
bool ignore_card_remove_event = false;


const char* validActions[] = {
  "EXPANDING", "CONTRACTING", "CONDUCTING", "INSULATING",
  "DETERIORATING", "CREATING", "DESTROYING", "INCREASING",
  "DECREASING", "ABSORBING", "RELEASING", "SOLIDIFYING",
  "LIGHTENING", "ENCUMBERING", "FORTIFYING", "HEATING", "COOLING"
};

const char* validTargets[] = {
    "FLESH", "MIND", "GAS", "SOLID", "LIQUID",
    "ENERGY", "LIGHT", "SOUND", "KRYSTAL", "PLANT"
};

// Block 4 stores the Type of the sample ("RAW" or "REFINED")
// Block 5 stores the first action (primary for refined, positive for RAW)
// Block 6 stores the first target (primary for refined, positive for RAW)
// Block 7 stores the second action (secondary for refined, negative for RAW)
// Block 8 stores the second target (secondary for refined, negative for RAW)


void setup() { 
  Serial.begin(9600);
  SPI.begin(); // Init SPI bus
  mfrc522.PCD_Init(); // Init MFRC522 
  Serial.println("Reader has booted");

  // Initialize default key
  for (byte i = 0; i < 6; i++) {
    key.keyByte[i] = 0xFF;
  }
  
#if defined(ESP32) || defined(ESP8266)
  EEPROM.begin(512);  // ESPS need to initialize EEPROM size. The Nano doesn't need to.
#endif
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
  ignore_card_remove_event = true; 
}

void processCommand(String command) {
  command.trim();
  
  int spaceIndex = command.indexOf(' ');  
  String keyword = (spaceIndex != -1) ? command.substring(0, spaceIndex) : command;
  String argument = (spaceIndex != -1) ? command.substring(spaceIndex + 1) : "";
  
  // Convert keyword to uppercase
  keyword.toUpperCase();

  // Convert argument to uppercase unless it's for WRITE
  if(keyword != "WRITE" && keyword != "NAME"){
    argument.toUpperCase();
  }
  
  if (keyword == "MREAD") {
    if (argument == "ON") {
      printMemory = true;
      Serial.println("Memory print enabled");
    } else if (argument == "OFF") {
      printMemory = false;
      Serial.println("Memory print disabled");
    } else {
      Serial.println("Unknown MREAD argument");
    }
  } else if (keyword == "WRITE") {
    data_to_write = argument;  // Store data for writing
    ignore_card_remove_event = true; // This prevents a tag lost & found spam after every operation
  } else if (keyword == "READ") {
    block_to_read = 4; // Prepare for reading.
    ignore_card_remove_event = true; 
  } else if (keyword == "NAME") {
    // Setting the name commands (used to control the name of the device). If we run this on a ESP, we have much better way of doing this.
    // On a duino nano there isn't a simple way to get a unique identifier, so we just have to store it to eeprom.
    if(argument != ""){
      // Keyword was provided, print it
      writeStringToEEPROM(0, argument);
      Serial.print("Setting name: ");
      Serial.println(argument);
    } else {
      // Print the keyword out
      String retrievedString = readStringFromEEPROM(0);
      Serial.print("Name: ");
      Serial.println(retrievedString);
    }
  } else if (keyword == "WRITETYPE") {
    if(argument != "REFINED" && argument != "RAW"){
      Serial.println("Unknown krystalium type. Only RAW and REFINED are supported");
      return;
    }
    data_to_write = argument;  // Store data for writing
    ignore_card_remove_event = true; // This prevents a tag lost & found spam after every operation
  } else if (keyword == "WRITEACTION1") {
    if(!isValidAction(argument)){
      Serial.println("Unknown action :(");
      return;
    }
    Serial.println("BJOOP");
  }
}

// Function to read a block and return the data as a string
String readBlock(byte block) {
  // Authenticate the block (use key A)
  status = mfrc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, block, &key, &(mfrc522.uid));
  if (status != MFRC522::STATUS_OK) {
    Serial.print("Authentication failed: ");
    Serial.println(mfrc522.GetStatusCodeName(status));
    return "";
  }

  // Read the block
  byte size = sizeof(buffer);
  status = mfrc522.MIFARE_Read(block, buffer, &size);
  if (status != MFRC522::STATUS_OK) {
    Serial.print("Read failed: ");
    Serial.println(mfrc522.GetStatusCodeName(status));
    return "";
  }

  // Convert the buffer to a string
  String data = "";
  for (byte i = 0; i < 16; i++) {
    if (buffer[i] != 0) {
      data += (char)buffer[i];
    }
  }
  return data;
}

bool writeDataToBlock(int blockNum, byte blockData[]) 
{
  // Authenticating the desired data block for write access using Key A
  status = mfrc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, blockNum, &key, &(mfrc522.uid));
  if (status != MFRC522::STATUS_OK) {
    Serial.print("Authentication failed for Write: ");
    Serial.println(mfrc522.GetStatusCodeName(status));
    return false;
  }
  
  // Write data to the block
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
  // Fill the rest of the block with empty data
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
      // A card was detected and we didn't have one already.
      detected_tag = toHexString(mfrc522.uid.uidByte, mfrc522.uid.size);
      if(!ignore_card_remove_event) {
        // We're not ignoring the "new card" event.
        Serial.print("Tag found: ");
        Serial.println(detected_tag);
        // Some debug prints
        if(printCardType) { 
          Serial.print(F("PICC type: "));
          MFRC522::PICC_Type piccType = mfrc522.PICC_GetType(mfrc522.uid.sak);
          Serial.println(mfrc522.PICC_GetTypeName(piccType));
        }
        if (printMemory) {
          readCardMemory();
        }
      } else {
        // If we are ignoring an event, we should start listening after ignoring it once.
        ignore_card_remove_event = false;
      }
    } else {
      // So, we do this indirectly, as the card reader seems to flip between being able to do something and not being able to do something.
      // Since we *know* that we are in a situation where it can do something, it's also the moment to write it. If we don't, we get random timeout issues
      // on the writing. We couldn't just use a normal retry, as it would try the same thing without allowing the states (or whatever the fuck is causing this)
      // to change. So future me (or idk, whoever reads this), learn from my folley. That retry stuff for the newCard present is there for a reason and it also affects the writing stuff. 
      if(data_to_write != "") {
        writeCardMemory(data_to_write);
      } 
      // TODO: Expand to include multiple blocks
      if(block_to_read != -1)
      {
        String blockData = readBlock(block_to_read);
        Serial.print("Data in Block ");
        Serial.print(4);
        Serial.print(": ");
        Serial.println(blockData);
        block_to_read = -1; // reset it again
      }
    }
    errorCount = 0;
  } else {
    if (detected_tag != "") {
      errorCount++;
      if (errorCount > errorThreshold) {
        if(!ignore_card_remove_event) {
          Serial.print("Tag lost: ");
          Serial.println(detected_tag);
        }
        detected_tag = "";
        errorCount = 0;
        mfrc522.PICC_HaltA();
        mfrc522.PCD_StopCrypto1();
      }
    }
  }
}

bool isValidAction(const String& action) {
  for (const char* validAction : validActions) {
    if (action.equals(validAction)) {
      return true;
    }
  }
  return false;
}

bool isValidTarget(const String& target) {
  for (const char* validTarget : validTargets) {
    if (target.equals(validTarget)) {
      return true;
    }
  }
  return false;
}

void writeStringToEEPROM(int addrOffset, const String &strToWrite) {
  byte len = strToWrite.length();
  EEPROM.write(addrOffset, len);
  for (int i = 0; i < len; i++)
  {
    EEPROM.write(addrOffset + 1 + i, strToWrite[i]);
  }
#if defined(ESP32) || defined(ESP8266)
  EEPROM.commit();  // ESPs requires a commit, the nano does not.
#endif
}

String readStringFromEEPROM(int addrOffset) {
  int newStrLen = EEPROM.read(addrOffset);
  char data[newStrLen + 1];
  for (int i = 0; i < newStrLen; i++)
  {
    data[i] = EEPROM.read(addrOffset + 1 + i);
  }
  data[newStrLen] = '\0';
  return String(data);
}
