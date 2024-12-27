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
bool printMemory = true;
bool printCardType = false;
String data_to_write = "";
byte blockData [16] = {};
byte buffer[18]; // To hold the read data
int blocks_to_read[10] = {0};
bool ignore_card_remove_event = false;
bool is_ntag = true; // Are we using ntag chips


struct MemoryMap {
  byte sample_type;
  byte primary_action;
  byte primary_target;
  byte secondary_action;
  byte secondary_target;
  byte depleted;
  byte purity;
};

// Define the memory mapping on the chips. Note that the numbers mean something quite different for both of em.
// Mifare use adresses that are 16 bytes, ntag uses adresses that are 4 bytes. 
MemoryMap mifareMapping = {4, 5, 6, 8, 9, 10, 12};
MemoryMap ntagMapping = {6, 9, 12, 15, 18, 21, 24};

MemoryMap activeMapping; 

String sample_type_to_write = ""; 
String primary_action_to_write = ""; 
String primary_target_to_write = "";  
String secondary_action_to_write = ""; 
String secondary_target_to_write = ""; 
String depleted_to_write = ""; 
String purity_to_write = "";

const char* validPurities[] = {
  "POLLUTED", "TARNISHED", "DIRTY", "BLEMISHED",
  "IMPURE", "UNBLEMISHED", "LUCID", "STAINLESS",
  "PRISTINE", "IMMACULATE", "PERFECT"
};

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

const char* validVulgarities[] = {
  "VULGAR", "LOW_MUNDANE", "HIGH_MUNDANE",
  "LOW_SEMI_PRECIOUS", "HIGH_SEMI_PRECIOUS",
  "PRECIOUS"
};

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

/**
 * Read string from a 4 byte ntag page
 */
String readPage(byte page) {
  byte buffer[18];
  byte size = sizeof(buffer);
  MFRC522::StatusCode status = mfrc522.MIFARE_Read(page, buffer, &size);
  if (status != MFRC522::STATUS_OK) {
    Serial.print("Failed to read page ");
    Serial.println(page);
    return "";
  }
  String data = "";
  for (byte i = 0; i < 4; i++) {
    data += buffer[i] != 0 ? (char)buffer[i] : ' ';
  }
  return data;
}

void readCardMemoryNTAG() {
  for (byte page = 0; page < 45; page++) {  // Adjust based on NTAG type (213=45, 215=135)
    String data = readPage(page);
    Serial.print("Page ");
    Serial.print(page);
    Serial.print(": ");
    Serial.println(data);
  }
}

/**
 * Write a string that is larger than 4 bytes to a card. 
 * Note that pages are 4 bytes. So when writing 5 bytes, we will use
 * 2 pages (aka; 8 bytes of memory). For convenience sake we don't do
 * any fragmentation or packing. 
 * We also don't have any protection to check if we are going over memory or 
 * if we are writing in memory that you shouldn't be writing to as of yet. 
 * This means it's possible to brick tags if you are not carefull.
 */
bool writeLargeStringToNTAG(byte startPage, String data) {
  data = padTo12Bytes(data, 12); // We pad them to 12 to ensure any old data is overridden.
  int length = data.length();
  int pageOffset = 0;
  
  // Iterate through the string in chunks of 4 bytes
  for (int i = 0; i < length; i += 4) {
    byte buffer[4] = {0x00, 0x00, 0x00, 0x00};  // Initialize 4-byte buffer

    // Copy 4 bytes or less from the string into the buffer
    for (int j = 0; j < 4; j++) {
      if ((i + j) < length) {
        buffer[j] = data[i + j];
      } else {
        buffer[j] = 0x00;  // Padding if the string is shorter than 4 bytes
      }
    }
    
    // Write to the current page
    if (!writeDataToPageNTAG(startPage + pageOffset, buffer)) {
      Serial.println("Failed to write large string.");
      return false;
    }
    
    pageOffset++;
  }
  return true;
}

String padToBytesLength(String data, int length = 12) {
  while (data.length() < length) {
    data += ' ';
  }
  return data;
}

bool writeDataToPageNTAG(byte page, byte* data) {
  MFRC522::StatusCode status;
  status = mfrc522.MIFARE_Ultralight_Write(page, data, 4);
  if (status != MFRC522::STATUS_OK) {
    Serial.print("Write failed at page ");
    Serial.print(page);
    Serial.print(": ");
    Serial.println(mfrc522.GetStatusCodeName(status));
    return false;
  }
  return true;
}

void readCardMemoryMifare() {
  // Mifare style reading.
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

bool isValidDepleted(const String& depleted) {
  return depleted == "DEPLETED" || depleted == "ACTIVE";
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
    if(argument == "ALL"){
      int all_blocks[] = {4, 5, 6, 8, 9, 10, 12};
      memcpy(blocks_to_read, all_blocks, sizeof(all_blocks));
    } else {
      int single_block[] = {argument.toInt()};
      memcpy(blocks_to_read, single_block, sizeof(single_block));
    }
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
    sample_type_to_write = argument;  // Store data for writing
  } else if (keyword == "WRITEDEPLETION") {
    if(!isValidDepleted(argument)){
      Serial.println("Unknown depletionstate");
      return;
    }
    depleted_to_write = argument;
  } else if (keyword == "WRITESAMPLE") {
    handleWriteSample(argument);
  } else {
    Serial.println("Unknown command");
  }
}

void handleWriteSample(String args) {
  int index1 = args.indexOf(' ');
  int index2 = args.indexOf(' ', index1 + 1);
  int index3 = args.indexOf(' ', index2 + 1);
  int index4 = args.indexOf(' ', index3 + 1);
  int index5 = args.indexOf(' ', index4 + 1);
  int index6 = args.indexOf(' ', index5 + 1);
  
  // Validate minimum required parameters
  if (index1 == -1 || index2 == -1 || index3 == -1 || index4 == -1) {
    Serial.println("Invalid WRITESAMPLE format. Usage: WRITESAMPLE {sample_type} {primary_action} {primary_target} {secondary_action} {secondary_target} [purity] [depleted]");
    return;
  }

  // Extract required parameters
  String sample_type = args.substring(0, index1);
  String primary_action = args.substring(index1 + 1, index2);
  String primary_target = args.substring(index2 + 1, index3);
  String secondary_action = args.substring(index3 + 1, index4);
  String secondary_target = args.substring(index4 + 1, index5);

  // Optional parameters
  String purity = "";
  String depleted = "";

  // Validation
  if (sample_type != "RAW" && sample_type != "REFINED") {
    Serial.println("Invalid sample type. Use RAW or REFINED.");
    return;
  }
  if (sample_type == "RAW") {
    if(index5 != -1) {
      depleted = args.substring(index5 + 1);
    }
    purity = "!"; // This will actually set it to be empty while writing 
  } else {
    purity = args.substring(index5 + 1, index6);
    if(index6 != -1) {
      depleted = args.substring(index6 + 1);
    }
  }
  
  if (!isValidAction(primary_action) || !isValidAction(secondary_action)) {
    Serial.println("Invalid action detected.");
    return;
  }

  if (!isValidTarget(primary_target) || !isValidTarget(secondary_target)) {
    Serial.println("Invalid target detected.");
    return;
  }

  // Specific validation for REFINED
  if (sample_type == "REFINED") {
    if (purity == "") {
      Serial.println("Purity is required for REFINED samples.");
      return;
    }
    if (!isValidPurity(purity)) {
      Serial.println("Invalid purity value.");
      return;
    }
  }

  if (depleted == "") {
    depleted = "ACTIVE"; // Set the default value
  }
  if (depleted != "" && !isValidDepleted(depleted)) {
    Serial.print("Invalid depleted value: ");
    Serial.println(depleted);
    return;
  }

  // Assign values to global variables
  sample_type_to_write = sample_type;
  primary_action_to_write = primary_action;
  primary_target_to_write = primary_target;
  secondary_action_to_write = secondary_action;
  secondary_target_to_write = secondary_target;
  purity_to_write = purity;
  depleted_to_write = depleted;
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

/**
 * Write data to mifare styled memory
 */
bool writeDataToBlock(int blockNum, byte blockData[]) {
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
  // Serial.println("Writing complete! ");
  return true;
}

bool writeCardMemory(int blockNum, String data) {
  if(is_ntag){
    return writeLargeStringToNTAG(blockNum, data);
  } else {
    byte blockData[16]; // 16 bytes for the block
    data.getBytes(blockData, 16); // Copy the string to the byte array
    // Fill the rest of the block with empty data
    for (int i = data.length(); i < 16; i++) {
      blockData[i] = '\0';
    }
  
    ignore_card_remove_event = true; // This prevents a tag lost & found spam after every operation
    return writeDataToBlock(blockNum, blockData);
  }
}

void detectCardType() {
  MFRC522::PICC_Type piccType = mfrc522.PICC_GetType(mfrc522.uid.sak);
  // Some debug prints
  if(printCardType) { 
    Serial.print(F("PICC type: "));
    MFRC522::PICC_Type piccType = mfrc522.PICC_GetType(mfrc522.uid.sak);
    Serial.println(mfrc522.PICC_GetTypeName(piccType));
  }
  if (piccType == MFRC522::PICC_TYPE_MIFARE_1K) {
    Serial.println("MIFARE Classic detected.");
    activeMapping = mifareMapping;
    is_ntag = false;
  } else if (piccType == MFRC522::PICC_TYPE_MIFARE_UL) {
    Serial.println("NTAG detected.");
    is_ntag = true;
    activeMapping = ntagMapping;
  } else {
    Serial.println("Unknown card type.");
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

        detectCardType();
        
        if (printMemory) {
          if(is_ntag) {
             readCardMemoryNTAG();
          } else {
            readCardMemoryMifare();
          }
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
        writeCardMemory(activeMapping.sample_type, data_to_write);
      } 

      if(sample_type_to_write != "") {
        writeCardMemory(activeMapping.sample_type, sample_type_to_write);
        sample_type_to_write = "";
      } 
      if(primary_action_to_write != "") {
        writeCardMemory(activeMapping.primary_action, primary_action_to_write);
        primary_action_to_write = "";
      }
      if(primary_target_to_write != "") {
        writeCardMemory(activeMapping.primary_target, primary_target_to_write);
        primary_target_to_write = "";
      }

      if(secondary_action_to_write != "") {
        writeCardMemory(activeMapping.secondary_action, secondary_action_to_write);
        secondary_action_to_write = "";
      }
      if(secondary_target_to_write != "") {
        writeCardMemory(activeMapping.secondary_target, secondary_target_to_write);
        secondary_target_to_write = "";
      }

      if(depleted_to_write != "") {
        writeCardMemory(activeMapping.depleted, depleted_to_write);
        depleted_to_write = "";
      }

      if(purity_to_write != "") {
        if(purity_to_write == "!") { // Special case, since we use empty strings as a way to check if we should do something, we use "!" as indication that stuff needs to be deleted
          writeCardMemory(activeMapping.purity, "");
        } else {
          writeCardMemory(activeMapping.purity, purity_to_write);
        }
        purity_to_write = "";
      }

      bool dataRead = false;
      bool firstBlock = true;

      for (int i = 0; i < sizeof(blocks_to_read) / sizeof(blocks_to_read[0]); i++) {
        if (blocks_to_read[i] == 0) break;
        int current_block = blocks_to_read[i];
        String blockData = readBlock(current_block);
    
        if (!firstBlock) {
          Serial.print(" ");  // Print space between blocks, but not before the first one
        }
        
        Serial.print(blockData);
        dataRead = true;
        firstBlock = false;  // After the first block, add spaces for subsequent blocks
    
        ignore_card_remove_event = true;
      }
      
      if (dataRead) {
        memset(blocks_to_read, 0, sizeof(blocks_to_read)); // Reset blocks_to_read after reading
        Serial.println();
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

bool isValidPurity(const String& purity) {
  for (const char* validPurity : validPurities) {
    if (purity.equals(validPurity)) {
        return true;
    }
  }
  return false;
}

bool isValidVulgarity(const String& vulgarity) {
  for (const char* validVulgarity : validVulgarities) {
    if (vulgarity.equals(validVulgarity)) {
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
